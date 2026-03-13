import os
import json
import boto3
import psycopg2
from psycopg2.extras import RealDictCursor
from domain.interfaces import IAnalysisRepository
from typing import Optional

def get_db_credentials():
    """Charge les credentials depuis AWS Secrets Manager (ou env variables en local)."""
    if os.environ.get("DB_HOST"):
        return {
            "host": os.environ.get("DB_HOST", "15.188.15.186"),
            "user": os.environ.get("DB_USER", "formalisadmin"),
            "password": os.environ.get("DB_PASSWORD", "s8VKtTLjRsF7wxasG3UAwpYlvUT78uTxNP0rGeTLFyAwuoh2LX2pm8T3xWHL"),
            "dbname": os.environ.get("DB_NAME", "formalis"),
            "port": os.environ.get("DB_PORT", "5432")
        }
    
    secret_name = os.environ.get('DB_SECRET_NAME')
    if not secret_name:
        raise ValueError("DB_SECRET_NAME non défini dans les variables d'environnement")
    
    secrets_client = boto3.client('secretsmanager')
    response = secrets_client.get_secret_value(SecretId=secret_name)
    return json.loads(response['SecretString'])

def get_db_connection():
    """Retourne une connexion psycopg2 au format RealDictCursor."""
    creds = get_db_credentials()
    return psycopg2.connect(
        host=creds.get("host"),
        user=creds.get("user"),
        password=creds.get("password"),
        dbname=creds.get("dbname"),
        port=creds.get("port"),
        cursor_factory=RealDictCursor
    )

class PostgresAnalysisRepository(IAnalysisRepository):
    def create_analysis(self, user_uuid: str, file_name: str, s3_key: str) -> str:
        import uuid
        analysis_id = str(uuid.uuid4())
        query = """
        INSERT INTO formalis_liasse_analysis (id, user_uuid, file_name, s3_key, status, created_at, updated_at)
        VALUES (%s, %s, %s, %s, 'PENDING', NOW(), NOW())
        RETURNING id;
        """
        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(query, (analysis_id, user_uuid, file_name, s3_key))
                analysis_id = cur.fetchone()['id']
                conn.commit()
                return analysis_id
        finally:
            conn.close()

    def update_status(self, analysis_id: str, status: str, extracted_data: Optional[dict] = None, error_message: Optional[str] = None):
        query = """
        UPDATE formalis_liasse_analysis
        SET status = %s, 
            extracted_data = COALESCE(%s, extracted_data), 
            error_message = COALESCE(%s, error_message),
            updated_at = NOW()
        WHERE id = %s;
        """
        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(query, (status, json.dumps(extracted_data) if extracted_data else None, error_message, analysis_id))
                conn.commit()
        finally:
            conn.close()

def get_analyses_for_user(user_uuid: str):
    """Récupère toutes les analyses pour un utilisateur (pour la route GET)."""
    query = """
    SELECT id, file_name, s3_key, status, extracted_data, error_message, created_at, updated_at
    FROM formalis_liasse_analysis
    WHERE user_uuid = %s
    ORDER BY created_at DESC;
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(query, (user_uuid,))
            results = []
            for row in cur.fetchall():
                row_dict = dict(row)
                row_dict['id'] = str(row_dict['id'])
                row_dict['created_at'] = row_dict['created_at'].isoformat() if row_dict['created_at'] else None
                row_dict['updated_at'] = row_dict['updated_at'].isoformat() if row_dict['updated_at'] else None
                results.append(row_dict)
            return results
    finally:
        conn.close()
