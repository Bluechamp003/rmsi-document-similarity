import json
import os
import time
start_time  = time.time()


from pdf_reader import extract_pages
from document_processor import process_document
from document_classifier import classify_document
from gemini_extractor import extract_information_with_gemini
from fingerprint_generator import generate_fingerprint
from similarity_engine import compare_documents
from grouping_engine import group_documents
from normalizer import normalize_fingerprint
from config import *
from logger import logger
from performance_export import save_performance
from preprocessor import preprocess_ocr
from page_selector import select_pages
from page_filter import filter_pages
from parallel_ocr import parallel_ocr



print("=" * 60)
print("PROPERTY DOCUMENT DUPLICATE DETECTION SYSTEM")
print("RMSI AI Prototype")
print("=" * 60)

os.makedirs(OUTPUT_FOLDER, exist_ok=True)


pdf_files = [
    f for f in os.listdir(INPUT_FOLDER)
    if f.lower().endswith(".pdf")
]
print("TOTAL PDFs =", len(pdf_files))

print(f"\nFound {len(pdf_files)} PDFs\n")

all_documents = []
processed_files = set()
failed_documents = []

if os.path.exists(CHECKPOINT_FILE):
    with open(CHECKPOINT_FILE, "r") as f:
        checkpoint = json.load(f)

    all_documents = checkpoint["documents"]
    processed_files = set(checkpoint["processed"])

    print("\nLoaded checkpoint.")
    print(f"Already processed {len(processed_files)} PDFs.\n")


# -------------------------------
# TIMING TRACKING
# -------------------------------
timings = {
    "page_extraction": 0,
    "ocr": 0,
    "gemini": 0,
    "fingerprint": 0,
    "similarity": 0,
    "grouping": 0,
}
total_pdfs = len(pdf_files)
print("PDF FILES:")
for pdf in pdf_files:
    print(pdf)

print("TOTAL PDFs:", len(pdf_files))
document_timings = []
print("\nTOTAL PDFs =", len(pdf_files))

for index, pdf in enumerate(pdf_files, start=1):
    print("\n====================================")
    print(f"Processing {index}/{total_pdfs}")
    print(f"Current File : {pdf}")
    print("====================================")

    logger.info("=" * 60)
    logger.info(f"Processing {index}/{total_pdfs}")
    logger.info(f"Current File : {pdf}")
    logger.info("=" * 60)
    # skip already processed files
    if pdf in processed_files:
        print(f"Skipping {pdf}")
        logger.info(f"Skipped {pdf}")
        continue

    # check cache by filename base
    filename_base = os.path.splitext(pdf)[0]
    cache_file = os.path.join(CACHE_DIR, filename_base + ".json")
    if os.path.exists(cache_file):
        print(f"✓ Using cached fingerprint for {filename_base}")
        with open(cache_file, "r") as f:
            fingerprint = json.load(f)
        all_documents.append({
            "filename": pdf,
            "fingerprint": fingerprint,
        })
        continue
    

    try:
        pdf_path = os.path.join(INPUT_FOLDER, pdf)
        document_start = time.perf_counter()

        # -------------------------------
        # PAGE EXTRACTION
        # -------------------------------
        page_start = time.perf_counter()

        extract_pages(pdf_path, OUTPUT_FOLDER)
        page_folder = os.path.join(
            OUTPUT_FOLDER,
            os.path.splitext(pdf)[0],
        )

        page_images = [
            os.path.join(page_folder, f)
            for f in os.listdir(page_folder)
            if f.endswith(".png")
        ]
        page_time = time.perf_counter() - page_start
        timings["page_extraction"] += page_time
        ocr_start = time.perf_counter()
        ocr_result = parallel_ocr(page_images, workers=4)

        important_pages = select_pages(ocr_result["pages"])

        print("All pages:", len(page_images))
        print("Important pages:", len(important_pages))

        info = {
            "filename": pdf,
            "text": ocr_result["text"],
            "pages": ocr_result["pages"],
            "page_count": len(page_images),
        }

        ocr_time = time.perf_counter() - ocr_start
        timings["ocr"] += ocr_time

        # -------------------------------
        # CLASSIFICATION
        # -------------------------------
        document_type = classify_document(info["text"])

        print("\n==============================")
        print(f"Document : {info['filename']}")
        print(f"Type     : {document_type}")
        print("==============================")

        # -------------------------------
        # GEMINI
        # -------------------------------
        image_path = os.path.join(
            OUTPUT_FOLDER,
            os.path.splitext(pdf)[0],
            "page_1.png",
        )

        clean_text = preprocess_ocr(info["text"])

        print("\n========== OCR PREPROCESSING ==========")
        print(f"Original OCR : {len(info['text'])} characters")
        print(f"Cleaned OCR  : {len(clean_text)} characters")
        print(f"Reduction    : {len(info['text']) - len(clean_text)} characters")
        print("=======================================\n")
        
        filtered_text = "\n".join(
                page["text"]
                for page in important_pages
            )
        print("\n========== PAGE FILTER ==========")
        print(f"Pages Found   : {info['page_count']}")
        print(f"Original OCR  : {len(info['text'])} chars")
        print(f"Filtered OCR  : {len(filtered_text)} chars")
        print("=================================\n")

        gemini_start = time.perf_counter()

        from fast_extractor import fast_extract, extraction_confidence

        fast_info = fast_extract(filtered_text)
        confidence = extraction_confidence(fast_info)

        print("\n========== FAST EXTRACTION ==========")
        print("Confidence:", confidence)
        print(fast_info)
        print("====================================")

        if confidence >= 0.8:
            print("Using FAST extraction. Gemini skipped.")
            structured_info = fast_info
        else:
            print("Low confidence. Sending to Gemini.")
            structured_info = extract_information_with_gemini(
                document_text=filtered_text,
                image_path=None,
            )

        gemini_time = time.perf_counter() - gemini_start
        timings["gemini"] += gemini_time

        print(f"\nOCR Characters : {len(info['text'])}")
        print(f"Gemini Time    : {gemini_time:.2f} sec")

        # -------------------------------
        # FINGERPRINT
        # -------------------------------
        fingerprint_start = time.perf_counter()
        fingerprint = generate_fingerprint(structured_info)
        
        fingerprint_time = time.perf_counter() - fingerprint_start
        timings["fingerprint"] += fingerprint_time

        # -------------------------------
        # STORE
        # -------------------------------
        all_documents.append(
            {
                "filename": info["filename"],
                "fingerprint": fingerprint,
            }
        )

        # -------------------------------
        # SAVE CHECKPOINT
        # -------------------------------
        processed_files.add(pdf)

        with open(CHECKPOINT_FILE, "w") as f:
            json.dump(
                {
                    "processed": list(processed_files),
                    "documents": all_documents,
                },
                f,
                indent=4,
            )

        # -------------------------------
        # PRINT RESULTS
        # -------------------------------
        print("\n----- PROPERTY FINGERPRINT -----")
        print(json.dumps(fingerprint, indent=4))

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
                "total": document_time,
            }
        )

        print("\n========== DOCUMENT PERFORMANCE ==========")
        print(f"Document        : {info['filename']}")
        print(f"Page Extraction : {page_time:.2f} sec")
        print(f"OCR             : {ocr_time:.2f} sec")
        print(f"Gemini          : {gemini_time:.2f} sec")
        print(f"Fingerprint     : {fingerprint_time * 1000:.2f} ms")
        print(f"TOTAL           : {document_time:.2f} sec")
        print("==========================================")

        logger.info(f"Successfully processed {info['filename']}")
        logger.info(f"Total Time : {document_time:.2f} sec")

    except Exception as e:
        print(f"\nError processing {pdf}")
        print(e)

        logger.error(f"Failed : {pdf}")
        logger.error(str(e))

        failed_documents.append(
            {
                "document": pdf,
                "reason": str(e),
            }
        )

        continue

