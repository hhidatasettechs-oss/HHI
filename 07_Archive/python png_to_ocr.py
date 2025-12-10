from pathlib import Path
from PIL import Image
import pytesseract
import json

def png_to_ocr(input_folder, output_file="ocr_output.jsonl"):
    folder = Path(input_folder)
    pngs = sorted(folder.glob("*.png"))

    if not pngs:from pathlib import Path
from PIL import Image
import pytesseract
import json

def png_to_ocr(input_folder, output_file="ocr_output.jsonl"):
    folder = Path(input_folder)
    pngs = sorted(folder.glob("*.png"))

    if not pngs:
        print("No PNGs found.")
        return

    with open(output_file, "w", encoding="utf-8") as out:
        for img_path in pngs:
            print(f"OCR → {img_path.name}")

            text = pytesseract.image_to_string(Image.open(img_path)).strip()

            line = {
                "filename": img_path.name,
                "text": text
            }

            out.write(json.dumps(line, ensure_ascii=False) + "\n")

    print(f"\nDone. Output saved to {output_file}")

if __name__ == "__main__":
    png_to_ocr(r"C:\Users\amy\OneDrive\screenshots_input")
