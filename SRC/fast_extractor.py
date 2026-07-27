import re


def fast_extract(text):

    result = {
        "document_type": None,
        "parcel_number": None,
        "recording_number": None,
        "book": None,
        "page": None,
        "grantor": None,
        "grantee": None,
        "county": None,
        "state": None,
        "subdivision": None,
        "tract": None,
        "lot_numbers": [],
        "road_names": [],
        "bearings": [],
        "distances": [],
        "important_keywords": [],
        "summary": None
    }

    text_upper = text.upper()

    # -----------------------------
    # Document Type
    # -----------------------------
    if "EASEMENT" in text_upper:
        result["document_type"] = "Easement"

    elif "DEED" in text_upper:
        result["document_type"] = "Deed"

    elif "SURVEY" in text_upper:
        result["document_type"] = "Survey"

    elif "PARCEL MAP" in text_upper:
        result["document_type"] = "Parcel Map"

    # -----------------------------
    # Parcel Number
    # -----------------------------
    parcel = re.search(
        r'PARCEL\s*(?:NO|NUMBER)?[:\s]*([0-9\-]+)',
        text_upper
    )

    if parcel:
        result["parcel_number"] = parcel.group(1)

    # -----------------------------
    # Recording Number
    # -----------------------------
    recording = re.search(
        r'(?:RECORDING|DOC|DOCUMENT)\s*(?:NO|NUMBER)?[:\s]*([0-9\-]+)',
        text_upper
    )

    if recording:
        result["recording_number"] = recording.group(1)

    # -----------------------------
    # Book and Page
    # -----------------------------
    book_page = re.search(
        r'BOOK\s*(\d+).*?PAGE\s*(\d+)',
        text_upper,
        re.DOTALL
    )

    if book_page:
        result["book"] = book_page.group(1)
        result["page"] = book_page.group(2)

    # -----------------------------
    # County
    # -----------------------------
    county = re.search(
        r'COUNTY\s+OF\s+([A-Z ]+)',
        text_upper
    )

    if not county:
        county = re.search(
            r'([A-Z]+)\s+COUNTY',
            text_upper
        )

    if county:
        value = county.group(1).strip().title()

        if value.upper() not in {
            "SITUATED IN THE",
            "SITUATED IRI THE",
            "COUNTY",
            ""
        }:
            result["county"] = value

    # -----------------------------
    # Keywords
    # -----------------------------
    keywords = [
        "easement",
        "survey",
        "parcel",
        "grant",
        "legal",
        "subdivision"
    ]

    for keyword in keywords:
        if keyword.upper() in text_upper:
            result["important_keywords"].append(keyword)

    return result


def extraction_confidence(data):

    important_fields = [
        "document_type",
        "parcel_number",
        "recording_number",
        "book",
        "page",
        "grantor",
        "grantee",
        "county",
        "state",
        "subdivision",
    ]

    score = sum(
        bool(data.get(field))
        for field in important_fields
    )

    return score / len(important_fields)