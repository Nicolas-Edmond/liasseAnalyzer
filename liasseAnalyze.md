# 🚀 Liasse EDI Analyze - Architecture Multi-Agents & Déploiement

Ce document détaille l'architecture agentique, l'IaC (AWS SAM) et la conteneurisation (Docker) pour le service `liasse-analyze`. L'objectif est d'analyser des Liasses Fiscales EDI (Impôt sur les Sociétés) pour extraire précisément :
1. **Le Chiffre d'Affaires**
2. **Les Capitaux Propres**
3. **Le Résultat de l'Exercice (Bénéfice/Perte)**

---

## 🤖 1. Architecture Agentique (LangChain & Deep Agents)

Plutôt qu'un simple prompt "fourre-tout", on utilise un workflow agentique où un Agent Coordinateur "spawn" des sous-agents hyper-spécialisés pour chaque métrique financière. Cela réduit les hallucinations et permet un focus total sur des feuillets spécifiques de la liasse (ex: feuillet 2052 pour le Bilan Passif, feuillet 2053 pour le Compte de Résultat).

### 📚 Documentation de Référence
La stack repose sur les frameworks officiels suivants :
- [LangChain Overview](https://docs.langchain.com/oss/python/langchain/overview) : Framework de base pour l'interface LLM et les abstractions.
- [Deep Agents Overview](https://docs.langchain.com/oss/python/deepagents/overview) : Pour la gestion avancée du contexte, le routing, et le spawning de sous-agents spécialisés.

---

## 📁 2. Structure du Repo

```bash
liasse-analyze/
├── src/
│   ├── __init__.py
│   ├── app.py                 # Point d'entrée Lambda (handler)
│   ├── agents/                # Logique Multi-Agents (LangChain/DeepAgents)
│   │   ├── __init__.py
│   │   ├── coordinator.py     # Agent principal qui délègue
│   │   ├── ca_agent.py        # Spécialiste Chiffre d'Affaires
│   │   ├── equity_agent.py    # Spécialiste Capitaux Propres
│   │   └── income_agent.py    # Spécialiste Résultat de l'exercice
│   ├── utils/                 # Helpers (gcp_config, s3, parsers PDF)
│   └── requirements.txt       # langchain, deepagents, google-cloud-secret-manager, etc.
├── .env                       # Variables locales (ignoré par git)
├── .gitignore
├── Dockerfile                 # Définition de l'image Lambda
├── template.yaml              # Infra AWS SAM
└── samconfig.toml             # Config de déploiement SAM
```

---

## 🔐 3. Gestion des Credentials (GCP -> AWS Secrets)

Les LLMs (Gemini via VertexAI) nécessitent un Service Account GCP. Ce JSON ne doit **jamais** être commité.
En production, il vit dans **AWS Secrets Manager**.

Dans ton `.env` local :
```env
GOOGLE_APPLICATION_CREDENTIALS=/var/task/credentials.json
GCP_PROJECT_ID=formalis-423312
```

---

## 🏗️ 4. Infrastructure as Code (AWS SAM)

Fichier `template.yaml`. Package Docker indispensable vu le poids de LangChain et des librairies de parsing PDF.

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31
Description: >
  liasse-analyze
  Extraction Agentique de Liasse EDI (CA, Capitaux Propres, Résultat) via LangChain/DeepAgents.

Globals:
  Function:
    Timeout: 300 # 5 minutes max (les workflows multi-agents prennent du temps)
    MemorySize: 2048 # LangChain + PDF en RAM nécessite un peu de marge
    Environment:
      Variables:
        GCP_PROJECT_ID: formalis-423312
        GCP_SECRET_NAME: !Ref GcpCredentialsSecret

Resources:
  GcpCredentialsSecret:
    Type: AWS::SecretsManager::Secret
    Properties:
      Name: formalis/liasse-analyze/gcp-credentials
      Description: "Service account GCP pour Gemini / VertexAI"

  LiasseAnalyzeFunction:
    Type: AWS::Serverless::Function
    Properties:
      PackageType: Image
      Architectures:
        - x86_64
      Policies:
        - Statement:
            - Effect: Allow
              Action:
                - secretsmanager:GetSecretValue
              Resource: !Ref GcpCredentialsSecret
      Events:
        ApiEvent:
          Type: Api
          Properties:
            Path: /analyze/edi
            Method: post
    Metadata:
      Dockerfile: Dockerfile
      DockerContext: .
      DockerTag: python3.11-v1

Outputs:
  LiasseAnalyzeApi:
    Description: "API Gateway endpoint URL"
    Value: !Sub "https://${ServerlessRestApi}.execute-api.${AWS::Region}.amazonaws.com/Prod/analyze/edi/"
```

---

## 🐳 5. Conteneurisation (Dockerfile)

Fichier `Dockerfile`.

```dockerfile
FROM public.ecr.aws/lambda/python:3.11

COPY src/requirements.txt ${LAMBDA_TASK_ROOT}

# Installation incluant langchain, deepagents, pdfplumber/pymupdf, etc.
RUN pip install -r requirements.txt --no-cache-dir

COPY src/ ${LAMBDA_TASK_ROOT}/

CMD [ "app.lambda_handler" ]
```

---

## 🐍 6. Code Lambda & Implémentation Agentique

### `src/app.py` (Lambda Handler)
Récupère les secrets et lance l'Agent Coordinateur.

```python
import os
import json
import boto3
from google.oauth2 import service_account
from agents.coordinator import run_extraction_workflow

secrets_client = boto3.client('secretsmanager')

def get_gcp_credentials():
    if os.path.exists("credentials.json"):
        return service_account.Credentials.from_service_account_file("credentials.json")
    
    secret_name = os.environ.get('GCP_SECRET_NAME')
    response = secrets_client.get_secret_value(SecretId=secret_name)
    return service_account.Credentials.from_service_account_info(json.loads(response['SecretString']))

def lambda_handler(event, context):
    try:
        gcp_creds = get_gcp_credentials()
        # Set pour LangChain/VertexAI
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = gcp_creds._service_account_email # Mock ou set path si écrit sur /tmp
        
        body = json.loads(event.get("body", "{}"))
        pdf_url = body.get("document_url")
        
        if not pdf_url:
            return {"statusCode": 400, "body": json.dumps({"error": "Missing document_url"})}

        # Lancement du workflow Multi-Agents (DeepAgents / LangChain)
        extraction_result = run_extraction_workflow(pdf_url)
        
        return {
            "statusCode": 200,
            "body": json.dumps({
                "status": "success",
                "data": extraction_result
            }),
        }
    except Exception as e:
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}
```

### `src/agents/coordinator.py` (Exemple d'implémentation LangChain/DeepAgents)
*\[SPECULATIVE\]* - Architecture de base utilisant les concepts Deep Agents pour le routage.

```python
from deepagents import create_deep_agent
from langchain.chat_models import ChatVertexAI

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
        return {"chiffre_affaires": 1500000}

    def extract_equity(text: str) -> dict:
        """Extrait les Capitaux Propres du Passif (feuillet 2051)."""
        return {"capitaux_propres": 350000}

    def extract_net_income(text: str) -> dict:
        """Extrait le Résultat de l'exercice (Bénéfice/Perte)."""
        return {"resultat_exercice": 45000}

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
    document_text = f"Contenu de la liasse EDI téléchargée depuis {document_url}..."
    
    response = coordinator.invoke({
        "messages": [
            {"role": "user", "content": f"Extrais les 3 KPIs financiers de cette liasse : {document_text}"}
        ]
    })
    
    # Parser la réponse du LLM pour garantir le format JSON
    return response["messages"][-1].content
```

---

## 🚀 7. Configuration de déploiement (`samconfig.toml`)

```toml
version = 0.1

[default]
[default.deploy]
[default.deploy.parameters]
stack_name = "liasse-edi-analyze-stack"
region = "eu-west-3"
capabilities = "CAPABILITY_IAM"
confirm_changeset = true
resolve_s3 = true
resolve_image_repos = true
image_repositories = []
```

---

## 🛠️ 8. Commandes Utiles

**Build & Run Local :**
```bash
sam build
sam local start-api -p 3000 --env-vars .env.json
```

**Test avec Curl :**
```bash
curl -X POST http://localhost:3000/analyze/edi \
  -H "Content-Type: application/json" \
  -d '{"document_url": "s3://bucket/liasse-edi-2023.pdf"}'
```

**Déploiement AWS :**
```bash
sam deploy --guided # Première fois
sam build && sam deploy # Fois suivantes
```
