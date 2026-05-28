import requests
import re

# ✅ SOURCES
SOURCE1_URL = "https://raw.githubusercontent.com/apistech/project/refs/heads/main/IndihomeTV.m3u"
SOURCE2_URL = "https://raw.githubusercontent.com/TakaMn/TakashiM3u/main/cignal.m3u"

OUTPUT_FILE = "movies.m3u"

HEADER = '#EXTM3U url-tvg="https://bit.ly/4a2SXO3" $BorpasFileFormat="1"'
HEADERS = {"User-Agent": "Mozilla/5.0"}


# ✅ Allowed channels (Source2 / Cignal)
SOURCE2_ALLOWED = [
    "hbo",
    "hbo hits",
    "hbo family",
    "hbo signature",
    "cinemax",
    "axn",
    "warner",
    "tap movies",
    "rock action",
    "rock entertainment",
    "hits",
    "dreamworks"
]


# ✅ TVG MAP
TVG_MAP = {
    # Premium
    "hbo": 'tvg-id="HBOAsia.sg@SD"',
    "hbo family": 'tvg-id="HBOFamilyAsia.sg@SD"',
    "hbo hits": 'tvg-id="HBOHitsAsia.sg@SD"',
    "hbo signature": 'tvg-id="HBOSignatureAsia.sg@SD"',
    "cinemax": 'tvg-id="CinemaxAsia.sg@SD"',
    "axn": 'tvg-id="AXNAsia.sg@SD"',
    "warner": 'tvg-id="WarnerTVAsia.sg@SD"',
    "tap movies": 'tvg-id="TapMoviesAsia.sg@SD"',
    "rock action": 'tvg-id="RockActionAsia.sg@SD"',
    "rock entertainment": 'tvg-id="RockEntertainmentAsia.sg@SD"',
    "hits movies": 'tvg-id="HitsMoviesAsia.sg@SD"',
    "hits": 'tvg-id="HitsAsia.sg@SD"',
    "dreamworks": 'tvg-id="DreamWorksAsia.sg@SD"',

    # Source1 (Indihome)
    "ccm": 'tvg-id="CelestialClassicMovies.id@SD"',
    "celestial movies": 'tvg-id="CelestialMoviesIndonesia.id@SD"',
    "galaxy premium": 'tvg-id="GalaxyPremium.id@SD"',
    "galaxy": 'tvg-id="Galaxy.id@SD"',
    "imc": 'tvg-id="IMC.id@SD"',
    "thrill": 'tvg-id="Thrill.hk@SD"',
    "studio universal": 'tvg-id="StudioUniversalLatinAmerica.us@Brazil"',
    "tvn movies": 'tvg-id="tvNMoviesAsia.hk@SD"',
    "zee bioskop": 'tvg-id="ZeeBioskop.id@SD"',
    "my cinema europe": 'tvg-id="MyCinemaEurope.ch@SD"',
    "wedotv movies": 'tvg-id="WeDoTVMovies.de@SD"',
}


# -----------------------------

def parse_m3u(content):
    lines = content.splitlines()
    entries = []
    i = 0

    while i < len(lines):
        if lines[i].startswith("#EXTINF"):
            block = [lines[i]]
            j = i + 1

            while j < len(lines):
                block.append(lines[j])
                if not lines[j].startswith("#"):
                    break
                j += 1

            entries.append(block)
            i = j + 1
        else:
            i += 1

    return entries


# ✅ Filter Source1 (Indihome → Movie group only)
def filter_source1(entries):
    result = []
    for block in entries:
        m = re.search(r'group-title="([^"]+)"', block[0], re.IGNORECASE)
        if m and "movie" in m.group(1).lower():
            result.append(block)
    return result


# ✅ Filter Source2 (Cignal → allowed channels)
def filter_source2(entries):
    result = []
    for block in entries:
        name = block[0].split(",", 1)[-1].strip().lower()

        if any(re.search(rf'\b{re.escape(ch)}\b', name) for ch in SOURCE2_ALLOWED):
            result.append(block)

    return result


# ✅ Remove unwanted
def remove_unwanted(entries):
    filtered = []

    for block in entries:
        full = "\n".join(block).lower()

        if "tagalized" in full:
            continue
        if "astro" in full:
            continue
        if "136.239." in full:
            continue
        if any(x in full for x in ["test", "backup", "offline"]):
            continue

        filtered.append(block)

    return filtered


# ✅ Deduplicate by channel name
def dedupe(entries):
    seen = set()
    result = []

    for block in entries:
        name = block[0].split(",", 1)[-1].strip().lower()

        if name not in seen:
            seen.add(name)
            result.append(block)

    return result


# ✅ Inject TVG-ID
def inject_tvg(extinf):
    name = extinf.split(",", 1)[-1].strip()
    lower = name.lower()

    extinf = re.sub(r'\s*tvg-id="[^"]*"', '', extinf)

    for key in sorted(TVG_MAP.keys(), key=len, reverse=True):
        if re.search(rf'\b{re.escape(key)}\b', lower):
            parts = extinf.split(",", 1)
            parts[0] += " " + TVG_MAP[key]
            return ",".join(parts)

    # fallback
    slug = re.sub(r'[^a-z0-9]+', '', lower)
    parts = extinf.split(",", 1)
    parts[0] += f' tvg-id="{slug}.auto"'
    return ",".join(parts)


# ✅ Clean EXTINF
def clean_extinf(line):
    line = re.sub(r'\s*group-title="[^"]+"', '', line)
    line = re.sub(r'\s+', ' ', line)
    return line.strip()


# -----------------------------

def main():
    print("Downloading Source1 (Indihome)...")
    source1 = requests.get(SOURCE1_URL, headers=HEADERS, timeout=10).text

    print("Downloading Source2 (Cignal)...")
    source2 = requests.get(SOURCE2_URL, headers=HEADERS, timeout=10).text

    print("Parsing...")
    s1_entries = parse_m3u(source1)
    s2_entries = parse_m3u(source2)

    print("Filtering...")
    s1_entries = filter_source1(s1_entries)
    s2_entries = filter_source2(s2_entries)

    print(f"✅ Source1 channels: {len(s1_entries)}")
    print(f"✅ Source2 channels: {len(s2_entries)}")

    merged = s1_entries + s2_entries
    merged = remove_unwanted(merged)
    merged = dedupe(merged)

    print("Writing file...")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(HEADER + "\n")

        for block in merged:
            for i, line in enumerate(block):
                if i == 0:
                    line = clean_extinf(line)
                    line = inject_tvg(line)
                f.write(line.strip() + "\n")

    print("✅ DONE: movies.m3u created")


# -----------------------------
if __name__ == "__main__":
    main()
