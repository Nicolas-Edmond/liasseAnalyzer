from langgraph.graph import StateGraph, START, END
from application.state import WorkflowState
from domain.interfaces import IDocumentParser, IFinancialAgent, IAnalysisRepository
import logging

logger = logging.getLogger(__name__)

class ExtractionWorkflow:
    def __init__(self, parser: IDocumentParser, agent: IFinancialAgent, db: IAnalysisRepository):
        self.parser = parser
        self.agent = agent
        self.db = db
        self.graph = self._build_graph()

    def _build_graph(self):
        builder = StateGraph(WorkflowState)
        
        builder.add_node("parse_document", self.parse_document_node)
        builder.add_node("extract_metrics", self.extract_metrics_node)
        
        builder.add_edge(START, "parse_document")
        builder.add_edge("parse_document", "extract_metrics")
        builder.add_edge("extract_metrics", END)
        
        return builder.compile()

    def parse_document_node(self, state: WorkflowState) -> dict:
        url = state["document_url"]
        analysis_id = state.get("analysis_id")
        
        logger.info(f"LangGraph [parse_document]: Démarrage pour l'URL {url}")
        try:
            if analysis_id:
                self.db.update_status(analysis_id, "PARSING_DOCUMENT")
                
            text = self.parser.extract_text(url)
            logger.info(f"LangGraph [parse_document]: Succès. {len(text)} caractères extraits.")
            
            if analysis_id:
                self.db.update_status(analysis_id, "DOCUMENT_PARSED")
                
            return {"document_text": text}
        except Exception as e:
            logger.error(f"LangGraph [parse_document]: Erreur - {e}")
            if analysis_id:
                self.db.update_status(analysis_id, "ERROR", error_message=f"Erreur de parsing PDF: {str(e)}")
            return {"error": f"Erreur de parsing PDF: {str(e)}"}

    def extract_metrics_node(self, state: WorkflowState) -> dict:
        analysis_id = state.get("analysis_id")
        
        if state.get("error"):
            logger.warning("LangGraph [extract_metrics]: Sauté car erreur présente.")
            return {}
        
        text = state["document_text"]
        logger.info("LangGraph [extract_metrics]: Lancement de l'agent financier...")
        try:
            if analysis_id:
                self.db.update_status(analysis_id, "EXTRACTING_METRICS")
                
            metrics = self.agent.extract_metrics(text)
            logger.info("LangGraph [extract_metrics]: Agent terminé avec succès.")
            
            result_data = {
                "chiffre_affaires": metrics.get("chiffre_affaires"),
                "capitaux_propres": metrics.get("capitaux_propres"),
                "resultat_exercice": metrics.get("resultat_exercice")
            }
            
            if analysis_id:
                self.db.update_status(analysis_id, "COMPLETED", extracted_data=result_data)
                
            return result_data
        except Exception as e:
            logger.error(f"LangGraph [extract_metrics]: Erreur - {e}")
            if analysis_id:
                self.db.update_status(analysis_id, "ERROR", error_message=f"Erreur d'extraction agentique: {str(e)}")
            return {"error": f"Erreur d'extraction agentique: {str(e)}"}

    def run(self, document_url: str, user_uuid: str = None, file_name: str = None, s3_key: str = None) -> dict:
        # Create analysis in DB right at the start if user_uuid is provided
        analysis_id = None
        if user_uuid:
            try:
                analysis_id = self.db.create_analysis(user_uuid, file_name or "Unknown", s3_key or "")
            except Exception as e:
                logger.error(f"Failed to create analysis in DB: {e}")
                
        initial_state = WorkflowState(
            analysis_id=analysis_id,
            document_url=document_url,
            document_text="",
            chiffre_affaires=None,
            capitaux_propres=None,
            resultat_exercice=None,
            error=None
        )
        result = self.graph.invoke(initial_state)
        
        # Add the analysis_id to the result so the handler can return it
        if analysis_id:
            result['analysis_id'] = analysis_id
            
        return result
