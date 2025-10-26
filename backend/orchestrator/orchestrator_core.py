"""
Orchestrator Core
Analyzes case files, detects tasks, and routes to appropriate AI agents
"""

import os
import re
import json
import asyncio
import logging
from typing import Dict, Any, List, Tuple
from datetime import datetime
from pathlib import Path

# Import all agents
from agents import (
    communication_guru,
    records_wrangler,
    legal_researcher,
    voice_bot_scheduler,
    evidence_sorter
)

# Import utilities
from utils.context_enricher import extract_case_context

# Import postprocessors
from postprocessors.brief_generator import generate_attorney_brief

# Configure logging
log_dir = Path(__file__).parent.parent.parent / "temp"
log_dir.mkdir(exist_ok=True)
log_file = log_dir / "orchestrator_logs.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


async def process_case_text(text: str) -> Dict[str, Any]:
    """
    Analyze case text, detect tasks, route to agents, and aggregate results.
    
    Args:
        text: Full case file text content
        
    Returns:
        dict: Structured JSON with:
            - summary: Brief case summary
            - detected_tasks: List of identified tasks
            - agent_outputs: Results from each agent
            - recommended_actions: Consolidated action items
            - overall_confidence: Average confidence across agents
            
    Example:
        {
            "summary": "Personal injury case with missing records...",
            "detected_tasks": [
                {"type": "records_analysis", "priority": "high"},
                {"type": "client_communication", "priority": "medium"}
            ],
            "agent_outputs": {
                "records_wrangler": {...},
                "communication_guru": {...}
            },
            "recommended_actions": ["Request MRI results...", "Call client..."],
            "overall_confidence": 0.85
        }
    """
    logger.info("=" * 70)
    logger.info("ORCHESTRATOR: Starting case analysis")
    logger.info(f"Case text length: {len(text)} characters")
    
    start_time = datetime.now()
    
    try:
        # Step 0: Extract case context metadata
        logger.info("Step 0: Extracting case context metadata...")
        context_metadata = extract_case_context(text)
        logger.info("Context extraction complete")
        
        # Step 1: Detect tasks using regex + pattern matching
        logger.info("Step 1: Detecting tasks from case text...")
        detected_tasks = await _detect_tasks(text)
        logger.info(f"Detected {len(detected_tasks)} task(s): {[t['type'] for t in detected_tasks]}")
        
        # Step 2: Create workflow based on detected tasks
        logger.info("Step 2: Creating agent workflow...")
        workflow = _create_workflow(detected_tasks)
        logger.info(f"Workflow created with {len(workflow)} agent(s): {[w['agent'] for w in workflow]}")
        
        # Step 3: Execute agents asynchronously
        logger.info("Step 3: Executing agents...")
        agent_outputs = await _execute_agents(text, workflow)
        logger.info(f"Completed {len(agent_outputs)} agent execution(s)")
        
        # Step 4: Aggregate results
        logger.info("Step 4: Aggregating results...")
        result = _aggregate_results(text, detected_tasks, agent_outputs)
        
        # Add context metadata to result
        result["context_metadata"] = context_metadata
        
        # Step 5: Generate attorney brief
        logger.info("Step 5: Generating attorney brief...")
        attorney_brief = await generate_attorney_brief(result)
        result["attorney_brief"] = attorney_brief
        logger.info(f"Attorney brief generated ({len(attorney_brief)} characters)")
        
        # Calculate execution time
        execution_time = (datetime.now() - start_time).total_seconds()
        result["execution_time_seconds"] = round(execution_time, 2)
        
        logger.info(f"ORCHESTRATOR: Completed successfully in {execution_time:.2f}s")
        logger.info(f"Overall confidence: {result.get('overall_confidence', 0):.2f}")
        logger.info("=" * 70)
        
        return result
        
    except Exception as e:
        logger.error(f"ORCHESTRATOR: Fatal error - {str(e)}", exc_info=True)
        return {
            "summary": "Error processing case file",
            "detected_tasks": [],
            "agent_outputs": {},
            "recommended_actions": [f"Error: {str(e)}"],
            "overall_confidence": 0.0,
            "error": str(e),
            "status": "failed"
        }


