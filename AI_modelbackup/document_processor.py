import os
from glob import glob

from ocr_processor import extract_text_from_image


def process_document(pdf_path):

    pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]

    image_folder = os.path.join("../extracted_pages", pdf_name)

    image_files = sorted(glob(os.path.join(image_folder, "*.png")))

    extracted_text = ""

    for image in image_files:

        extracted_text += extract_text_from_image(image)

        extracted_text += "\n"

    return {

        "filename": os.path.basename(pdf_path),

        "pages": len(image_files),

        "has_text": len(extracted_text.strip()) > 0,

        "text": extracted_text

    }