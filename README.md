# Property Document Duplicate Detection System
### RMSI AI Prototype

---

## Project Overview

This prototype automates the identification of duplicate or highly similar property documents before downstream processing.

Property documents received from clients often contain duplicates or multiple versions of the same document. Processing every document individually increases OCR cost, AI processing time, and manual verification effort.

This system extracts meaningful information from each document, generates a standardized property fingerprint, compares documents based on their extracted information, and groups similar documents together.

The final output is a set of document groups where each group represents documents that likely refer to the same property or legal record.

---

# Objectives

- Reduce duplicate document processing
- Minimize OCR and AI costs
- Speed up downstream workflows
- Automatically group similar property documents
- Produce structured information from unstructured legal documents

---

# Pipeline

```
                PDF Documents
                      │
                      ▼
          Page Extraction (PyMuPDF)
                      │
                      ▼
                  OCR Engine
               (Text Extraction)
                      │
                      ▼
            Document Classification
                      │
                      ▼
         Gemini Structured Extraction
                      │
                      ▼
          Property Fingerprint Generator
                      │
                      ▼
          Fingerprint Normalization
                      │
                      ▼
          Similarity Calculation
                      │
                      ▼
             Document Grouping
                      │
                      ▼
      JSON Results + Performance Report
```

---

# Project Structure

```
ai_model/

│
├── SRC/
│   ├── main.py
│   ├── config.py
│   ├── pdf_reader.py
│   ├── document_processor.py
│   ├── document_classifier.py
│   ├── gemini_extractor.py
│   ├── fingerprint_generator.py
│   ├── normalizer.py
│   ├── similarity_engine.py
│   ├── grouping_engine.py
│   ├── logger.py
│   └── performance_export.py
│
├── input_pdfs/
│
├── extracted_pages/
│
├── checkpoint.json
│
├── results.json
│
├── performance.csv
│
├── failed_documents.json
│
├── run.log
│
└── README.md
```

---

# Processing Workflow

For every PDF:

1. Extract pages as high-resolution images.
2. Perform OCR to extract document text.
3. Classify the document type.
4. Send OCR text and first-page image to Gemini.
5. Generate a structured property fingerprint.
6. Normalize extracted values.
7. Store fingerprint.
8. Compare fingerprints against every other document.
9. Group similar documents.
10. Save results and performance metrics.

---

# Fingerprint Information

Each document is converted into a structured fingerprint containing information such as:

- Document Type
- Recording Number
- Parcel Number
- Grantor
- Grantee
- County
- State
- Book
- Page
- Subdivision
- Tract
- Lot Numbers
- Road Names
- Bearings
- Distances
- Important Keywords

These fingerprints are used instead of raw OCR text for similarity comparison.

---

# Output Files

## results.json

Contains grouped documents after similarity comparison.

Example

```json
{
    "total_documents":23,
    "total_groups":7,
    "groups":[
        [
            "Doc123.pdf",
            "Doc125.pdf"
        ]
    ]
}
```

---

## performance.csv

Contains execution time for every document.

Example

|Document|Page Extraction|OCR|Gemini|Fingerprint|Total|
|---------|---------------|---|-------|-----------|------|
|Doc1.pdf|2.1|7.4|18.5|0.01|28.1|

---

## checkpoint.json

Stores processed documents.

Allows interrupted runs to resume without reprocessing completed PDFs.

---

## failed_documents.json

Stores documents that could not be processed successfully.

Example

```json
[
    {
        "document":"Doc321.pdf",
        "reason":"OCR failed"
    }
]
```

---

## run.log

Execution log containing processing information, errors, and progress.

---

# Performance Monitoring

The system records execution time for:

- Page Extraction
- OCR
- Gemini Extraction
- Fingerprint Generation
- Similarity Computation
- Document Grouping

Both cumulative and per-document timings are available.

---

# Current Limitations

- Gemini contributes the majority of processing time.
- Similarity thresholds are manually configured.
- Documents are processed sequentially.
- No graphical interface.
- OCR quality depends on scan quality.
- Extremely poor scans may reduce extraction accuracy.

---

# Possible Future Improvements

- Parallel document processing
- Local LLM extraction to reduce Gemini dependency
- Batch Gemini requests
- Incremental similarity indexing
- Web dashboard
- Confidence scoring for matches
- Automatic duplicate explanation
- Database integration
- API deployment
- GPU-accelerated OCR

---

# Technologies Used

- Python
- PyMuPDF
- Tesseract OCR
- Google Gemini
- JSON
- CSV
- Logging
- VS Code

---

# How to Run

1. Place PDFs inside:

```
input_pdfs/
```

2. Configure API key inside `.env`.

3. Run

```bash
python main.py
```

4. Outputs are generated automatically.

---

# Author

Prototype developed as part of an AI internship project at RMSI.

Designed to demonstrate an end-to-end pipeline for automated duplicate detection of scanned property documents.