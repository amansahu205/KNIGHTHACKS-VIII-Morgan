# Orchestrator Documentation

## Overview

The Orchestrator is the central intelligence system that analyzes case files, detects actionable tasks, and routes work to specialized AI agents.

## Architecture

```
Case File Upload
      ↓
Task Detection (regex + patterns)
      ↓
Workflow Creation
      ↓
Async Agent Execution
      ↓
Result Aggregation
      ↓
Structured JSON Output
```

## Components

### 1. orchestrator_core.py

**Main Function**: `process_case_text(text: str)`

**Workflow**:
1. **Task Detection** - Analyzes case text using regex patterns and keywords
2. **Workflow Creation** - Maps detected tasks to appropriate agents
3. **Agent Execution** - Runs agents asynchronously with error handling
4. **Result Aggregation** - Combines agent outputs into structured response

### 2. router.py

**Main Function**: `process_case_file(text: str)`

Simple wrapper that delegates to `orchestrator_core.process_case_text()`.

## Task Detection

The orchestrator detects 5 types of tasks:

### 1. Records Analysis
**Triggers**:
- "missing record", "incomplete record", "duplicate record"
- "need record", "awaiting record", "not received"
- "outstanding record", "pending record"

**Routes to**: `records_wrangler`

### 2. Client Communication
**Triggers**:
- "client anxious", "client worried", "client called"
- "client concerned", "reassure client", "update client"
- "client follow-up", "client needs"

**Routes to**: `communication_guru`

### 3. Legal Research
**Triggers**:
- "legal issue", "precedent", "case law", "statute"
- "legal research", "legal question", "jurisdiction"
- "verdict", "ruling", "legal basis"

**Routes to**: `legal_researcher`

### 4. Scheduling
**Triggers**:
- "schedule call", "schedule meeting", "contact witness"
- "call needed", "follow-up call", "appointment"
- "deposition", "interview witness", "phone number"

**Routes to**: `voice_bot_scheduler`

### 5. Evidence Organization
**Triggers**:
- "evidence", "exhibit", "document inventory", "photo"
- "medical bill", "police report", "witness statement"
- "classify document", "organize evidence"

**Routes to**: `evidence_sorter`

## Agent Execution

### Async Execution
- All agents run concurrently using `asyncio.gather()`
- Maximum execution time: 60 seconds per agent
- Timeout results in graceful fallback

### Error Handling
```python
{
    "status": "agent_unavailable",
    "error": "Error message",
    "agent_name": "agent_name"
}
```

### Success Response
```python
{
    "status": "success",
    "agent_name": "agent_name",
    "execution_time": 2.34,
    # ... agent-specific output
}
```

## Output Format

```json
{
    "summary": "Case #2024-PI-1234 | Type: Personal Injury | Detected 3 actionable task(s) | Analyzed by 3 AI agent(s)",
    "detected_tasks": [
        {
            "type": "records_analysis",
            "priority": "high",
            "match_count": 5,
            "confidence": 0.8
        }
    ],
    "agent_outputs": {
        "records_wrangler": {
            "status": "success",
            "agent_name": "records_wrangler",
            "execution_time": 2.45,
            "missing_records": [...],
            "duplicates": [...],
            "recommended_action": "...",
            "confidence_score": 0.85
        },
        "communication_guru": {
            "status": "success",
            "agent_name": "communication_guru",
            "execution_time": 1.89,
            "tone": "anxious",
            "message_draft": "...",
            "reasoning": "..."
        }
    },
    "recommended_actions": [
        "[records_wrangler] Request MRI results from St. Mary's Hospital",
        "[communication_guru] Send drafted message to client"
    ],
    "overall_confidence": 0.85,
    "agents_executed": 3,
    "agents_successful": 3,
    "execution_time_seconds": 3.45,
    "timestamp": "2024-10-25T22:30:15.123456"
}
```

## Logging

All orchestrator activity is logged to `temp/orchestrator_logs.log`.

**Log Levels**:
- `INFO`: Normal operation (task detection, agent execution, results)
- `WARNING`: Non-critical issues (no tasks detected, using defaults)
- `ERROR`: Agent failures, exceptions

**Log Format**:
```
2024-10-25 22:30:15,123 - orchestrator_core - INFO - ORCHESTRATOR: Starting case analysis
2024-10-25 22:30:15,234 - orchestrator_core - INFO - Step 1: Detecting tasks from case text...
2024-10-25 22:30:15,345 - orchestrator_core - INFO -   Detected: records_analysis (priority: high, matches: 5)
2024-10-25 22:30:15,456 - orchestrator_core - INFO - Step 2: Creating agent workflow...
2024-10-25 22:30:15,567 - orchestrator_core - INFO -   Executing 3 agent(s) concurrently...
2024-10-25 22:30:17,890 - orchestrator_core - INFO -     Agent records_wrangler completed in 2.32s
2024-10-25 22:30:18,901 - orchestrator_core - INFO - ORCHESTRATOR: Completed successfully in 3.45s
```

