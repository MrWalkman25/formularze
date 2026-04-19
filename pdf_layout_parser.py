import fitz
import re


def get_text_blocks(pdf_path: str, page_index: int) -> list[dict]:
    doc = fitz.open(pdf_path)

    try:
        if page_index < 0 or page_index >= len(doc):
            raise IndexError(f"Page index out of range: {page_index}")

        page = doc[page_index]
        raw_blocks = page.get_text("blocks")

        blocks = []

        for block in raw_blocks:
            x0, y0, x1, y1, text, block_no, block_type = block

            if block_type != 0:
                continue

            if not text or not text.strip():
                continue

            blocks.append({
                "x0": x0,
                "y0": y0,
                "x1": x1,
                "y1": y1,
                "text": text.strip(),
            })

        return blocks

    finally:
        doc.close()


def get_words(pdf_path: str, page_index: int) -> list[dict]:
    doc = fitz.open(pdf_path)

    try:
        if page_index < 0 or page_index >= len(doc):
            raise IndexError(f"Page index out of range: {page_index}")

        page = doc[page_index]
        raw_words = page.get_text("words")

        words = []

        for word in raw_words:
            x0, y0, x1, y1, text, block_no, line_no, word_no = word

            if not text or not text.strip():
                continue

            words.append({
                "x0": x0,
                "y0": y0,
                "x1": x1,
                "y1": y1,
                "text": text.strip(),
                "block_no": block_no,
                "line_no": line_no,
                "word_no": word_no,
            })

        return words

    finally:
        doc.close()


def normalize_text(text: str) -> str:
    text = text.strip()
    text = re.sub(r"\s+", " ", text)
    return text


def build_text_lines(words: list[dict], y_tolerance: float = 2.5) -> list[dict]:
    """
    Групує слова в рядки.
    Спочатку пробуємо спертися на block_no/line_no з PyMuPDF,
    але додатково допускаємо невеликий розкид по y.
    """

    if not words:
        return []

    words_sorted = sorted(
        words,
        key=lambda w: (
            w.get("block_no", 0),
            w.get("line_no", 0),
            w["y0"],
            w["x0"],
        )
    )

    lines = []
    current_words = []

    def flush_current():
        nonlocal current_words

        if not current_words:
            return

        current_words = sorted(current_words, key=lambda w: w["x0"])

        text = " ".join(w["text"] for w in current_words)
        line = {
            "x0": min(w["x0"] for w in current_words),
            "y0": min(w["y0"] for w in current_words),
            "x1": max(w["x1"] for w in current_words),
            "y1": max(w["y1"] for w in current_words),
            "text": normalize_text(text),
            "words": current_words.copy(),
            "block_no": current_words[0].get("block_no"),
            "line_no": current_words[0].get("line_no"),
        }
        lines.append(line)
        current_words = []

    prev = None

    for word in words_sorted:
        if prev is None:
            current_words.append(word)
            prev = word
            continue

        same_block = word.get("block_no") == prev.get("block_no")
        same_line = word.get("line_no") == prev.get("line_no")
        close_y = abs(word["y0"] - prev["y0"]) <= y_tolerance

        if same_block and same_line and close_y:
            current_words.append(word)
        else:
            flush_current()
            current_words.append(word)

        prev = word

    flush_current()
    return lines


def build_label_phrases(
    lines: list[dict],
    max_gap_factor: float = 1.8,
    max_phrase_words: int = 4,
) -> list[dict]:
    """
    Будує фрази-підписи з рядків.
    Логіка проста:
    - беремо слова в рядку
    - склеюємо сусідні слова, якщо між ними нормальний проміжок
    - зберігаємо короткі фрази як label candidates

    Це ще не "поле", це тільки фраза з геометрією.
    """

    phrases = []

    for line in lines:
        words = line["words"]
        if not words:
            continue

        avg_height = sum((w["y1"] - w["y0"]) for w in words) / len(words)
        max_gap = max(8.0, avg_height * max_gap_factor)

        current_group = [words[0]]

        def flush_group():
            nonlocal current_group

            if not current_group:
                return

            text = normalize_text(" ".join(w["text"] for w in current_group))

            if 1 <= len(current_group) <= max_phrase_words:
                phrases.append({
                    "x0": min(w["x0"] for w in current_group),
                    "y0": min(w["y0"] for w in current_group),
                    "x1": max(w["x1"] for w in current_group),
                    "y1": max(w["y1"] for w in current_group),
                    "text": text,
                    "words": current_group.copy(),
                    "source_line_text": line["text"],
                })

            current_group = []

        for prev_word, word in zip(words, words[1:]):
            gap = word["x0"] - prev_word["x1"]

            if gap <= max_gap:
                current_group.append(word)
            else:
                flush_group()
                current_group = [word]

        flush_group()

    return phrases


