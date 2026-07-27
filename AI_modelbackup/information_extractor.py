import os
import json
from dotenv import load_dotenv
from google import genai

# Load environment variables
load_dotenv()

# Configure Gemini
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MODEL_NAME = "gemini-2.5-flash"


def extract_information(ocr_text):

    prompt = f"""
You are an expert legal document analyzer.

Extract the following information from the OCR text.

Return ONLY valid JSON.

{{
    "document_type":"",
    "grantor":"",
    "grantee":"",
    "county":"",
    "state":"",
    "property_description":"",
    "easement_type":"",
    "lot_numbers":[],
    "bearings":[],
    "distances":[],
    "important_keywords":[]
}}

OCR TEXT:

{ocr_text}
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )

    result = response.text.strip()

    if result.startswith("```json"):
        result = result.replace("```json", "").replace("```", "").strip()
    elif result.startswith("```"):
        result = result.replace("```", "").strip()

    try:
        return json.loads(result)
    except Exception:
        return {
            "error": "Failed to parse JSON",
            "raw_response": result
        }


if __name__ == "__main__":
    sample_text = """
    SOUTHERN CALIFORNIA EDISON COMPANY

    County of Riverside

    State of California

    easement and right of way to construct, use, maintain, operate,
    overhead and underground electrical supply systems.
    """

    info = extract_information(sample_text)

    print(json.dumps(info, indent=4))