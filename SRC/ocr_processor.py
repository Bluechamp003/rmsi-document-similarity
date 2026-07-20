from PIL import Image
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r"C:\Users\Arnav.Goyal\ocr\tesseract.exe"

def extract_text_from_image(image_path):

    print("Opening image:", image_path)

    image = Image.open(image_path)

    print("Image size:", image.size)

    text = pytesseract.image_to_string(image)

    print("OCR completed")
    print("Characters extracted:", len(text))
    print(repr(text[:200]))

    return text
