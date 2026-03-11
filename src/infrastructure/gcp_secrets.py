import os
import json
import boto3
from google.oauth2 import service_account

def setup_gcp_credentials():
    """Charge les credentials via AWS Secrets Manager."""
    if os.path.exists("credentials.json"):
        creds = service_account.Credentials.from_service_account_file("credentials.json")
    else:
        secret_name = os.environ.get('GCP_SECRET_NAME')
        if not secret_name:
            print("Warning: GCP_SECRET_NAME not set. LLM calls will fail without ADC.")
            return
        
        secrets_client = boto3.client('secretsmanager')
        response = secrets_client.get_secret_value(SecretId=secret_name)
        creds = service_account.Credentials.from_service_account_info(json.loads(response['SecretString']))
        
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = getattr(creds, '_service_account_email', '')
