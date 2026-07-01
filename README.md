# Pardus Cleaner

Pardus için geliştirilmiş disk temizleme uygulaması.

## Özellikler

- APT paket önbelleği temizleme
- Pacman önbelleği temizleme (Arch)
- Çöp kutusu temizleme
- Küçük resim önbelleği temizleme
- pip/npm önbelleği temizleme
- Firefox önbelleği temizleme
- Sistem günlükleri (journald) temizleme
- Docker kullanılmayan imageleri temizleme
- Flatpak kullanılmayan çalışma zamanları temizleme
- Snap önbelleği temizleme
- Genel uygulama önbelleği temizleme
- Otomatik dağıtım tespiti (Pardus/Debian/Ubuntu/Arch/Fedora)
- Güvenli dosya silme (shutil, shell glob yok)
- Temizlik öncesi/sonrası karşılaştırma
- Hata raporlama
- İlerleme çubuğu
- Koyu tema desteği

## Bağımlılıklar

- python3
- python-gobject (PyGObject)
- GTK 3.20+

## Kullanım

```bash
cd && git clone https://github.com/385ahmet/pardus-cleaner && cd pardus-cleaner && /usr/bin/python3 src/Main.py
```

## .deb Paketi Kurulumu

```bash
cd && git clone https://github.com/385ahmet/pardus-cleaner && cd pardus-cleaner && sudo dpkg -i pardus-cleaner_3.0.0-1_all.deb && sudo apt install -f
```
Yada Pardus ile gelen .deb yükleyiciyi kullanabilirsin.

Kurulumdan sonra menüden "Pardus Cleaner" ile çalıştırabilirsin.
