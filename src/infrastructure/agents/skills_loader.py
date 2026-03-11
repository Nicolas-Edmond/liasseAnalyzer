"""
Charge les skills au format Agent Skills (SKILL.md) pour le StateBackend.
Compatible Lambda et local : les fichiers sont lus depuis le disque et passés via invoke(files=...).
"""
from pathlib import Path
from deepagents.backends.utils import create_file_data

SKILLS_ROOT = Path(__file__).parent / "skills"
VIRTUAL_PREFIX = "/skills"


def load_skills_files() -> dict:
    """
    Parcourt skills/<name>/SKILL.md et retourne un dict prêt pour agent.invoke(files=...).
    Les clés sont des chemins virtuels (/skills/<name>/SKILL.md) attendus par le StateBackend.
    """
    files = {}
    if not SKILLS_ROOT.exists():
        return files

    for skill_dir in SKILLS_ROOT.iterdir():
        if not skill_dir.is_dir():
            continue
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            continue

        content = skill_md.read_text(encoding="utf-8")
        virtual_path = f"{VIRTUAL_PREFIX}/{skill_dir.name}/SKILL.md"
        files[virtual_path] = create_file_data(content)

    return files


def get_skills_path() -> str:
    """Retourne le chemin virtuel des skills pour create_deep_agent(skills=[...])."""
    return f"{VIRTUAL_PREFIX}/"
