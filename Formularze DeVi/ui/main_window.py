import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw

from core.pdf_loader import get_pdf_page_count, get_page_size, render_page_to_pixbuf
from core.pdf_layout_parser import get_text_blocks, get_words
from core.field_candidate_detector import detect_field_candidates


class PdfOverlayWidget(Gtk.Overlay):
    def __init__(self):
        super().__init__()
        self.picture = Gtk.Picture()
        self.picture.set_can_shrink(False)
        self.picture.set_halign(Gtk.Align.START)
        self.picture.set_valign(Gtk.Align.START)
        self.set_child(self.picture)

        self.drawing_area = Gtk.DrawingArea()
        self.drawing_area.set_draw_func(self.draw_overlay)
        self.drawing_area.set_halign(Gtk.Align.START)
        self.drawing_area.set_valign(Gtk.Align.START)
        self.add_overlay(self.drawing_area)

        self.debug_items = []
        self.candidate_items = []
        self.current_pixbuf = None
        self.page_width = 1
        self.page_height = 1
        self.page_x0 = 0
        self.page_y0 = 0

    def set_page_pixbuf(self, pixbuf):
        self.current_pixbuf = pixbuf
        self.picture.set_pixbuf(pixbuf)

        if pixbuf is not None:
            self.drawing_area.set_content_width(pixbuf.get_width())
            self.drawing_area.set_content_height(pixbuf.get_height())

        self.drawing_area.queue_draw()

    def set_debug_items(self, items, page_width, page_height, page_x0, page_y0):
        self.debug_items = items
        self.page_width = page_width
        self.page_height = page_height
        self.page_x0 = page_x0
        self.page_y0 = page_y0
        self.drawing_area.queue_draw()

    def clear_debug_items(self):
        self.debug_items = []
        self.drawing_area.queue_draw()

    def set_candidate_items(self, items, page_width, page_height, page_x0, page_y0):
        self.candidate_items = items
        self.page_width = page_width
        self.page_height = page_height
        self.page_x0 = page_x0
        self.page_y0 = page_y0
        self.drawing_area.queue_draw()

    def clear_candidate_items(self):
        self.candidate_items = []
        self.drawing_area.queue_draw()

    def _draw_rectangles(self, cr, items, r, g, b, a, line_width):
        if self.current_pixbuf is None or self.page_width <= 0 or self.page_height <= 0:
            return

        pixbuf_width = self.current_pixbuf.get_width()
        pixbuf_height = self.current_pixbuf.get_height()

        scale_x = pixbuf_width / self.page_width
        scale_y = pixbuf_height / self.page_height

        cr.set_source_rgba(r, g, b, a)
        cr.set_line_width(line_width)

        for item in items:
            x0 = (item["x0"] - self.page_x0) * scale_x
            y0 = (item["y0"] - self.page_y0) * scale_y
            x1 = (item["x1"] - self.page_x0) * scale_x
            y1 = (item["y1"] - self.page_y0) * scale_y

            cr.rectangle(x0, y0, x1 - x0, y1 - y0)
            cr.stroke()

    def draw_overlay(self, area, cr, width, height):
        self._draw_rectangles(cr, self.debug_items, 1.0, 0.0, 0.0, 0.6, 0.5)
        self._draw_rectangles(cr, self.candidate_items, 0.0, 0.3, 1.0, 0.9, 1.5)


