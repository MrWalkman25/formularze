import fitz
import gi

gi.require_version("GdkPixbuf", "2.0")
from gi.repository import GdkPixbuf


def get_pdf_page_count(pdf_path: str) -> int:
    """
    Повертає кількість сторінок у PDF.
    """
    doc = fitz.open(pdf_path)
    try:
        return len(doc)
    finally:
        doc.close()



def get_page_size(pdf_path: str, page_index: int) -> tuple[float, float, float, float]:
    """
    Zwraca: (width, height, x0, y0)
    """
    doc = fitz.open(pdf_path)
    try:
        page = doc[page_index]
        rect = page.rect
        # Ważne: rect.x0 i rect.y0 to początek widocznego obszaru
        return rect.width, rect.height, rect.x0, rect.y0
    finally:
        doc.close()


def render_page_to_pixbuf(pdf_path: str, page_index: int, target_width: int) -> GdkPixbuf.Pixbuf:
    """
    Відкриває PDF, рендерить вказану сторінку під задану ширину
    і повертає її як GdkPixbuf.Pixbuf.
    """

    if target_width <= 0:
        raise ValueError("target_width must be greater than 0")

    doc = fitz.open(pdf_path)

    try:
        if page_index < 0 or page_index >= len(doc):
            raise IndexError(f"Page index out of range: {page_index}")

        page = doc[page_index]

        page_rect = page.rect
        page_width = page_rect.width

        scale = target_width / page_width
        matrix = fitz.Matrix(scale, scale)

        pix = page.get_pixmap(matrix=matrix, alpha=False)

        pixbuf = GdkPixbuf.Pixbuf.new_from_data(
            pix.samples,
            GdkPixbuf.Colorspace.RGB,
            False,
            8,
            pix.width,
            pix.height,
            pix.stride,
            None,
            None,
        )

        return pixbuf
    finally:
        doc.close()