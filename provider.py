import requests
import re

SOURCE_URL = "https://raw.githubusercontent.com/apistech/project/refs/heads/main/IndihomeTV.m3u"
OUTPUT_FILE = "moviestv.m3u"

def download_m3u(url):
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.text

def extract_entries(m3u_text):
    lines = m3u_text.splitlines()
    entries = []

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        if line.startswith("#EXTINF"):
            extinf = line
            stream_url = ""

            j = i + 1
            while j < len(lines):
                next_line = lines[j].strip()

                # skip metadata lines
                if next_line.startswith("#"):
                    j += 1
                    continue
                else:
                    stream_url = next_line
                    break

            entries.append((extinf, stream_url))
            i = j
        else:
            i += 1

    return entries

def filter_movies(entries):
    movies = []

    for extinf, url in entries:
        match = re.search(r'group-title="([^"]+)"', extinf, re.IGNORECASE)

        if match and match.group(1).lower() == "movies":
            movies.append((extinf, url))

    return movies

def save_m3u(entries, file_path):
    with open(file_path, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for extinf, url in entries:
            f.write(f"{extinf}\n{url}\n")

def main():
    print("Downloading playlist...")
    content = download_m3u(SOURCE_URL)

    print("Parsing entries...")
    entries = extract_entries(content)

    print(f"Total entries: {len(entries)}")

    movies = filter_movies(entries)

    print(f'Movie group ("Movies") entries: {len(movies)}')

    save_m3u(movies, OUTPUT_FILE)

    print(f"Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
