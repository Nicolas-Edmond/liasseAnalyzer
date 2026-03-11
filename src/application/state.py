from typing import TypedDict, Optional

class WorkflowState(TypedDict):
    document_url: str
    document_text: str
    chiffre_affaires: Optional[float]
    capitaux_propres: Optional[float]
    resultat_exercice: Optional[float]
    error: Optional[str]
