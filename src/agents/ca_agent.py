def get_ca(text: str) -> float:
    """
    Sous-agent spécialisé pour extraire le chiffre d'affaires.
    [SPECULATIVE] Idéalement, on utiliserait un agent LangChain spécifique ici 
    avec le prompt concentré sur les feuillets 2052/2053.
    """
    # TODO: Connect to an LLM chain strictly focused on CA
    # For now, returning a mock value
    return 1500000.0
