import os
from domain.interfaces import IFinancialAgent
from deepagents import create_deep_agent
from langchain_google_vertexai import ChatVertexAI

class DeepAgentsFinancialAgent(IFinancialAgent):
    def __init__(self):
        # Lazy load pour éviter les soucis de credentials à l'import
        self.model_name = "gemini-2.5-flash"
        
    def _get_llm(self):
        return ChatVertexAI(model_name=self.model_name, temperature=0)

    def _run_agent(self, text: str, prompt: str) -> float:
        # [SPECULATIVE] Wrapper métier via deepagents
        agent = create_deep_agent(
            model=self._get_llm(),
            system_prompt=prompt
        )
        
        # Sécurisation : on passe une partie du texte si trop grand
        response = agent.invoke({"messages": [{"role": "user", "content": text[:30000]}]}) 
        
        try:
            content = response["messages"][-1].content.strip().replace(" ", "").replace(",", ".")
            return float(content)
        except (ValueError, TypeError, KeyError):
            return 0.0

    def extract_chiffre_affaires(self, text: str) -> float:
        prompt = "Tu es expert comptable. Extrait UNIQUEMENT le Chiffre d'Affaires du feuillet 2052/2053 (Liasse EDI). Réponds par un nombre brut, sans texte."
        return self._run_agent(text, prompt)

    def extract_capitaux_propres(self, text: str) -> float:
        prompt = "Tu es expert comptable. Extrait UNIQUEMENT les Capitaux Propres du feuillet 2051. Réponds par un nombre brut, sans texte."
        return self._run_agent(text, prompt)

    def extract_resultat_exercice(self, text: str) -> float:
        prompt = "Tu es expert comptable. Extrait UNIQUEMENT le Résultat de l'exercice. Réponds par un nombre brut, sans texte."
        return self._run_agent(text, prompt)
