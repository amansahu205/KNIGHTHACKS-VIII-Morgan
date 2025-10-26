"""
Orchestrator Router
Detects actionable tasks from case files and routes to specialized agents
"""

from typing import Dict, Any
from .orchestrator_core import process_case_text


async def process_case_file(text: str) -> Dict[str, Any]:
    """
    Process case file text through AI orchestrator.
    
    This function:
    1. Analyzes the case file text
    2. Detects actionable tasks using regex + pattern matching
    3. Routes tasks to appropriate agents
    4. Executes agents asynchronously
    5. Aggregates and returns structured results
    
    Args:
        text: Raw text content from uploaded case file
        
    Returns:
        dict: Structured JSON with detected tasks and agent results
        
    Example output:
        {
            "summary": "Case #2024-PI-1234 | Type: Personal Injury...",
            "detected_tasks": [
                {"type": "records_analysis", "priority": "high"},
                {"type": "client_communication", "priority": "medium"}
            ],
            "agent_outputs": {
                "records_wrangler": {...},
                "communication_guru": {...}
            },
            "recommended_actions": ["Request MRI results...", "Call client..."],
            "overall_confidence": 0.85,
            "execution_time_seconds": 3.45
        }
    """
    # Delegate to orchestrator core
    return await process_case_text(text)
