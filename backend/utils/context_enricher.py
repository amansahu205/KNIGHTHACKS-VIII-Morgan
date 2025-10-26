"""
Context Enricher Utility
Extracts structured metadata from legal case text using regex and heuristics
"""

import re
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)


def extract_case_context(text: str) -> Dict[str, Any]:
    """
    Extract structured metadata from legal case text.
    
    Args:
        text: Raw case file text
        
    Returns:
        dict: Structured metadata with confidence scores
        
    Example:
        {
            "client_name": {"value": "Emily Watson", "confidence": 0.95},
            "case_number": {"value": "2024-PI-8888", "confidence": 0.88},
            "case_type": {"value": "premises liability", "confidence": 0.9},
            "insurance_company": {"value": "State Farm", "confidence": 0.85},
            "date_of_incident": {"value": "2024-02-15", "confidence": 0.92},
            "medical_providers": [
                {"value": "St. Mary's Hospital", "confidence": 0.93},
                {"value": "Dr. Patricia Williams", "confidence": 0.90}
            ]
        }
    """
    logger.info("=" * 70)
    logger.info("CONTEXT ENRICHER: Starting metadata extraction")
    logger.info(f"Text length: {len(text)} characters")
    
    context = {}
    
    # Extract each field
    context["client_name"] = _extract_client_name(text)
    context["case_number"] = _extract_case_number(text)
    context["case_type"] = _extract_case_type(text)
    context["insurance_company"] = _extract_insurance_company(text)
    context["date_of_incident"] = _extract_incident_date(text)
    context["medical_providers"] = _extract_medical_providers(text)
    
    # Log extraction summary
    _log_extraction_summary(context)
    
    logger.info("CONTEXT ENRICHER: Extraction complete")
    logger.info("=" * 70)
    
    return context


def _extract_client_name(text: str) -> Dict[str, Any]:
    """
    Extract client name from text.
    
    Patterns:
    - "Client: John Doe"
    - "Plaintiff: Jane Smith"
    - "Claimant: Robert Johnson"
    """
    patterns = [
        # "Client: Name" (capture 2-4 words max, stop at newline or punctuation)
        (r'client\s*:?\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})(?:\s|$|\n)', 0.95),
        # "Plaintiff: Name"
        (r'plaintiff\s*:?\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})(?:\s|$|\n)', 0.90),
        # "Claimant: Name"
        (r'claimant\s*:?\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})(?:\s|$|\n)', 0.85),
        # "Patient: Name" (medical cases)
        (r'patient\s*:?\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})(?:\s|$|\n)', 0.80),
    ]
    
    for pattern, confidence in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            name = match.group(1).strip()
            logger.info(f"  Client name found: {name} (confidence: {confidence})")
            return {"value": name, "confidence": confidence}
    
    logger.warning("  Client name not found")
    return {"value": None, "confidence": 0.0}


def _extract_case_number(text: str) -> Dict[str, Any]:
    """
    Extract case number from text.
    
    Patterns:
    - "Case #2024-PI-1234"
    - "Case No. MM-2024-5678"
    - "File #: 2024-1234"
    - "Docket No: CV-2024-001"
    """
    patterns = [
        # "Case #2024-XX-1234" or "Case No. 2024-XX-1234"
        (r'case\s*(?:#|no\.?|number)?\s*:?\s*([A-Z0-9]{2,4}-[A-Z0-9]{2,4}-[0-9]{3,6})', 0.95),
        # "MM-2024-1234" or similar standalone
        (r'\b([A-Z]{2}-\d{4}-\d{3,6})\b', 0.90),
        # "Case #1234" simple format
        (r'case\s*(?:#|no\.?|number)?\s*:?\s*(\d{4,6})', 0.80),
        # "File #: 2024-1234"
        (r'file\s*(?:#|no\.?|number)?\s*:?\s*([A-Z0-9-]{4,})', 0.85),
        # "Docket No: CV-2024-001"
        (r'docket\s*(?:#|no\.?|number)?\s*:?\s*([A-Z0-9-]{4,})', 0.85),
    ]
    
    for pattern, confidence in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            case_num = match.group(1).strip()
            logger.info(f"  Case number found: {case_num} (confidence: {confidence})")
            return {"value": case_num, "confidence": confidence}
    
    logger.warning("  Case number not found")
    return {"value": None, "confidence": 0.0}


