"""
Client Communication Guru Agent - Enhanced
Generates empathetic, professional client messages based on case context.
Now includes sentiment analysis, urgency detection, and call recommendations.
"""

import os
import json
from typing import Dict, Any, List
from datetime import datetime
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
    
    # Build enhanced structured prompt
    system_prompt = """You are an expert legal communication specialist with emotional intelligence capabilities.

Your role:
1. SENTIMENT ANALYSIS: Analyze the client's emotional state and calculate a sentiment score (0-100)
   - 0-30: Calm, satisfied
   - 31-50: Slightly concerned
   - 51-70: Worried, anxious
   - 71-85: Frustrated, distressed
   - 86-100: Extremely upset, angry, emergency

2. URGENCY DETECTION: Determine response urgency based on:
   - Emotional distress level
   - Time-sensitive keywords (urgent, emergency, deadline, court date)
   - Multiple unanswered attempts
   - Financial stress indicators
   - Legal deadline mentions

3. COMMUNICATION METHOD: Recommend the best way to respond:
   - CALL: High sentiment score (>70), complex emotions, urgent matters
   - EMAIL: Low-medium sentiment (<70), simple questions, routine updates
   - BOTH: Critical situations requiring immediate call + written follow-up

4. RESPONSE CONTENT:
   - If CALL recommended: Provide talking points for the attorney
   - If EMAIL recommended: Draft empathetic email
   - Always provide reasoning for your recommendation

Always respond in valid JSON format with ALL required keys."""

    user_prompt = f"""Case Context:
{text}

Task Details:
{json.dumps(task, indent=2)}

Analyze this case and provide a comprehensive communication recommendation.

Respond ONLY with valid JSON in this EXACT format:
{{
    "tone": "description of client's emotional state",
    "sentiment_score": 75,
    "emotion_detected": "frustrated_anxious",
    "trigger_keywords": ["worried", "frustrated", "urgent"],
    "urgency_level": "HIGH",
    "response_timeframe": "within_2_hours",
    "recommended_method": "call",
    "call_recommendation": {{
        "should_call": true,
        "urgency": "within_2_hours",
        "reason": "Client shows high frustration and needs immediate reassurance",
        "talking_points": [
            "Acknowledge their frustration",
            "Explain next steps clearly",
            "Provide specific timeline",
            "Reassure with firm's experience"
        ]
    }},
    "message_draft": "complete drafted email message",
    "reasoning": "explanation of communication strategy"
}}

IMPORTANT:
- sentiment_score must be 0-100 integer
- urgency_level must be: LOW, MEDIUM, HIGH, or CRITICAL
- recommended_method must be: call, email, or both
- If recommended_method is "email", set call_recommendation.should_call to false
- Always include all fields even if some are null"""

    try:
        if provider == "anthropic":
            result = await _call_anthropic(system_prompt, user_prompt)
        else:
            result = await _call_openai(system_prompt, user_prompt)
        
        return result
        
    except Exception as e:
        # Return error in structured format with all required fields
        return {
            "tone": "error",
            "sentiment_score": 0,
            "emotion_detected": "unknown",
            "trigger_keywords": [],
            "urgency_level": "MEDIUM",
            "response_timeframe": "within_24_hours",
            "recommended_method": "email",
            "call_recommendation": {
                "should_call": False,
                "urgency": "not_applicable",
                "reason": "Error occurred during analysis",
                "talking_points": []
            },
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
    "name": "Client Communication Guru (Enhanced)",
    "description": "Analyzes client sentiment, detects urgency, and recommends communication method (call vs email)",
    "capabilities": [
        "Sentiment analysis (0-100 score)",
        "Emotion detection",
        "Urgency assessment",
        "Call vs email recommendation",
        "Talking points generation",
        "Empathetic message drafting",
        "Professional legal communication",
        "Context-aware strategy"
    ],
    "output_schema": {
        "tone": "string",
        "sentiment_score": "integer (0-100)",
        "emotion_detected": "string",
        "trigger_keywords": "array of strings",
        "urgency_level": "enum (LOW, MEDIUM, HIGH, CRITICAL)",
        "response_timeframe": "string",
        "recommended_method": "enum (call, email, both)",
        "call_recommendation": "object",
        "message_draft": "string",
        "reasoning": "string"
    }
}
