from difflib import SequenceMatcher


# ------------------------------------
# STRING SIMILARITY
# ------------------------------------
def similarity(a, b):

    # Missing data should not punish the score
    if a is None or b is None:
        return None

    return SequenceMatcher(
        None,
        str(a).lower(),
        str(b).lower()
    ).ratio()


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

    score = 0
    total = 0

    # FIELD WEIGHTS
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


    # NORMAL FIELDS
    for field, weight in weights.items():

        sim = similarity(
            fp1.get(field),
            fp2.get(field)
        )

        # Ignore missing fields
        if sim is None:
            continue

        total += weight

        if sim >= 0.90:
            score += weight

        elif sim >= 0.75:
            score += weight * 0.7

        elif sim >= 0.60:
            score += weight * 0.4


    # LIST COMPARISON FUNCTION
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


    # SUMMARY (low importance)
    summary_sim = similarity(
        fp1.get("summary"),
        fp2.get("summary")
    )

    if summary_sim is not None:
        total += 5
        score += summary_sim * 5


    # Recording number exact match bonus
    rec1 = fp1.get("recording_number")
    rec2 = fp2.get("recording_number")

    if rec1 and rec2:
        if str(rec1) == str(rec2):
            score += 20
            total += 20


    # Parcel number exact match bonus
    parcel1 = fp1.get("parcel_number")
    parcel2 = fp2.get("parcel_number")

    if parcel1 and parcel2:
        if str(parcel1) == str(parcel2):
            score += 15
            total += 15


    if total == 0:
        return 0


    similarity_percentage = round(
        (score / total) * 100,
        2
    )

    return similarity_percentage
