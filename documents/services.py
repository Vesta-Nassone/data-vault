import re
import fitz  # PyMuPDF


def extract_text_from_pdf(file_path: str) -> str:
    """Extract raw text from a PDF file."""
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text


def parse_fields_from_text(text: str) -> list[dict]:
    """
    Parse key fields from raw text using regex heuristics.
    Returns list of dicts: {key, original_value, data_type, confidence}

    Note: I used AI to generate regex patterns for common fields like customer name, account number, date, etc.
    """
    fields = []

    patterns = {
        "customer_name": {
            "patterns": [
                r"(?:Name|Customer Name|Full Name|Account Holder)[:\s]+([A-Z][a-zA-Z]+(?:\s[A-Z][a-zA-Z]+)+)",
            ],
            "data_type": "string",
        },
        "account_number": {
            "patterns": [
                r"(?:Account\s*(?:Number|No|#))[:\s]*(\d{6,12})",
            ],
            "data_type": "string",
        },
        "routing_number": {
            "patterns": [
                r"(?:Routing\s*(?:Number|No|#)|ABA)[:\s]*(\d{9})",
            ],
            "data_type": "string",
        },
        "amount": {
            "patterns": [
                r"(?:Amount|Total|Balance|Sum)[:\s]*\$?([\d,]+\.?\d{0,2})",
            ],
            "data_type": "number",
        },
        "date": {
            "patterns": [
                r"(?:Date|Effective Date|Signed Date)[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
                r"(?:Date|Effective Date|Signed Date)[:\s]*(\w+\s\d{1,2},?\s\d{4})",
            ],
            "data_type": "date",
        },
        "ssn": {
            "patterns": [
                r"(?:SSN|Social Security|TIN|Tax ID)[:\s]*(\d{3}-?\d{2}-?\d{4})",
            ],
            "data_type": "string",
        },
        "ein": {
            "patterns": [
                r"(?:EIN|Employer ID)[:\s]*(\d{2}-?\d{7})",
            ],
            "data_type": "string",
        },
        "address": {
            "patterns": [
                r"(?:Address|Street)[:\s]+(.+(?:Street|St|Avenue|Ave|Road|Rd|Blvd|Drive|Dr|Lane|Ln).+)",
            ],
            "data_type": "string",
        },
        "email": {
            "patterns": [
                r"(?:Email|E-mail)[:\s]*([\w.+-]+@[\w-]+\.[\w.-]+)",
            ],
            "data_type": "string",
        },
    }

    for key, config in patterns.items():
        for pattern in config["patterns"]:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                fields.append(
                    {
                        "key": key,
                        "original_value": match.group(1).strip(),
                        "data_type": config["data_type"],
                        "confidence": 0.70,
                    }
                )
                break  # take first match per key

    return fields
