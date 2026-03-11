import os
import json
import boto3
from google.oauth2 import service_account
from agents.coordinator import run_extraction_workflow

secrets_client = boto3.client('secretsmanager')

def get_gcp_credentials():
    if os.path.exists("credentials.json"):
        return service_account.Credentials.from_service_account_file("credentials.json")
    
    secret_name = os.environ.get('GCP_SECRET_NAME')
    response = secrets_client.get_secret_value(SecretId=secret_name)
    return service_account.Credentials.from_service_account_info(json.loads(response['SecretString']))

def lambda_handler(event, context):
    try:
        gcp_creds = get_gcp_credentials()
        # Set pour LangChain/VertexAI
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = gcp_creds._service_account_email # Mock ou set path si écrit sur /tmp
        
        body = json.loads(event.get("body", "{}"))
        pdf_url = body.get("document_url")
        
        if not pdf_url:
            return {"statusCode": 400, "body": json.dumps({"error": "Missing document_url"})}

        # Lancement du workflow Multi-Agents (DeepAgents / LangChain)
        extraction_result = run_extraction_workflow(pdf_url)
        
        return {
            "statusCode": 200,
            "body": json.dumps({
                "status": "success",
                "data": extraction_result
            }),
        }
    except Exception as e:
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}
