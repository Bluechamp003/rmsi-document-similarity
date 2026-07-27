
from difflib import SequenceMatcher    # Nfrom difflib import SequenceMatcher

INVALID_VALUES = {
    "",
    "unknown",
    "n/a",
    "none",
    "null",
    "situated in the",
    "situated iri the",
    "grant",
}


# ------------------------------------
# STRING SIMILARITY
# ------------------------------------
def similarity(a, b):

    if a is None or b is None:
        return None

    a = str(a).strip().lower()
    b = str(b).strip().lower()

    if a in INVALID_VALUES or b in INVALID_VALUES:
        return None

    # Normalize company names
    replacements = [
        " ltd.",
        " ltd",
        " company",
        " corporation",
        " corp.",
        " corp",
        " inc.",
        " inc",
    ]

    for word in replacements:
        a = a.replace(word, "")
        b = b.replace(word, "")

    a = " ".join(a.split())
    b = " ".join(b.split())

    return SequenceMatcher(None, a, b).ratio()


# ------------------------------------
# LIST SIMILARITY (Jaccard)
# ------------------------------------
def list_similarity(list1, list2):

    if not list1 or not list2:
        return None

    set1 = set(str(x).lower() for x in list1)
    set2 = set(str(x).lower() for x in list2)

    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))

    if union == 0:
        return None

    return intersection / union


# ------------------------------------
# COMPARE DOCUMENTS
# ------------------------------------
def compare_documents(fp1, fp2):

    # -----------------------------
    # CHECK FINGERPRINT QUALITY
    # -----------------------------
    important_fields = [
        "recording_number",
        "parcel_number",
        "grantor",
        "grantee",
        "subdivision",
        "summary",
    ]

    filled1 = sum(
        1 for field in important_fields
        if fp1.get(field) not in [None, "", []]
    )

    filled2 = sum(
        1 for field in important_fields
        if fp2.get(field) not in [None, "", []]
    )

    if filled1 < 2 or filled2 < 2:
        return 0

    score = 0
    total = 0
    reasons = []
    

    # -----------------------------
    # FIELD WEIGHTS
    # -----------------------------
    weights = {
        "recording_number": 35,
        "parcel_number": 25,
        "grantor": 15,
        "grantee": 15,
        "subdivision": 10,
        "county": 5,
        "state": 2,
        "tract": 5,
        "document_type": 3,
        "book": 2,
        "page": 2,
    }

        # -----------------------------
    # NORMAL FIELD COMPARISON
    # -----------------------------
    for field, weight in weights.items():

        sim = similarity(
            fp1.get(field),
            fp2.get(field)
        )

        if sim is None:
            continue

        total += weight

        if sim >= 0.90:
            score += weight
            reasons.append(f"✓ {field.replace('_',' ').title()} matched")

        elif sim >= 0.75:
            score += weight * 0.7
            reasons.append(f"≈ {field.replace('_',' ').title()} similar")

        elif sim >= 0.60:
            score += weight * 0.4
            reasons.append(f"~ {field.replace('_',' ').title()} partially matched")

        else:
            reasons.append(f"✗ {field.replace('_',' ').title()} different")

    # -----------------------------
    # BOOK COMPARISON
    # -----------------------------
    book1 = fp1.get("book")
    book2 = fp2.get("book")

    if book1 and book2:
        total += 8

        if str(book1).strip() == str(book2).strip():
            score += 8
            reasons.append("✓ Book matched")
        else:
            score -= 8
            reasons.append("✗ Book different")

    # -----------------------------
    # PAGE COMPARISON
    # -----------------------------
    page1 = fp1.get("page")
    page2 = fp2.get("page")

    if page1 and page2:
        total += 8

        if str(page1).strip() == str(page2).strip():
            score += 8
            reasons.append("✓ Page matched")
        else:
            score -= 8
            reasons.append("✗ Page different")

    # -----------------------------
    # LIST COMPARISON
    # -----------------------------
    list_fields = {
        "lot_numbers": 5,
        "road_names": 5,
        "bearings": 20,
        "distances": 20,
        "important_keywords": 5,
    }

    for field, weight in list_fields.items():

        sim = list_similarity(
            fp1.get(field, []),
            fp2.get(field, [])
        )

        if sim is None:
            continue

        total += weight
        score += sim * weight

        if sim >= 0.80:
            reasons.append(f"✓ {field.replace('_',' ').title()} similar ({round(sim*100)}%)")
        elif sim >= 0.50:
            reasons.append(f"≈ {field.replace('_',' ').title()} partially similar ({round(sim*100)}%)")

    # -----------------------------
    # LOT NUMBER BONUS
    # -----------------------------
    lots1 = set(str(x).lower() for x in fp1.get("lot_numbers", []))
    lots2 = set(str(x).lower() for x in fp2.get("lot_numbers", []))

    if lots1 and lots2:
        total += 15

        if lots1 == lots2:
            score += 15
            reasons.append("✓ Lot numbers matched")
        else:
            score -= 15
            reasons.append("✗ Lot numbers different")

    # -----------------------------
    # SUMMARY
    # -----------------------------
    summary_sim = similarity(
        fp1.get("summary"),
        fp2.get("summary")
    )

    if summary_sim is not None:
        total += 2
        score += summary_sim * 2

    # -----------------------------
    # RECORDING NUMBER BONUS
    # -----------------------------
    rec1 = fp1.get("recording_number")
    rec2 = fp2.get("recording_number")

    if rec1 and rec2:
        total += 20

        if str(rec1).lower() == str(rec2).lower():
            score += 20
            reasons.append(f"✓ Recording Number matched ({rec1})")
        else:
            score -= 20
            reasons.append(f"✗ Recording Number differs ({rec1} vs {rec2})")

    # -----------------------------
    # PARCEL NUMBER BONUS
    # -----------------------------
    parcel1 = fp1.get("parcel_number")
    parcel2 = fp2.get("parcel_number")

    if parcel1 and parcel2:
        total += 15

        if str(parcel1) == str(parcel2):
            score += 15
            reasons.append(f"✓ Parcel Number matched ({parcel1})")
        else:
            reasons.append(f"✗ Parcel Number differs ({parcel1} vs {parcel2})")

    # -----------------------------
    # FINAL SCORE
    # -----------------------------
    if total == 0:
        return 0, []

    similarity_percentage = round((score / total) * 100, 2)

    return similarity_percentage, reasons