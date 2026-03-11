# LiasseAnalyzer

**LiasseAnalyzer** est une application Serverless (AWS Lambda) d'extraction intelligente de données financières à partir de liasses fiscales (format EDI / PDF). 
Elle utilise une architecture pilotée par les modèles (LLMs) via **VertexAI (Gemini 2.5 Flash)** pour extraire de manière déterministe le Chiffre d'Affaires, les Capitaux Propres et le Résultat de l'Exercice.

## 🏗️ Architecture & Technologies

Le projet suit les principes de la **Clean Architecture (Domain-Driven Design)** et s'appuie sur des agents conversationnels et des graphes d'exécution :

- **LangGraph** : Orchestration du workflow d'extraction (`parse_document` $\rightarrow$ `extract_metrics`).
- **Deep Agents** : Moteur agentique pour le raisonnement et l'extraction structurée.
- **Agent Skills (SKILL.md)** : Utilisation de la spec [Agent Skills](https://agentskills.io/specification) avec _progressive disclosure_ pour injecter dynamiquement les règles comptables (ex: exclusion des "autres produits" pour le CA).
- **PyMuPDF (fitz)** : Parsing des documents PDF (support des sources locales, HTTP et Amazon S3).
- **Pydantic** : Validation stricte des schémas d'extraction (`ExtractionOutput`).
- **AWS SAM / Docker** : Déploiement Serverless conteneurisé.

Un diagramme d'architecture détaillé est disponible dans le fichier [`architecture.drawio`](./architecture.drawio) ou via la documentation textuelle [`docs/ARCHITECTURE.md`](./docs/ARCHITECTURE.md).

## 📂 Structure du projet (DDD)

```text
src/
├── domain/                    # Cœur métier (entités, ports/interfaces)
├── application/               # Cas d'usage, graphe d'orchestration (LangGraph)
├── infrastructure/            # Implémentations (Parsers, Agents, Skills, Secrets)
│   ├── agents/
│   │   ├── skills/            # Compétences au format SKILL.md
│   │   ├── financial_agent.py # Agent Deep Agents
│   │   └── skills_loader.py   # Loader de compétences (StateBackend)
│   └── container.py           # Composition Root (Injection de dépendances)
└── presentation/
    └── handler.py             # Point d'entrée AWS Lambda
```

## 🚀 Fonctionnement de l'API

L'application expose un endpoint `POST /analyze/edi` via API Gateway.

### Requête

```json
{
  "document_url": "https://example.com/ma-liasse-fiscale.pdf"
}
```

### Réponse (Succès - 200 OK)

```json
{
  "status": "success",
  "data": {
    "chiffre_affaires": 82890.0,
    "capitaux_propres": 15000.0,
    "resultat_exercice": 4500.0
  }
}
```

## 🛠️ Développement Local

1. **Prérequis** :
   - Python 3.11+
   - AWS SAM CLI
   - Docker (pour le build AWS)
   - Clé de compte de service GCP (pour Vertex AI)

2. **Configuration** :
   Le projet utilise `gcp_secrets.py` pour récupérer les credentials depuis AWS Secrets Manager. Pour faire tourner le code en local, assurez-vous que votre environnement local est authentifié via ADC (`gcloud auth application-default login`) ou que la variable d'environnement `GOOGLE_APPLICATION_CREDENTIALS` est définie.

3. **Exécuter les tests locaux** :
   Un script permet de tester tous les PDF présents dans le dossier `test/` (qui ne sont pas versionnés pour des raisons de confidentialité) :
   ```bash
   python test_local.py
   # Les résultats seront enregistrés dans test_local.log
   ```

## ☁️ Déploiement (AWS SAM)

Le déploiement se fait via **AWS Serverless Application Model (SAM)** avec des conteneurs Docker (nécessaire pour les dépendances natives comme PyMuPDF).

```bash
# 1. Build de l'image Docker
sam build --use-container

# 2. Déploiement sur AWS
sam deploy --guided
```

L'infrastructure provisionne :
- 1 API Gateway
- 1 fonction Lambda (Timeout 5 min, 2GB RAM)
- 1 secret AWS Secrets Manager (`formalis/liasse-analyze/gcp-credentials`) pour les accès à VertexAI.
