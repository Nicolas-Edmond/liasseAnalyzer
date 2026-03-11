import os
import sys
import glob
import logging
import json
from dotenv import load_dotenv

# Configuration du logging détaillé pour voir ce que fait l'agent/le workflow
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("test_local.log")
    ]
)
logger = logging.getLogger("TestLocal")

# Ajout du dossier src au PYTHONPATH pour les imports relatifs
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from infrastructure.document_parser import PyMuPDFDocumentParser
from infrastructure.agents.financial_agent import DeepAgentsFinancialAgent
from application.workflow import ExtractionWorkflow

def test_file(test_pdf: str, workflow: ExtractionWorkflow):
    logger.info(f"\n==============================================")
    logger.info(f"📄 Analyse de : {test_pdf}")
    logger.info(f"==============================================")
    
    if not os.path.exists(test_pdf):
        logger.error(f"❌ Erreur : Le fichier {test_pdf} n'existe pas.")
        return

    logger.info("🧠 Lancement de l'agent... (Veuillez patienter)")
    result = workflow.run(test_pdf)
    
    logger.info("\n📊 RÉSULTATS DE L'EXTRACTION :")
    if result.get("error"):
        logger.error(f"❌ Erreur rencontrée : {result['error']}")
    else:
        logger.info(f"✅ Extraction réussie pour {os.path.basename(test_pdf)} :")
        logger.info(json.dumps({
            "chiffre_affaires": result.get('chiffre_affaires'),
            "capitaux_propres": result.get('capitaux_propres'),
            "resultat_exercice": result.get('resultat_exercice')
        }, indent=4))
        
def main():
    logger.info("🚀 Démarrage du test local Multi-Agents (LangGraph + DeepAgents)...")
    
    # Chargement des variables d'environnement
    load_dotenv()
    
    cred_path = os.getenv("GCP_CREDENTIAL_PATH")
    if cred_path and os.path.exists(cred_path):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = cred_path
        logger.info(f"✅ GOOGLE_APPLICATION_CREDENTIALS set to {cred_path}")
    else:
        logger.warning("⚠️ Warning: Aucune clé GCP trouvée. Assurez-vous d'avoir ADC configuré.")

    logger.info("\n⚙️  Initialisation des composants du Workflow...")
    parser = PyMuPDFDocumentParser()
    agent = DeepAgentsFinancialAgent()
    workflow = ExtractionWorkflow(parser=parser, agent=agent)

    # Récupérer tous les PDF dans le dossier test/
    test_folder = "test/"
    pdf_files = glob.glob(f"{test_folder}*.pdf")
    
    if not pdf_files:
        logger.error(f"❌ Aucun fichier PDF trouvé dans {test_folder}.")
        return
        
    logger.info(f"📁 Trouvé {len(pdf_files)} fichiers à analyser dans '{test_folder}':")
    for file in pdf_files:
        logger.info(f"  - {os.path.basename(file)}")

    # Lancer le workflow sur chaque fichier
    for pdf_file in pdf_files:
        test_file(pdf_file, workflow)
        
    logger.info("\n🏁 Tests terminés sur tous les fichiers. Voir test_local.log pour le détail.")

if __name__ == "__main__":
    main()
