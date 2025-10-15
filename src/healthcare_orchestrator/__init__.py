"""
Healthcare Agent Orchestrator

A production-ready healthcare agent orchestrator for MedImageParse 
using Microsoft Agent Framework (MAF).
"""

__version__ = "0.1.0"
__author__ = "Arturo Quiroga"

from healthcare_orchestrator.orchestrator import HealthcareOrchestrator
from healthcare_orchestrator.config.settings import Settings

__all__ = ["HealthcareOrchestrator", "Settings"]
