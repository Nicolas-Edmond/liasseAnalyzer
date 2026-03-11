import os
import sys
from dotenv import load_dotenv

# Ajout du dossier src au PYTHONPATH pour les imports relatifs
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from infrastructure.document_parser import PyMuPDFDocumentParser
from infrastructure.agents.financial_agent import DeepAgentsFinancialAgent
from application.workflow import ExtractionWorkflow

def main():
    print("🚀 Démarrage du test local Multi-Agents (LangGraph + DeepAgents)...")
    
    # Chargement des variables d'environnement (GCP_PROJECT_ID, GOOGLE_APPLICATION_CREDENTIALS, etc.)
    load_dotenv()
    
    # On force le chemin des credentials si défini dans le .env custom
    cred_path = os.getenv("GCP_CREDENTIAL_PATH")
    if cred_path and os.path.exists(cred_path):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = cred_path
        print(f"✅ GOOGLE_APPLICATION_CREDENTIALS set to {cred_path}")
    else:
        print("⚠️ Warning: Aucune clé GCP trouvée. Assurez-vous d'avoir ADC configuré.")

    # Choix du PDF de test
    test_pdf = "test/JULIA_WEILLER_SAS-IS-Simplifié-2023.pdf"
    print(f"\n📄 Fichier à analyser : {test_pdf}")
    
    if not os.path.exists(test_pdf):
        print(f"❌ Erreur : Le fichier {test_pdf} n'existe pas.")
        return

    print("\n⚙️  Initialisation du Workflow...")
    parser = PyMuPDFDocumentParser()
    agent = DeepAgentsFinancialAgent()
    workflow = ExtractionWorkflow(parser=parser, agent=agent)

    print("🧠 Lancement de l'agent... (Veuillez patienter)")
    result = workflow.run(test_pdf)
    
    print("\n📊 RÉSULTATS DE L'EXTRACTION :")
    if result.get("error"):
        print(f"❌ Erreur rencontrée : {result['error']}")
    else:
        print("✅ Extraction réussie :")
        print(f"   - Chiffre d'Affaires : {result.get('chiffre_affaires')} €")
        print(f"   - Capitaux Propres   : {result.get('capitaux_propres')} €")
        print(f"   - Résultat de l'exo  : {result.get('resultat_exercice')} €")

if __name__ == "__main__":
    main()
