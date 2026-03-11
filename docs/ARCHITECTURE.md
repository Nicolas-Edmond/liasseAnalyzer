# Architecture liasseAnalyzer

## Vue d'ensemble

Architecture **DDD (Domain-Driven Design)** avec **LangGraph** (orchestration) et **Deep Agents** (extraction LLM), conforme à la spec [Agent Skills](https://agentskills.io/specification).

## Couches

```
src/
├── domain/                    # Cœur métier (0 dépendance externe)
│   ├── entities.py            # Modèles Pydantic
│   └── interfaces.py          # Ports (IDocumentParser, IFinancialAgent)
├── application/               # Cas d'usage et orchestration
│   ├── schemas/               # Schémas Pydantic (input/output)
│   │   └── extraction.py      # ExtractionOutput
│   ├── state.py               # WorkflowState (TypedDict LangGraph)
│   └── workflow.py            # ExtractionWorkflow (StateGraph)
├── infrastructure/            # Implémentations concrètes
│   ├── agents/
│   │   ├── skills/            # Skills natifs Deep Agents (SKILL.md)
│   │   │   ├── chiffre-affaires/
│   │   │   ├── capitaux-propres/
│   │   │   └── resultat-exercice/
│   │   ├── financial_agent.py # DeepAgentsFinancialAgent
│   │   └── skills_loader.py   # Charge SKILL.md pour StateBackend
│   ├── container.py           # Composition Root (DI)
│   ├── document_parser.py     # PyMuPDFDocumentParser
│   └── gcp_secrets.py
└── presentation/
    └── handler.py             # Lambda handler
```

## Flux

1. **API Gateway** → Lambda `handler.py`
2. **handler** appelle `create_extraction_workflow()` (composition root)
3. **ExtractionWorkflow** (LangGraph) : `parse_document` → `extract_metrics`
4. **parse_document** : `PyMuPDFDocumentParser` extrait le texte du PDF
5. **extract_metrics** : `DeepAgentsFinancialAgent` invoque l'agent avec `skills=["/skills/"]`
6. L'agent Deep Agents utilise la **progressive disclosure** : il matche les skills par `description` et charge uniquement les `SKILL.md` pertinents
7. Sortie structurée via `ExtractionOutput` (Pydantic) pour garantir le format JSON

## Skills (Agent Skills spec)

Chaque skill est un dossier avec `SKILL.md` contenant :
- **Frontmatter** : `name`, `description` (utilisé pour le matching)
- **Contenu** : instructions d'extraction pour la métrique

Le `skills_loader` lit les fichiers et les passe à `invoke(files=...)` pour le StateBackend (compatible Lambda).

## Références

- [LangGraph Overview](https://docs.langchain.com/oss/python/langgraph/overview)
- [Deep Agents Overview](https://docs.langchain.com/oss/python/deepagents/overview)
- [Deep Agents Skills](https://docs.langchain.com/oss/python/deepagents/skills)
- [Agent Skills Specification](https://agentskills.io/specification)
