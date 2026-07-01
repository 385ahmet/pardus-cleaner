import gi
import subprocess
import os
import shutil
import threading
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib, Gdk
from pathlib import Path


def detect_distro():
    try:
        with open("/etc/os-release") as f:
            data = f.read()
        if "ID=pardus" in data or "ID_LIKE=pardus" in data:
            return "pardus"
        if "ID=debian" in data or "ID_LIKE=debian" in data:
            return "debian"
        if "ID=ubuntu" in data or "ID_LIKE=ubuntu" in data:
            return "ubuntu"
        if "ID=arch" in data or "ID_LIKE=arch" in data:
            return "arch"
        if "ID=fedora" in data or "ID_LIKE=fedora" in data:
            return "fedora"
        return "linux"
    except:
        return "linux"


def is_installed(cmd):
    return shutil.which(cmd) is not None


def safe_rmtree(path: str) -> str | None:
    expanded = os.path.expanduser(path)
    p = Path(expanded)
    if not p.exists():
        return None
    if not p.is_dir():
        return f"{path} bir dizin değil, atlandı"
    try:
        shutil.rmtree(p)
        return None
    except PermissionError:
        return f"{path} için izin yok"
    except OSError as e:
        return f"{path} temizlenemedi: {e}"


def get_dir_size(path: str) -> int:
    expanded = os.path.expanduser(path)
    p = Path(expanded)
    if not p.exists() or not p.is_dir():
        return 0
    total = 0
    try:
        for entry in p.rglob("*"):
            if entry.is_file() and not entry.is_symlink():
                total += entry.stat().st_size
    except (PermissionError, OSError):
        pass
    return total


def format_bytes(b: int) -> str:
    for u in ["B", "KB", "MB", "GB"]:
        if b < 1024:
            return f"{b:.1f} {u}"
        b //= 1024
    return f"{b:.1f} TB"


class CleaningItem:
    def __init__(self, key, name, dir_path=None, clean_func=None, distros=None):
        self.key = key
        self.name = name
        self.dir_path = dir_path
        self.clean_func = clean_func
        self.distros = distros

    def is_visible(self, distro):
        if self.distros is None:
            return True
        return distro in self.distros

    def get_size(self):
        if not self.dir_path:
            return 0
        return get_dir_size(self.dir_path)

    def clean(self):
        if self.clean_func:
            return self.clean_func()
        if self.dir_path:
            return safe_rmtree(self.dir_path)
        return None


