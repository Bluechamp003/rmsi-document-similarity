import os
import json

from pdf_reader import extract_pages
from document_processor import process_document
from document_classifier import classify_document
from gemini_extractor import extract_information_with_gemini
from fingerprint_generator import generate_fingerprint
from similarity_engine import compare_documents
from grouping_engine import group_documents
from normalizer import normalize_fingerprint

INPUT_FOLDER = "../input_pdfs"
OUTPUT_FOLDER = "../extracted_pages"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

pdf_files = [
    f for f in os.listdir(INPUT_FOLDER)
    if f.lower().endswith(".pdf")
][:]

print(f"\nFound {len(pdf_files)} PDFs\n")
all_documents = []

for pdf in pdf_files:

    pdf_path = os.path.join(INPUT_FOLDER, pdf)

    # Step 1: Convert PDF pages to images
    extract_pages(pdf_path, OUTPUT_FOLDER)

    # Step 2: Extract OCR text
    info = process_document(pdf_path)

    # Step 3: Classify the document
    document_type = classify_document(info["text"])

    print("\n==============================")
    print(f"Document : {info['filename']}")
    print(f"Type     : {document_type}")
    print("==============================")

    # Step 4: Path to first page image
    image_path = os.path.join(
        OUTPUT_FOLDER,
        os.path.splitext(pdf)[0],
        "page_1.png"
    )

    # Step 5: Extract information using Gemini (text + image)
    structured_info = extract_information_with_gemini(
        document_text=info["text"],
        image_path=image_path
    )
    fingerprint = generate_fingerprint(structured_info)
    all_documents.append(
    {
        "filename": info["filename"],
        "fingerprint": fingerprint
    }
)
    print("\n----- PROPERTY FINGERPRINT -----")
    print(json.dumps(fingerprint, indent=4))

    # Step 6: Print the extracted information
    print(json.dumps(structured_info, indent=4))

   
   




...
# Compare every document
for i in range(len(all_documents)):

    for j in range(i + 1, len(all_documents)):

        print("\n==============================")
        print("DOCUMENT 1")
        print(all_documents[i]["filename"])
        print(json.dumps(all_documents[i]["fingerprint"], indent=4))

        print("\nDOCUMENT 2")
        print(all_documents[j]["filename"])
        print(json.dumps(all_documents[j]["fingerprint"], indent=4))

        score = compare_documents(
            all_documents[i]["fingerprint"],
            all_documents[j]["fingerprint"]
        )

        print(f"\nSimilarity = {score}%")
# -------------------------------
# STEP 3 GOES HERE
# -------------------------------

print("\n==============================")
print("DOCUMENT GROUPS")
print("==============================")

groups = group_documents(all_documents)

for i, group in enumerate(groups, start=1):

    print(f"\nGroup {i}")

    for document in group:
        print("  -", document)

# -------------------------------
# SAVE RESULTS
# -------------------------------

with open("../results.json", "w") as f:
    json.dump(groups, f, indent=4)

print("\nResults saved to results.json")

print("\nFinished!")