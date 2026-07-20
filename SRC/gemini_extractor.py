import os
import json
from dotenv import load_dotenv
from google import genai
from PIL import Image

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

MAX_CHARACTERS = 5000


def extract_information_with_gemini(document_text=None, image_path=None):

    prompt = """
You are an expert land records analyst.

Analyze the provided document.

It may be

• Property deed
• Easement
• Survey Map
• Plat Map
• Parcel Map

Return ONLY valid JSON.

{
    "document_type": null,
    "parcel_number": null,
    "recording_number": null,
    "book": null,
    "page": null,
    "grantor": null,
    "grantee": null,
    "county": null,
    "state": null,
    "subdivision": null,
    "tract": null,
    "lot_numbers": [],
    "road_names": [],
    "bearings": [],
    "distances": [],
    "important_keywords": [],
    "summary": null
}
"""

    contents = [prompt]

    if document_text:
        contents.append(
            "OCR TEXT:\n" + document_text[:MAX_CHARACTERS]
        )

    if image_path:
        image = Image.open(image_path)
        contents.append(image)

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=contents
    )

    response_text = response.text.strip()

    response_text = response_text.replace("```json", "")
    response_text = response_text.replace("```", "")
    response_text = response_text.strip()

    try:
        return json.loads(response_text)

    except Exception:

        return {
            "error": "Gemini returned invalid JSON.",
            "raw_response": response_text
        }