class PardusCleaner:
    def __init__(self):
        self.distro = detect_distro()
        self.errors = []
        self._build_items()

    def _build_items(self):
        self.items = []

        self.items.append(CleaningItem(
            "apt", "APT paket onbelleği",
            "/var/cache/apt/archives",
            lambda: subprocess.run(["pkexec", "apt", "clean"], capture_output=True, timeout=120) and None,
            distros=["pardus", "debian", "ubuntu"],
        ))

        self.items.append(CleaningItem(
            "pacman", "Pacman onbelleği",
            "/var/cache/pacman/pkg",
            lambda: subprocess.run(["pkexec", "pacman", "-Sc", "--noconfirm"], capture_output=True, timeout=120) and None,
            distros=["arch"],
        ))

        self.items.append(CleaningItem(
            "trash", "Çöp kutusu",
            "~/.local/share/Trash/files",
        ))

        self.items.append(CleaningItem(
            "thumb", "Küçük resim onbelleği",
            "~/.cache/thumbnails",
        ))

        self.items.append(CleaningItem(
            "pip", "pip onbelleği",
            "~/.cache/pip",
        ))

        self.items.append(CleaningItem(
            "npm", "npm onbelleği",
            "~/.npm",
        ))

        self.items.append(CleaningItem(
            "firefox", "Firefox onbelleği",
            "~/.cache/mozilla/firefox",
        ))

        self.items.append(CleaningItem(
            "journal", "Sistem günlükleri (journald)",
            clean_func=lambda: subprocess.run(
                ["pkexec", "journalctl", "--vacuum-time=7d"], capture_output=True, timeout=30
            ) and None,
        ))

        self.items.append(CleaningItem(
            "docker", "Docker (kullanılmayan imageler)",
            clean_func=lambda: subprocess.run(
                ["docker", "system", "prune", "-f"], capture_output=True, timeout=120
            ) and None,
            distros=["pardus", "debian", "ubuntu", "arch", "fedora"],
        ))

        self.items.append(CleaningItem(
            "flatpak", "Flatpak kullanılmayan çalışma zamanları",
            clean_func=lambda: subprocess.run(
                ["flatpak", "uninstall", "--unused", "-y"], capture_output=True, timeout=120
            ) and None,
        ))

        self.items.append(CleaningItem(
            "snap", "Snap onbelleği",
            "/var/lib/snapd/cache",
            lambda: subprocess.run(["pkexec", "sh", "-c", "rm -rf /var/lib/snapd/cache/*"], capture_output=True, timeout=30) and None,
        ))

        self.items.append(CleaningItem(
            "genel-cache", "Genel uygulama onbelleği",
            "~/.cache",
        ))

        self.checkboxes = {}

    def _visible_items(self):
        return [item for item in self.items if item.is_visible(self.distro)]

    def get_size_str(self, dir_path):
        if not dir_path:
            return "0 B"
        return format_bytes(get_dir_size(dir_path))

    def build_ui(self):
        self.win = Gtk.Window(title="Pardus Cleaner")
        self.win.set_default_size(600, 500)
        self.win.connect("destroy", Gtk.main_quit)

        settings = Gtk.Settings.get_default()
        if settings:
            settings.set_property("gtk-application-prefer-dark-theme", True)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        vbox.set_margin_top(15)
        vbox.set_margin_bottom(15)
        vbox.set_margin_start(15)
        vbox.set_margin_end(15)

        title = Gtk.Label(label="Pardus Cleaner")
        title.get_style_context().add_class("title")
        vbox.pack_start(title, False, False, 0)

        distro_label = Gtk.Label(label=f"Tespit edilen: {self.distro}")
        distro_label.get_style_context().add_class("dim-label")
        vbox.pack_start(distro_label, False, False, 0)

        btn_box = Gtk.Box(spacing=5)
        self.btn_all = Gtk.Button(label="Hepsini seç")
        self.btn_all.connect("clicked", self.toggle_all)
        btn_box.pack_start(self.btn_all, False, False, 0)
        vbox.pack_start(btn_box, False, False, 0)

        scroll = Gtk.ScrolledWindow()
        self.listbox = Gtk.ListBox()
        scroll.add(self.listbox)
        vbox.pack_start(scroll, True, True, 0)

        for item in self._visible_items():
            row = Gtk.ListBoxRow()
            hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            check = Gtk.CheckButton(label=item.name)
            size_label = Gtk.Label(label=self.get_size_str(item.dir_path))
            size_label.get_style_context().add_class("dim-label")
            hbox.pack_start(check, True, True, 0)
            hbox.pack_end(size_label, False, False, 0)
            row.add(hbox)
            self.listbox.add(row)
            self.checkboxes[item.key] = check

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

        self.error_label = Gtk.Label(label="")
        self.error_label.get_style_context().add_class("error")
        self.error_label.set_visible(False)
        vbox.pack_start(self.error_label, False, False, 0)

        button = Gtk.Button(label="Temizle")
        button.get_style_context().add_class("suggested-action")
        button.connect("clicked", self.on_clean)
        vbox.pack_start(button, False, False, 0)

        self.win.add(vbox)

    def toggle_all(self, btn):
        selected = [c for c in self.checkboxes.values()]
        if not selected:
            return
        all_selected = all(c.get_active() for c in selected)
        for c in selected:
            c.set_active(not all_selected)
        btn.set_label("Hiçbirini seç" if not all_selected else "Hepsini seç")

    def on_clean(self, btn):
        selected_keys = [k for k, c in self.checkboxes.items() if c.get_active()]
        if not selected_keys:
            return

        self.errors = []
        self.error_label.set_visible(False)
        self.total_before = 0
        for key in selected_keys:
            item = next((i for i in self.items if i.key == key), None)
            if item:
                self.total_before += item.get_size()
        self.lbl_before.set_label(f"Önce: {format_bytes(self.total_before)}")
        self.lbl_result.set_label("Temizleniyor...")
        self.lbl_result.get_style_context().remove_class("error")
        btn.set_sensitive(False)
        self.progress.set_fraction(0)

        thread = threading.Thread(target=self.clean_thread, args=(selected_keys, btn))
        thread.daemon = True
        thread.start()

    def clean_thread(self, keys, btn):
        total = len(keys)
        for idx, key in enumerate(keys):
            item = next((i for i in self.items if i.key == key), None)
            if not item:
                continue
            GLib.idle_add(self.progress.set_fraction, idx / total)
            GLib.idle_add(self.lbl_result.set_label, f"{item.name} temizleniyor...")

            err = item.clean()
            if err:
                self.errors.append(f"{item.name}: {err}")

        GLib.idle_add(self.progress.set_fraction, 1)
        self.total_after = 0
        for key in keys:
            item = next((i for i in self.items if i.key == key), None)
            if item:
                self.total_after += item.get_size()

        freed = self.total_before - self.total_after
        GLib.idle_add(self.lbl_after.set_label, f"Sonra: {format_bytes(self.total_after)}")

        if self.errors:
            GLib.idle_add(self.lbl_result.set_label, f"{format_bytes(freed)} boşaltıldı ({len(self.errors)} hata)")
            GLib.idle_add(self.lbl_result.get_style_context().add_class, "error")
            GLib.idle_add(self.error_label.set_text, "\n".join(self.errors[:3]))
            GLib.idle_add(self.error_label.set_visible, True)
        else:
            GLib.idle_add(self.lbl_result.set_label, f"{format_bytes(freed)} boşaltıldı")

        GLib.idle_add(btn.set_sensitive, True)

        for key in keys:
            item = next((i for i in self.items if i.key == key), None)
            if not item:
                continue
            row_idx = [i.key for i in self._visible_items()].index(key)
            row = self.listbox.get_row_at_index(row_idx)
            if row:
                hbox = row.get_child()
                labels = [c for c in hbox.get_children() if isinstance(c, Gtk.Label)]
                if labels:
                    labels[0].set_text(self.get_size_str(item.dir_path))

    def run(self):
        self.build_ui()
        self.win.show_all()
        Gtk.main()


if __name__ == "__main__":
    PardusCleaner().run()
