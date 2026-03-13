from abc import ABC, abstractmethod
from typing import Optional

class IDocumentParser(ABC):
    @abstractmethod
    def extract_text(self, document_url: str) -> str:
        pass

class IFinancialAgent(ABC):
    @abstractmethod
    def extract_metrics(self, text: str) -> dict:
        """
        Doit retourner un dictionnaire contenant :
        - chiffre_affaires (float)
        - capitaux_propres (float)
        - resultat_exercice (float)
        """
        pass

class IAnalysisRepository(ABC):
    @abstractmethod
    def create_analysis(self, user_uuid: str, file_name: str, s3_key: str) -> str:
        pass

    @abstractmethod
    def update_status(self, analysis_id: str, status: str, extracted_data: Optional[dict] = None, error_message: Optional[str] = None):
        pass

    @abstractmethod
    def get_by_user(self, user_uuid: str) -> list:
        pass
