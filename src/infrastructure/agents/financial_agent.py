"""
Agent financier utilisant Deep Agents avec Skills natifs (progressive disclosure).
Conforme à la spec Agent Skills : https://agentskills.io/specification
"""
import os
import uuid
import logging
from domain.interfaces import IFinancialAgent
from deepagents import create_deep_agent
from langchain_google_vertexai import ChatVertexAI
from langgraph.checkpoint.memory import MemorySaver

from application.schemas.extraction import ExtractionOutput
from .skills_loader import load_skills_files, get_skills_path

logger = logging.getLogger(__name__)


class DeepAgentsFinancialAgent(IFinancialAgent):
    """
    Extrait CA, capitaux propres et résultat via un Deep Agent
    dont les compétences sont chargées au format SKILL.md (Agent Skills spec).
    """

    def __init__(self):
        self.model_name = os.getenv("GCP_MODEL_NAME", "gemini-2.5-flash")
        self._checkpointer = MemorySaver()

    def _get_llm(self):
        return ChatVertexAI(model_name=self.model_name, temperature=0.0)

    def extract_metrics(self, text: str) -> dict:
        llm = self._get_llm()
        structured_llm = llm.with_structured_output(ExtractionOutput)

        system_prompt = (
            "Tu es un expert-comptable. Extraits les 3 métriques suivantes d'une Liasse Fiscale EDI : "
            "1. Chiffre d'Affaires (ventes marchandises + production vendue UNIQUEMENT, pas autres produits ; 0 si vide), "
            "2. Capitaux Propres, "
            "3. Résultat de l'Exercice (bénéfice=positif, perte=négatif). "
            "Utilise tes skills pour connaître les règles d'extraction. "
            "Retourne ensuite les valeurs numériques structurées."
        )

        agent = create_deep_agent(
            model=llm,
            skills=[get_skills_path()],
            system_prompt=system_prompt,
            checkpointer=self._checkpointer,
        )

        safe_text = text[:800000]
        prompt_user = (
            "Voici le texte de la liasse fiscale :\n\n"
            f"{safe_text}\n\n"
            "Analyse et extrais les 3 métriques demandées en suivant tes skills."
        )

        skills_files = load_skills_files()
        logger.info("Invoking DeepAgent with native skills (progressive disclosure)...")

        response = agent.invoke(
            {
                "messages": [{"role": "user", "content": prompt_user}],
                "files": skills_files,
            },
            config={"configurable": {"thread_id": str(uuid.uuid4())}},
        )

        # Appel structuré final pour forcer le format Pydantic
        final_messages = response["messages"] + [
            {"role": "user", "content": "Renvoie l'objet structuré final avec chiffre_affaires, capitaux_propres, resultat_exercice (float ou null)."}
        ]
        structured_result: ExtractionOutput = structured_llm.invoke(final_messages)

        logger.info(f"Structured extraction result: {structured_result.model_dump()}")
        return structured_result.model_dump()