class MainWindow(Adw.ApplicationWindow):
    def __init__(self, application):
        super().__init__(application=application)

        self.set_title("Formularze DeVi")
        self.set_default_size(900, 600)

        self.current_pdf_path = None
        self.current_page_index = 0
        self.total_pages = 0
        self.debug_mode_enabled = False
        self.debug_view_mode = "blocks"
        self.detect_mode_enabled = False

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_content(box)

        headerbar = Adw.HeaderBar()
        title_widget = Adw.WindowTitle(title="Formularze DeVi")
        headerbar.set_title_widget(title_widget)
        headerbar.set_show_start_title_buttons(True)
        headerbar.set_show_end_title_buttons(True)
        box.append(headerbar)

        open_button = Gtk.Button(label="Відкрити PDF")
        open_button.connect("clicked", self.on_open_pdf_clicked)
        headerbar.pack_start(open_button)

        self.prev_button = Gtk.Button(label="Назад")
        self.prev_button.connect("clicked", self.on_prev_page_clicked)
        self.prev_button.set_sensitive(False)
        headerbar.pack_start(self.prev_button)

        self.next_button = Gtk.Button(label="Далі")
        self.next_button.connect("clicked", self.on_next_page_clicked)
        self.next_button.set_sensitive(False)
        headerbar.pack_start(self.next_button)

        self.debug_button = Gtk.ToggleButton(label="Debug layout")
        self.debug_button.connect("toggled", self.on_debug_toggled)
        self.debug_button.set_sensitive(False)
        headerbar.pack_start(self.debug_button)

        self.debug_mode_dropdown = Gtk.DropDown.new_from_strings(["Blocks", "Words"])
        self.debug_mode_dropdown.set_selected(0)
        self.debug_mode_dropdown.connect("notify::selected", self.on_debug_mode_changed)
        self.debug_mode_dropdown.set_sensitive(False)
        headerbar.pack_start(self.debug_mode_dropdown)

        self.detect_button = Gtk.ToggleButton(label="Detect fields")
        self.detect_button.connect("toggled", self.on_detect_toggled)
        self.detect_button.set_sensitive(False)
        headerbar.pack_start(self.detect_button)

        page_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)

        self.page_entry = Gtk.Entry()
        self.page_entry.set_width_chars(2)
        self.page_entry.set_max_width_chars(3)
        self.page_entry.set_alignment(0.5)
        self.page_entry.set_placeholder_text("1")
        self.page_entry.set_sensitive(False)
        self.page_entry.connect("activate", self.on_page_entry_activate)
        page_box.append(self.page_entry)

        self.page_label = Gtk.Label(label="/ -")
        page_box.append(self.page_label)

        headerbar.pack_end(page_box)

        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_hexpand(True)
        self.scrolled_window.set_vexpand(True)
        box.append(self.scrolled_window)

        self.pdf_widget = PdfOverlayWidget()
        self.scrolled_window.set_child(self.pdf_widget)

    def on_open_pdf_clicked(self, button):
        dialog = Gtk.FileDialog()
        dialog.set_title("Відкрити PDF")

        pdf_filter = Gtk.FileFilter()
        pdf_filter.set_name("PDF files")
        pdf_filter.add_mime_type("application/pdf")
        dialog.set_default_filter(pdf_filter)

        dialog.open(self, None, self.on_file_selected)

    def on_file_selected(self, dialog, result):
        try:
            file = dialog.open_finish(result)
        except Exception as error:
            print(f"Скасовано або помилка діалогу: {error}")
            return

        if file is None:
            return

        pdf_path = file.get_path()
        if not pdf_path:
            print("Не вдалося отримати шлях до файлу")
            return

        try:
            self.current_pdf_path = pdf_path
            self.current_page_index = 0
            self.total_pages = get_pdf_page_count(pdf_path)

            self.debug_mode_enabled = False
            self.debug_view_mode = "blocks"
            self.detect_mode_enabled = False

            self.debug_button.set_active(False)
            self.debug_mode_dropdown.set_selected(0)
            self.detect_button.set_active(False)

            self.update_navigation_ui()
            self.render_current_pdf_page()

            print(f"Відкрито PDF: {pdf_path}")
            print(f"Усього сторінок: {self.total_pages}")
        except Exception as error:
            print(f"Помилка при відкритті PDF: {error}")

    def on_prev_page_clicked(self, button):
        if self.current_page_index > 0:
            self.current_page_index -= 1
            self.update_navigation_ui()
            self.render_current_pdf_page()

    def on_next_page_clicked(self, button):
        if self.current_page_index < self.total_pages - 1:
            self.current_page_index += 1
            self.update_navigation_ui()
            self.render_current_pdf_page()

    def on_page_entry_activate(self, entry):
        if not self.current_pdf_path or self.total_pages <= 0:
            return

        text = entry.get_text().strip()

        if not text.isdigit():
            print(f"Некоректний номер сторінки: {text}")
            self.update_navigation_ui()
            return

        page_number = int(text)

        if page_number < 1 or page_number > self.total_pages:
            print(f"Номер сторінки поза межами: {page_number}")
            self.update_navigation_ui()
            return

        self.current_page_index = page_number - 1
        self.update_navigation_ui()
        self.render_current_pdf_page()

    def on_debug_toggled(self, button):
        self.debug_mode_enabled = button.get_active()
        self.render_current_pdf_page()

    def on_debug_mode_changed(self, dropdown, _param):
        selected_index = dropdown.get_selected()
        self.debug_view_mode = "blocks" if selected_index == 0 else "words"

        if self.debug_mode_enabled:
            self.render_current_pdf_page()

    def on_detect_toggled(self, button):
        self.detect_mode_enabled = button.get_active()
        self.render_current_pdf_page()

    def update_navigation_ui(self):
        has_pdf = self.current_pdf_path is not None and self.total_pages > 0

        self.prev_button.set_sensitive(has_pdf and self.current_page_index > 0)
        self.next_button.set_sensitive(has_pdf and self.current_page_index < self.total_pages - 1)
        self.page_entry.set_sensitive(has_pdf)
        self.debug_button.set_sensitive(has_pdf)
        self.debug_mode_dropdown.set_sensitive(has_pdf)
        self.detect_button.set_sensitive(has_pdf)

        if has_pdf:
            current_page_number = self.current_page_index + 1
            self.page_entry.set_text(str(current_page_number))
            self.page_label.set_text(f"/ {self.total_pages}")
        else:
            self.page_entry.set_text("")
            self.page_label.set_text("/ -")

    def render_current_pdf_page(self):
        if not self.current_pdf_path:
            return

        viewport_width = self.scrolled_window.get_width()

        if viewport_width <= 0:
            viewport_width = 800

        target_width = max(100, viewport_width - 40)

        try:
            pixbuf = render_page_to_pixbuf(
                self.current_pdf_path,
                self.current_page_index,
                target_width
            )
            self.pdf_widget.set_page_pixbuf(pixbuf)

            page_width, page_height, x0, y0 = get_page_size(
                self.current_pdf_path,
                self.current_page_index
            )

            if self.debug_mode_enabled:
                if self.debug_view_mode == "blocks":
                    debug_items = get_text_blocks(self.current_pdf_path, self.current_page_index)
                else:
                    debug_items = get_words(self.current_pdf_path, self.current_page_index)

                self.pdf_widget.set_debug_items(debug_items, page_width, page_height, x0, y0)
                print(f"Debug mode: {self.debug_view_mode}")
                print(f"Debug items: {len(debug_items)}")
            if self.detect_mode_enabled:
                words = get_words(self.current_pdf_path, self.current_page_index)
                candidates = detect_field_candidates(
                    words,
                    self.current_pdf_path,
                    self.current_page_index
                )
                self.pdf_widget.set_candidate_items(candidates, page_width, page_height, x0, y0)
                print(f"Detected candidates: {len(candidates)}")
            else:
                self.pdf_widget.clear_candidate_items()

            print(f"Показано сторінку: {self.current_page_index + 1}")
            print(f"Ширина viewport: {viewport_width}")
            print(f"Ширина рендера: {target_width}")
        except Exception as error:
            print(f"Помилка при рендері сторінки: {error}")