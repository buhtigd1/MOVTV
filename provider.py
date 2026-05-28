import requests
import re

INDIHOME_URL = "https://raw.githubusercontent.com/apistech/project/refs/heads/main/IndihomeTV.m3u"
CIGNAL_URL = "https://raw.githubusercontent.com/TakaMn/TakashiM3u/main/cignal.m3u"

OUTPUT_FILE = "movies.m3u"

HEADER = '#EXTM3U url-tvg="https://bit.ly/4a2SXO3" $BorpasFileFormat="1" $NestedGroupsSeparator="/" refresh="720"'

# ✅ Allowed Cignal channels
CIGNAL_ALLOWED = [
    "tap movies","hbo","hbo hits","hbo family","hbo signature",
    "cinemax","axn","warner tv",
    "rock action","rock entertainment",
    "hits hd","hits now","hits movies",
    "dreamworks"
]

# ✅ TVG mapping
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
}

# ✅ Download safely
def download(url):
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        return r.text
    except requests.RequestException as e:
        print(f"❌ Failed to download: {url}\n{e}")
        return ""

# ✅ Parse M3U blocks
def parse_m3u(content):
    lines = content.splitlines()
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

# ✅ Filter Indihome movies
def filter_indihome(entries):
    result = []
    for block in entries:
        m = re.search(r'group-title="([^"]+)"', block[0], re.IGNORECASE)
        if m and "movie" in m.group(1).lower():
            result.append(block)
    return result

# ✅ Filter Cignal channels
def filter_cignal(entries):
    result = []
    for block in entries:
        name = block[0].split(",", 1)[-1].lower().strip()

        if any(ch in name for ch in CIGNAL_ALLOWED):
            result.append(block)

    return result

# ✅ Remove bad streams (ZTE + Astro)
def is_block_allowed(block):
    text = " ".join(block).lower()
    url = block[-1].lower() if block else ""

    # ❌ Remove ZTE streams
    if (
        "136.239." in url or
        ":6610" in url or
        "zte.com" in url
    ):
        return False

    # ❌ Remove Astro streams
    if "linearjitp-playback.astro.com.my" in url:
        return False

    return True

# ✅ Inject tvg-id
def inject_tvg(extinf):
    name = extinf.split(",", 1)[-1].lower().strip()

    for key in sorted(TVG_MAP.keys(), key=len, reverse=True):
        if key in name:
            tvg = TVG_MAP[key]

            extinf = re.sub(r'\s*tvg-id="[^"]+"', '', extinf)
            extinf = extinf.replace("#EXTINF:-1", f"#EXTINF:-1 {tvg}")
            break

    return extinf

# ✅ Remove group-title
def clean_extinf(line):
    return re.sub(r'\s*group-title="[^"]+"', '', line, flags=re.IGNORECASE)

# ✅ Main
def main():
    print("Downloading...")

    indihome = download(INDIHOME_URL)
    cignal = download(CIGNAL_URL)

    print("Parsing...")

    ind_entries = parse_m3u(indihome)
    cig_entries = parse_m3u(cignal)

    print("Filtering...")

    ind_movies = filter_indihome(ind_entries)
    cig_selected = filter_cignal(cig_entries)

    merged = []

    # ✅ Apply final filtering (ZTE + Astro removal)
    for block in ind_movies + cig_selected:
        if is_block_allowed(block):
            merged.append(block)

    print(f"Total channels: {len(merged)}")

    print("Writing file...")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(HEADER + "\n")

        for block in merged:
            for idx, line in enumerate(block):

                if idx == 0:
                    line = clean_extinf(line)
                    line = inject_tvg(line)

                f.write(line + "\n")

    print("✅ Done: movies.m3u")

if __name__ == "__main__":
    main()
