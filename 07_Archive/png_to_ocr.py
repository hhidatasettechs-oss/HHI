import json
from pathlib import Path
from PIL import Image
import pytesseract

# ----- YOUR FOLDER PATH -----
INPUT_FOLDER = r"C:\Users\amy\OneDrive\screenshots_input"
OUTPUT_FILE = "ocr_output.jsonl"


def png_to_ocr(input_folder, output_file):
    folder = Path(input_folder)

    print(f"Checking folder: {folder}")

    if not folder.exists():
        print("❌ ERROR: Folder does NOT exist.")
        return

    pngs = sorted(folder.glob("*.png"))

    if not pngs:
        print("❌ ERROR: No PNG files found in this folder.")
        return

    print(f"Found {len(pngs)} PNG files.")

    with open(output_file, "w", encoding="utf-8") as out:
        for img_path in pngs:
            print(f"OCR → {img_path.name}")
            text = pytesseract.image_to_string(Image.open(img_path)).strip()

            entry = {
                "filename": img_path.name,
                "text": text
            }

            out.write(json.dumps(entry, ensure_ascii=False) + "\n")

    print(f"\n✅ DONE. OCR saved to {output_file}")


if __name__ == "__main__":
    png_to_ocr(INPUT_FOLDER, OUTPUT_FILE)