# -------------------------------
# DOCUMENT COMPARISON
# -------------------------------
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

        score, reasons = compare_documents(
            all_documents[i]["fingerprint"],
            all_documents[j]["fingerprint"],
        )

        print(f"\nSimilarity = {score}%")
        print("Reasons:")
        for reason in reasons:
            print(f"  - {reason}")

timings["similarity"] += time.perf_counter() - start
print("\n========== ALL DOCUMENTS ==========")

for i, doc in enumerate(all_documents):
    print(i, doc["filename"])

print("===================================")

# -------------------------------=
# DOCUMENT GROUPING
# -------------------------------
print("\n==============================")
print("DOCUMENT GROUPS")
print("==============================")
start = time.perf_counter()


print("\n========== ALL DOCUMENTS ==========")
print("Total documents:", len(all_documents))

for i, doc in enumerate(all_documents):
    print(i, doc["filename"])

print("===================================")
groups = group_documents(all_documents)

for i, group in enumerate(groups, start=1):
    print(f"\nGroup {i}")
    for document in group:
        print("  -", document)

timings["grouping"] += time.perf_counter() - start

# -------------------------------
# SAVE RESULTS
# -------------------------------
summary = {
    "total_documents": len(all_documents),
    "total_groups": len(groups),
    "total_comparisons": len(all_documents) * (len(all_documents) - 1) // 2,
    "groups": groups,
}

with open(RESULTS_FILE, "w") as f:
    json.dump(summary, f, indent=4)

print("\nResults saved to results.json")
with open("../failed_documents.json", "w") as f:
    json.dump(failed_documents, f, indent=4)

print("\n========== FINAL REPORT ==========")
print(f"Documents Processed : {len(all_documents)}")
print(f"Failed Documents    : {len(failed_documents)}")
print(f"Groups Created      : {len(groups)}")
print("==================================")
save_performance(document_timings)

print("\nFinished!")
logger.info("=" * 60)
logger.info("Pipeline Finished Successfully")
logger.info(f"Documents Processed : {len(all_documents)}")
logger.info(f"Failed Documents    : {len(failed_documents)}")
logger.info(f"Groups Created      : {len(groups)}")
logger.info("=" * 60)

print("\n========== PERFORMANCE ==========")
if document_timings:
    avg_page = sum(d["page_extraction"] for d in document_timings) / len(document_timings)
    avg_ocr = sum(d["ocr"] for d in document_timings) / len(document_timings)
    avg_gemini = sum(d["gemini"] for d in document_timings) / len(document_timings)
    avg_total = sum(d["total"] for d in document_timings) / len(document_timings)

    print("\n========== AVERAGE ==========")
    print(f"Page Extraction : {avg_page:.2f} sec")
    print(f"OCR             : {avg_ocr:.2f} sec")
    print(f"Gemini          : {avg_gemini:.2f} sec")
    print(f"Total           : {avg_total:.2f} sec")

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
    print(f"Fingerprint     : {d['fingerprint'] * 1000:.2f} ms")
    print(f"TOTAL           : {d['total']:.2f} sec")

print("\n========== SUMMARY ==========")
print(f"Documents Processed : {len(all_documents)}")
print(f"Groups Created      : {len(groups)}")
print(f"Comparisons Made    : {len(all_documents) * (len(all_documents) - 1) // 2}")
print("=============================")

end_time = time.time()
total_time = end_time - start_time
print(f"\nTotal Execution Time: {total_time:.2f} seconds")

