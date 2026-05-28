import requests
import re

SOURCE1_URL = "https://raw.githubusercontent.com/apistech/project/refs/heads/main/IndihomeTV.m3u"
SOURCE2_URL = "https://raw.githubusercontent.com/TakaMn/TakashiM3u/main/cignal.m3u"

OUTPUT_FILE = "movies.m3u"

HEADER = '#EXTM3U url-tvg="https://bit.ly/4a2SXO3" $BorpasFileFormat="1"'

headers = {
    "User-Agent": "Mozilla/5.0"
}

# ✅ Allowed channels (source2)
SOURCE2_ALLOWED = [
    "tap movies","hbo","hbo hits","hbo family","hbo signature",
    "cinemax","axn","warner tv",
    "rock action","rock entertainment",
    "hits hd","hits now","hits movies",
    "dreamworks"
]

# ✅ FULL TVG MAP (expanded)
TVG_MAP = {
    # premium
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

    # ✅ source1 additions
    "ccm": 'tvg-id="CCMAsia.sg@SD"',
    "celestial movies": 'tvg-id="CelestialMoviesAsia.sg@SD"',
    "galaxy premium": 'tvg-id="GalaxyPremiumAsia.sg@SD"',
    "galaxy": 'tvg-id="GalaxyAsia.sg@SD"',
    "imc": 'tvg-id="IMCAsia.sg@SD"',
    "thrill": 'tvg-id="ThrillAsia.sg@SD"',
    "studio universal": 'tvg-id="StudioUniversalAsia.sg@SD"',
    "tvn movies": 'tvg-id="tvNMoviesAsia.sg@SD"',
    "zee bioskop": 'tvg-id="ZeeBioskopAsia.sg@SD"',
    "my cinema europe": 'tvg-id="MyCinemaEurope.uk@SD"',
    "wedotv movies": 'tvg-id="WeDoTVMovies.de@SD"',
}

# ✅ LOGO REPLACEMENT
LOGO_MAP = {
    "https://divign0fdw3sv.cloudfront.net/Images/ChannelLogo/contenthub/449_144.png":
        "https://images.now-tv.com/shares/channelPreview/img/en_hk/color/ch111_170_122",

    "https://uploads-ssl.webflow.com/64e961c3862892bff815289d/64f57100366fe5c8cb6088a7_logo_ext_web.png?fbclid=IwY2xjawGIHF9leHRuA2FlbQIxMAABHaW0_Y0A9XL4w1ZXDSwAZCAxe62ui1Oy3gU5wjykfHsZ0eCjzNxl05M0JQ_aem_NIH5vZtTty4_B8wy5fB2LA":
        "https://raw.githubusercontent.com/didikc/TV-Logo/main/logos/rockaction-ph.png",

    "https://divign0fdw3sv.cloudfront.net/Images/ChannelLogo/contenthub/450_144.png":
        "https://images.now-tv.com/shares/channelPreview/img/en_hk/color/ch112_170_122",

    "https://cdn.prod.website-files.com/67ad5259c6e804a40b4bae92/67ad5259c6e804a40b4bb0c1_logo_ent_red_web.png":
        "https://raw.githubusercontent.com/didikc/TV-Logo/main/logos/rockentertainment-ph.png",  
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


def filter_source1(entries):
    result = []
    for block in entries:
        m = re.search(r'group-title="([^"]+)"', block[0], re.IGNORECASE)
        if m and "movie" in m.group(1).lower():
            result.append(block)
    return result


def filter_source2(entries):
    result = []
    for block in entries:
        name = block[0].split(",", 1)[-1].strip().lower()

        if any(name.startswith(ch) for ch in SOURCE2_ALLOWED):
            result.append(block)
    return result


def remove_unwanted(entries):
    filtered = []

    for block in entries:
        full = "\n".join(block).lower()
        name = block[0].split(",", 1)[-1].lower()

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


def dedupe(entries):
    seen = set()
    result = []

    for block in entries:
        name = block[0].split(",", 1)[-1].strip().lower()
        if name not in seen:
            seen.add(name)
            result.append(block)

    return result


def inject_tvg(extinf):
    name = extinf.split(",", 1)[-1].strip()
    name_lower = name.lower()

    # remove old tvg-id
    extinf = re.sub(r'\s*tvg-id="[^"]*"', '', extinf)

    # match known
    for key in sorted(TVG_MAP.keys(), key=len, reverse=True):
        if name_lower.startswith(key):
            parts = extinf.split(",", 1)
            parts[0] += " " + TVG_MAP[key]
            return ",".join(parts)

    # ✅ fallback auto id
    slug = re.sub(r'[^a-z0-9]+', '', name_lower)
    parts = extinf.split(",", 1)
    parts[0] += f' tvg-id="{slug}.auto"'
    return ",".join(parts)


def replace_logo(line):
    for old, new in LOGO_MAP.items():
        if old in line:
            line = line.replace(old, new)
    return line


def clean_extinf(line):
    line = re.sub(r'\s*group-title="[^"]+"', '', line)
    line = replace_logo(line)
    line = re.sub(r'\s+', ' ', line)
    return line.strip()


# -----------------------------

def main():
    print("Downloading...")

    src1 = requests.get(SOURCE1_URL, headers=headers, timeout=10).text
    src2 = requests.get(SOURCE2_URL, headers=headers, timeout=10).text

    print("Parsing...")

    s1 = parse_m3u(src1)
    s2 = parse_m3u(src2)

    print("Filtering...")

    s1 = filter_source1(s1)
    s2 = filter_source2(s2)

    merged = s1 + s2
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
