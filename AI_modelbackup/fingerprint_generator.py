def generate_fingerprint(structured_info):

    def clean_sorted_list(values):
        if not values:
            return []

        return sorted(str(v).strip() for v in values if v is not None)

    fingerprint = {

        "document_type": structured_info.get("document_type"),

        "county": structured_info.get("county"),

        "state": structured_info.get("state"),

        "book": structured_info.get("book"),

        "page": structured_info.get("page"),

        "parcel_number": structured_info.get("parcel_number"),

        "recording_number": structured_info.get("recording_number"),

        "grantor": structured_info.get("grantor"),

        "grantee": structured_info.get("grantee"),

        "subdivision": structured_info.get("subdivision"),

        "tract": structured_info.get("tract"),

        "lot_numbers": clean_sorted_list(
            structured_info.get("lot_numbers", [])
        ),

        "road_names": clean_sorted_list(
            structured_info.get("road_names", [])
        ),

        "bearings": clean_sorted_list(
            structured_info.get("bearings", [])
        ),

        "distances": clean_sorted_list(
            structured_info.get("distances", [])
        ),

        "important_keywords": clean_sorted_list(
            structured_info.get("important_keywords", [])
        ),

        "summary": structured_info.get("summary")

    }

    return fingerprint