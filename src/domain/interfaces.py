from abc import ABC, abstractmethod

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
