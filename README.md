# 📚 libro.fm-backup-creator

A **Python 3.11** tool to create a **local backup of your Libro.fm audiobook library** using your existing browser login session.

This project:
- Exports your Libro.fm library as CSV
- Discovers download links for each book
- Downloads all audiobook ZIP files
- Extracts and cleans up the audio files
- Organizes everything by **Author / Title**

⚠️ **For personal backups only.** Respect Libro.fm’s terms of service.

---

## Features

- Automatically detects Libro.fm login cookies from your browser
- Downloads **all purchased audiobooks**
- Extracts ZIP archives into playable audio files
- Renames files to remove redundant prefixes
- Simple, single-command execution
- No virtual environment required

---

## Requirements

- **Python 3.11.5+**
- A browser you have logged into **https://libro.fm/**
- Supported browsers (via `browser_cookie3`):
  - Firefox
  - Chrome / Chromium
  - Edge
  - Etc...

---

## Installation

1. **Clone the repository**
    ```bash
   git clone https://github.com/V-Karch/libro.fm-backup-creator.git
   cd libro.fm-backup-creator

2. **Install dependencies**
    ```bash
    pip install -r requirements.txt

## Authentication (Important)

This project **does not ask for your username or password**.

Instead, it:
- Reads your existing **Libro.fm session cookies**
- Automatically finds them using `browser_cookie3`

### Before running:
1. Open your browser
2. Log in to **https://libro.fm/**
3. Make sure the login is recent

If no cookies are found, the program will stop with a clear error message.

---

## Usage

Run the program:

```bash 
python main.py
```

## Output Structure

By default, output is saved in the following manner:
```bash
library_out/
└── Author Name/
    └── Book Title/
        ├── 01 Chapter Title.mp3
        ├── 02 Chapter Title.mp3
        └── ...
```

You can change the output directory by modifying the call to:
```py
library.backup("your_output_directory")
```

