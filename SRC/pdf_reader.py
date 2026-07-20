import fitz
import os


def extract_pages(pdf_path, output_folder):

    pdf = fitz.open(pdf_path)

    pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]

    pdf_output = os.path.join(output_folder, pdf_name)

    os.makedirs(pdf_output, exist_ok=True)

    print(f"\nReading {pdf_name}")

    # Render at 300 DPI
    matrix = fitz.Matrix(300 / 72, 300 / 72)

    for page_number in range(len(pdf)):

        page = pdf.load_page(page_number)

        pix = page.get_pixmap(matrix=matrix)

        image_path = os.path.join(
            pdf_output,
            f"page_{page_number + 1}.png"
        )

        pix.save(image_path)

        print(f"Saved {image_path}")

    pdf.close()