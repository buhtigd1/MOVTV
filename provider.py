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
        line = lines[i].strip()

        if line.startswith("#EXTINF"):
            block = [line]  # start full block

            j = i + 1

            # collect ALL metadata + URL
            while j < len(lines):
                next_line = lines[j].strip()

                block.append(next_line)

                # URL = first non-# line
                if not next_line.startswith("#"):
                    break

                j += 1

            entries.append(block)
            i = j
        else:
            i += 1

    # ✅ filter Movies
    movies = []
    for block in entries:
        extinf = block[0]

        m = re.search(r'group-title="([^"]+)"', extinf, re.IGNORECASE)
        if m and "movie" in m.group(1).lower():
            movies.append(block)

    # ✅ write FULL blocks (with VLCOPT + KODIPROP preserved)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for block in movies:
            for line in block:
                f.write(line + "\n")

    print(f"Saved {len(movies)} movie channels (with metadata intact)")

if __name__ == "__main__":
    main()
