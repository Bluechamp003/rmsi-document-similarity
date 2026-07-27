import re


def preprocess_ocr(text: str) -> str:
    """
    Cleans OCR output before sending it to Gemini.
    """

    if not text:
        return ""

    # Remove multiple blank lines
    text = re.sub(r"\n\s*\n+", "\n", text)

    # Remove repeated spaces
    text = re.sub(r"[ \t]+", " ", text)

    # Remove very short noisy lines
    lines = []

    for line in text.split("\n"):

        line = line.strip()

        if len(line) < 3:
            continue

        lines.append(line)

    text = "\n".join(lines)

    # Limit maximum size sent to Gemini
    MAX_CHARS = 5000

    if len(text) > MAX_CHARS:
        text = text[:MAX_CHARS]

    return text