async def _detect_tasks(text: str) -> List[Dict[str, Any]]:
    """
    Detect actionable tasks from case text using regex patterns and keywords.
    
    Args:
        text: Case file text
        
    Returns:
        list: Detected tasks with type and priority
    """
    tasks = []
    text_lower = text.lower()
    
    # Task detection patterns
    patterns = {
        "records_analysis": {
            "keywords": [
                r"missing.*record", r"incomplete.*record", r"duplicate.*record",
                r"need.*record", r"awaiting.*record", r"not.*received",
                r"outstanding.*record", r"pending.*record"
            ],
            "priority": "high"
        },
        "client_communication": {
            "keywords": [
                r"client.*anxious", r"client.*worried", r"client.*called",
                r"client.*concerned", r"reassure.*client", r"update.*client",
                r"client.*follow.?up", r"client.*needs"
            ],
            "priority": "high"
        },
        "legal_research": {
            "keywords": [
                r"legal.*issue", r"precedent", r"case.*law", r"statute",
                r"legal.*research", r"legal.*question", r"jurisdiction",
                r"verdict", r"ruling", r"legal.*basis"
            ],
            "priority": "medium"
        },
        "scheduling": {
            "keywords": [
                r"schedule.*call", r"schedule.*meeting", r"contact.*witness",
                r"call.*needed", r"follow.?up.*call", r"appointment",
                r"deposition", r"interview.*witness", r"phone.*number"
            ],
            "priority": "medium"
        },
        "evidence_organization": {
            "keywords": [
                r"evidence", r"exhibit", r"document.*inventory", r"photo",
                r"medical.*bill", r"police.*report", r"witness.*statement",
                r"classify.*document", r"organize.*evidence"
            ],
            "priority": "low"
        }
    }
    
    # Check each pattern
    for task_type, config in patterns.items():
        matches = 0
        for keyword_pattern in config["keywords"]:
            if re.search(keyword_pattern, text_lower):
                matches += 1
        
        if matches > 0:
            tasks.append({
                "type": task_type,
                "priority": config["priority"],
                "match_count": matches,
                "confidence": min(matches / len(config["keywords"]), 1.0)
            })
            logger.info(f"  Detected: {task_type} (priority: {config['priority']}, matches: {matches})")
    
    # Sort by priority and match count
    priority_order = {"high": 3, "medium": 2, "low": 1}
    tasks.sort(key=lambda x: (priority_order[x["priority"]], x["match_count"]), reverse=True)
    
    # If no tasks detected, default to basic analysis
    if not tasks:
        logger.warning("  No specific tasks detected, using default workflow")
        tasks = [
            {"type": "records_analysis", "priority": "medium", "match_count": 0, "confidence": 0.5},
            {"type": "evidence_organization", "priority": "low", "match_count": 0, "confidence": 0.5}
        ]
    
    return tasks


