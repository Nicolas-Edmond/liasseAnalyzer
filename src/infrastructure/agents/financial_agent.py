import os
import json
import logging
from domain.interfaces import IFinancialAgent
from deepagents import create_deep_agent
from langchain_google_vertexai import ChatVertexAI
from langchain.tools import tool
from .skills import load_skill_prompt
from application.schemas.extraction import ExtractionOutput

logger = logging.getLogger(__name__)

@tool
def load_skill(skill_name: str) -> str:
    """Charge les règles et connaissances spécifiques pour extraire une métrique financière depuis des fichiers Markdown.
    Compétences disponibles (skill_name) :
    - 'chiffre_affaires' : Outil pour comprendre comment extraire le CA (fichiers liasses 2052/2033-B).
    - 'capitaux_propres' : Outil pour comprendre comment extraire les capitaux propres (fichiers liasses 2051/2033-A).
    - 'resultat_exercice' : Outil pour comprendre comment extraire le résultat (fichiers liasses 2051/2053 ou 2033-A/2033-B).
    """
    logger.info(f"Agent is loading skill: {skill_name}")
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
        Utilise structured_output de Gemini pour garantir le format de sortie Pydantic.
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
            "ÉTAPE 3 : Extrait avec précision les valeurs numériques."
        )

        llm = self._get_llm()
        # On utilise LLM.with_structured_output pour forcer le schéma Pydantic
        structured_llm = llm.with_structured_output(ExtractionOutput)

        # Création de l'agent
        # On passe le LLM standard à l'agent pour qu'il puisse utiliser les tools
        # puis on fera un appel final structuré
        agent = create_deep_agent(
            model=llm,
            tools=[load_skill],
            system_prompt=system_prompt,
        )
        
        safe_text = text[:800000] # Limite arbitraire safe
        
        prompt_user = (
            "Voici le texte de la liasse fiscale :\n\n"
            f"{safe_text}\n\n"
            "Analyse ce texte en utilisant tes outils pour comprendre comment faire."
        )

        logger.info("Invoking DeepAgent to analyze the document with tools...")
        # L'agent réfléchit et utilise les tools
        response = agent.invoke({
            "messages": [{"role": "user", "content": prompt_user}]
        })
        
        # On passe tout l'historique (réflexion de l'agent + document)
        # pour forcer la sortie structurée finale via Pydantic
        logger.info("Generating structured output via Pydantic schema...")
        final_messages = response["messages"] + [
            {"role": "user", "content": "Maintenant, renvoie uniquement l'objet structuré final avec les 3 métriques extraites (ou null si introuvable)."}
        ]
        
        structured_result: ExtractionOutput = structured_llm.invoke(final_messages)
        
        logger.info(f"Structured extraction result: {structured_result.model_dump()}")
        return structured_result.model_dump()
