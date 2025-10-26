"""
AI Agents Module for KNIGHTHACKS-VIII-Morgan
Specialized agents for legal case processing tasks
"""

from . import communication_guru
from . import records_wrangler
from . import legal_researcher
from . import voice_bot_scheduler
from . import evidence_sorter

__all__ = [
    'communication_guru',
    'records_wrangler',
    'legal_researcher',
    'voice_bot_scheduler',
    'evidence_sorter'
]
