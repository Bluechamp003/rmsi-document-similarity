import re


def classify_document(text):

    # Convert to uppercase for case-insensitive matching
    text = text.upper()

    map_score = 0
    text_score = 0

    # -------------------------
    # MAP INDICATORS
    # -------------------------

    map_keywords = [
        "LOT",
        "LOTS",
        "TRACT",
        "SEE PAGE",
        "MAP",
        "BOUNDARY",
        "NORTH",
        "SOUTH",
        "EAST",
        "WEST",
        "RANGE",
        "SECTION",
        "TOWNSHIP",
        "CURVE",
        "RADIUS",
        "BEARING"
    ]

    for word in map_keywords:
        if word in text:
            map_score += 3

    # Bearings like:
    # N 45° E
    # S 23°15' W
    bearing_pattern = r"[NS]\s*\d+.*?[EW]"
    map_score += len(re.findall(bearing_pattern, text))

    # -------------------------
    # TEXT DOCUMENT INDICATORS
    # -------------------------

    text_keywords = [
        "GRANTOR",
        "GRANTEE",
        "COUNTY",
        "STATE",
        "EASEMENT",
        "GRANT DEED",
        "QUITCLAIM",
        "RECITAL",
        "RECORDER",
        "NOTARY",
        "RECORDED",
        "WITNESS",
        "AGREEMENT"
    ]

    for word in text_keywords:
        if word in text:
            text_score += 3

    # -------------------------
    # TEXT LENGTH CHECK
    # -------------------------

    character_count = len(text.strip())

    if character_count < 300:
        map_score += 5
    else:
        text_score += 5

    # -------------------------
    # FINAL DECISION
    # -------------------------

    print("\n----- DOCUMENT CLASSIFIER -----")
    print(f"Map Score  : {map_score}")
    print(f"Text Score : {text_score}")

    if map_score > text_score:
        return "MAP_DOCUMENT"

    return "TEXT_DOCUMENT"