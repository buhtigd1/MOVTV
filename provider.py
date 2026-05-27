import requests
import re

SOURCE_URL = "https://raw.githubusercontent.com/apistech/project/refs/heads/main/IndihomeTV.m3u"
OUTPUT_FILE = "movies.m3u"

def main():
    r = requests.get(SOURCE_URL, timeout=30)
    r.raise_for_status()
    content = r.text

    lines = content.splitlines()
    entries = []

    i = 0
    while i < len(lines):
        if lines[i].startswith("#EXTINF"):
            extinf = lines[i]
            j = i + 1

            while j < len(lines) and lines[j].startswith("#"):
                j += 1

            if j < len(lines):
                url = lines[j]
                entries.append((extinf, url))

            i = j
        else:
            i += 1

    movies = []
    for e, u in entries:
        m = re.search(r'group-title="([^"]+)"', e, re.IGNORECASE)
        if m and "movie" in m.group(1).lower():
            movies.append((e, u))

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for e, u in movies:
            f.write(f"{e}\n{u}\n")

    print(f"Saved {len(movies)} movie channels")

if __name__ == "__main__":
    main()
