# AI Agents Documentation

## Overview

Each agent is a specialized module that processes specific legal tasks using LLM-powered analysis.

## Agent Structure

All agents follow this standard interface:

```python
async def run(text: str, task: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process a specific task.
    
    Args:
        text: Full case file text content
        task: Task details from orchestrator
        
    Returns:
        dict: Structured JSON output specific to agent
    """
```

## Available Agents

### 1. Client Communication Guru

**File**: `communication_guru.py`

**Purpose**: Generate empathetic, professional client messages

**Input**:
- `text`: Case file content
- `task`: Task details with client context

**Output**:
```json
{
    "tone": "Client's emotional state",
    "message_draft": "Complete drafted message",
    "reasoning": "Communication strategy explanation"
}
```

**Example Usage**:
```python
from agents.communication_guru import run

result = await run(case_text, {
    "task_type": "client_reassurance",
    "context": "Client anxious about timeline",
    "client_info": {"name": "John Doe"}
})
```

### 2. Records Wrangler

**File**: `records_wrangler.py`

**Purpose**: Identify missing, incomplete, or duplicate records in legal cases

**Input**:
- `text`: Case file with documentation details
- `task`: Task details with case type and context

**Output**:
```json
{
    "missing_records": [
        {
            "type": "medical_report",
            "description": "MRI results from St. Mary's Hospital",
            "urgency": "high",
            "source": "St. Mary's Radiology Department"
        }
    ],
    "duplicates": [
        {
            "type": "police_report",
            "instances": 2,
            "description": "Report #2024-1234 appears twice"
        }
    ],
    "recommended_action": "Contact St. Mary's records department...",
    "confidence_score": 0.85
}
```

**Record Types Detected**:
- Medical reports (hospital, doctor's notes, MRI/X-ray, treatment plans)
- Police reports and incident statements
- Insurance documents (claims, approvals, denials)
- Witness statements and depositions
- Employment records (for lost wages)
- Property damage assessments
- Expert opinions and evaluations

**Example Usage**:
```python
from agents.records_wrangler import run

result = await run(case_text, {
    "task_type": "record_analysis",
    "case_type": "personal_injury_motor_vehicle"
})
```

### 3. Legal Researcher

**File**: `legal_researcher.py`

**Purpose**: Find relevant legal precedents, statutes, and verdicts to support case arguments

**Input**:
- `text`: Case file or attorney query with legal issues
- `task`: Task details with jurisdiction and case type

**Output**:
```json
{
    "relevant_cases": [
        {
            "case_name": "Rowland v. Christian",
            "citation": "69 Cal.2d 108, 443 P.2d 561 (1968)",
            "summary": "California Supreme Court eliminated traditional distinctions...",
            "relevance": "Establishes duty of reasonable care for all persons on property"
        }
    ],
    "legal_basis": "California premises liability law under negligence standard",
    "reasoning_summary": "The precedents establish that business owners owe...",
    "confidence_score": 0.88
}
```

**Research Capabilities**:
- Case law research (state and federal)
- Statute identification
- Legal precedent analysis
- Citation formatting
- Legal reasoning synthesis
- Jurisdictional research

**Supported Case Types**:
- Personal injury
- Premises liability
- Negligence
- Contract disputes
- Employment law
- Insurance claims
- Medical malpractice

**Example Usage**:
```python
from agents.legal_researcher import run

result = await run(case_text, {
    "task_type": "legal_research",
    "jurisdiction": "california",
    "case_type": "premises_liability",
    "legal_issue": "duty of care for hazardous conditions"
})
```

### 4. Voice Bot Scheduler

**File**: `voice_bot_scheduler.py`

**Purpose**: Coordinate calls, meetings, and communications with clients, witnesses, and other parties

**Input**:
- `text`: Case file with contact information and communication needs
- `task`: Task details with urgency and context

**Output**:
```json
{
    "action_type": "call",
    "contact_name": "Sarah Mitchell",
    "contact_number": "+1-555-123-4567",
    "contact_email": "sarah.mitchell@email.com",
    "suggested_time": "Tuesday-Thursday, 5:00 PM - 7:00 PM",
    "call_script": "Hello Ms. Mitchell, this is [Name] from...",
    "reasoning": "Witness works 9-5, best to call after work hours...",
    "confidence_score": 0.87
}
```

**Scheduling Capabilities**:
- Contact information extraction and standardization
- Phone number formatting (+1-XXX-XXX-XXXX)
- Email validation
- Optimal time window recommendations
- Professional call script generation
- Communication method selection (call/email/meeting)

**Communication Types**:
- Client follow-ups
- Witness interviews
- Medical provider contacts
- Insurance adjuster communications
- Opposing counsel coordination
- Expert witness scheduling

**Example Usage**:
```python
from agents.voice_bot_scheduler import run

result = await run(case_text, {
    "task_type": "witness_interview",
    "context": "Need witness statement for accident case",
    "urgency": "high"
})
```

### 5. Evidence Sorter

**File**: `evidence_sorter.py`

**Purpose**: Classify and organize case evidence, extract metadata, and identify gaps

**Input**:
- `text`: Case file with evidence inventory or document contents
- `task`: Task details with case type and context

**Output**:
```json
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
```

**Evidence Categories**:
- Medical (hospital records, test results, treatment plans)
- Photographic (accident scene, injuries, property damage)
- Financial (bills, wage statements, receipts)
- Correspondence (emails, letters, text messages)
- Testimonial (witness statements, depositions, affidavits)
- Police/Official (police reports, incident reports, citations)
- Expert (expert opinions, evaluations, certifications)
- Physical (physical objects, clothing, vehicle parts)
- Digital (electronic records, social media, GPS data)

**Metadata Extracted**:
- Document type and category
- Date of creation/occurrence
- Author/source/creator
- Relevance score (0.0-1.0)
- Authenticity status (verified/unverified/questionable/pending)

**Example Usage**:
```python
from agents.evidence_sorter import run

result = await run(case_text, {
    "task_type": "evidence_analysis",
    "case_type": "personal_injury"
})
```

## Configuration

Agents use environment variables for LLM configuration:

- `DEFAULT_LLM_PROVIDER`: `openai` or `anthropic` (default: `openai`)
- `DEFAULT_MODEL`: Model name (default: `gpt-4-turbo-preview`)
- `TEMPERATURE`: 0.0-1.0 (default: `0.7`)
- `MAX_TOKENS`: Max response length (default: `4096`)

## Testing

Test individual agents using scripts in `/temp/`:

```bash
# Set API key
export OPENAI_API_KEY='your-key-here'

# Test Communication Guru
python temp/test_communication_guru.py

# Test Records Wrangler
python temp/test_records_wrangler.py

# Test Legal Researcher
python temp/test_legal_researcher.py

# Test Voice Bot Scheduler
python temp/test_voice_bot_scheduler.py

# Test Evidence Sorter
python temp/test_evidence_sorter.py
```

## Adding New Agents

1. Create new file: `backend/agents/your_agent.py`
2. Implement `async def run(text: str, task: dict) -> dict`
3. Add structured prompt and JSON output
4. Update `__init__.py` to export the agent
5. Create test script in `temp/test_your_agent.py`
