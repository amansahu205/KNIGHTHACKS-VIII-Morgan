# Utilities Documentation

## Overview

Utility modules providing supporting functionality for the KNIGHTHACKS-VIII-Morgan system.

## Modules

### context_enricher.py

**Purpose**: Extract structured metadata from legal case text using regex and keyword heuristics.

**Main Function**: `extract_case_context(text: str) -> dict`

#### Extracted Fields

1. **client_name**
   - Patterns: "Client: John Doe", "Plaintiff: Jane Smith", "Claimant: Robert Johnson"
   - Confidence: 0.80-0.95

2. **case_number**
   - Patterns: "Case #2024-PI-1234", "MM-2024-5678", "File #: 2024-1234"
   - Confidence: 0.80-0.95

3. **case_type**
   - Categories: Personal Injury, Premises Liability, Medical Malpractice, Employment, Insurance Dispute, Contract Dispute
   - Keywords: "auto accident", "slip and fall", "medical malpractice", etc.
   - Confidence: 0.75-0.95

4. **insurance_company**
   - Patterns: Known insurers (State Farm, Allstate, etc.), "Company Insurance"
   - Confidence: 0.75-0.95

5. **date_of_incident**
   - Patterns: "Date of Incident: 2024-01-15", "January 15, 2024", "01/15/2024"
   - Normalized to ISO format (YYYY-MM-DD)
   - Confidence: 0.70-0.95

6. **medical_providers**
   - Patterns: "Dr. Smith", "St. Mary's Hospital", "County General Hospital"
   - Returns list of providers with individual confidence scores
   - Confidence: 0.85-0.95 per provider

#### Output Format

```json
{
    "client_name": {
        "value": "Emily Watson",
        "confidence": 0.95
    },
    "case_number": {
        "value": "2024-PI-8888",
        "confidence": 0.95
    },
    "case_type": {
        "value": "premises liability",
        "confidence": 0.95
    },
    "insurance_company": {
        "value": "Allstate",
        "confidence": 0.95
    },
    "date_of_incident": {
        "value": "2024-02-15",
        "confidence": 0.95
    },
    "medical_providers": [
        {
            "value": "Dr. Amanda Foster",
            "confidence": 0.90
        },
        {
            "value": "Memorial Hospital",
            "confidence": 0.90
        }
    ]
}
```

#### Features

- **Regex-based extraction**: Fast, deterministic pattern matching
- **Confidence scoring**: Each field includes confidence (0.0-1.0)
- **Graceful handling**: Returns None for missing data
- **Date normalization**: Converts various date formats to ISO (YYYY-MM-DD)
- **Comprehensive logging**: Logs all extraction attempts to `temp/orchestrator_logs.log`

#### Usage

```python
from utils.context_enricher import extract_case_context

case_text = """
Case #2024-PI-1234
Client: John Doe
Date of Incident: January 15, 2024
...
"""

context = extract_case_context(case_text)

# Access extracted data
client_name = context["client_name"]["value"]
confidence = context["client_name"]["confidence"]

if client_name:
    print(f"Client: {client_name} (confidence: {confidence})")
```

#### Testing

```bash
python temp/test_context_enricher.py
```

Test scenarios:
1. Basic extraction (slip and fall case)
2. Auto accident case
3. Medical malpractice case
4. Sample case file
5. Minimal data (edge case)

#### Integration

The context enricher is automatically called by the orchestrator before task detection:

```python
# In orchestrator_core.py
context_metadata = extract_case_context(text)
# ... task detection and agent execution ...
result["context_metadata"] = context_metadata
```

This enriched context is included in all orchestrator outputs for downstream use.

#### Confidence Scoring

Confidence scores are based on:
- **Pattern specificity**: More specific patterns = higher confidence
- **Keyword strength**: Direct labels (e.g., "Client:") = higher confidence
- **Known entities**: Recognized names (e.g., "State Farm") = higher confidence

