import requests
import re

# ✅ SOURCES
SOURCE1_URL = "https://raw.githubusercontent.com/apistech/project/refs/heads/main/IndihomeTV.m3u"
SOURCE2_URL = "https://raw.githubusercontent.com/TakaMn/TakashiM3u/main/cignal.m3u"

OUTPUT_FILE = "movies.m3u"

HEADER = '#EXTM3U url-tvg="https://bit.ly/4a2SXO3" $BorpasFileFormat="1" refresh="720"'

# ✅ Allowed SOURCE2 channels
SOURCE2_ALLOWED = [
    "tap movies","hbo","hbo hits","hbo family","hbo signature",
    "cinemax","axn","warner tv",
    "rock action","rock entertainment",
    "hits hd","hits now","hits movies",
    "dreamworks"
]

# ✅ TVG-ID MAP
TVG_MAP = {
    "hbo": 'tvg-id="HBOAsia.sg@SD"',
    "hbo family": 'tvg-id="HBOFamilyAsia.sg@SD"',
    "hbo hits": 'tvg-id="HBOHitsAsia.sg@SD"',
    "hbo signature": 'tvg-id="HBOSignatureAsia.sg@SD"',
    "cinemax": 'tvg-id="CinemaxAsia.sg@SD"',
    "axn": 'tvg-id="AXNAsia.sg@SD"',
    "warner tv": 'tvg-id="WarnerTVAsia.sg@SD"',
    "tap movies": 'tvg-id="TapMoviesAsia.sg@SD"',
    "rock action": 'tvg-id="RockActionAsia.sg@SD"',
    "rock entertainment": 'tvg-id="RockEntertainmentAsia.sg@SD"',
    "hits now": 'tvg-id="HitsNowAsia.sg@SD"',
    "hits movies": 'tvg-id="HitsMoviesAsia.sg@SD"',
    "hits hd": 'tvg-id="HitsAsia.sg@SD"',
    "dreamworks": 'tvg-id="DreamWorksAsia.sg@SD"',
}

# ✅ Parse M3U as blocks
def parse_m3u(content):
    lines = content.splitlines()
    entries = []
    i = 0

    while i < len(lines):
        if lines[i].startswith("#EXTINF"):
            block = [lines[i]]
            j = i + 1

            while j < len(lines):
                line = lines[j]
                block.append(line)

                if not line.startswith("#"):
                    break
                j += 1

            entries.append(block)
            i = j + 1
        else:
            i += 1

    return entries


# ✅ Source1 = Movies only
def filter_source1(entries):
    result = []
    for block in entries:
        m = re.search(r'group-title="([^"]+)"', block[0], re.IGNORECASE)
        if m and "movie" in m.group(1).lower():
            result.append(block)
    return result


# ✅ Source2 = selected channels
def filter_source2(entries):
    result = []
    for block in entries:
        name = block[0].split(",", 1)[-1].lower()
        if any(ch in name for ch in SOURCE2_ALLOWED):
            result.append(block)
    return result


# ✅ REMOVE UNWANTED (KEY FIX)
def remove_unwanted(entries):
    filtered = []

    for block in entries:
        full_block_text = "\n".join(block).lower()
        name = block[0].split(",", 1)[-1].lower()

        # ❌ remove ONLY DreamWorks (Tagalized)
        if "dreamworks" in name and "tagalized" in name:
            continue

        # ❌ remove ALL Astro by URL OR name
        if "astro.com.my" in full_block_text:
            continue

        if "astro" in name:
            continue

        filtered.append(block)

    return filtered


# ✅ Inject tvg-id correctly
def inject_tvg(extinf):
    name = extinf.split(",", 1)[-1].lower().strip()

    # remove ALL existing tvg-id (including empty)
    extinf = re.sub(r'\s*tvg-id="[^"]*"', '', extinf)

    for key in sorted(TVG_MAP.keys(), key=len, reverse=True):
        if key in name:
            tvg = TVG_MAP[key]

            parts = extinf.split(",", 1)
            parts[0] = parts[0].strip() + f" {tvg}"

            return ",".join(parts)

    return extinf


# ✅ Clean EXTINF line
def clean_extinf(line):
    line = re.sub(r'\s*group-title="[^"]+"', '', line, flags=re.IGNORECASE)
    line = re.sub(r'\s+', ' ', line)
    line = re.sub(r',\s*', ',', line)
    return line.strip()


def main():
    print("Downloading sources...")

    src1 = requests.get(SOURCE1_URL, timeout=30).text
    src2 = requests.get(SOURCE2_URL, timeout=30).text

    print("Parsing...")

    src1_entries = parse_m3u(src1)
    src2_entries = parse_m3u(src2)

    print("Filtering...")

    src1_movies = filter_source1(src1_entries)
    src2_selected = filter_source2(src2_entries)

    merged = src1_movies + src2_selected

    # ✅ remove unwanted blocks (Astro + Tagalized)
    merged = remove_unwanted(merged)

    print(f"Final channels: {len(merged)}")

    # ✅ WRITE OUTPUT
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(HEADER + "\n")

        for block in merged:
            for idx, line in enumerate(block):

                if idx == 0:
                    line = clean_extinf(line)
                    line = inject_tvg(line)

                f.write(line.strip() + "\n")

    print("✅ DONE: movies.m3u generated successfully")


if __name__ == "__main__":
    main()
