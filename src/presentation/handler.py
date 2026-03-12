import json
import os
from infrastructure.gcp_secrets import setup_gcp_credentials
from infrastructure.container import create_extraction_workflow

def lambda_handler(event, context):
    try:
        setup_gcp_credentials()
        body = json.loads(event.get("body", "{}"))
        
        # Support pour la clé S3 relative (upload front) ou l'URL absolue
        pdf_url = body.get("document_url")
        s3_key = body.get("s3_key")
        
        if s3_key:
            # Construction de l'URL S3 attendue par PyMuPDFDocumentParser
            bucket = os.getenv("DIRECT_UPLOAD_BUCKET", "formalis-direct-upload-s3")
            pdf_url = f"s3://{bucket}/{s3_key}"
            
        if not pdf_url:
            return {
                "statusCode": 400, 
                "body": json.dumps({"error": "Missing document_url or s3_key in payload"})
            }

        workflow = create_extraction_workflow()
        
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
