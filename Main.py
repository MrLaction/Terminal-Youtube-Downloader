import os
import re
import sys
from yt_dlp import YoutubeDL


def intro():
    try:
        with open("ASCII.txt", "r", encoding="utf-8") as f:
            print(f.read())
        print("\nWelcome to The Pepe's Pirate Ship YouTube ➜ MP4 (Audio + Video)\n")
    except FileNotFoundError:
        print("ASCII.txt file not found")


# 1) URL Validator
def validate_url(url):
    pattern = r'^(https?\:\/\/)?(www\.)?(youtube\.com|youtu\.be)\/.+$'
    return bool(re.match(pattern, url))


# 2) Extract info (without downloading) and return list of formats
def get_formats(url):
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
    }
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return info.get('formats', []), info.get('title', 'video')
    except Exception as e:
        print(f"Error extracting video information: {e}")
        return [], None


# 3) Show available qualities (only video and video+audio mp4/webm) and return a dict mapping option→format_id
def show_qualities(formats):
    print("\nAvailable formats (video only / video+audio):")
    options = {}
    index = 1

    # Filter:
    # - formats with video (vcodec != 'none')
    # - ext is mp4 or webm
    filtered = [f for f in formats if f.get('vcodec') != 'none' and f.get('ext') in ('mp4', 'webm')]
    # Sort by descending resolution (if available), then fps
    filtered.sort(key=lambda x: (
        int(x.get('height') or 0),
        int(x.get('fps') or 0)
    ), reverse=True)

    seen = set()
    for fmt in filtered:
        # Avoid duplicate resolution+fps+ext
        key_repr = f"{fmt.get('height')}x{fmt.get('fps')} {fmt.get('ext')} {fmt.get('acodec') != 'none'}"
        if key_repr in seen:
            continue
        seen.add(key_repr)

        # Show useful info:
        res = fmt.get('resolution') or f"{fmt.get('width')}x{fmt.get('height')}"
        fps = fmt.get('fps') or '-'
        ext = fmt.get('ext')
        has_audio = (fmt.get('acodec') != 'none')
        size_mb = None
        if fmt.get('filesize') or fmt.get('filesize_approx'):
            size = fmt.get('filesize') or fmt.get('filesize_approx')
            size_mb = round(size / (1024*1024), 1)
        size_str = f"{size_mb} MB" if size_mb else "—"

        tag = fmt.get('format_id')
        options[str(index)] = fmt
        print(f"{index}. [{tag}] {res} | fps: {fps} | ext: {ext} | {'with audio' if has_audio else 'video only'} | {size_str}")
        index += 1

    if not options:
        print("   (No mp4 or webm video formats found.)")
    return options


# New function to sanitize the title and remove invalid filename characters
def sanitize_filename(title):
    """
    Replace all invalid filename characters with underscores (_).
    Keeps letters, numbers, hyphens, and underscores; everything else becomes '_'.
    """
    return re.sub(r'[^0-9A-Za-z_\-]', '_', title)


# 4) Function to download selected format (and merge with audio if needed)
def download_with_yt_dlp(url, selected_format, title):
    fmt_id = selected_format.get('format_id')
    has_audio = selected_format.get('acodec') != 'none'

    if has_audio:
        format_str = fmt_id
    else:
        # If video-only, request best available audio in m4a to merge later
        format_str = f"{fmt_id}+bestaudio[ext=m4a]/best[ext=m4a]/bestaudio"

    # Output folder = current directory
    output_dir = os.getcwd()
    # Clean title to avoid problematic characters
    base = sanitize_filename(title)
    out_template = os.path.join(output_dir, f"{base}.%(ext)s")

    # Config options
    ydl_opts = {
        'format': format_str,
        'merge_output_format': 'mp4',    # force mp4 output
        'outtmpl': out_template,         # save in cwd with clean name
        'quiet': False,                  # show progress
        'noprogress': False,
        'no_warnings': True,
        'retries': 3,                    # retry 3 times on failure
        # Headers to emulate a real browser and avoid 403
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/114.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Referer': 'https://www.youtube.com/'
        },
        'geo_bypass': True,           # try to bypass geographic restrictions
        'nocheckcertificate': True,   # ignore SSL certificate errors
        # 'cookiefile': 'cookies.txt', # Uncomment if cookies are needed for restricted videos
    }

    with YoutubeDL(ydl_opts) as ydl:
        print("\nStarting download (with browser-like headers)…")
        try:
            ydl.download([url])
            print(f"\nProcess completed. Check '{output_dir}' for the file.")
        except Exception as e:
            print(f"\nError during download: {e}")


if __name__ == "__main__":
    intro()

    # Repeat until a valid link is entered or 'Exit' is typed
    while True:
        url = input("Enter a valid YouTube link (or type 'Exit' to quit): ").strip()
        if url.lower() == "exit":
            print("Thanks for using us :).")
            sys.exit(0)
        if validate_url(url):
            break
        print("Invalid URL. Try again or type 'Exit' to quit.\n")

    # 2) Get formats without downloading (and title to name the file)
    formats, title = get_formats(url)
    if not formats or title is None:
        print("Could not retrieve video information. Exiting.")
        sys.exit(1)

    # 3) Show quality menu
    options = show_qualities(formats)
    if not options:
        print("No video formats available for this link.")
        sys.exit(1)

    choice = input("\nChoose the desired option (number): ").strip()
    selected = options.get(choice)
    if not selected:
        print("Invalid option. Exiting.")
        sys.exit(1)

    # 4) Download
    download_with_yt_dlp(url, selected, title)
