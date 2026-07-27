
print("TEST STARTED")

from ocr_processor import extract_text_from_image

print("IMPORT SUCCESSFUL")

text = extract_text_from_image(
    "../extracted_pages/Doc285260/page_1.png"
)

print("OCR RESULT:")
print(repr(text))

print("DONE")