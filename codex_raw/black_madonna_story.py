from typing import List, Tuple
import os
import textwrap
from datetime import datetime

class MinimalPDFv2:
    PAGE_SIZE = (612, 792)

    def __init__(self, title: str = "", author: str = ""):
        print(f"Initializing MinimalPDFv2 with title='{title}', author='{author}'")
        self.title = title
        self.author = author
        self.objs: List[bytes] = []
        self.offsets: List[int] = []
        self.buffer = bytearray()
        self.page_contents: List[int] = []
        self.page_objs: List[int] = []
        self.font_obj: int = 0
        self.pages_obj: int = 0
        self.catalog_obj: int = 0
        self.info_obj: int = 0

    @staticmethod
    def _esc(s: str) -> str:
        return s.replace("\\", "\\\\").replace("(", r"\\(").replace(")", r"\\)")

    def _begin(self):
        print("Starting new PDF buffer")
        self.buffer = bytearray(b"%PDF-1.4\n%\xE2\xE3\xCF\xD3\n")
        self.offsets = []

    def _add(self, raw: bytes) -> int:
        obj_num = len(self.offsets) + 1
        print(f"Adding object {obj_num}, size={len(raw)} bytes")
        self.offsets.append(len(self.buffer))
        self.buffer += f"{obj_num} 0 obj\n".encode("latin-1")
        self.buffer += raw
        self.buffer += b"\nendobj\n"
        return obj_num

    def _add_stream(self, payload: bytes, extra_dict: str = "") -> int:
        print(f"Adding stream of length {len(payload)}")
        d = f"<< /Length {len(payload)} {extra_dict}>>\nstream\n".encode("latin-1")
        d += payload + b"\nendstream"
        return self._add(d)

    def add_page_text(self, text_lines: List[str], font_size: int = 12, leading: int = 16,
                       margins: Tuple[int, int, int, int] = (54, 54, 54, 54)):
        print(f"Adding page text: {len(text_lines)} lines")
        w, h = self.PAGE_SIZE
        left, right, top, bottom = margins
        usable_w = w - left - right
        avg_char_w = font_size * 0.5
        max_chars = max(10, int(usable_w / avg_char_w))

        wrapped: List[str] = []
        for line in text_lines:
            if not line:
                wrapped.append("")
            else:
                wrapped.extend(textwrap.wrap(line, width=max_chars))
        print(f"Wrapped into {len(wrapped)} lines for PDF page")

        y = h - top
        parts: List[str] = ["BT", f"/F1 {font_size} Tf", f"{left} {y} Td"]
        for seg in wrapped:
            y -= leading
            if seg:
                seg_clean = seg.replace("\u2014", "--")
                parts.append(f"({self._esc(seg_clean)}) Tj")
            else:
                parts.append("() Tj")
            parts.append(f"0 -{leading} Td")
        parts.append("ET")
        safe_text = "\n".join(parts).replace("\u2014", "--")
        stream = safe_text.encode("latin-1", errors="replace")
        contents_obj = self._add_stream(stream)
        self.page_contents.append(contents_obj)
        print(f"Added content object #{contents_obj}")

    def save(self, path: str):
        print(f"Saving PDF to {path}")
        self._begin()
        self.font_obj = self._add(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
        pages_kids = []
        for cobj in self.page_contents:
            page_dict = (
                f"<< /Type /Page /Parent 0 0 R /MediaBox [0 0 {self.PAGE_SIZE[0]} {self.PAGE_SIZE[1]}] "
                f"/Resources << /Font << /F1 {self.font_obj} 0 R >> >> /Contents {cobj} 0 R >>"
            ).encode("latin-1")
            pobj = self._add(page_dict)
            self.page_objs.append(pobj)
            pages_kids.append(f"{pobj} 0 R")
            print(f"Added page object #{pobj}")
        kids_str = " ".join(pages_kids)
        self.pages_obj = self._add(f"<< /Type /Pages /Kids [{kids_str}] /Count {len(pages_kids)} >>".encode("latin-1"))
        catalog = f"<< /Type /Catalog /Pages {self.pages_obj} 0 R >>".encode("latin-1")
        self.catalog_obj = self._add(catalog)
        meta = [f"/Producer (MinimalPDFv2)"]
        if self.title:
            meta.append(f"/Title ({self._esc(self.title)})")
        if self.author:
            meta.append(f"/Author ({self._esc(self.author)})")
        meta_str = " ".join(meta).encode("latin-1", errors="replace")
        self.info_obj = self._add(b"<< " + meta_str + b" >>")
        xref_start = len(self.buffer)
        self.buffer += b"xref\n"
        total = len(self.offsets) + 1
        print(f"Writing xref with {total} objects")
        self.buffer += f"0 {total}\n".encode("latin-1")
        self.buffer += b"0000000000 65535 f \n"
        for off in self.offsets:
            self.buffer += f"{off:010} 00000 n \n".encode("latin-1")
        self.buffer += b"trailer\n"
        trailer = f"<< /Size {total} /Root {self.catalog_obj} 0 R /Info {self.info_obj} 0 R >>\n".encode("latin-1")
        self.buffer += trailer
        self.buffer += b"startxref\n"
        self.buffer += f"{xref_start}\n".encode("latin-1")
        self.buffer += b"%%EOF"
        with open(path, "wb") as f:
            f.write(self.buffer)
        print(f"PDF '{path}' written successfully. Size: {len(self.buffer)} bytes")

def build_short_codex() -> List[str]:
    print("Building short codex text...")
    return [
        "Black Madonna: The Cowboy's Daughter -- Short Codex",
        "",
        "GENESIS OF DUST",
        "Born Dec 5, 1977, Albuquerque. Only child of Brenda Lenora Pierce Adams and Floyd Wesley Adams. O-negative bloodline and a sky that taught endurance.",
        "",
        "SIN EATER CHILD",
        "A house of grief and rage. Mother's words as knives, father's distance like a locked gate. Learned love = service; safety = silence.",
        "",
        "THE DESCENT",
        "Eddie, older and controlling. Drugs, abortion, the first hard lesson: devotion without protection is a cage.",
        "",
        "THE RIVER WITNESS",
        "Llano River as sanctuary and school. Water held what people would not. Joy and sorrow braided under Texas sun.",
        "",
        "SMOKE AND ASH",
        "Lincoln, Houston, Vietnam--love and betrayal, meth and survival, jail and awakening. Even darkness became a classroom.",
        "",
        "BLACK MADONNA RISING",
        "The Great Mother revealed as comfort and fire. No longer savior or sinner--sovereign.",
        "",
        "LAW OF STILLNESS",
        "Rest isn't quitting. It's the field going fallow so life can root again."
    ]

def build_expanded_codex() -> List[str]:
    print("Building expanded codex text...")
    return [
        "Black Madonna: A Gospel of Dust and Fire -- Expanded Codex",
        "",
        "DESERT WOMB",
        "Albuquerque birth by C-section. Bloodlines O- and AB-, a family stitched by loss. Ezzell Elementary, isolation, sky-wide prayers. The Great Mother moved first in wind and river light.",
        "",
        "SIN-EATER'S HOUSE",
        "Mother's praise in public, cruelty in private. Father's prejudice and distance. Learned to be Pie--the sweet mask that kept the peace. Survived by shrinking, scanning, serving.",
        "",
        "TRACK BOY",
        "Met Eddie after 8th grade. Older, charming, and cruel. Control dressed as love. Abortion in San Antonio, alone. Early drugs. A girl taught to perform devotion as proof of worth.",
        "",
        "THE RIVER REMEMBERS",
        "Llano River: home between homes. Water as witness to firsts--love, loss, and the wild relief of being fully alive.",
        "",
        "HOUSTON NIGHTS",
        "Viet families, churches, beauty school. Jail visits, loyalty, and the line between love and survival. Learned languages of hustle and prayer.",
        "",
        "REFUGEE LOVE & SPELLS",
        "Lincoln, Nebraska. Children born 1999, 2002, 2006. Vietnam trip ruptures--accusations, altars, curses, broken trust and returns. The sacred and the street braided tight.",
        "",
        "SMOKE, STEEL, AND SPEED",
        "Divorce. Meth. Prison. Not madness--hyper-vigilance perfected. The cost of never resting. The body learned that quiet can be safe.",
        "",
        "BLACK MADONNA",
        "She arrives as soil and sword. Comfort that cauterizes. Law that loves. You stop earning holiness and start inhabiting it.",
        "",
        "THE LAW OF CONTAINED FIRE",
        "You don't flood anymore. You channel. Help without rescuing. Love without bleeding. Create without burning down.",
        "",
        "WITNESS MODE",
        "Today's vow: I rest without fear. I rise without apology. The Great Mother never forgot her cowboy's daughter."
    ]

def create_codex_pdfs(short_path: str = "Black_Madonna_Short.pdf", expanded_path: str = "Black_Madonna_Expanded.pdf", author: str = "Amy Pierce Adams"):
    print("Creating both codex PDFs...")
    short_lines = build_short_codex()
    long_lines = build_expanded_codex()
    pdf1 = MinimalPDFv2(title="Black Madonna: The Cowboy's Daughter (Short)", author=author)
    for i in range(0, len(short_lines), 45):
        print(f"Adding chunk of short codex lines {i} to {i+45}")
        pdf1.add_page_text(short_lines[i:i+45], font_size=12, leading=16)
    pdf1.save(short_path)
    pdf2 = MinimalPDFv2(title="Black Madonna: A Gospel of Dust and Fire (Expanded)", author=author)
    for i in range(0, len(long_lines), 40):
        print(f"Adding chunk of expanded codex lines {i} to {i+40}")
        pdf2.add_page_text(long_lines[i:i+40], font_size=12, leading=16)
    pdf2.save(expanded_path)
    print("PDF creation completed.")
    return short_path, expanded_path

def _test_files_exist(paths: List[str]):
    print("Testing existence and size of output files...")
    for p in paths:
        print(f"Checking {p}")
        assert os.path.exists(p), f"Expected file not found: {p}"
        size = os.path.getsize(p)
        print(f"File {p} size={size} bytes")
        assert size > 500, f"PDF too small or empty: {p} (size={size})"

def run_tests():
    print("Running tests for codex PDF creation...")
    paths = create_codex_pdfs()
    _test_files_exist(list(paths))
    print("All tests passed successfully.")
    return {"ok": True, "paths": paths, "timestamp": datetime.utcnow().isoformat()}

if __name__ == "__main__":
    print("Executing as main program...")
    result = run_tests()
    print("Generated:", result["paths"])
