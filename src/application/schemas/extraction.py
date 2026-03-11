from pydantic import BaseModel, Field
from typing import Optional

class ExtractionOutput(BaseModel):
    chiffre_affaires: Optional[float] = Field(
        default=None, 
        description="Le montant du chiffre d'affaires extrait. Doit être un nombre."
    )
    capitaux_propres: Optional[float] = Field(
        default=None, 
        description="Le montant des capitaux propres extraits. Doit être un nombre, peut être négatif."
    )
    resultat_exercice: Optional[float] = Field(
        default=None, 
        description="Le résultat de l'exercice extrait (bénéfice ou perte). Doit être un nombre, positif pour bénéfice, négatif pour perte."
    )
