
import pytesseract
from PIL import Image

# Set the Tesseract executable path
pytesseract.pytesseract.tesseract_cmd = r"C:\Users\anuma\AppData\Local\Tesseract-OCR\tesseract.exe"

# Open an image
img = Image.open("sample.png")

# Extract text from the image
text = pytesseract.image_to_string(img)

print("Extracted Text:")
print(text)