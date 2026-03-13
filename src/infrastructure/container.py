"""
Composition Root : point unique d'injection des dépendances (DDD).
Wiring de l'application sans couplage entre les couches.
"""
from typing import Optional
from domain.interfaces import IDocumentParser, IFinancialAgent, IAnalysisRepository
from infrastructure.document_parser import PyMuPDFDocumentParser
from infrastructure.agents.financial_agent import DeepAgentsFinancialAgent
from infrastructure.db import PostgresAnalysisRepository
from application.workflow import ExtractionWorkflow


def create_extraction_workflow(
    parser: Optional[IDocumentParser] = None,
    agent: Optional[IFinancialAgent] = None,
    db: Optional[IAnalysisRepository] = None,
) -> ExtractionWorkflow:
    """Factory du cas d'usage principal d'extraction."""
    parser = parser or PyMuPDFDocumentParser()
    agent = agent or DeepAgentsFinancialAgent()
    db = db or PostgresAnalysisRepository()
    return ExtractionWorkflow(parser=parser, agent=agent, db=db)
