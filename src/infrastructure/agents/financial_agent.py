import os
import json
from domain.interfaces import IFinancialAgent
from deepagents import create_deep_agent
from langchain_google_vertexai import ChatVertexAI
from langchain.tools import tool
from .skills import load_skill_prompt

@tool
def load_skill(skill_name: str) -> str:
    """Charge les règles et connaissances spécifiques pour extraire une métrique financière depuis des fichiers Markdown.
    Compétences disponibles (skill_name) :
    - 'chiffre_affaires' : Outil pour comprendre comment extraire le CA (fichiers liasses 2052/2033-B).
    - 'capitaux_propres' : Outil pour comprendre comment extraire les capitaux propres (fichiers liasses 2051/2033-A).
    - 'resultat_exercice' : Outil pour comprendre comment extraire le résultat (fichiers liasses 2051/2053 ou 2033-A/2033-B).
    """
    return load_skill_prompt(skill_name)

class DeepAgentsFinancialAgent(IFinancialAgent):
    def __init__(self):
        # Initialisation lazy pour les tests locaux (credentials via variables d'environnement)
        self.model_name = os.getenv("GCP_MODEL_NAME", "gemini-2.5-flash")
        
    def _get_llm(self):
        # On peut forcer une temperature basse pour plus de déterminisme
        return ChatVertexAI(model_name=self.model_name, temperature=0.0)

    def extract_metrics(self, text: str) -> dict:
        """
        Extrait les 3 KPIs via le pattern Skills (Progressive Disclosure).
        L'agent charge les skills nécessaires puis extrait les données depuis le texte.
        """
        system_prompt = (
            "Tu es un expert-comptable très précis et méticuleux. "
            "Ta mission est d'extraire les 3 métriques suivantes d'une Liasse Fiscale EDI : "
            "1. Chiffre d'Affaires\n"
            "2. Capitaux Propres\n"
            "3. Résultat de l'Exercice\n\n"
            "ÉTAPE 1 : Utilise impérativement l'outil `load_skill` pour chacune de ces 3 métriques "
            "afin de connaître les règles d'extraction exactes (les lignes et feuillets à regarder).\n\n"
            "ÉTAPE 2 : Parcours le document et trouve les montants. "
            "Ne prends que le montant, pas le texte. Attention aux signes (positif/négatif).\n\n"
            "ÉTAPE 3 : Retourne STRICTEMENT un objet JSON valide avec les clés "
            "`chiffre_affaires`, `capitaux_propres`, et `resultat_exercice`. "
            "Les valeurs doivent être de type float ou null si introuvable."
        )

        agent = create_deep_agent(
            model=self._get_llm(),
            tools=[load_skill],
            system_prompt=system_prompt,
        )
        
        # Le contexte peut être large, Gemini 1.5/2.5 a une grande fenêtre de contexte
        # Mais on le tronque par précaution s'il dépasse vraiment les limites
        safe_text = text[:800000] # Limite arbitraire safe
        
        prompt_user = (
            "Voici le texte de la liasse fiscale :\n\n"
            f"{safe_text}\n\n"
            "Analyse ce texte et renvoie moi l'objet JSON contenant les 3 métriques demandées."
        )

        response = agent.invoke({
            "messages": [{"role": "user", "content": prompt_user}]
        })
        
        raw_content = response["messages"][-1].content
        if isinstance(raw_content, list):
            # Handle potential list of blocks (text/tool calls)
            texts = [block.get('text', '') for block in raw_content if isinstance(block, dict) and 'text' in block]
            if not texts:
                texts = [str(block) for block in raw_content if isinstance(block, str)]
            raw_content = "".join(texts)
            
        raw_content = raw_content.strip()
        
        # Nettoyage et parsing du JSON (cas d'hallucination des markdown code blocks)
        if raw_content.startswith("```json"):
            raw_content = raw_content[7:]
        if raw_content.startswith("```"):
            raw_content = raw_content[3:]
        if raw_content.endswith("```"):
            raw_content = raw_content[:-3]
            
        try:
            metrics = json.loads(raw_content)
            return {
                "chiffre_affaires": float(metrics.get("chiffre_affaires", 0.0) or 0.0),
                "capitaux_propres": float(metrics.get("capitaux_propres", 0.0) or 0.0),
                "resultat_exercice": float(metrics.get("resultat_exercice", 0.0) or 0.0)
            }
        except Exception as e:
            print(f"[ERROR] Failed to parse JSON from LLM: {e}")
            print(f"Raw Output: {raw_content}")
            return {"chiffre_affaires": None, "capitaux_propres": None, "resultat_exercice": None}