def _extract_case_type(text: str) -> Dict[str, Any]:
    """
    Infer case type from keywords.
    
    Categories:
    - Personal Injury (auto accident, motor vehicle, car crash)
    - Premises Liability (slip and fall, trip and fall)
    - Medical Malpractice (medical negligence, surgical error)
    - Employment (wrongful termination, discrimination, harassment)
    - Insurance Dispute (claim denial, bad faith)
    - Contract Dispute (breach of contract)
    """
    text_lower = text.lower()
    
    case_types = [
        # Personal Injury - Auto
        (["auto accident", "motor vehicle accident", "car accident", "car crash", 
          "vehicle collision", "traffic accident"], "personal injury - motor vehicle", 0.95),
        
        # Personal Injury - Premises Liability
        (["slip and fall", "trip and fall", "premises liability", "dangerous condition",
          "hazardous condition", "wet floor"], "premises liability", 0.95),
        
        # Medical Malpractice
        (["medical malpractice", "medical negligence", "surgical error", "misdiagnosis",
          "wrong medication", "hospital negligence"], "medical malpractice", 0.95),
        
        # Employment
        (["wrongful termination", "employment discrimination", "workplace harassment",
          "retaliation", "hostile work environment", "wage dispute"], "employment law", 0.90),
        
        # Insurance Dispute
        (["insurance dispute", "claim denial", "bad faith insurance", "coverage dispute",
          "insurance claim"], "insurance dispute", 0.90),
        
        # Contract Dispute
        (["breach of contract", "contract dispute", "agreement violation",
          "contractual obligation"], "contract dispute", 0.85),
        
        # General Personal Injury
        (["personal injury", "bodily injury", "negligence", "liability"],
         "personal injury", 0.75),
    ]
    
    # Check each category
    for keywords, case_type, confidence in case_types:
        for keyword in keywords:
            if keyword in text_lower:
                logger.info(f"  Case type found: {case_type} (keyword: '{keyword}', confidence: {confidence})")
                return {"value": case_type, "confidence": confidence}
    
    logger.warning("  Case type not found")
    return {"value": None, "confidence": 0.0}


