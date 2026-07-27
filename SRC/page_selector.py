KEYWORDS = [
    "grant",
    "grantee",
    "grantor",
    "parcel",
    "lot",
    "tract",
    "book",
    "page",
    "recording",
    "county",
    "state",
    "easement",
    "survey",
    "subdivision",
    "legal"
]


def select_pages(ocr_pages):

    selected_pages = []

    for page in ocr_pages:

        text = page["text"].lower()

        score = 0

        for keyword in KEYWORDS:
            if keyword in text:
                score += 1

        if score >= 2:
            selected_pages.append(page)

    if not selected_pages:
        return ocr_pages

    return selected_pages