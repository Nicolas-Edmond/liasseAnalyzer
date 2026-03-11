import fitz  # PyMuPDF
import boto3
import urllib.request
import tempfile
import os

s3_client = boto3.client('s3')

def extract_text_from_pdf(document_url: str) -> str:
    """
    Télécharge et parse un PDF depuis S3 ou une URL publique.
    Retourne le texte consolidé.
    """
    try:
        if document_url.startswith("s3://"):
            # S3 url: s3://bucket-name/path/to/file.pdf
            parts = document_url.replace("s3://", "").split("/", 1)
            bucket = parts[0]
            key = parts[1]
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                s3_client.download_file(bucket, key, tmp.name)
                local_path = tmp.name
        else:
            # URL HTTP/HTTPS
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                urllib.request.urlretrieve(document_url, tmp.name)
                local_path = tmp.name

        text = ""
        with fitz.open(local_path) as doc:
            for page in doc:
                text += page.get_text()
                
        os.remove(local_path)
        return text

    except Exception as e:
        print(f"Error extracting PDF: {e}")
        return "Erreur d'extraction du document."