def _extract_insurance_company(text: str) -> Dict[str, Any]:
    """
    Extract insurance company name.
    
    Patterns:
    - Words ending with: Insurance, Assurance, Claims, Mutual
    - Common insurers: State Farm, Allstate, Geico, Progressive, etc.
    """
    # Common insurance company names
    known_insurers = [
        "state farm", "allstate", "geico", "progressive", "farmers",
        "nationwide", "liberty mutual", "usaa", "travelers", "american family",
        "aig", "metlife", "prudential", "aetna", "cigna", "united healthcare",
        "blue cross", "anthem"
    ]
    
    text_lower = text.lower()
    
    # Check for known insurers first (higher confidence)
    for insurer in known_insurers:
        if insurer in text_lower:
            # Get the actual cased version from text
            pattern = re.compile(re.escape(insurer), re.IGNORECASE)
            match = pattern.search(text)
            if match:
                name = match.group(0)
                logger.info(f"  Insurance company found: {name} (confidence: 0.95)")
                return {"value": name, "confidence": 0.95}
    
    # Pattern-based detection (lower confidence)
    patterns = [
        # "Company Name Insurance"
        (r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+Insurance', 0.85),
        # "Company Name Assurance"
        (r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+Assurance', 0.85),
        # "Company Name Mutual"
        (r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+Mutual', 0.80),
        # "Insurance Company: Name"
        (r'insurance\s+company\s*:?\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', 0.80),
        # "Carrier: Name"
        (r'carrier\s*:?\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', 0.75),
    ]
    
    for pattern, confidence in patterns:
        match = re.search(pattern, text)
        if match:
            name = match.group(1).strip()
            # Add "Insurance" if not present
            if "insurance" not in name.lower():
                name = f"{name} Insurance"
            logger.info(f"  Insurance company found: {name} (confidence: {confidence})")
            return {"value": name, "confidence": confidence}
    
    logger.warning("  Insurance company not found")
    return {"value": None, "confidence": 0.0}


def _extract_incident_date(text: str) -> Dict[str, Any]:
    """
    Extract date of incident.
    
    Patterns:
    - "Date of Incident: 2024-01-15"
    - "Incident Date: January 15, 2024"
    - "Date of Accident: 01/15/2024"
    - First valid date in text
    """
    # Look for explicit incident date labels first
    label_patterns = [
        r'(?:date\s+of\s+)?(?:incident|accident|injury|occurrence)\s*:?\s*([A-Za-z]+\s+\d{1,2},?\s+\d{4})',
        r'(?:date\s+of\s+)?(?:incident|accident|injury|occurrence)\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
        r'(?:date\s+of\s+)?(?:incident|accident|injury|occurrence)\s*:?\s*(\d{4}-\d{2}-\d{2})',
    ]
    
    for pattern in label_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            date_str = match.group(1).strip()
            normalized_date = _normalize_date(date_str)
            if normalized_date:
                logger.info(f"  Incident date found: {normalized_date} (confidence: 0.95)")
                return {"value": normalized_date, "confidence": 0.95}
    
    # Look for any date in the text (lower confidence)
    date_patterns = [
        # "January 15, 2024" or "Jan 15, 2024"
        r'\b([A-Z][a-z]+\.?\s+\d{1,2},?\s+\d{4})\b',
        # "2024-01-15"
        r'\b(\d{4}-\d{2}-\d{2})\b',
        # "01/15/2024" or "1/15/24"
        r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b',
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, text)
        if match:
            date_str = match.group(1).strip()
            normalized_date = _normalize_date(date_str)
            if normalized_date:
                logger.info(f"  Date found: {normalized_date} (confidence: 0.70)")
                return {"value": normalized_date, "confidence": 0.70}
    
    logger.warning("  Incident date not found")
    return {"value": None, "confidence": 0.0}


def _extract_medical_providers(text: str) -> List[Dict[str, Any]]:
    """
    Extract medical provider names (hospitals, doctors).
    
    Patterns:
    - "Dr. Smith", "Doctor Johnson"
    - "St. Mary's Hospital", "County General Hospital"
    - "Memorial Medical Center"
    """
    providers = []
    seen = set()  # Avoid duplicates
    
    # Doctor patterns
    doctor_patterns = [
        # "Dr. FirstName LastName" or "Dr. LastName"
        (r'Dr\.?\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)', 0.90),
        # "Doctor FirstName LastName"
        (r'Doctor\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)', 0.85),
        # "Physician: Dr. Name"
        (r'physician\s*:?\s*Dr\.?\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)', 0.90),
    ]
    
    for pattern, confidence in doctor_patterns:
        for match in re.finditer(pattern, text):
            name = f"Dr. {match.group(1).strip()}"
            if name.lower() not in seen:
                seen.add(name.lower())
                providers.append({"value": name, "confidence": confidence})
                logger.info(f"  Medical provider found: {name} (confidence: {confidence})")
    
    # Hospital patterns
    hospital_patterns = [
        # "Name Hospital" or "Name Medical Center"
        (r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:Hospital|Medical\s+Center|Clinic|Healthcare)', 0.90),
        # "St. Mary's Hospital" or "Mt. Sinai"
        (r'(?:St\.|Mt\.|Saint)\s+([A-Z][a-z]+(?:\'s)?)\s+(?:Hospital|Medical\s+Center|Clinic)', 0.95),
        # "County General Hospital"
        (r'([A-Z][a-z]+\s+General)\s+Hospital', 0.90),
        # "Memorial Hospital"
        (r'(Memorial)\s+(?:Hospital|Medical\s+Center)', 0.85),
    ]
    
    for pattern, confidence in hospital_patterns:
        for match in re.finditer(pattern, text):
            # Reconstruct full name
            if "st." in match.group(0).lower() or "mt." in match.group(0).lower():
                name = match.group(0).strip()
            else:
                name = f"{match.group(1).strip()} Hospital"
            
            if name.lower() not in seen:
                seen.add(name.lower())
                providers.append({"value": name, "confidence": confidence})
                logger.info(f"  Medical provider found: {name} (confidence: {confidence})")
    
    if not providers:
        logger.warning("  No medical providers found")
    
    return providers


def _normalize_date(date_str: str) -> Optional[str]:
    """
    Normalize date string to ISO format (YYYY-MM-DD).
    
    Args:
        date_str: Date string in various formats
        
    Returns:
        str: ISO formatted date or None if parsing fails
    """
    # Try different date formats
    formats = [
        "%Y-%m-%d",           # 2024-01-15
        "%m/%d/%Y",           # 01/15/2024
        "%m-%d-%Y",           # 01-15-2024
        "%m/%d/%y",           # 01/15/24
        "%B %d, %Y",          # January 15, 2024
        "%b %d, %Y",          # Jan 15, 2024
        "%B %d %Y",           # January 15 2024
        "%b %d %Y",           # Jan 15 2024
    ]
    
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str.strip(), fmt)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            continue
    
    return None


def _log_extraction_summary(context: Dict[str, Any]) -> None:
    """
    Log summary of extracted metadata.
    
    Args:
        context: Extracted context dictionary
    """
    logger.info("Extraction Summary:")
    
    for key, value in context.items():
        if isinstance(value, list):
            if value:
                logger.info(f"  {key}: {len(value)} item(s) found")
                for item in value:
                    logger.info(f"    - {item['value']} (confidence: {item['confidence']})")
            else:
                logger.info(f"  {key}: None")
        else:
            if value.get("value"):
                logger.info(f"  {key}: {value['value']} (confidence: {value['confidence']})")
            else:
                logger.info(f"  {key}: None")


# Utility function for testing
def extract_and_display(text: str) -> None:
    """
    Extract context and display results (for testing).
    
    Args:
        text: Case file text
    """
    context = extract_case_context(text)
    
    print("\n" + "=" * 70)
    print("EXTRACTED CONTEXT")
    print("=" * 70)
    
    for key, value in context.items():
        if isinstance(value, list):
            print(f"\n{key.upper()}:")
            if value:
                for item in value:
                    print(f"  - {item['value']} (confidence: {item['confidence']:.2f})")
            else:
                print("  None")
        else:
            print(f"\n{key.upper()}:")
            if value.get("value"):
                print(f"  Value: {value['value']}")
                print(f"  Confidence: {value['confidence']:.2f}")
            else:
                print("  None")
    
    print("\n" + "=" * 70)
