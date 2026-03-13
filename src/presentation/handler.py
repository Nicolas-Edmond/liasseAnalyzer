import json
import os
import traceback
from infrastructure.gcp_secrets import setup_gcp_credentials
from infrastructure.container import create_extraction_workflow
from infrastructure.db import get_analyses_for_user

def lambda_handler(event, context):
    try:
        # Check if request comes from Function URL (RequestContext.Http.Method) or API Gateway (httpMethod)
        http_method = event.get('httpMethod')
        if not http_method and event.get('requestContext', {}).get('http', {}).get('method'):
            http_method = event['requestContext']['http']['method']
            
        if not http_method:
            http_method = 'POST' # Fallback
        
        # Cross-Origin support handles OPTIONS
        if http_method == 'OPTIONS':
            return {
                "statusCode": 200,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "Content-Type",
                    "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
                },
                "body": json.dumps({"message": "OK"})
            }

        setup_gcp_credentials()
        
        if http_method == 'GET':
            return handle_get_analyses(event)
        elif http_method == 'POST':
            return handle_post_analysis(event)
        else:
            return {
                "statusCode": 405,
                "body": json.dumps({"error": f"Method {http_method} not allowed"})
            }
            
    except Exception as e:
        traceback.print_exc()
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}

def handle_get_analyses(event):
    """Gère la requête GET pour récupérer les analyses d'un utilisateur."""
    # Handle both API Gateway and Function URL query parameters
    query_params = event.get('queryStringParameters') or {}
    user_uuid = query_params.get('user_uuid')
    
    if not user_uuid:
        return {
            "statusCode": 400,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"error": "Missing user_uuid parameter"})
        }
        
    try:
        analyses = get_analyses_for_user(user_uuid)
        return {
            "statusCode": 200,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"status": "success", "data": analyses})
        }
    except Exception as e:
        traceback.print_exc()
        return {
            "statusCode": 500,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"error": f"Failed to retrieve analyses: {str(e)}"})
        }

def handle_post_analysis(event):
    """Gère la requête POST pour soumettre un document à analyser."""
    body_str = event.get("body", "{}")
    # Si le body est encodé en base64 (cas avec Function URL parfois), il faudrait le décoder, 
    # mais partons du principe que l'event est du JSON brut pour le moment.
    if event.get("isBase64Encoded", False):
        import base64
        body_str = base64.b64decode(body_str).decode('utf-8')
        
    body = json.loads(body_str)
    
    # Support pour la clé S3 relative (upload front) ou l'URL absolue
    pdf_url = body.get("document_url")
    s3_key = body.get("s3_key")
    user_uuid = body.get("user_uuid")
    file_name = body.get("file_name", s3_key or pdf_url)
    
    if s3_key:
        # Construction de l'URL S3 attendue par PyMuPDFDocumentParser
        bucket = os.getenv("DIRECT_UPLOAD_BUCKET", "formalis-direct-upload-s3")
        pdf_url = f"s3://{bucket}/{s3_key}"
        
    if not pdf_url:
        return {
            "statusCode": 400, 
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"error": "Missing document_url or s3_key in payload"})
        }

    workflow = create_extraction_workflow()
    
    # 4. Exécution du Cas d'Usage Application
    result_state = workflow.run(pdf_url, user_uuid, file_name, s3_key)
    
    if result_state.get("error"):
        return {
            "statusCode": 500, 
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"error": result_state["error"], "analysis_id": result_state.get("analysis_id")})
        }
        
    # 5. Formatage de la Réponse (Presentation serialization)
    return {
        "statusCode": 200,
        "headers": {"Access-Control-Allow-Origin": "*"},
        "body": json.dumps({
            "status": "success",
            "analysis_id": result_state.get("analysis_id"),
            "data": {
                "chiffre_affaires": result_state.get("chiffre_affaires"),
                "capitaux_propres": result_state.get("capitaux_propres"),
                "resultat_exercice": result_state.get("resultat_exercice")
            }
        })
    }
