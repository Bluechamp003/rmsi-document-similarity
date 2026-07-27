import fitz
import os


def extract_pages(pdf_path, output_folder):

    pdf = fitz.open(pdf_path)

    pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
    pdf_output = os.path.join(output_folder, pdf_name)

    os.makedirs(pdf_output, exist_ok=True)

    print(f"\nReading {pdf_name}")

    dpi_scale = 300 / 72

    for page_number in range(len(pdf)):

        page = pdf.load_page(page_number)
        print(f"Page size (points): {page.rect.width:.2f} x {page.rect.height:.2f}")
        print(f"Page size (inches): {page.rect.width/72:.2f} x {page.rect.height/72:.2f}")
      
        
        
        rect = page.rect

        width = rect.width * dpi_scale
        height = rect.height * dpi_scale

        MAX_DIMENSION = 6000

        scale = min(
            MAX_DIMENSION / width,
            MAX_DIMENSION / height,
            1
        )

        matrix = fitz.Matrix(
            dpi_scale * scale,
            dpi_scale * scale
        )

        pix = page.get_pixmap(matrix=matrix)

        image_path = os.path.join(
            pdf_output,
            f"page_{page_number + 1}.png"
        )

        pix.save(image_path)

        print(f"Saved {image_path}")

    pdf.close()
    