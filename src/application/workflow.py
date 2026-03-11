from langgraph.graph import StateGraph, START, END
from application.state import WorkflowState
from domain.interfaces import IDocumentParser, IFinancialAgent

class ExtractionWorkflow:
    def __init__(self, parser: IDocumentParser, agent: IFinancialAgent):
        self.parser = parser
        self.agent = agent
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
        try:
            text = self.parser.extract_text(state["document_url"])
            return {"document_text": text}
        except Exception as e:
            return {"error": f"Erreur de parsing PDF: {str(e)}"}

    def extract_metrics_node(self, state: WorkflowState) -> dict:
        if state.get("error"):
            return {}
        
        text = state["document_text"]
        
        try:
            metrics = self.agent.extract_metrics(text)
            return {
                "chiffre_affaires": metrics.get("chiffre_affaires"),
                "capitaux_propres": metrics.get("capitaux_propres"),
                "resultat_exercice": metrics.get("resultat_exercice")
            }
        except Exception as e:
            return {"error": f"Erreur d'extraction agentique: {str(e)}"}

    def run(self, document_url: str) -> dict:
        initial_state = WorkflowState(
            document_url=document_url,
            document_text="",
            chiffre_affaires=None,
            capitaux_propres=None,
            resultat_exercice=None,
            error=None
        )
        return self.graph.invoke(initial_state)
