"""
Voice Bot Scheduler Agent
Coordinates calls, meetings, and communications with clients, witnesses, and other parties
"""

import os
import json
import re
from typing import Dict, Any, List
from openai import AsyncOpenAI
from anthropic import AsyncAnthropic


# Initialize LLM clients
openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
anthropic_client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


async def run(text: str, task: Dict[str, Any]) -> Dict[str, Any]:
    """
    Schedule calls, meetings, and communications based on case needs.
    
    Args:
        text: Full case file text with contact information and communication needs
        task: Task details from orchestrator containing:
            - task_type: Type of communication needed (follow_up, witness_contact, etc.)
            - context: Additional context about the communication purpose
            - urgency: Priority level (low, medium, high)
            
    Returns:
        dict: Structured JSON with:
            - action_type: Type of action ('call', 'email', 'meeting')
            - contact_name: Name of person to contact
            - contact_number: Phone number (standardized format)
            - contact_email: Email address (if applicable)
            - suggested_time: Best time window for contact
            - call_script: Script for paralegal or voice bot
            - reasoning: Explanation for scheduling recommendation
            - confidence_score: 0.0-1.0 confidence in the recommendation
            
    Example:
        {
            "action_type": "call",
            "contact_name": "Sarah Mitchell",
            "contact_number": "+1-555-123-4567",
            "contact_email": "sarah.mitchell@email.com",
            "suggested_time": "Tuesday-Thursday, 2:00 PM - 4:00 PM",
            "call_script": "Hello Ms. Mitchell, this is [Name] from...",
            "reasoning": "Witness needs to provide statement...",
            "confidence_score": 0.85
        }
    """
    
    # Get LLM provider from environment (default to OpenAI)
    provider = os.getenv("DEFAULT_LLM_PROVIDER", "openai").lower()
    
    # Build structured prompt
    system_prompt = """You are an expert legal scheduling assistant specializing in coordinating communications for law firms.

Your role:
1. Analyze case information to identify communication needs
2. Extract and standardize contact information (names, phone numbers, emails)
3. Determine the most appropriate communication method (call, email, meeting)
4. Suggest optimal contact time windows based on context and urgency
5. Generate professional call scripts for paralegals or automated voice systems
6. Provide clear reasoning for scheduling recommendations

Communication Types:
- Client follow-ups (case updates, reassurance, information gathering)
- Witness interviews (statement collection, fact verification)
- Medical provider contacts (records requests, clarifications)
- Insurance adjuster communications (claim status, negotiations)
- Opposing counsel coordination (discovery, settlement discussions)
- Expert witness scheduling (evaluations, depositions)

Phone Number Formatting:
- Standardize to: +1-XXX-XXX-XXXX format for US numbers
- Include country code when available
- Extract from various formats: (555) 123-4567, 555.123.4567, etc.

Time Window Considerations:
- Client calls: Evenings/weekends often better (after work hours)
- Business contacts: Weekdays 9 AM - 5 PM
- Medical offices: Weekdays 8 AM - 4 PM (avoid lunch 12-1 PM)
- Urgent matters: Same day or next business day
- Routine follow-ups: Within 3-5 business days

Call Script Guidelines:
- Professional and courteous tone
- Clear identification of caller and law firm
- Concise purpose statement
- Specific information needed or action requested
- Offer to answer questions
- Thank the person for their time

Always respond in valid JSON format with these exact keys:
- action_type: string ('call', 'email', or 'meeting')
- contact_name: string
- contact_number: string (standardized format)
- contact_email: string (or empty if not available)
- suggested_time: string (specific time window)
- call_script: string (complete script)
- reasoning: string (explanation for recommendation)
- confidence_score: number between 0.0 and 1.0"""

    user_prompt = f"""Case Information:
{text}

Task Details:
{json.dumps(task, indent=2)}

Analyze this case and determine what communication needs to be scheduled.

Extract contact information, suggest the best communication method and timing, and generate an appropriate call script.

Respond ONLY with valid JSON in this exact format:
{{
    "action_type": "call|email|meeting",
    "contact_name": "Full name of person to contact",
    "contact_number": "+1-XXX-XXX-XXXX",
    "contact_email": "email@example.com or empty string",
    "suggested_time": "Specific time window recommendation",
    "call_script": "Complete professional call script",
    "reasoning": "Explanation for this scheduling recommendation",
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
            "action_type": "call",
            "contact_name": "",
            "contact_number": "",
            "contact_email": "",
            "suggested_time": "",
            "call_script": "",
            "reasoning": f"Error scheduling communication: {str(e)}",
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
        "action_type": result.get("action_type", "call"),
        "contact_name": result.get("contact_name", ""),
        "contact_number": result.get("contact_number", ""),
        "contact_email": result.get("contact_email", ""),
        "suggested_time": result.get("suggested_time", ""),
        "call_script": result.get("call_script", ""),
        "reasoning": result.get("reasoning", ""),
        "confidence_score": result.get("confidence_score", 0.0)
    }
    
    # Validate action_type
    valid_actions = ["call", "email", "meeting"]
    if validated["action_type"].lower() not in valid_actions:
        validated["action_type"] = "call"
    else:
        validated["action_type"] = validated["action_type"].lower()
    
    # Standardize phone number format
    if validated["contact_number"]:
        validated["contact_number"] = _standardize_phone_number(validated["contact_number"])
    
    # Validate email format (basic check)
    if validated["contact_email"]:
        validated["contact_email"] = _validate_email(validated["contact_email"])
    
    # Validate confidence score
    try:
        score = float(validated["confidence_score"])
        validated["confidence_score"] = max(0.0, min(1.0, score))  # Clamp to 0-1
    except (ValueError, TypeError):
        validated["confidence_score"] = 0.0
    
    return validated


def _standardize_phone_number(phone: str) -> str:
    """
    Standardize phone number to +1-XXX-XXX-XXXX format.
    
    Args:
        phone: Phone number in any format
        
    Returns:
        str: Standardized phone number
    """
    # Remove all non-digit characters
    digits = re.sub(r'\D', '', phone)
    
    # Handle different length numbers
    if len(digits) == 10:
        # US number without country code
        return f"+1-{digits[:3]}-{digits[3:6]}-{digits[6:]}"
    elif len(digits) == 11 and digits[0] == '1':
        # US number with country code
        return f"+1-{digits[1:4]}-{digits[4:7]}-{digits[7:]}"
    elif len(digits) > 11:
        # International number
        return f"+{digits[:2]}-{digits[2:]}"
    else:
        # Return as-is if format is unclear
        return phone


def _validate_email(email: str) -> str:
    """
    Basic email validation.
    
    Args:
        email: Email address to validate
        
    Returns:
        str: Validated email or empty string if invalid
    """
    # Basic email regex pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if re.match(pattern, email.strip()):
        return email.strip().lower()
    else:
        return ""


# Agent metadata for orchestrator
AGENT_INFO = {
    "name": "Voice Bot Scheduler",
    "description": "Coordinates calls, meetings, and communications with clients, witnesses, and other parties",
    "capabilities": [
        "Contact information extraction",
        "Phone number standardization",
        "Communication method recommendation",
        "Time window optimization",
        "Call script generation",
        "Meeting coordination",
        "Email drafting support"
    ],
    "output_schema": {
        "action_type": "string",
        "contact_name": "string",
        "contact_number": "string",
        "contact_email": "string",
        "suggested_time": "string",
        "call_script": "string",
        "reasoning": "string",
        "confidence_score": "number"
    },
    "communication_types": [
        "client_follow_up",
        "witness_interview",
        "medical_provider_contact",
        "insurance_adjuster",
        "opposing_counsel",
        "expert_witness_scheduling"
    ]
}
