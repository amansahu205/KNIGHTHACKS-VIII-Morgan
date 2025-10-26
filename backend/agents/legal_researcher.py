"""
Legal Researcher Agent
Finds relevant legal precedents, statutes, and verdicts to support case arguments
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
    Research relevant legal precedents and statutes for case support.
    
    Args:
        text: Full case file text or attorney query
        task: Task details from orchestrator containing:
            - task_type: Type of legal research needed
            - jurisdiction: Legal jurisdiction (state, federal)
            - case_type: Type of case (personal injury, contract, etc.)
            - legal_issue: Specific legal issue to research
            
    Returns:
        dict: Structured JSON with:
            - relevant_cases: List of supporting cases with citations
            - legal_basis: Primary legal foundation for the argument
            - reasoning_summary: How cases support the argument
            - confidence_score: 0.0-1.0 confidence in research quality
            
    Example:
        {
            "relevant_cases": [
                {
                    "case_name": "Smith v. Jones",
                    "citation": "123 F.3d 456 (9th Cir. 2020)",
                    "summary": "Court held that...",
                    "relevance": "Directly supports our negligence claim"
                }
            ],
            "legal_basis": "Negligence under state tort law...",
            "reasoning_summary": "The precedents establish...",
            "confidence_score": 0.82
        }
    """
    
    # Get LLM provider from environment (default to OpenAI)
    provider = os.getenv("DEFAULT_LLM_PROVIDER", "openai").lower()
    
    # Build structured prompt with legal research context
    system_prompt = """You are an expert legal research assistant specializing in finding relevant case law, statutes, and legal precedents.

Your role:
1. Analyze the legal issue presented in the case
2. Identify 2-3 most relevant legal precedents or statutes
3. Provide accurate citations (even if synthetic for demo purposes)
4. Explain how each precedent supports the legal argument
5. Synthesize a clear legal reasoning summary
6. Assess confidence in the research quality

Legal Research Guidelines:
- Focus on precedents from the same jurisdiction when possible
- Prioritize recent cases (last 10 years) unless landmark cases apply
- Consider both favorable and distinguishable precedents
- Cite specific holdings and legal principles
- Explain the factual similarities to the current case

Case Types to Consider:
- Personal Injury (negligence, premises liability, medical malpractice)
- Contract disputes
- Employment law
- Insurance claims
- Property disputes
- Civil rights

Citation Format:
- Case law: [Case Name], [Volume] [Reporter] [Page] ([Court] [Year])
- Statutes: [Code] § [Section] ([Year])

Always respond in valid JSON format with these exact keys:
- relevant_cases: array of objects with case_name, citation, summary, relevance
- legal_basis: string describing primary legal foundation
- reasoning_summary: string explaining how cases support the argument
- confidence_score: number between 0.0 and 1.0"""

    user_prompt = f"""Case Information:
{text}

Research Task:
{json.dumps(task, indent=2)}

Conduct legal research to find 2-3 relevant precedents or statutes that support this case.

For demonstration purposes, you may use realistic synthetic legal precedents if actual case law is not available in your training data. Ensure citations follow proper legal format.

Respond ONLY with valid JSON in this exact format:
{{
    "relevant_cases": [
        {{
            "case_name": "Case Name v. Defendant Name",
            "citation": "Volume Reporter Page (Court Year)",
            "summary": "Brief summary of the holding and key facts",
            "relevance": "How this case supports our argument"
        }}
    ],
    "legal_basis": "Primary legal foundation (tort law, contract law, statute, etc.)",
    "reasoning_summary": "Comprehensive explanation of how the precedents support the legal argument",
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
            "relevant_cases": [],
            "legal_basis": "",
            "reasoning_summary": f"Error conducting legal research: {str(e)}",
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
        "relevant_cases": result.get("relevant_cases", []),
        "legal_basis": result.get("legal_basis", ""),
        "reasoning_summary": result.get("reasoning_summary", ""),
        "confidence_score": result.get("confidence_score", 0.0)
    }
    
    # Validate relevant_cases structure
    if not isinstance(validated["relevant_cases"], list):
        validated["relevant_cases"] = []
    
    for case in validated["relevant_cases"]:
        if not isinstance(case, dict):
            continue
        # Ensure required fields for each case
        case.setdefault("case_name", "Unknown Case")
        case.setdefault("citation", "Citation not available")
        case.setdefault("summary", "")
        case.setdefault("relevance", "")
    
    # Limit to 5 cases maximum for clarity
    if len(validated["relevant_cases"]) > 5:
        validated["relevant_cases"] = validated["relevant_cases"][:5]
    
    # Validate confidence score
    try:
        score = float(validated["confidence_score"])
        validated["confidence_score"] = max(0.0, min(1.0, score))  # Clamp to 0-1
    except (ValueError, TypeError):
        validated["confidence_score"] = 0.0
    
    return validated


def _get_synthetic_precedents(case_type: str, jurisdiction: str = "federal") -> List[Dict[str, Any]]:
    """
    Provide synthetic legal precedents for demonstration purposes.
    In production, this would query a legal database API.
    
    Args:
        case_type: Type of legal case
        jurisdiction: Legal jurisdiction
        
    Returns:
        list: Synthetic precedent cases
    """
    # Synthetic precedents organized by case type
    precedents_db = {
        "personal_injury": [
            {
                "case_name": "Palsgraf v. Long Island Railroad Co.",
                "citation": "248 N.Y. 339, 162 N.E. 99 (1928)",
                "summary": "Landmark case establishing duty and proximate cause in negligence claims. Court held that duty is owed only to foreseeable plaintiffs within the zone of danger.",
                "relevance": "Establishes foundational negligence principles applicable to personal injury claims"
            },
            {
                "case_name": "Rowland v. Christian",
                "citation": "69 Cal.2d 108, 443 P.2d 561 (1968)",
                "summary": "California Supreme Court eliminated traditional distinctions between invitees, licensees, and trespassers in premises liability cases.",
                "relevance": "Supports modern premises liability analysis based on reasonableness"
            }
        ],
        "premises_liability": [
            {
                "case_name": "Rowland v. Christian",
                "citation": "69 Cal.2d 108, 443 P.2d 561 (1968)",
                "summary": "Eliminated traditional status-based duties in premises liability, adopting general negligence standard.",
                "relevance": "Establishes duty of reasonable care for all persons on property"
            },
            {
                "case_name": "Sprecher v. Adamson Companies",
                "citation": "30 Cal.3d 358, 636 P.2d 1121 (1981)",
                "summary": "Property owner liable for dangerous conditions they create or maintain, even if not obvious to visitors.",
                "relevance": "Supports liability for hazardous conditions on premises"
            }
        ],
        "negligence": [
            {
                "case_name": "Vaughan v. Menlove",
                "citation": "132 Eng. Rep. 490 (1837)",
                "summary": "Established objective reasonable person standard for negligence rather than subjective standard.",
                "relevance": "Foundational case for reasonable person standard in negligence analysis"
            },
            {
                "case_name": "Summers v. Tice",
                "citation": "33 Cal.2d 80, 199 P.2d 1 (1948)",
                "summary": "Burden of proof shifts to defendants when multiple parties act negligently and plaintiff cannot identify which caused injury.",
                "relevance": "Supports burden-shifting in cases with multiple potential tortfeasors"
            }
        ]
    }
    
    return precedents_db.get(case_type.lower(), precedents_db.get("negligence", []))


# Agent metadata for orchestrator
AGENT_INFO = {
    "name": "Legal Researcher",
    "description": "Finds relevant legal precedents, statutes, and verdicts to support case arguments",
    "capabilities": [
        "Case law research",
        "Statute identification",
        "Precedent analysis",
        "Legal reasoning synthesis",
        "Citation formatting",
        "Jurisdictional research"
    ],
    "output_schema": {
        "relevant_cases": "array[object]",
        "legal_basis": "string",
        "reasoning_summary": "string",
        "confidence_score": "number"
    },
    "supported_case_types": [
        "personal_injury",
        "premises_liability",
        "negligence",
        "contract_dispute",
        "employment_law",
        "insurance_claim",
        "medical_malpractice"
    ]
}
