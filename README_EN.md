# ORC Screenshot Tool

[中文文档](README.md) | English

A lightweight Windows desktop screenshot tool with built-in OCR text recognition and multi-language translation. Capture screenshots, automatically recognize text, and translate — ideal for reading foreign-language interfaces, documents, and code comments.

## Features

- **Hotkey Capture** — Global hotkey `Ctrl+Shift+A`, supports full-screen and region selection, multi-monitor support
- **Local OCR** — Powered by RapidOCR (PaddleOCR v4), recognizes Chinese and English text offline
- **Auto Translation** — Automatically translates via Google Translate after OCR, supports Chinese/English/Japanese/Korean/French/German/Spanish/Russian and more
- **Screenshot Encryption** — Screenshots saved in XOR-encrypted format, key bound to local machine
- **Clipboard Integration** — Screenshots auto-copied to clipboard, OCR text and translations one-click copy
- **System Tray** — Runs minimized in the system tray, no taskbar clutter

## Requirements

- Windows 10 / 11
- Python 3.12+ (only needed to run from source)

## Quick Start

### Using the Pre-built EXE (Recommended)

Double-click `ORC_Screenshot_Tool_v1.0.4.exe` to run — no Python installation required.

> Windows SmartScreen may show an "Unknown Publisher" warning on first launch. Click "More info" → "Run anyway".

### Running from Source

```bash
# Clone the repository
git clone https://github.com/sundent1235/ORC.git
cd ORC

# Install dependencies
pip install -r requirements.txt

# Run
python main.py
```

### Building the EXE Yourself

```bash
pip install pyinstaller

# Single-file mode (for distribution, outputs a single EXE)
pyinstaller ORC.spec

# Directory mode (for development/debugging, faster startup)
pyinstaller ORC-dir.spec
```

- Single file: `dist/ORC截图工具.exe`
- Directory mode: `dist/ORC截图工具_dev/ORC截图工具_dev.exe`

## Project Structure

```
ORC/
├── main.py               # Entry point
├── requirements.txt       # Dependencies
├── ORC.spec              # PyInstaller single-file build config
├── ORC-dir.spec          # PyInstaller directory-mode build config
├── assets/               # Icon resources
│   ├── generate_icon.py  # Icon generation script (PIL)
│   ├── icon.ico          # Multi-size ICO (embedded in EXE)
│   └── icon.png          # 256×256 PNG (loaded at runtime)
├── core/                 # Core modules
│   ├── hotkey.py         # Native Windows hotkey (RegisterHotKey API)
│   ├── ocr_engine.py     # RapidOCR (PaddleOCR v4) OCR engine
│   ├── screenshot.py     # Screenshot management + XOR encryption
│   └── translator.py     # Google Translate module
├── ui/                   # UI modules
│   ├── main_window.py    # Screenshot region selection window
│   ├── ocr_dialog.py     # OCR result dialog (preview + recognition + translation)
│   └── tray_icon.py      # System tray icon + context menu
└── utils/                # Utility modules
    ├── clipboard.py      # Clipboard operations
    └── config.py         # JSON config management
```

## Configuration

Config file located at `~/.orc_screenshot/config.json`, created automatically on first run:

```json
{
    "hotkey_screenshot": "ctrl+shift+a",
    "save_dir": "~/Pictures/Screenshots",
    "source_lang": "auto",
    "target_lang": "zh-CN",
    "auto_copy_clipboard": true,
    "image_format": "PNG",
    "show_tray": true,
    "encrypt_screenshots": true,
    "hide_screenshot_folder": true
}
```

## Tech Stack

| Component | Purpose |
|-----------|---------|
| PyQt5 | GUI framework |
| mss | Screen capture |
| RapidOCR (PaddleOCR v4) | Local OCR recognition |
| deep-translator | Google Translate API |
| Pillow | Image processing |
| truststore | Windows system SSL certificates |
| PyInstaller | Package as EXE |

## Known Issues

- Translation requires internet access; OCR text is sent to Google servers via HTTP. Be mindful of privacy if screenshots contain sensitive information.
- The EXE is not code-signed; Windows SmartScreen will show an "Unknown Publisher" warning.
- Encrypted screenshots use a machine-bound key and can only be decrypted on the same machine. Disable encryption or manually decrypt before transferring to another computer.

## Changelog

See [CHANGELOG.md](CHANGELOG.md)