def _create_workflow(detected_tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Create agent execution workflow based on detected tasks.
    
    Args:
        detected_tasks: List of detected tasks
        
    Returns:
        list: Workflow with agent assignments
    """
    workflow = []
    
    # Map task types to agents
    task_to_agent = {
        "records_analysis": "records_wrangler",
        "client_communication": "communication_guru",
        "legal_research": "legal_researcher",
        "scheduling": "voice_bot_scheduler",
        "evidence_organization": "evidence_sorter"
    }
    
    # Create workflow entries
    for task in detected_tasks:
        task_type = task["type"]
        agent_name = task_to_agent.get(task_type)
        
        if agent_name:
            workflow.append({
                "agent": agent_name,
                "task": task,
                "priority": task["priority"]
            })
    
    # Remove duplicates while preserving order
    seen = set()
    unique_workflow = []
    for item in workflow:
        agent = item["agent"]
        if agent not in seen:
            seen.add(agent)
            unique_workflow.append(item)
    
    return unique_workflow


async def _execute_agents(text: str, workflow: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Execute agents asynchronously based on workflow.
    
    Args:
        text: Case file text
        workflow: Agent workflow
        
    Returns:
        dict: Agent outputs keyed by agent name
    """
    agent_outputs = {}
    
    # Map agent names to modules
    agent_modules = {
        "records_wrangler": records_wrangler,
        "communication_guru": communication_guru,
        "legal_researcher": legal_researcher,
        "voice_bot_scheduler": voice_bot_scheduler,
        "evidence_sorter": evidence_sorter
    }
    
    # Create tasks for async execution
    async_tasks = []
    agent_names = []
    
    for workflow_item in workflow:
        agent_name = workflow_item["agent"]
        task_info = workflow_item["task"]
        
        agent_module = agent_modules.get(agent_name)
        if agent_module:
            # Create task context
            task_context = {
                "task_type": task_info["type"],
                "priority": task_info["priority"],
                "context": f"Detected from case analysis with {task_info['match_count']} indicators"
            }
            
            # Create async task with error handling
            async_task = _execute_single_agent(
                agent_name,
                agent_module,
                text,
                task_context
            )
            async_tasks.append(async_task)
            agent_names.append(agent_name)
    
    # Execute all agents concurrently
    logger.info(f"  Executing {len(async_tasks)} agent(s) concurrently...")
    results = await asyncio.gather(*async_tasks, return_exceptions=True)
    
    # Process results
    for agent_name, result in zip(agent_names, results):
        if isinstance(result, Exception):
            logger.error(f"  Agent {agent_name} failed: {str(result)}")
            agent_outputs[agent_name] = {
                "status": "agent_unavailable",
                "error": str(result),
                "message": f"Agent {agent_name} encountered an error"
            }
        else:
            logger.info(f"  Agent {agent_name} completed successfully")
            agent_outputs[agent_name] = result
    
    return agent_outputs


async def _execute_single_agent(
    agent_name: str,
    agent_module: Any,
    text: str,
    task: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Execute a single agent with error handling and timeout.
    
    Args:
        agent_name: Name of the agent
        agent_module: Agent module
        text: Case file text
        task: Task context
        
    Returns:
        dict: Agent output or error
    """
    logger.info(f"    Starting agent: {agent_name}")
    start_time = datetime.now()
    
    try:
        # Execute agent with timeout (60 seconds)
        result = await asyncio.wait_for(
            agent_module.run(text, task),
            timeout=60.0
        )
        
        execution_time = (datetime.now() - start_time).total_seconds()
        logger.info(f"    Agent {agent_name} completed in {execution_time:.2f}s")
        
        # Add metadata
        result["agent_name"] = agent_name
        result["execution_time"] = round(execution_time, 2)
        result["status"] = "success"
        
        return result
        
    except asyncio.TimeoutError:
        logger.error(f"    Agent {agent_name} timed out after 60s")
        return {
            "status": "agent_unavailable",
            "error": "Agent execution timed out",
            "agent_name": agent_name
        }
    except Exception as e:
        logger.error(f"    Agent {agent_name} error: {str(e)}")
        return {
            "status": "agent_unavailable",
            "error": str(e),
            "agent_name": agent_name
        }


def _aggregate_results(
    text: str,
    detected_tasks: List[Dict[str, Any]],
    agent_outputs: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Aggregate agent results into final output.
    
    Args:
        text: Original case text
        detected_tasks: Detected tasks
        agent_outputs: Agent outputs
        
    Returns:
        dict: Aggregated results
    """
    logger.info("  Aggregating agent results...")
    
    # Generate case summary
    summary = _generate_summary(text, detected_tasks, agent_outputs)
    
    # Collect recommended actions from all agents
    recommended_actions = []
    confidence_scores = []
    
    for agent_name, output in agent_outputs.items():
        if output.get("status") == "agent_unavailable":
            continue
        
        # Extract confidence score
        if "confidence_score" in output:
            confidence_scores.append(output["confidence_score"])
        
        # Extract recommended actions
        if "recommended_action" in output:
            action = output["recommended_action"]
            if action and action.strip():
                recommended_actions.append(f"[{agent_name}] {action}")
        
        # Extract message_draft from communication_guru
        if agent_name == "communication_guru" and "message_draft" in output:
            recommended_actions.append(f"[{agent_name}] Send drafted message to client")
        
        # Extract missing records from records_wrangler
        if agent_name == "records_wrangler" and "missing_records" in output:
            missing = output.get("missing_records", [])
            if missing:
                recommended_actions.append(f"[{agent_name}] Obtain {len(missing)} missing record(s)")
        
        # Extract scheduling from voice_bot_scheduler
        if agent_name == "voice_bot_scheduler" and "call_script" in output:
            contact = output.get("contact_name", "contact")
            recommended_actions.append(f"[{agent_name}] Schedule call with {contact}")
    
    # Calculate overall confidence
    overall_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
    
    # Build final result
    result = {
        "summary": summary,
        "detected_tasks": detected_tasks,
        "agent_outputs": agent_outputs,
        "recommended_actions": recommended_actions,
        "overall_confidence": round(overall_confidence, 2),
        "agents_executed": len(agent_outputs),
        "agents_successful": sum(1 for o in agent_outputs.values() if o.get("status") != "agent_unavailable"),
        "timestamp": datetime.now().isoformat()
    }
    
    logger.info(f"  Aggregation complete: {result['agents_successful']}/{result['agents_executed']} agents successful")
    
    return result


def _generate_summary(
    text: str,
    detected_tasks: List[Dict[str, Any]],
    agent_outputs: Dict[str, Any]
) -> str:
    """
    Generate a brief case summary.
    
    Args:
        text: Case text
        detected_tasks: Detected tasks
        agent_outputs: Agent outputs
        
    Returns:
        str: Case summary
    """
    # Extract case number if present
    case_number_match = re.search(r'case\s*#?\s*(\d{4}-[A-Z]{2}-\d+)', text, re.IGNORECASE)
    case_number = case_number_match.group(1) if case_number_match else "Unknown"
    
    # Extract case type if present
    case_type_match = re.search(r'case\s*type:\s*([^\n]+)', text, re.IGNORECASE)
    case_type = case_type_match.group(1).strip() if case_type_match else "Unknown"
    
    # Count successful agents
    successful_agents = sum(1 for o in agent_outputs.values() if o.get("status") != "agent_unavailable")
    
    # Build summary
    summary_parts = [
        f"Case #{case_number}",
        f"Type: {case_type}",
        f"Detected {len(detected_tasks)} actionable task(s)",
        f"Analyzed by {successful_agents} AI agent(s)"
    ]
    
    # Add key findings
    if "records_wrangler" in agent_outputs:
        records = agent_outputs["records_wrangler"]
        if records.get("status") != "agent_unavailable":
            missing_count = len(records.get("missing_records", []))
            if missing_count > 0:
                summary_parts.append(f"{missing_count} missing record(s) identified")
    
    if "evidence_sorter" in agent_outputs:
        evidence = agent_outputs["evidence_sorter"]
        if evidence.get("status") != "agent_unavailable":
            evidence_count = len(evidence.get("evidence_summary", []))
            if evidence_count > 0:
                summary_parts.append(f"{evidence_count} piece(s) of evidence classified")
    
    return " | ".join(summary_parts)


# Agent metadata for reference
AGENT_CAPABILITIES = {
    "communication_guru": "Drafts empathetic client messages",
    "records_wrangler": "Identifies missing/duplicate records",
    "legal_researcher": "Finds relevant legal precedents",
    "voice_bot_scheduler": "Coordinates calls and meetings",
    "evidence_sorter": "Classifies and organizes evidence"
}
