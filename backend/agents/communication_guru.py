"""
Client Communication Guru Agent
Generates empathetic, professional client messages based on case context
"""

import os
import json
from typing import Dict, Any
from openai import AsyncOpenAI
from anthropic import AsyncAnthropic


# Initialize LLM clients
openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
anthropic_client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


async def run(text: str, task: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate empathetic client communication based on case context.
    
    Args:
        text: Full case file text content
        task: Task details from orchestrator containing:
            - task_type: Type of communication needed
            - context: Additional context for the message
            - client_info: Client details if available
            
    Returns:
        dict: Structured JSON with:
            - tone: Detected client tone/emotional state
            - message_draft: Generated empathetic message
            - reasoning: Explanation of communication approach
            
    Example:
        {
            "tone": "anxious, seeking reassurance",
            "message_draft": "Dear [Client Name], ...",
            "reasoning": "Client appears concerned about timeline..."
        }
    """
    
    # Get LLM provider from environment (default to OpenAI)
    provider = os.getenv("DEFAULT_LLM_PROVIDER", "openai").lower()
    
    # Build structured prompt
    system_prompt = """You are an expert legal communication specialist helping attorneys draft empathetic, professional client messages.

Your role:
1. Analyze the client's emotional state and concerns from the case context
2. Draft a compassionate, clear message that addresses their needs
3. Maintain professional legal communication standards
4. Provide reasoning for your communication approach

Always respond in valid JSON format with these exact keys:
- tone: string describing the client's emotional state
- message_draft: string with the complete drafted message
- reasoning: string explaining your communication strategy"""

    user_prompt = f"""Case Context:
{text}

Task Details:
{json.dumps(task, indent=2)}

Based on this case information, analyze the client's tone and draft an empathetic message the attorney can send.

Respond ONLY with valid JSON in this exact format:
{{
    "tone": "description of client's emotional state",
    "message_draft": "complete drafted message for the client",
    "reasoning": "explanation of communication approach"
}}"""

    try:
        if provider == "anthropic":
            result = await _call_anthropic(system_prompt, user_prompt)
        else:
            result = await _call_openai(system_prompt, user_prompt)
        
        return result
        
    except Exception as e:
        # Return error in structured format
        return {
            "tone": "error",
            "message_draft": "",
            "reasoning": f"Error generating communication: {str(e)}",
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


# Agent metadata for orchestrator
AGENT_INFO = {
    "name": "Client Communication Guru",
    "description": "Drafts empathetic, professional client messages",
    "capabilities": [
        "Tone analysis",
        "Empathetic message generation",
        "Professional legal communication",
        "Context-aware drafting"
    ],
    "output_schema": {
        "tone": "string",
        "message_draft": "string",
        "reasoning": "string"
    }
}
