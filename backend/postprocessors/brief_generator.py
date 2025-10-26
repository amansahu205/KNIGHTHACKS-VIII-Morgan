"""
Brief Generator
Generates professional attorney briefs from orchestrator outputs
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)


async def generate_attorney_brief(orchestrator_output: Dict[str, Any]) -> str:
    """
    Generate a professional attorney brief from orchestrator output.
    
    Args:
        orchestrator_output: Complete orchestrator output with:
            - context_metadata: Extracted case metadata
            - detected_tasks: List of detected tasks
            - agent_outputs: Results from all agents
            - recommended_actions: List of recommended actions
            
    Returns:
        str: Professional summary paragraph (120-180 words)
        
    Example:
        "Case #2024-PI-8888 for client Emily Watson involves a premises 
        liability matter stemming from an incident on February 15, 2024. 
        The case involves Allstate Insurance and treatment at Memorial 
        Hospital. Our analysis identified 3 missing medical records..."
    """
    logger.info("=" * 70)
    logger.info("BRIEF GENERATOR: Starting attorney brief generation")
    start_time = datetime.now()
    
    try:
        # Extract components
        context = orchestrator_output.get("context_metadata", {})
        agent_outputs = orchestrator_output.get("agent_outputs", {})
        recommended_actions = orchestrator_output.get("recommended_actions", [])
        
        # Build brief sections
        sections = []
        
        # Section 1: Case Overview
        overview = _generate_case_overview(context)
        if overview:
            sections.append(overview)
        
        # Section 2: Agent Findings
        findings = _generate_agent_findings(agent_outputs)
        if findings:
            sections.append(findings)
        
        # Section 3: Recommended Actions
        actions = _generate_action_summary(recommended_actions)
        if actions:
            sections.append(actions)
        
        # Combine sections
        brief = " ".join(sections)
        
        # Calculate execution time
        execution_time = (datetime.now() - start_time).total_seconds()
        
        logger.info(f"BRIEF GENERATOR: Brief generated ({len(brief)} characters)")
        logger.info(f"Execution time: {execution_time:.3f}s")
        logger.info("=" * 70)
        
        return brief
        
    except Exception as e:
        logger.error(f"BRIEF GENERATOR: Error generating brief - {str(e)}", exc_info=True)
        return "Error generating attorney brief. Please review case file manually."


def _generate_case_overview(context: Dict[str, Any]) -> str:
    """
    Generate case overview section from context metadata.
    
    Args:
        context: Context metadata from context enricher
        
    Returns:
        str: Case overview paragraph
    """
    parts = []
    
    # Case identification
    case_number = context.get("case_number", {}).get("value")
    client_name = context.get("client_name", {}).get("value")
    case_type = context.get("case_type", {}).get("value")
    
    if case_number and client_name:
        parts.append(f"This office represents {client_name} in Case #{case_number}, which")
    elif case_number:
        parts.append(f"Case #{case_number}")
    elif client_name:
        parts.append(f"This office represents {client_name} in a matter that")
    else:
        parts.append("This case")
    
    # Case type
    if case_type:
        parts.append(f"involves a {case_type} claim")
    
    # Incident date
    incident_date = context.get("date_of_incident", {}).get("value")
    if incident_date:
        # Format date nicely
        try:
            from datetime import datetime
            dt = datetime.strptime(incident_date, "%Y-%m-%d")
            formatted_date = dt.strftime("%B %d, %Y")
            parts.append(f"arising from an incident that occurred on {formatted_date}")
        except:
            parts.append(f"arising from an incident on {incident_date}")
    
    # Key parties
    key_parties = []
    
    insurance = context.get("insurance_company", {}).get("value")
    if insurance:
        key_parties.append(f"the defendant's carrier is {insurance}")
    
    providers = context.get("medical_providers", [])
    if providers and len(providers) > 0:
        # Mention first provider
        first_provider = providers[0].get("value")
        if first_provider:
            if len(providers) > 1:
                key_parties.append(f"the client received treatment at {first_provider} and other facilities")
            else:
                key_parties.append(f"the client received treatment at {first_provider}")
    
    if key_parties:
        parts.append(f". {key_parties[0].capitalize()}")
        if len(key_parties) > 1:
            parts.append(f", and {key_parties[1]}")
    
    overview = " ".join(parts)
    if not overview.endswith("."):
        overview += "."
    
    return overview


def _generate_agent_findings(agent_outputs: Dict[str, Any]) -> str:
    """
    Generate findings section from agent outputs.
    
    Args:
        agent_outputs: Results from all agents
        
    Returns:
        str: Agent findings summary
    """
    findings = []
    
    # Records Wrangler
    if "records_wrangler" in agent_outputs:
        records_summary = summarize_agent_result("records_wrangler", agent_outputs["records_wrangler"])
        if records_summary:
            findings.append(records_summary)
    
    # Communication Guru
    if "communication_guru" in agent_outputs:
        comm_summary = summarize_agent_result("communication_guru", agent_outputs["communication_guru"])
        if comm_summary:
            findings.append(comm_summary)
    
    # Legal Researcher
    if "legal_researcher" in agent_outputs:
        legal_summary = summarize_agent_result("legal_researcher", agent_outputs["legal_researcher"])
        if legal_summary:
            findings.append(legal_summary)
    
    # Evidence Sorter
    if "evidence_sorter" in agent_outputs:
        evidence_summary = summarize_agent_result("evidence_sorter", agent_outputs["evidence_sorter"])
        if evidence_summary:
            findings.append(evidence_summary)
    
    # Voice Bot Scheduler
    if "voice_bot_scheduler" in agent_outputs:
        scheduler_summary = summarize_agent_result("voice_bot_scheduler", agent_outputs["voice_bot_scheduler"])
        if scheduler_summary:
            findings.append(scheduler_summary)
    
    if findings:
        return "Our comprehensive case analysis has " + ", ".join(findings) + "."
    
    return ""


def summarize_agent_result(agent_name: str, data: Dict[str, Any]) -> Optional[str]:
    """
    Summarize individual agent result.
    
    Args:
        agent_name: Name of the agent
        data: Agent output data
        
    Returns:
        str: One-line summary or None if agent failed
    """
    # Check if agent was successful
    if data.get("status") == "agent_unavailable":
        return None
    
    if agent_name == "records_wrangler":
        return _summarize_records_wrangler(data)
    elif agent_name == "communication_guru":
        return _summarize_communication_guru(data)
    elif agent_name == "legal_researcher":
        return _summarize_legal_researcher(data)
    elif agent_name == "evidence_sorter":
        return _summarize_evidence_sorter(data)
    elif agent_name == "voice_bot_scheduler":
        return _summarize_voice_bot_scheduler(data)
    
    return None


def _summarize_records_wrangler(data: Dict[str, Any]) -> Optional[str]:
    """Summarize Records Wrangler output."""
    missing = data.get("missing_records", [])
    duplicates = data.get("duplicates", [])
    
    parts = []
    
    if missing:
        count = len(missing)
        if count == 1:
            parts.append("identified 1 missing record")
        else:
            parts.append(f"identified {count} missing records")
    
    if duplicates:
        count = len(duplicates)
        if count == 1:
            parts.append("found 1 duplicate document")
        else:
            parts.append(f"found {count} duplicate documents")
    
    if not parts:
        parts.append("confirmed all records are complete")
    
    return " and ".join(parts)


def _summarize_communication_guru(data: Dict[str, Any]) -> Optional[str]:
    """Summarize Communication Guru output."""
    tone = data.get("tone", "")
    
    if tone:
        return f"detected {tone} client tone and prepared appropriate response"
    
    return "prepared client communication"


def _summarize_legal_researcher(data: Dict[str, Any]) -> Optional[str]:
    """Summarize Legal Researcher output."""
    cases = data.get("relevant_cases", [])
    
    if cases:
        count = len(cases)
        if count == 1:
            case_name = cases[0].get("case_name", "relevant case")
            return f"found 1 relevant precedent ({case_name})"
        else:
            return f"found {count} relevant legal precedents"
    
    return "completed legal research"


def _summarize_evidence_sorter(data: Dict[str, Any]) -> Optional[str]:
    """Summarize Evidence Sorter output."""
    evidence = data.get("evidence_summary", [])
    missing = data.get("missing_evidence", [])
    
    parts = []
    
    if evidence:
        count = len(evidence)
        
        # Count by authenticity status
        verified = sum(1 for e in evidence if e.get("authenticity_status") == "verified")
        
        if count == 1:
            parts.append("catalogued 1 piece of evidence")
        else:
            parts.append(f"catalogued {count} pieces of evidence")
        
        if verified > 0:
            parts.append(f"{verified} verified")
    
    if missing:
        count = len(missing)
        if count == 1:
            parts.append("noted 1 missing exhibit")
        else:
            parts.append(f"noted {count} missing exhibits")
    
    if parts:
        return " (".join(parts) + ")" if "(" not in " ".join(parts) else " and ".join(parts)
    
    return "organized case evidence"


def _summarize_voice_bot_scheduler(data: Dict[str, Any]) -> Optional[str]:
    """Summarize Voice Bot Scheduler output."""
    contact_name = data.get("contact_name", "")
    action_type = data.get("action_type", "contact")
    
    if contact_name:
        return f"scheduled {action_type} with {contact_name}"
    
    return f"prepared {action_type} coordination"


def _generate_action_summary(recommended_actions: List[str]) -> str:
    """
    Generate action summary from recommended actions.
    
    Args:
        recommended_actions: List of recommended actions
        
    Returns:
        str: Action summary
    """
    if not recommended_actions:
        return "The case file appears complete at this time, and no immediate follow-up actions are required pending further developments."
    
    # Take top 3 actions
    top_actions = recommended_actions[:3]
    
    if len(top_actions) == 1:
        return f"To advance this matter, the following action is recommended: {_clean_action(top_actions[0])}."
    elif len(top_actions) == 2:
        return f"To advance this matter, the following actions are recommended: {_clean_action(top_actions[0])}, and {_clean_action(top_actions[1])}."
    else:
        # List first 2, then "and X more"
        remaining = len(recommended_actions) - 2
        if remaining == 1:
            return f"To advance this matter, priority actions include: {_clean_action(top_actions[0])}, {_clean_action(top_actions[1])}, and one additional follow-up item."
        else:
            return f"To advance this matter, priority actions include: {_clean_action(top_actions[0])}, {_clean_action(top_actions[1])}, and {remaining} additional follow-up items."


def _clean_action(action: str) -> str:
    """
    Clean action text for brief.
    
    Args:
        action: Raw action text
        
    Returns:
        str: Cleaned action text
    """
    # Remove agent prefix like "[records_wrangler]"
    import re
    cleaned = re.sub(r'^\[[\w_]+\]\s*', '', action)
    
    # Lowercase first letter
    if cleaned:
        cleaned = cleaned[0].lower() + cleaned[1:]
    
    # Remove trailing period
    cleaned = cleaned.rstrip('.')
    
    return cleaned


# Utility function for testing
def generate_brief_sync(orchestrator_output: Dict[str, Any]) -> str:
    """
    Synchronous wrapper for testing.
    
    Args:
        orchestrator_output: Orchestrator output
        
    Returns:
        str: Generated brief
    """
    import asyncio
    return asyncio.run(generate_attorney_brief(orchestrator_output))