def get_graphics(pdf_path: str, page_index: int) -> list[dict]:
    """
    Pobiera rysunki (wektorowe) ze strony.
    Interesują nas małe prostokąty, które mogą być checkboxami.
    """
    doc = fitz.open(pdf_path)
    try:
        if page_index < 0 or page_index >= len(doc):
            return []

        page = doc[page_index]
        paths = page.get_drawings()
        rects = []

        for path in paths:
            # r to obwiednia danego rysunku (ścieżki)
            r = path["rect"]

            # Interesują nas małe, w miarę kwadratowe kształty
            # Checkboxy zwykle mają bok ok. 8-15 pkt.
            if 5 < r.width < 25 and 5 < r.height < 25:
                # Sprawdzamy proporcje (czy to kwadrat)
                ratio = r.width / r.height
                if 0.7 < ratio < 1.4:
                    rects.append({
                        "x0": r.x0,
                        "y0": r.y0,
                        "x1": r.x1,
                        "y1": r.y1,
                    })

        return rects
    finally:
        doc.close()

def get_layout_lines(pdf_path: str, page_index: int) -> tuple[list[dict], list[dict]]:
    """
    Pobiera wszystkie poziome i pionowe linie z wektorowej warstwy PDF.
    Zwraca (h_lines, v_lines).
    """
    doc = fitz.open(pdf_path)
    try:
        if page_index < 0 or page_index >= len(doc):
            return [], []

        page = doc[page_index]
        paths = page.get_drawings()
        
        h_lines = []
        v_lines = []
        
        for path in paths:
            for item in path["items"]:
                if item[0] == "l":
                    p1, p2 = item[1], item[2]
                    # Pozioma linia
                    if abs(p1.y - p2.y) < 2:
                        h_lines.append({
                            "y": (p1.y + p2.y) / 2,
                            "x0": min(p1.x, p2.x),
                            "x1": max(p1.x, p2.x)
                        })
                    # Pionowa linia
                    elif abs(p1.x - p2.x) < 2:
                        v_lines.append({
                            "x": (p1.x + p2.x) / 2,
                            "y0": min(p1.y, p2.y),
                            "y1": max(p1.y, p2.y)
                        })
                elif item[0] == "re":
                    # Prostokąt - traktujemy jako 4 linie
                    r = item[1]
                    h_lines.append({"y": r.y0, "x0": r.x0, "x1": r.x1})
                    h_lines.append({"y": r.y1, "x0": r.x0, "x1": r.x1})
                    v_lines.append({"x": r.x0, "y0": r.y0, "y1": r.y1})
                    v_lines.append({"x": r.x1, "y0": r.y0, "y1": r.y1})

        return h_lines, v_lines
    finally:
        doc.close()


def get_acroform_widgets(pdf_path: str, page_index: int) -> list[dict]:
    """
    Pobiera gotowe pola formularza (AcroForm widgets), jeśli dokument je posiada.
    Zwraca listę słowników z metadanymi i koordynatami pól.
    """
    doc = fitz.open(pdf_path)
    try:
        if page_index < 0 or page_index >= len(doc):
            return []

        page = doc[page_index]
        widgets = []

        for widget in page.widgets():
            rect = widget.rect
            
            # Mapowanie typów widgetów PyMuPDF na nasze wewnętrжні
            f_type = "text"
            if widget.field_type == fitz.PDF_WIDGET_TYPE_CHECKBOX:
                f_type = "checkbox"
            elif widget.field_type == fitz.PDF_WIDGET_TYPE_RADIOBUTTON:
                f_type = "checkbox" # Traktujemy radio jak checkbox dla uproszczenia
            
            widgets.append({
                "field_name": widget.field_name or "unknown",
                "field_type": f_type,
                "x0": rect.x0,
                "y0": rect.y0,
                "x1": rect.x1,
                "y1": rect.y1,
                "page_index": page_index
            })

        return widgets
    finally:
        doc.close()