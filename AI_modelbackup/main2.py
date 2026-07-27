import os
import json

import time

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




timings = {
    "page_extraction": 0,
    "ocr": 0,
    "gemini": 0,
    "fingerprint": 0,
    "similarity": 0,
    "grouping": 0
}
document_timings = []
for pdf in pdf_files:
   

   

    pdf_path = os.path.join(INPUT_FOLDER, pdf)
    document_start = time.perf_counter()
    page_start = time.perf_counter()
    extract_pages(pdf_path, OUTPUT_FOLDER)
    page_time = time.perf_counter() - page_start
    timings["page_extraction"] += page_time
    ocr_start = time.perf_counter()
    info = process_document(pdf_path)
    ocr_time = time.perf_counter() - ocr_start
    timings["ocr"] += ocr_time


   
    document_type = classify_document(info["text"])

    print("\n==============================")
    print(f"Document : {info['filename']}")
    print(f"Type     : {document_type}")
    print("==============================")

    image_path = os.path.join(
        OUTPUT_FOLDER,
        os.path.splitext(pdf)[0],
        "page_1.png"
    )

    # -------------------------------
    # GEMINI EXTRACTION
    # -------------------------------
    gemini_start = time.perf_counter()

    structured_info = extract_information_with_gemini(
        document_text=info["text"],
        image_path=image_path
    )

    gemini_time = time.perf_counter() - gemini_start
    timings["gemini"] += gemini_time

    print(f"\n{info['filename']}")
    print(f"OCR Characters : {len(info['text'])}")
    print(f"Gemini Time    : {gemini_time:.2f} sec")

    # -------------------------------
    # FINGERPRINT GENERATION
    # -------------------------------
    fingerprint_start = time.perf_counter()

    fingerprint = generate_fingerprint(structured_info)

    fingerprint_time = time.perf_counter() - fingerprint_start
    timings["fingerprint"] += fingerprint_time

    all_documents.append(
        {
            "filename": info["filename"],
            "fingerprint": fingerprint
        }
    )

    # -------------------------------
    # SAVE CHECKPOINT
    # -------------------------------
    

   

    # -------------------------------
    # PRINT RESULTS
    # -------------------------------
    print("\n----- PROPERTY FINGERPRINT -----")
    print(json.dumps(fingerprint, indent=4))

    print(json.dumps(structured_info, indent=4))

    # -------------------------------
    
    # -------------------------------
    # -------------------------------
    # DOCUMENT PERFORMANCE
    # -------------------------------

    document_time = time.perf_counter() - document_start

    document_timings.append(
        {
            "document": info["filename"],
            "page_extraction": page_time,
            "ocr": ocr_time,
            "gemini": gemini_time,
            "fingerprint": fingerprint_time,
            "total": document_time
        }
    )

    print("\n========== DOCUMENT PERFORMANCE ==========")
    print(f"Document        : {info['filename']}")
    print(f"Page Extraction : {page_time:.2f} sec")
    print(f"OCR             : {ocr_time:.2f} sec")
    print(f"Gemini          : {gemini_time:.2f} sec")
    print(f"Fingerprint     : {fingerprint_time*1000:.2f} ms")
    print(f"TOTAL           : {document_time:.2f} sec")
    print("==========================================\n")
# Compare every document
start = time.perf_counter()
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
timings["similarity"] += time.perf_counter() - start
   

# -------------------------------
# STEP 3 GOES HERE
# -------------------------------

print("\n==============================")
print("DOCUMENT GROUPS")
print("==============================")
start = time.perf_counter()

groups = group_documents(all_documents)

for i, group in enumerate(groups, start=1):

    print(f"\nGroup {i}")

    for document in group:
        print("  -", document)
timings["grouping"] += time.perf_counter() - start

# -------------------------------
# SAVE RESULTS
# -------------------------------

with open("../results.json", "w") as f:
    json.dump(groups, f, indent=4)

print("\nResults saved to results.json")


print("\nFinished!")
print("\n========== PERFORMANCE ==========")

for stage, seconds in timings.items():
    print(f"{stage:20} {seconds:.2f} sec")
    print("\n============================================")
print("PER DOCUMENT PERFORMANCE SUMMARY")
print("============================================")

for d in document_timings:

    print(f"\nDocument        : {d['document']}")
    print(f"Page Extraction : {d['page_extraction']:.2f} sec")
    print(f"OCR             : {d['ocr']:.2f} sec")
    print(f"Gemini          : {d['gemini']:.2f} sec")
    print(f"Fingerprint     : {d['fingerprint']*1000:.2f} ms")
    print(f"TOTAL           : {d['total']:.2f} sec")