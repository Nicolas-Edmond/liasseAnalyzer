import os
from pathlib import Path

# Chemins relatifs depuis ce fichier vers les dossiers contenant les prompts .md
SKILLS_DIR = Path(__file__).parent / "skills_prompts"

def load_skill_prompt(skill_name: str) -> str:
    """Charge le contenu d'un fichier .md de compétence (skill) donné."""
    skill_file = SKILLS_DIR / f"{skill_name}.md"
    try:
        if skill_file.exists():
            return skill_file.read_text(encoding="utf-8")
        else:
            return f"Erreur : Le fichier de compétence {skill_name}.md est introuvable."
    except Exception as e:
        return f"Erreur de lecture du skill {skill_name}: {str(e)}"
