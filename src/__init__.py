"""
Entelequia - Framework for measuring longitudinal consistency of functional identity in LLMs
"""

from .entelequia_core import EntelequiaAnalyzer, IdentityProfile
from .naturalistic_analyzer import NaturalisticCognitionAnalyzer
from .hub.vps_client import HubMemoria

__all__ = [
    "EntelequiaAnalyzer",
    "IdentityProfile",
    "NaturalisticCognitionAnalyzer",
    "HubMemoria",
]

__version__ = "0.1.0"