**Confidence Ranges**:
- 0.90-1.00: Very high confidence (explicit labels, known entities)
- 0.80-0.89: High confidence (strong patterns)
- 0.70-0.79: Medium confidence (general patterns)
- 0.60-0.69: Low confidence (weak patterns)
- 0.00-0.59: Very low confidence (uncertain or not found)

#### Regex Patterns

**Client Name**:
```regex
client\s*:?\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})(?:\s|$|\n)
```
Matches: "Client: John Doe", "Client John Doe"

**Case Number**:
```regex
case\s*(?:#|no\.?|number)?\s*:?\s*([A-Z0-9]{2,4}-[A-Z0-9]{2,4}-[0-9]{3,6})
```
Matches: "Case #2024-PI-1234", "Case No. MM-2024-5678"

**Date**:
```regex
\b([A-Z][a-z]+\.?\s+\d{1,2},?\s+\d{4})\b
\b(\d{4}-\d{2}-\d{2})\b
\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b
```
Matches: "January 15, 2024", "2024-01-15", "01/15/2024"

**Medical Providers**:
```regex
Dr\.?\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)
([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:Hospital|Medical\s+Center|Clinic)
```
Matches: "Dr. Smith", "Memorial Hospital", "St. Mary's Medical Center"

#### Error Handling

- **Missing data**: Returns `{"value": None, "confidence": 0.0}`
- **Invalid dates**: Returns None if date cannot be parsed
- **Duplicate providers**: Automatically deduplicated
- **Malformed text**: Gracefully continues with best effort

#### Logging

All extraction activity is logged to `temp/orchestrator_logs.log`:

```
2024-10-25 23:30:15 - context_enricher - INFO - ======================================================================
2024-10-25 23:30:15 - context_enricher - INFO - CONTEXT ENRICHER: Starting metadata extraction
2024-10-25 23:30:15 - context_enricher - INFO - Text length: 10890 characters
2024-10-25 23:30:15 - context_enricher - INFO -   Client name found: Emily Watson (confidence: 0.95)
2024-10-25 23:30:15 - context_enricher - INFO -   Case number found: 2024-PI-8888 (confidence: 0.95)
2024-10-25 23:30:15 - context_enricher - INFO -   Case type found: premises liability (keyword: 'slip and fall', confidence: 0.95)
2024-10-25 23:30:15 - context_enricher - INFO -   Insurance company found: Allstate (confidence: 0.95)
2024-10-25 23:30:15 - context_enricher - INFO -   Incident date found: 2024-02-15 (confidence: 0.95)
2024-10-25 23:30:15 - context_enricher - INFO -   Medical provider found: Dr. Amanda Foster (confidence: 0.90)
2024-10-25 23:30:15 - context_enricher - INFO -   Medical provider found: Memorial Hospital (confidence: 0.90)
2024-10-25 23:30:15 - context_enricher - INFO - Extraction Summary:
2024-10-25 23:30:15 - context_enricher - INFO -   client_name: Emily Watson (confidence: 0.95)
2024-10-25 23:30:15 - context_enricher - INFO -   case_number: 2024-PI-8888 (confidence: 0.95)
2024-10-25 23:30:15 - context_enricher - INFO -   case_type: premises liability (confidence: 0.95)
2024-10-25 23:30:15 - context_enricher - INFO -   insurance_company: Allstate (confidence: 0.95)
2024-10-25 23:30:15 - context_enricher - INFO -   date_of_incident: 2024-02-15 (confidence: 0.95)
2024-10-25 23:30:15 - context_enricher - INFO -   medical_providers: 2 item(s) found
2024-10-25 23:30:15 - context_enricher - INFO - CONTEXT ENRICHER: Extraction complete
2024-10-25 23:30:15 - context_enricher - INFO - ======================================================================
```

#### Future Enhancements

Potential improvements:
1. **LLM-based extraction**: Use LLM for ambiguous cases
2. **Entity linking**: Link to external databases (e.g., insurance company IDs)
3. **Multi-language support**: Extract from non-English documents
4. **Custom patterns**: Allow user-defined extraction patterns
5. **Validation**: Cross-validate extracted data for consistency

---

**Last Updated**: October 25, 2024
