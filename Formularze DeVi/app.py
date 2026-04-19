import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Adw

from ui.main_window import MainWindow


class DeViApp(Adw.Application):
    def __init__(self):
        super().__init__(application_id="com.devi.formularze")

    def do_activate(self):
        window = MainWindow(application=self)
        window.present()