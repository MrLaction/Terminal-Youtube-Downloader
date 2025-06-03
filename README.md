# The Pepe's Pirate Ship: YouTube ➜ MP4 (Audio + Video)

This program allows you to download YouTube videos in MP4 format, selecting from available quality options, and automatically merging audio and video when needed. It uses the `yt-dlp` library and requires `ffmpeg` to be installed on your system.

---

## Features

- Download YouTube videos in MP4 format.
- Choose from available resolutions and formats.
- Automatically merges video and audio if they are separate.
- Works on Windows, macOS, Linux, and Termux (Android).

---

## Requirements

- Python 3.7 or higher
- `ffmpeg` installed on the system (required to merge audio and video)
- The `ASCII.txt` file in the same directory as the script (optional, used for intro display)

---

## Installation and Execution

### Windows

1. Install Python from [https://www.python.org](https://www.python.org).
2. Install `ffmpeg`:
   - Using Chocolatey:
     ```bash
     choco install ffmpeg
     ```
   - Or download it manually from [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)
3. Open a terminal (CMD or PowerShell) and run:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   pip install -r requirements.txt
   python Main.py
   ```

---

### macOS

1. Make sure Python 3 is installed.
2. Install `ffmpeg`:
   ```bash
   brew install ffmpeg
   ```
3. In the terminal, run:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   python3 Main.py
   ```

---

### Linux (Debian/Ubuntu)

1. Install dependencies:
   ```bash
   sudo apt update
   sudo apt install python3 python3-venv ffmpeg
   ```
2. Then run:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   python3 Main.py
   ```

---

### Termux (Android)

1. Open Termux and run:
   ```bash
   pkg update
   pkg install python ffmpeg
   pip install --upgrade pip
   pip install yt-dlp
   ```
2. Download `Main.py` and `ASCII.txt` into the same directory.
3. Execute:
   ```bash
   python Main.py
   ```

---

## Additional Notes

- If `ASCII.txt` is missing, the program will still work but the visual intro will not be shown.
- You can exit the program by typing `Exit` when prompted for a URL.
- An internet connection is required.
- **Occasionally a video format may not appear in the list on the first attempt** (for example, due to temporary YouTube CDN or network hiccups). If you don’t see the expected formats, simply restart the program and try the same URL again. In most cases, the missing format will reappear on a second attempt.

---

## By: The Pepe's Pirate Ship Crew  
Contributions are welcome.
