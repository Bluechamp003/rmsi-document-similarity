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


def filter_pages(page_texts):

    useful_pages = []

    for page in page_texts:

        text = page["text"]

        score = 0

        lower = text.lower()

        for keyword in KEYWORDS:

            if keyword in lower:
                score += 1

        if score >= 2:
            useful_pages.append(text)


    if not useful_pages:
        return "\n".join(
            page["text"]
            for page in page_texts
        )


    return "\n".join(useful_pages)