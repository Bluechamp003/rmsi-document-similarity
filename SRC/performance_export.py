import csv

def save_performance(document_timings):

    with open("../performance.csv", "w", newline="") as f:

        writer = csv.writer(f)

        writer.writerow([
            "Document",
            "Page Extraction",
            "OCR",
            "Gemini",
            "Fingerprint",
            "Total"
        ])

        for doc in document_timings:

            writer.writerow([
                doc["document"],
                round(doc["page_extraction"], 2),
                round(doc["ocr"], 2),
                round(doc["gemini"], 2),
                round(doc["fingerprint"], 4),
                round(doc["total"], 2)
            ])