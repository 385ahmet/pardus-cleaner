# Pardus Cleaner

Pardus için geliştirilmiş bir disk temizleme uygulaması.

## Özellikler

- APT paket önbelleği temizleme
- Çöp kutusu temizleme
- Küçük resim önbelleği temizleme
- pip/npm/AUR önbelleği temizleme
- Pacman önbelleği temizleme
- Sistem günlükleri temizleme
- Firefox önbelleği temizleme
- Genel uygulama önbelleği temizleme
- Temizlik öncesi/sonrası karşılaştırma
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
cd && git clone https://github.com/385ahmet/pardus-cleaner && cd pardus-cleaner && sudo dpkg -i pardus-cleaner_1.0.0-1_all.deb
cd && cd pardus-cleaner && sudo apt install -f
```
Yada Pardus ile gelen .deb yükleyiciyi kullanabilirsin.

Kurulumdan sonra menüden "Pardus Cleaner" ile çalıştırabilirsin.
