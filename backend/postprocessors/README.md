# Postprocessors Documentation

## Overview

Postprocessor modules that transform orchestrator outputs into human-readable formats for attorney review and client communication.

## Modules

### brief_generator.py

**Purpose**: Generate professional attorney briefs from orchestrator outputs.

**Main Function**: `generate_attorney_brief(orchestrator_output: dict) -> str`

#### Input

Complete orchestrator output containing:
- `context_metadata` - Extracted case metadata
- `detected_tasks` - List of detected tasks
- `agent_outputs` - Results from all agents
- `recommended_actions` - List of recommended actions

#### Output

Professional summary paragraph (120-180 words) covering:
- Client name, case number, and case type
- Date of incident and key parties (insurer, medical providers)
- Main findings from each agent
- Recommended next actions

#### Example Output

```
This office represents Emily Watson in Case #2024-PI-8888, which involves 
a premises liability claim arising from an incident that occurred on 
February 15, 2024. The defendant's carrier is Allstate Insurance, and the 
client received treatment at Memorial Hospital and other facilities. Our 
comprehensive case analysis has identified 3 missing records and found 1 
duplicate document, detected anxious client tone and prepared appropriate 
response, found 2 relevant legal precedents, catalogued 5 pieces of evidence 
(4 verified), noted 1 missing exhibit, scheduled call with Sarah Mitchell. 
To advance this matter, priority actions include: request MRI results from 
St. Mary's Hospital, obtain physical therapy records (8 sessions), and 3 
additional follow-up items.
```

#### Features

- **Template-based generation**: No LLM calls, fast and deterministic
- **Professional tone**: Attorney-appropriate language
- **Comprehensive coverage**: Includes all agent findings
- **Action prioritization**: Highlights top 3 recommended actions
- **Graceful handling**: Works with partial or missing data
- **Logging**: All generation activity logged

#### Agent Summarization

The brief generator includes specialized summarizers for each agent:

##### Records Wrangler
- Mentions missing records count
- Notes duplicate documents
- Confirms completeness if no issues

**Example**: "identified 3 missing records and found 1 duplicate document"

##### Communication Guru
- Reports detected client tone
- Mentions prepared response

**Example**: "detected anxious client tone and prepared appropriate response"

##### Legal Researcher
- Lists number of relevant precedents
- Mentions key case names

**Example**: "found 2 relevant legal precedents (Martinez v. SuperMart)"

##### Evidence Sorter
- Reports evidence count
- Notes verified vs unverified
- Mentions missing exhibits

**Example**: "catalogued 5 pieces of evidence (4 verified), noted 1 missing exhibit"

##### Voice Bot Scheduler
- Reports scheduled contacts
- Mentions action type (call/email/meeting)

**Example**: "scheduled call with Sarah Mitchell"

#### Usage

```python
from postprocessors.brief_generator import generate_attorney_brief

# After orchestrator completes
orchestrator_output = await process_case_text(case_text)

# Generate brief
brief = await generate_attorney_brief(orchestrator_output)

print(brief)
```

#### Integration

The brief generator is automatically called by the orchestrator after all agents complete:

```python
# In orchestrator_core.py (Step 5)
attorney_brief = await generate_attorney_brief(result)
result["attorney_brief"] = attorney_brief
```

#### Testing

```bash
python temp/test_brief_generator.py
```

Test scenarios:
1. Comprehensive case (all 5 agents)
2. Partial case (single agent)
3. Minimal context (no agents)
4. Mixed results (some agent failures)

#### Helper Functions

##### `summarize_agent_result(agent_name, data)`
Generates one-line summary for individual agent output.

**Parameters**:
- `agent_name` (str): Name of the agent
- `data` (dict): Agent output data

**Returns**: One-line summary string or None if agent failed

##### `_generate_case_overview(context)`
Creates case overview from context metadata.

##### `_generate_agent_findings(agent_outputs)`
Compiles findings from all agents.

##### `_generate_action_summary(recommended_actions)`
Summarizes top recommended actions.

##### `_clean_action(action)`
Cleans action text (removes agent prefix, normalizes case).

#### Output Format

The brief follows this structure:

1. **Case Overview** (1-2 sentences)
   - Client identification
   - Case number and type
   - Incident date
   - Key parties (insurance, medical providers)

2. **Agent Findings** (2-4 sentences)
   - Summary from each successful agent
   - Comma-separated list format

3. **Recommended Actions** (1-2 sentences)
   - Top 2-3 priority actions
   - Additional items count if more than 3

#### Logging

All brief generation activity is logged to `temp/orchestrator_logs.log`:

```
2024-10-26 00:15:30 - brief_generator - INFO - ======================================================================
2024-10-26 00:15:30 - brief_generator - INFO - BRIEF GENERATOR: Starting attorney brief generation
2024-10-26 00:15:30 - brief_generator - INFO - BRIEF GENERATOR: Brief generated (766 characters)
2024-10-26 00:15:30 - brief_generator - INFO - Execution time: 0.003s
2024-10-26 00:15:30 - brief_generator - INFO - ======================================================================
```

#### Error Handling

- **Missing context**: Uses generic language ("This case")
- **No agent outputs**: Reports no findings
- **Agent failures**: Skips failed agents silently
- **No actions**: States "no immediate actions required"
- **Generation error**: Returns error message

#### Performance

- **Generation time**: < 0.01 seconds
- **No LLM calls**: Instant, deterministic
- **Memory efficient**: Processes output in-place

#### Customization

To customize the brief format:

1. **Modify templates**: Edit string templates in generation functions
2. **Adjust verbosity**: Change word count targets in comments
3. **Add sections**: Create new generation functions
4. **Change tone**: Modify language in template strings

#### Future Enhancements

Potential improvements:
1. **LLM-based generation**: Use LLM for more natural language
2. **Multiple formats**: Generate different brief styles (executive, technical, client-facing)
3. **Formatting**: Add markdown or HTML formatting
4. **Localization**: Support multiple languages
5. **Templates**: Allow custom templates via configuration

---

**Last Updated**: October 26, 2024