## Usage

### Basic Usage

```python
from orchestrator.router import process_case_file

# Process case file
result = await process_case_file(case_text)

# Access results
summary = result["summary"]
tasks = result["detected_tasks"]
agent_outputs = result["agent_outputs"]
actions = result["recommended_actions"]
confidence = result["overall_confidence"]
```

### With FastAPI

```python
from fastapi import FastAPI, UploadFile
from orchestrator.router import process_case_file

app = FastAPI()

@app.post("/process_file")
async def upload_case_file(file: UploadFile):
    content = await file.read()
    text = content.decode('utf-8')
    
    result = await process_case_file(text)
    return result
```

## Testing

```bash
# Run orchestrator tests
python temp/test_orchestrator.py
```

**Test Scenarios**:
1. Comprehensive case (multiple tasks, all agents)
2. Simple case (minimal tasks)
3. Client communication focus (specific agent)
4. Error handling (invalid input)
5. Sample file processing (realistic data)

## Performance

**Typical Execution Times**:
- Task detection: < 0.1s
- Single agent: 1-3s (depends on LLM)
- Multiple agents (concurrent): 2-5s
- Total orchestration: 3-6s

**Optimization**:
- Agents run concurrently (not sequentially)
- 60-second timeout prevents hanging
- Regex-based task detection (fast, no LLM needed)

## Error Handling

### Agent Failures
- Individual agent failures don't stop orchestration
- Failed agents return `"status": "agent_unavailable"`
- Other agents continue execution
- Partial results still returned

### Timeout Handling
- Agents timeout after 60 seconds
- Timeout treated as agent failure
- Graceful fallback with error message

### Invalid Input
- Empty text: Uses default workflow
- No tasks detected: Runs basic analysis agents
- Malformed text: Continues with best effort

## Configuration

### Environment Variables

Used by agents (not orchestrator directly):
- `OPENAI_API_KEY` - OpenAI API key
- `ANTHROPIC_API_KEY` - Anthropic API key
- `DEFAULT_LLM_PROVIDER` - LLM provider (openai/anthropic)
- `DEFAULT_MODEL` - Model name
- `TEMPERATURE` - LLM temperature (0.0-1.0)
- `MAX_TOKENS` - Max response tokens

### Timeouts

Modify in `orchestrator_core.py`:
```python
# Agent execution timeout (default: 60 seconds)
result = await asyncio.wait_for(
    agent_module.run(text, task),
    timeout=60.0  # Change this value
)
```

## Extending the Orchestrator

### Adding New Task Types

1. Add pattern to `_detect_tasks()`:
```python
patterns = {
    "new_task_type": {
        "keywords": [
            r"keyword1", r"keyword2", r"keyword3"
        ],
        "priority": "medium"
    }
}
```

2. Map to agent in `_create_workflow()`:
```python
task_to_agent = {
    "new_task_type": "new_agent_name"
}
```

3. Import new agent in `orchestrator_core.py`:
```python
from agents import new_agent_name
```

### Customizing Workflow

Modify `_create_workflow()` to change agent selection logic:
- Add conditional routing
- Implement agent dependencies
- Create sequential workflows
- Add agent prioritization

## Best Practices

1. **Always check agent status** before using output
2. **Log important decisions** for debugging
3. **Handle partial results** gracefully
4. **Monitor execution times** for performance
5. **Review logs regularly** for issues
6. **Test with realistic data** before deployment

## Troubleshooting

### No Tasks Detected
- Check case text contains relevant keywords
- Review regex patterns in `_detect_tasks()`
- Check log file for detection details

### Agent Failures
- Verify API keys are set
- Check agent logs for specific errors
- Ensure agents are properly imported
- Review timeout settings

### Slow Performance
- Check LLM response times
- Reduce number of concurrent agents
- Optimize agent prompts
- Consider caching results

### Log File Issues
- Ensure `temp/` directory exists
- Check file permissions
- Verify logging configuration

## API Reference

### process_case_text(text: str)

**Parameters**:
- `text` (str): Case file text content

**Returns**:
- `dict`: Structured orchestration results

**Raises**:
- Returns error dict instead of raising exceptions

### _detect_tasks(text: str)

**Parameters**:
- `text` (str): Case file text

**Returns**:
- `list[dict]`: Detected tasks with metadata

### _create_workflow(detected_tasks: list)

**Parameters**:
- `detected_tasks` (list): Tasks from detection

**Returns**:
- `list[dict]`: Agent workflow

### _execute_agents(text: str, workflow: list)

**Parameters**:
- `text` (str): Case file text
- `workflow` (list): Agent workflow

**Returns**:
- `dict`: Agent outputs keyed by agent name

### _aggregate_results(text: str, detected_tasks: list, agent_outputs: dict)

**Parameters**:
- `text` (str): Original case text
- `detected_tasks` (list): Detected tasks
- `agent_outputs` (dict): Agent results

**Returns**:
- `dict`: Aggregated final output

---

**Last Updated**: October 25, 2024
