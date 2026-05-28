import requests
import re

# ✅ SOURCES
SOURCE_1_URL = "https://raw.githubusercontent.com/apistech/project/refs/heads/main/IndihomeTV.m3u"
SOURCE_2_URL = "https://github.com/TakaMn/TakashiM3u/blob/main/cignal.m3u"

OUTPUT_FILE = "movies.m3u"

HEADER = '#EXTM3U url-tvg="https://bit.ly/4a2SXO3" $BorpasFileFormat="1" $NestedGroupsSeparator="/"'

# ✅ Fetch playlist
def fetch_playlist(url):
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        return r.text.splitlines()
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return []

# ✅ Extract channel blocks
def extract_entries(lines):
    entries = []
    i = 0

    while i < len(lines):
        line = lines[i].strip()

        if line.startswith("#EXTINF"):
            block = [line]
            j = i + 1

            while j < len(lines):
                next_line = lines[j].strip()
                block.append(next_line)

                if not next_line.startswith("#"):
                    break
                j += 1

            entries.append(block)
            i = j
        else:
            i += 1

    return entries

# ✅ Check movie group
def is_movie(block):
    extinf = block[0]
    m = re.search(r'group-title="([^"]+)"', extinf, re.IGNORECASE)
    return m and "movie" in m.group(1).lower()

# ✅ Clean EXTINF (remove group-title)
def clean_block(block):
    cleaned = []
    for idx, line in enumerate(block):
        if idx == 0:
            line = re.sub(r'\s*group-title="[^"]+"', '', line)
        cleaned.append(line)
    return cleaned

# ✅ Filter SOURCE 2 (ZTE + Astro removal)
def is_valid_source2(block):
    extinf = block[0].lower()
    url = block[-1].lower() if block else ""

    # ❌ Remove Astro
    if "astro" in extinf:
        return False
    if "linearjitp-playback.astro.com.my" in url:
        return False

    # ❌ Remove Any
    if (
        "136.239.158.10:6610" in url
    ):
        return False

    return True

def main():
    # ✅ Load sources
    lines1 = fetch_playlist(SOURCE_1_URL)
    lines2 = fetch_playlist(SOURCE_2_URL)

    entries1 = extract_entries(lines1)
    entries2 = extract_entries(lines2)

    merged = []

    # ✅ SOURCE 1 → movies only
    for block in entries1:
        if is_movie(block):
            merged.append(clean_block(block))

    # ✅ SOURCE 2 → filtered + movies only
    for block in entries2:
        if is_valid_source2(block) and is_movie(block):
            merged.append(clean_block(block))

    # ✅ NO DEDUPLICATION (duplicates kept)

    # ✅ Write output
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(HEADER + "\n")
        for block in merged:
            for line in block:
                f.write(line + "\n")

    print(f"✅ Saved {len(merged)} movie channels (duplicates kept)")

if __name__ == "__main__":
    main()
