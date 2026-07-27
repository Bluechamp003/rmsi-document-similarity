import pytesseract
from concurrent.futures import ThreadPoolExecutor
from PIL import Image


def ocr_single_page(image_path):

    try:
        image = Image.open(image_path)

        text = pytesseract.image_to_string(
            image,
            config="--psm 6"
        )

        return {
            "image": image_path,
            "text": text
        }

    except Exception as e:

        return {
            "image": image_path,
            "text": "",
            "error": str(e)
        }



def parallel_ocr(image_paths, workers=4):

    with ThreadPoolExecutor(
        max_workers=workers
    ) as executor:

        results = list(
            executor.map(
                ocr_single_page,
                image_paths
            )
        )


    combined_text = "\n".join(
        page["text"]
        for page in results
    )


    return {
        "pages": results,
        "text": combined_text
    }