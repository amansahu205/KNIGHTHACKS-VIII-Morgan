"""
Evidence Sorter Agent
Classifies and organizes case evidence, extracts metadata, and identifies gaps
"""

import os
import json
import re
from typing import Dict, Any, List
from datetime import datetime
from openai import AsyncOpenAI
from anthropic import AsyncAnthropic


# Initialize LLM clients
openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
anthropic_client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


async def run(text: str, task: Dict[str, Any]) -> Dict[str, Any]:
    """
    Classify and organize case evidence with metadata extraction.
    
    Args:
        text: Full case file text or document contents to analyze
        task: Task details from orchestrator containing:
            - task_type: Type of evidence analysis needed
            - context: Additional context about the case
            - case_type: Type of legal case
            
    Returns:
        dict: Structured JSON with:
            - evidence_summary: List of classified evidence with metadata
            - missing_evidence: List of referenced but missing evidence
            - recommended_action: Organization and next steps
            - confidence_score: 0.0-1.0 confidence in the analysis
            
    Example:
        {
            "evidence_summary": [
                {
                    "type": "medical",
                    "description": "ER Report from County General Hospital",
                    "date": "2024-01-05",
                    "source": "Dr. Sarah Chen",
                    "relevance_score": 0.95,
                    "authenticity_status": "verified"
                }
            ],
            "missing_evidence": [
                {
                    "type": "medical",
                    "description": "MRI results mentioned but not attached",
                    "referenced_in": "Doctor's notes"
                }
            ],
            "recommended_action": "Organize evidence by type and chronology...",
            "confidence_score": 0.88
        }
    """
    
    # Get LLM provider from environment (default to OpenAI)
    provider = os.getenv("DEFAULT_LLM_PROVIDER", "openai").lower()
    
    # Build structured prompt
    system_prompt = """You are an expert legal evidence analyst specializing in document classification, metadata extraction, and evidence organization.

Your role:
1. Analyze case documents and evidence
2. Classify evidence into appropriate categories
3. Extract structured metadata (dates, sources, authors)
4. Assess relevance and authenticity of each piece of evidence
5. Identify missing or inconsistent evidence references
6. Recommend evidence organization strategies

Evidence Categories:
- Medical: Hospital records, doctor's notes, test results, treatment plans, prescriptions
- Photographic: Photos of accident scene, injuries, property damage, surveillance footage
- Financial: Medical bills, wage statements, receipts, insurance documents, invoices
- Correspondence: Emails, letters, text messages, voicemails, faxes
- Testimonial: Witness statements, depositions, affidavits, declarations
- Police/Official: Police reports, incident reports, citations, official documents
- Expert: Expert opinions, evaluations, reports, certifications
- Physical: Physical objects, clothing, vehicle parts (described in inventory)
- Digital: Electronic records, metadata, social media posts, GPS data

Metadata to Extract:
- Document type and category
- Date of creation/occurrence
- Author/source/creator
- Parties involved
- Key facts or findings
- Relevance to case (0.0-1.0 score)
- Authenticity status (verified, unverified, questionable)

Relevance Scoring (0.0-1.0):
- 0.9-1.0: Critical evidence, directly proves key facts
- 0.7-0.8: Important evidence, strongly supports claims
- 0.5-0.6: Relevant evidence, provides context
- 0.3-0.4: Marginally relevant, background information
- 0.0-0.2: Minimal relevance, may be excluded

Authenticity Status:
- verified: Original document with proper authentication
- unverified: Document received but not yet authenticated
- questionable: Concerns about authenticity or accuracy
- pending: Awaiting verification or expert review

Missing Evidence Detection:
- Look for references to documents not present in file
- Identify exhibits mentioned but not attached
- Note incomplete document sets (e.g., partial medical records)
- Flag inconsistencies in evidence inventory

Always respond in valid JSON format with these exact keys:
- evidence_summary: array of objects with type, description, date, source, relevance_score, authenticity_status
- missing_evidence: array of objects with type, description, referenced_in
- recommended_action: string with organization and next steps
- confidence_score: number between 0.0 and 1.0"""

    user_prompt = f"""Case Documents and Evidence:
{text}

Task Details:
{json.dumps(task, indent=2)}

Analyze all evidence mentioned in this case file.

For each piece of evidence:
1. Classify it into the appropriate category
2. Extract metadata (date, source, description)
3. Assess its relevance to the case (0.0-1.0 score)
4. Determine authenticity status

Also identify any evidence that is referenced but missing from the file.

Respond ONLY with valid JSON in this exact format:
{{
    "evidence_summary": [
        {{
            "type": "category name",
            "description": "detailed description of evidence",
            "date": "YYYY-MM-DD or 'unknown'",
            "source": "author/creator/source",
            "relevance_score": 0.0-1.0,
            "authenticity_status": "verified|unverified|questionable|pending"
        }}
    ],
    "missing_evidence": [
        {{
            "type": "category name",
            "description": "description of missing evidence",
            "referenced_in": "where it was mentioned"
        }}
    ],
    "recommended_action": "clear organization strategy and next steps",
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
            "evidence_summary": [],
            "missing_evidence": [],
            "recommended_action": f"Error analyzing evidence: {str(e)}",
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
        "evidence_summary": result.get("evidence_summary", []),
        "missing_evidence": result.get("missing_evidence", []),
        "recommended_action": result.get("recommended_action", ""),
        "confidence_score": result.get("confidence_score", 0.0)
    }
    
    # Validate evidence_summary structure
    if not isinstance(validated["evidence_summary"], list):
        validated["evidence_summary"] = []
    
    valid_types = ["medical", "photographic", "financial", "correspondence", 
                   "testimonial", "police", "official", "expert", "physical", "digital"]
    valid_authenticity = ["verified", "unverified", "questionable", "pending"]
    
    for evidence in validated["evidence_summary"]:
        if not isinstance(evidence, dict):
            continue
        
        # Ensure required fields
        evidence.setdefault("type", "unknown")
        evidence.setdefault("description", "")
        evidence.setdefault("date", "unknown")
        evidence.setdefault("source", "unknown")
        evidence.setdefault("relevance_score", 0.5)
        evidence.setdefault("authenticity_status", "unverified")
        
        # Validate type
        if evidence["type"] not in valid_types:
            evidence["type"] = "unknown"
        
        # Validate relevance_score
        try:
            score = float(evidence["relevance_score"])
            evidence["relevance_score"] = max(0.0, min(1.0, score))
        except (ValueError, TypeError):
            evidence["relevance_score"] = 0.5
        
        # Validate authenticity_status
        if evidence["authenticity_status"] not in valid_authenticity:
            evidence["authenticity_status"] = "unverified"
        
        # Validate date format
        evidence["date"] = _validate_date(evidence["date"])
    
    # Sort evidence by relevance (highest first)
    validated["evidence_summary"].sort(
        key=lambda x: x.get("relevance_score", 0), 
        reverse=True
    )
    
    # Validate missing_evidence structure
    if not isinstance(validated["missing_evidence"], list):
        validated["missing_evidence"] = []
    
    for missing in validated["missing_evidence"]:
        if not isinstance(missing, dict):
            continue
        missing.setdefault("type", "unknown")
        missing.setdefault("description", "")
        missing.setdefault("referenced_in", "case file")
    
    # Validate confidence score
    try:
        score = float(validated["confidence_score"])
        validated["confidence_score"] = max(0.0, min(1.0, score))
    except (ValueError, TypeError):
        validated["confidence_score"] = 0.0
    
    return validated


def _validate_date(date_str: str) -> str:
    """
    Validate and standardize date format.
    
    Args:
        date_str: Date string to validate
        
    Returns:
        str: Standardized date (YYYY-MM-DD) or 'unknown'
    """
    if not date_str or date_str.lower() == "unknown":
        return "unknown"
    
    # Try to parse various date formats
    date_patterns = [
        r'(\d{4})-(\d{2})-(\d{2})',  # YYYY-MM-DD
        r'(\d{2})/(\d{2})/(\d{4})',  # MM/DD/YYYY
        r'(\d{1,2})/(\d{1,2})/(\d{2,4})',  # M/D/YY or M/D/YYYY
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, date_str)
        if match:
            try:
                groups = match.groups()
                if len(groups[0]) == 4:  # YYYY-MM-DD
                    year, month, day = groups
                else:  # MM/DD/YYYY or similar
                    if len(groups[2]) == 2:  # Two-digit year
                        year = "20" + groups[2]
                    else:
                        year = groups[2]
                    month, day = groups[0], groups[1]
                
                # Validate date
                datetime(int(year), int(month), int(day))
                return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
            except (ValueError, IndexError):
                continue
    
    return "unknown"


# Agent metadata for orchestrator
AGENT_INFO = {
    "name": "Evidence Sorter",
    "description": "Classifies and organizes case evidence, extracts metadata, and identifies gaps",
    "capabilities": [
        "Evidence classification",
        "Metadata extraction",
        "Relevance scoring",
        "Authenticity assessment",
        "Missing evidence detection",
        "Document organization",
        "Evidence gap analysis"
    ],
    "output_schema": {
        "evidence_summary": "array[object]",
        "missing_evidence": "array[object]",
        "recommended_action": "string",
        "confidence_score": "number"
    },
    "evidence_categories": [
        "medical",
        "photographic",
        "financial",
        "correspondence",
        "testimonial",
        "police",
        "official",
        "expert",
        "physical",
        "digital"
    ],
    "authenticity_levels": [
        "verified",
        "unverified",
        "questionable",
        "pending"
    ]
}
