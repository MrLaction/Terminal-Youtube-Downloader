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
        # no download here, just extract info
    }
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return info.get('formats', []), info.get('title', 'video')


# 3) Show available qualities (only video and video+audio mp4/webm) and return a dict mapping option→format_id
def show_qualities(formats):
    print("\nAvailable formats (video only / video+audio):")
    options = {}
    index = 1

    # Filter:
    # - formats with video (vcodec != 'none')
    # - ext is mp4 or webm (you can add others if you want)
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


# 4) Function to download selected format (and merge with audio if needed)
def download_with_yt_dlp(url, selected_format, title):
    # If format contains audio (acodec != 'none'), just that format_id is enough.
    fmt_id = selected_format.get('format_id')
    has_audio = selected_format.get('acodec') != 'none'

    if has_audio:
        format_str = f"{fmt_id}"
    else:
        # If video-only, request best available audio in mp4 to merge later.
        format_str = f"{fmt_id}+bestaudio[ext=m4a]/best[ext=m4a]/bestaudio"

    # Output folder = current directory
    output_dir = os.getcwd()
    # Clean title to avoid weird characters
    base = title.replace(" ", "_").replace("/", "_")
    out_template = os.path.join(output_dir, f"{base}.%(ext)s")

    # Config options
    ydl_opts = {
        'format': format_str,
        'merge_output_format': 'mp4',    # force mp4 output
        'outtmpl': out_template,         # save in cwd with clean name
        'quiet': False,                  # show progress
        'noprogress': False,
        'no_warnings': True,
        'retries': 3,                   # retry 3 times on failure
    }

    with YoutubeDL(ydl_opts) as ydl:
        print("\nStarting download and possible merging...")
        ydl.download([url])
        print(f"\nProcess completed. Check '{output_dir}' for the finished file.")


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
