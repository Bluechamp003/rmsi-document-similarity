import re


def clean_string(value):
    if value is None:
        return None

    value = str(value).lower().strip()

    value = value.replace(",", "")
    value = value.replace(".", "")
    value = value.replace(";", "")
    value = value.replace(":", "")

    value = re.sub(r"\s+", " ", value)

    return value


def normalize_list(values):

    if values is None:
        return []

    if isinstance(values, str):
        values = [values]

    cleaned = []

    for value in values:

        value = clean_string(value)

        if value:
            cleaned.append(value)

    return sorted(list(set(cleaned)))



def normalize_recording_number(value):

    if value is None:
        return None

    value = str(value)

    numbers = re.findall(r"\d+", value)

    if numbers:
        return numbers[0]

    return clean_string(value)
def normalize_company(name):

    if name is None:
        return None

    name = clean_string(name)

    words_to_remove = [
    "a corporation",
    "corporation",
    "inc",
    "llc",
    "company"
]

    for word in words_to_remove:
        name = name.replace(word, "")

    name = re.sub(r"\s+", " ", name).strip()

    return name
def normalize_person_or_company(name):

    if name is None:
        return None

    name = normalize_company(name)

    name = name.replace("a partnership", "")

    return name.strip()
def normalize_distance(distance):

    if distance is None:
        return None

    distance = clean_string(distance)

    match = re.search(r"(\d+(\.\d+)?)", distance)

    if match:
        return match.group(1)

    return distance
NUMBER_WORDS = {
    "one":"1",
    "two":"2",
    "three":"3",
    "four":"4",
    "five":"5",
    "six":"6",
    "seven":"7",
    "eight":"8",
    "nine":"9",
    "ten":"10"
}

def normalize_lot(value):

    if value is None:
        return None

    value = clean_string(value)

    for word, number in NUMBER_WORDS.items():
        value = value.replace(word, number)

    return value
def normalize_grantee(value):

    if value is None:
        return []

    if isinstance(value, list):
        companies = value

    else:
        companies = re.split(r"\band\b|;", str(value))

    result = []

    for company in companies:

        company = normalize_company(company)

        if company:
            result.append(company)

    return sorted(list(set(result)))
def normalize_fingerprint(fp):

    fp["document_type"] = clean_string(fp.get("document_type"))

    fp["county"] = clean_string(fp.get("county"))

    fp["state"] = clean_string(fp.get("state"))

    fp["book"] = clean_string(fp.get("book"))

    fp["page"] = clean_string(fp.get("page"))

    fp["parcel_number"] = clean_string(fp.get("parcel_number"))

    fp["recording_number"] = normalize_recording_number(
        fp.get("recording_number")
    )

    fp["grantor"] = normalize_person_or_company(
        fp.get("grantor")
    )

    fp["subdivision"] = clean_string(fp.get("subdivision"))

    fp["tract"] = clean_string(fp.get("tract"))

    fp["grantee"] = normalize_grantee(
        fp.get("grantee")
    )

    fp["lot_numbers"] = sorted(
        normalize_lot(x)
        for x in fp.get("lot_numbers", [])
    )

    fp["road_names"] = normalize_list(
        fp.get("road_names")
    )

    fp["bearings"] = normalize_list(
        fp.get("bearings")
    )

    fp["distances"] = sorted(
        normalize_distance(x)
        for x in fp.get("distances", [])
    )

    fp["important_keywords"] = normalize_list(
        fp.get("important_keywords")
    )

    return fp
