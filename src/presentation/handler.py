import json
from infrastructure.gcp_secrets import setup_gcp_credentials
from infrastructure.document_parser import PyMuPDFDocumentParser
from infrastructure.agents.financial_agent import DeepAgentsFinancialAgent
from application.workflow import ExtractionWorkflow

def lambda_handler(event, context):
    try:
        # 1. Config GCP via AWS Secrets (Infra setup)
        setup_gcp_credentials()
        
        # 2. Parsing de la requête HTTP (Presentation parsing)
        body = json.loads(event.get("body", "{}"))
        pdf_url = body.get("document_url")
        
        if not pdf_url:
            return {"statusCode": 400, "body": json.dumps({"error": "Missing document_url"})}

        # 3. Injection de Dépendances (Wiring)
        parser = PyMuPDFDocumentParser()
        agent = DeepAgentsFinancialAgent()
        workflow = ExtractionWorkflow(parser=parser, agent=agent)
        
        # 4. Exécution du Cas d'Usage Application
        result_state = workflow.run(pdf_url)
        
        if result_state.get("error"):
            return {"statusCode": 500, "body": json.dumps({"error": result_state["error"]})}
            
        # 5. Formatage de la Réponse (Presentation serialization)
        return {
            "statusCode": 200,
            "body": json.dumps({
                "status": "success",
                "data": {
                    "chiffre_affaires": result_state.get("chiffre_affaires"),
                    "capitaux_propres": result_state.get("capitaux_propres"),
                    "resultat_exercice": result_state.get("resultat_exercice")
                }
            })
        }
    except Exception as e:
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}
