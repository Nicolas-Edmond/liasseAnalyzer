import fitz
import boto3
import urllib.request
import tempfile
import os
from domain.interfaces import IDocumentParser

class PyMuPDFDocumentParser(IDocumentParser):
    def __init__(self):
        self.s3_client = boto3.client('s3')

    def extract_text(self, document_url: str) -> str:
        try:
            if document_url.startswith("s3://"):
                parts = document_url.replace("s3://", "").split("/", 1)
                bucket, key = parts[0], parts[1]
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    self.s3_client.download_file(bucket, key, tmp.name)
                    local_path = tmp.name
            else:
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
            raise RuntimeError(f"Failed to parse document: {str(e)}")
