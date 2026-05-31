import gi
import subprocess
import os
import threading
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib, Gdk

class PardusCleaner:
    def __init__(self):
        self.items = [
            {"key": "apt", "name": "APT paket önbelleği", "dir": "/var/cache/apt/archives", "cmd": ["pkexec", "apt", "clean"]},
            {"key": "trash", "name": "Çöp kutusu", "dir": "~/.local/share/Trash/files", "cmd": ["rm", "-rf"]},
            {"key": "thumb", "name": "Küçük resim önbelleği", "dir": "~/.cache/thumbnails", "cmd": ["rm", "-rf"]},
            {"key": "pip", "name": "pip önbelleği", "dir": "~/.cache/pip", "cmd": ["rm", "-rf"]},
            {"key": "npm", "name": "npm önbelleği", "dir": "~/.npm", "cmd": ["rm", "-rf"]},
            {"key": "aur", "name": "AUR build önbelleği", "dir": "~/.cache/yay", "cmd": ["rm", "-rf"]},
            {"key": "journal", "name": "Sistem günlükleri", "dir": None, "cmd": ["pkexec", "journalctl", "--vacuum-time=7d"]},
            {"key": "pacman", "name": "Pacman önbelleği", "dir": "/var/cache/pacman/pkg", "cmd": ["pkexec", "pacman", "-Sc", "--noconfirm"]},
            {"key": "firefox", "name": "Firefox önbelleği", "dir": "~/.cache/mozilla", "cmd": ["rm", "-rf"]},
            {"key": "cache", "name": "Genel uygulama önbelleği", "dir": "~/.cache/*", "cmd": ["rm", "-rf"]},
        ]
        self.checkboxes = {}
        self.sizes = {}
        self.total_before = 0
        self.total_after = 0

    def get_size(self, path):
        if not path:
            return "0 B"
        path = os.path.expanduser(path)
        if not os.path.exists(path):
            return "0 B"
        try:
            r = subprocess.run(["du", "-sb", path], capture_output=True, text=True, timeout=5)
            bytes_val = int(r.stdout.split()[0])
            return self.format_bytes(bytes_val)
        except:
            return "0 B"

    def get_size_bytes(self, path):
        if not path:
            return 0
        path = os.path.expanduser(path)
        if not os.path.exists(path):
            return 0
        try:
            r = subprocess.run(["du", "-sb", path], capture_output=True, text=True, timeout=5)
            return int(r.stdout.split()[0])
        except:
            return 0

    def format_bytes(self, b):
        for u in ["B", "KB", "MB", "GB"]:
            if b < 1024:
                return f"{b:.1f} {u}"
            b /= 1024
        return f"{b:.1f} TB"

    def build_ui(self):
        self.win = Gtk.Window(title="Pardus Cleaner")
        self.win.set_default_size(600, 500)
        self.win.connect("destroy", Gtk.main_quit)

        self.apply_theme()

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        vbox.set_margin_top(15)
        vbox.set_margin_bottom(15)
        vbox.set_margin_start(15)
        vbox.set_margin_end(15)

        title = Gtk.Label(label="Pardus Cleaner")
        title.get_style_context().add_class("title")
        vbox.pack_start(title, False, False, 0)

        btn_box = Gtk.Box(spacing=5)
        self.btn_all = Gtk.Button(label="Hepsini seç")
        self.btn_all.connect("clicked", self.toggle_all)
        btn_box.pack_start(self.btn_all, False, False, 0)
        vbox.pack_start(btn_box, False, False, 0)

        scroll = Gtk.ScrolledWindow()
        self.listbox = Gtk.ListBox()
        scroll.add(self.listbox)
        vbox.pack_start(scroll, True, True, 0)

        for item in self.items:
            row = Gtk.ListBoxRow()
            hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            check = Gtk.CheckButton(label=item["name"])
            size_label = Gtk.Label(label=self.get_size(item["dir"]))
            size_label.get_style_context().add_class("dim-label")
            hbox.pack_start(check, True, True, 0)
            hbox.pack_end(size_label, False, False, 0)
            row.add(hbox)
            self.listbox.add(row)
            self.checkboxes[item["key"]] = check

        self.progress = Gtk.ProgressBar()
        vbox.pack_start(self.progress, False, False, 0)

        status_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.lbl_before = Gtk.Label(label="Önce: 0 B")
        self.lbl_after = Gtk.Label(label="Sonra: 0 B")
        self.lbl_result = Gtk.Label(label="")
        status_box.pack_start(self.lbl_before, False, False, 0)
        status_box.pack_start(self.lbl_after, False, False, 0)
        status_box.pack_end(self.lbl_result, False, False, 0)
        vbox.pack_start(status_box, False, False, 0)

        button = Gtk.Button(label="Temizle")
        button.get_style_context().add_class("suggested-action")
        button.connect("clicked", self.on_clean)
        vbox.pack_start(button, False, False, 0)

        self.win.add(vbox)

    def apply_theme(self):
        settings = Gtk.Settings.get_default()
        if settings:
            settings.set_property("gtk-application-prefer-dark-theme", True)

    def toggle_all(self, btn):
        all_selected = all(c.get_active() for c in self.checkboxes.values())
        for c in self.checkboxes.values():
            c.set_active(not all_selected)
        btn.set_label("Hiçbirini seç" if not all_selected else "Hepsini seç")

    def on_clean(self, btn):
        selected = [k for k, c in self.checkboxes.items() if c.get_active()]
        if not selected:
            return

        self.total_before = sum(self.get_size_bytes(self.get_item_by_key(k)["dir"]) for k in selected)
        self.lbl_before.set_label(f"Önce: {self.format_bytes(self.total_before)}")
        self.lbl_result.set_label("Temizleniyor...")

        btn.set_sensitive(False)
        self.progress.set_fraction(0)

        thread = threading.Thread(target=self.clean_thread, args=(selected, btn))
        thread.daemon = True
        thread.start()

    def get_item_by_key(self, key):
        for i in self.items:
            if i["key"] == key:
                return i
        return None

    def clean_thread(self, selected, btn):
        total = len(selected)
        for idx, key in enumerate(selected):
            item = self.get_item_by_key(key)
            GLib.idle_add(self.progress.set_fraction, (idx) / total)
            GLib.idle_add(self.lbl_result.set_label, f"{item['name']} temizleniyor...")

            try:
                if key == "trash":
                    subprocess.run(["rm", "-rf", os.path.expanduser("~/.local/share/Trash/files")])
                elif key == "thumb":
                    subprocess.run(["rm", "-rf", os.path.expanduser("~/.cache/thumbnails")])
                elif key == "pip":
                    subprocess.run(["rm", "-rf", os.path.expanduser("~/.cache/pip")])
                elif key == "npm":
                    subprocess.run(["rm", "-rf", os.path.expanduser("~/.npm")])
                elif key == "aur":
                    subprocess.run(["rm", "-rf", os.path.expanduser("~/.cache/yay")])
                elif key == "firefox":
                    subprocess.run(["rm", "-rf", os.path.expanduser("~/.cache/mozilla")])
                elif key == "cache":
                    subprocess.run(["rm", "-rf", os.path.expanduser("~/.cache/*")])
                elif key == "apt":
                    subprocess.run(["pkexec", "apt", "clean"], capture_output=True, timeout=60)
                elif key == "journal":
                    subprocess.run(["pkexec", "journalctl", "--vacuum-time=7d"], capture_output=True, timeout=30)
                elif key == "pacman":
                    subprocess.run(["pkexec", "pacman", "-Sc", "--noconfirm"], capture_output=True, timeout=60)
            except:
                pass

        GLib.idle_add(self.progress.set_fraction, 1)
        self.total_after = sum(self.get_size_bytes(self.get_item_by_key(k)["dir"]) for k in selected)
        freed = self.total_before - self.total_after

        GLib.idle_add(self.lbl_after.set_label, f"Sonra: {self.format_bytes(self.total_after)}")
        GLib.idle_add(self.lbl_result.set_label, f"{self.format_bytes(freed)} boşaltıldı")
        GLib.idle_add(btn.set_sensitive, True)

        for key in selected:
            item = self.get_item_by_key(key)
            row_idx = [i["key"] for i in self.items].index(key)
            row = self.listbox.get_row_at_index(row_idx)
            if row:
                hbox = row.get_child()
                labels = [c for c in hbox.get_children() if isinstance(c, Gtk.Label)]
                if labels:
                    labels[0].set_text(self.get_size(item["dir"]))

    def run(self):
        self.build_ui()
        self.win.show_all()
        Gtk.main()

if __name__ == "__main__":
    PardusCleaner().run()
