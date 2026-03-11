from abc import ABC, abstractmethod

class IDocumentParser(ABC):
    @abstractmethod
    def extract_text(self, document_url: str) -> str:
        pass

class IFinancialAgent(ABC):
    @abstractmethod
    def extract_chiffre_affaires(self, text: str) -> float:
        pass
        
    @abstractmethod
    def extract_capitaux_propres(self, text: str) -> float:
        pass
        
    @abstractmethod
    def extract_resultat_exercice(self, text: str) -> float:
        pass
