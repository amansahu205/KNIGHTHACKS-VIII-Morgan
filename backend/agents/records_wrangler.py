"""
Records Wrangler Agent
Identifies missing, incomplete, or duplicate records in legal cases
"""

import os
import json
from typing import Dict, Any, List
from openai import AsyncOpenAI
from anthropic import AsyncAnthropic


# Initialize LLM clients
openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
anthropic_client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


async def run(text: str, task: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze case documents to identify missing or duplicate records.
    
    Args:
        text: Full case file text content with legal/insurance documentation
        task: Task details from orchestrator containing:
            - task_type: Type of record analysis needed
            - context: Additional context about the case
            - case_type: Type of legal case (e.g., personal injury, insurance claim)
            
    Returns:
        dict: Structured JSON with:
            - missing_records: List of missing/incomplete records with details
            - duplicates: List of duplicate records found
            - recommended_action: Attorney action steps to obtain/reconcile records
            - confidence_score: 0.0-1.0 confidence in the analysis
            
    Example:
        {
            "missing_records": [
                {
                    "type": "medical_report",
                    "description": "MRI scan results from St. Mary's Hospital",
                    "urgency": "high",
                    "source": "St. Mary's Hospital Radiology Dept"
                }
            ],
            "duplicates": [
                {
                    "type": "police_report",
                    "instances": 2,
                    "description": "Incident report #2024-1234 appears twice"
                }
            ],
            "recommended_action": "Contact St. Mary's Hospital records department...",
            "confidence_score": 0.85
        }
    """
    
    # Get LLM provider from environment (default to OpenAI)
    provider = os.getenv("DEFAULT_LLM_PROVIDER", "openai").lower()
    
    # Build structured prompt
    system_prompt = """You are an expert legal records analyst specializing in identifying missing, incomplete, or duplicate documentation in legal cases.

Your role:
1. Analyze case files to identify what records are present
2. Detect missing or incomplete critical documents (medical reports, police statements, insurance approvals, witness statements, etc.)
3. Identify any duplicate records that need reconciliation
4. Assess the urgency and importance of each missing record
5. Provide clear action steps for attorneys to obtain missing records

Common record types to check:
- Medical records (hospital reports, doctor's notes, MRI/X-ray results, treatment plans)
- Police reports and incident statements
- Insurance documents (claims, approvals, denials, correspondence)
- Witness statements and depositions
- Employment records (for lost wages claims)
- Property damage assessments
- Expert opinions and evaluations

Always respond in valid JSON format with these exact keys:
- missing_records: array of objects with type, description, urgency, source
- duplicates: array of objects with type, instances, description
- recommended_action: string with clear attorney action steps
- confidence_score: number between 0.0 and 1.0"""

    user_prompt = f"""Case Documentation:
{text}

Task Details:
{json.dumps(task, indent=2)}

Analyze this case documentation and identify:
1. What records are missing or incomplete
2. Any duplicate records that need reconciliation
3. Recommended actions to obtain missing records
4. Your confidence level in this analysis

Respond ONLY with valid JSON in this exact format:
{{
    "missing_records": [
        {{
            "type": "record_type",
            "description": "detailed description of missing record",
            "urgency": "low|medium|high",
            "source": "where to obtain this record"
        }}
    ],
    "duplicates": [
        {{
            "type": "record_type",
            "instances": number,
            "description": "description of duplicate"
        }}
    ],
    "recommended_action": "clear step-by-step actions for attorney",
    "confidence_score": 0.0-1.0
}}"""

    try:
        if provider == "anthropic":
            result = await _call_anthropic(system_prompt, user_prompt)
        else:
            result = await _call_openai(system_prompt, user_prompt)
        
        # Validate and sanitize output
        result = _validate_output(result)
        return result
        
    except Exception as e:
        # Return error in structured format
        return {
            "missing_records": [],
            "duplicates": [],
            "recommended_action": f"Error analyzing records: {str(e)}",
            "confidence_score": 0.0,
            "error": str(e)
        }


async def _call_openai(system_prompt: str, user_prompt: str) -> Dict[str, Any]:
    """
    Call OpenAI API with structured JSON output.
    
    Args:
        system_prompt: System instructions
        user_prompt: User query with case context
        
    Returns:
        dict: Parsed JSON response from LLM
    """
    model = os.getenv("DEFAULT_MODEL", "gpt-4-turbo-preview")
    
    response = await openai_client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=float(os.getenv("TEMPERATURE", "0.7")),
        max_tokens=int(os.getenv("MAX_TOKENS", "4096")),
        response_format={"type": "json_object"}  # Force JSON output
    )
    
    content = response.choices[0].message.content
    return json.loads(content)


async def _call_anthropic(system_prompt: str, user_prompt: str) -> Dict[str, Any]:
    """
    Call Anthropic Claude API with structured JSON output.
    
    Args:
        system_prompt: System instructions
        user_prompt: User query with case context
        
    Returns:
        dict: Parsed JSON response from LLM
    """
    model = os.getenv("DEFAULT_MODEL", "claude-3-5-sonnet-20241022")
    
    response = await anthropic_client.messages.create(
        model=model,
        max_tokens=int(os.getenv("MAX_TOKENS", "4096")),
        temperature=float(os.getenv("TEMPERATURE", "0.7")),
        system=system_prompt,
        messages=[
            {"role": "user", "content": user_prompt}
        ]
    )
    
    content = response.content[0].text
    
    # Extract JSON from response (Claude may wrap it in markdown)
    if "```json" in content:
        content = content.split("```json")[1].split("```")[0].strip()
    elif "```" in content:
        content = content.split("```")[1].split("```")[0].strip()
    
    return json.loads(content)


def _validate_output(result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate and sanitize agent output to ensure proper structure.
    
    Args:
        result: Raw output from LLM
        
    Returns:
        dict: Validated and sanitized output
    """
    # Ensure all required keys exist
    validated = {
        "missing_records": result.get("missing_records", []),
        "duplicates": result.get("duplicates", []),
        "recommended_action": result.get("recommended_action", ""),
        "confidence_score": result.get("confidence_score", 0.0)
    }
    
    # Validate missing_records structure
    if not isinstance(validated["missing_records"], list):
        validated["missing_records"] = []
    
    for record in validated["missing_records"]:
        if not isinstance(record, dict):
            continue
        # Ensure required fields
        record.setdefault("type", "unknown")
        record.setdefault("description", "")
        record.setdefault("urgency", "medium")
        record.setdefault("source", "unknown")
    
    # Validate duplicates structure
    if not isinstance(validated["duplicates"], list):
        validated["duplicates"] = []
    
    for duplicate in validated["duplicates"]:
        if not isinstance(duplicate, dict):
            continue
        duplicate.setdefault("type", "unknown")
        duplicate.setdefault("instances", 0)
        duplicate.setdefault("description", "")
    
    # Validate confidence score
    try:
        score = float(validated["confidence_score"])
        validated["confidence_score"] = max(0.0, min(1.0, score))  # Clamp to 0-1
    except (ValueError, TypeError):
        validated["confidence_score"] = 0.0
    
    return validated


# Agent metadata for orchestrator
AGENT_INFO = {
    "name": "Records Wrangler",
    "description": "Identifies missing, incomplete, or duplicate records in legal cases",
    "capabilities": [
        "Missing record detection",
        "Duplicate record identification",
        "Urgency assessment",
        "Action recommendation",
        "Multi-document analysis"
    ],
    "output_schema": {
        "missing_records": "array[object]",
        "duplicates": "array[object]",
        "recommended_action": "string",
        "confidence_score": "number"
    },
    "record_types": [
        "medical_report",
        "police_report",
        "insurance_document",
        "witness_statement",
        "employment_record",
        "property_damage_assessment",
        "expert_opinion"
    ]
}
