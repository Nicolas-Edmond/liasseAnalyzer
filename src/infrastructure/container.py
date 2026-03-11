"""
Composition Root : point unique d'injection des dépendances (DDD).
Wiring de l'application sans couplage entre les couches.
"""
from typing import Optional
from domain.interfaces import IDocumentParser, IFinancialAgent
from infrastructure.document_parser import PyMuPDFDocumentParser
from infrastructure.agents.financial_agent import DeepAgentsFinancialAgent
from application.workflow import ExtractionWorkflow


def create_extraction_workflow(
    parser: Optional[IDocumentParser] = None,
    agent: Optional[IFinancialAgent] = None,
) -> ExtractionWorkflow:
    """Factory du cas d'usage principal d'extraction."""
    parser = parser or PyMuPDFDocumentParser()
    agent = agent or DeepAgentsFinancialAgent()
    return ExtractionWorkflow(parser=parser, agent=agent)
