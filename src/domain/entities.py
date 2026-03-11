from pydantic import BaseModel
from typing import Optional

class FinancialMetrics(BaseModel):
    chiffre_affaires: Optional[float] = None
    capitaux_propres: Optional[float] = None
    resultat_exercice: Optional[float] = None

class ExtractionRequest(BaseModel):
    document_url: str
