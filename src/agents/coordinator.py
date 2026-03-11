from deepagents import create_deep_agent
from langchain_google_vertexai import ChatVertexAI

def run_extraction_workflow(document_url: str) -> dict:
    """
    Workflow principal. 
    1. Télécharge/Parse le PDF (Liasse EDI).
    2. Utilise `deepagents` pour spawner des sous-agents dédiés.
    """
    # LLM Initialization
    llm = ChatVertexAI(model_name="gemini-2.5-flash")
    
    # Définition des tools (qui peuvent être eux-mêmes des sous-agents LangChain)
    def extract_revenue(text: str) -> dict:
        """Extrait le Chiffre d'Affaires du feuillet 2052/2053."""
        # Logique de sous-agent ici
        from agents.ca_agent import get_ca
        return {"chiffre_affaires": get_ca(text)}

    def extract_equity(text: str) -> dict:
        """Extrait les Capitaux Propres du Passif (feuillet 2051)."""
        from agents.equity_agent import get_equity
        return {"capitaux_propres": get_equity(text)}

    def extract_net_income(text: str) -> dict:
        """Extrait le Résultat de l'exercice (Bénéfice/Perte)."""
        from agents.income_agent import get_income
        return {"resultat_exercice": get_income(text)}

    # Création du Deep Agent coordinateur
    coordinator = create_deep_agent(
        model=llm,
        tools=[extract_revenue, extract_equity, extract_net_income],
        system_prompt=(
            "Tu es un expert-comptable superviseur. Ton but est d'extraire les données financières "
            "d'une Liasse Fiscale EDI. Utilise tes outils spécialisés pour extraire le CA, "
            "les capitaux propres et le résultat de l'exercice. Retourne un JSON consolidé."
        )
    )

    # Simulation d'extraction de texte PDF
    from utils.pdf_parser import extract_text_from_pdf
    document_text = extract_text_from_pdf(document_url)
    
    response = coordinator.invoke({
        "messages": [
            {"role": "user", "content": f"Extrais les 3 KPIs financiers de cette liasse : {document_text}"}
        ]
    })
    
    # Parser la réponse du LLM pour garantir le format JSON
    return response["messages"][-1].content
