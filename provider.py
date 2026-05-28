import requests
import re

# ✅ Sources
SOURCE1_URL = "https://raw.githubusercontent.com/apistech/project/refs/heads/main/IndihomeTV.m3u"
SOURCE2_URL = "https://raw.githubusercontent.com/TakaMn/TakashiM3u/main/cignal.m3u"
SOURCE3_URL = "https://raw.githubusercontent.com/buhtigd1/PTV2/main/pluto_us.m3u"

OUTPUT_FILE = "movies.m3u"

HEADER = '#EXTM3U url-tvg="https://bit.ly/4a2SXO3,https://github.com/matthuisman/i.mjh.nz/raw/master/PlutoTV/us.xml.gz" $BorpasFileFormat="1" $NestedGroupsSeparator="/" refresh="720"'

# ✅ Allowed Source 2 channels
CIGNAL_ALLOWED = [
    "tap movies",
    "hbo","hbo hits","hbo family","hbo signature","cinemax",
    "axn","warner tv",
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
    "axn": 'tvg-id="AXNAsia.sg@Singapore"',
    "warner tv": 'tvg-id=""',
    "tap movies": 'tvg-id=""',
    "rock action": 'tvg-id="ROCKAction.sg@SD"',
    "rock entertainment": 'tvg-id="ROCKEntertainment.sg@SD"',
    "hits now": 'tvg-id="HITSNOW.sg@SD"',
    "hits movies": 'tvg-id="HITSMovies.sg@SD"',
    "hits hd": 'tvg-id="HITS.sg@SD"',
}

def download(url):
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        return r.text
    except requests.RequestException as e:
        print(f"❌ Failed: {url}\n{e}")
        return ""

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

# ✅ Source 1 filter
def filter_source1(entries):
    result = []
    for block in entries:
        m = re.search(r'group-title="([^"]+)"', block[0], re.IGNORECASE)
        if m and "movie" in m.group(1).lower():
            result.append(block)
    return result

# ✅ Source 2 filter
def filter_source2(entries):
    result = []
    for block in entries:
        name = block[0].split(",", 1)[-1].lower().strip()
        if any(ch in name for ch in CIGNAL_ALLOWED):
            result.append(block)
    return result

# ✅ Source 3 filter (Pluto Movies only)
def filter_source3(entries):
    result = []
    for block in entries:
        m = re.search(r'group-title="([^"]+)"', block[0], re.IGNORECASE)
        if m and m.group(1).strip().lower() == "movies":
            result.append(block)
    return result

# ✅ Remove bad streams
def is_block_allowed(block):
    url = block[-1].lower() if block else ""

    if "136.239." in url or ":6610" in url or "zte.com" in url:
        return False

    if "linearjitp-playback.astro.com.my" in url:
        return False

    return True

# ✅ Remove DreamWorks Tagalized
def remove_tagalized(block):
    name = block[0].split(",", 1)[-1].lower()
    if "dreamworks" in name and any(x in name for x in ["tagalized", "tagalog", "tag dub"]):
        return False
    return True

# ✅ Inject tvg-id
def inject_tvg(extinf):
    name = extinf.split(",", 1)[-1].lower().strip()

    extinf = re.sub(r'\s*tvg-id=""', '', extinf)

    if 'tvg-id="' in extinf:
        return extinf

    for key in sorted(TVG_MAP.keys(), key=len, reverse=True):
        if key in name:
            tvg = TVG_MAP[key]
            extinf = extinf.replace("#EXTINF:-1", f"#EXTINF:-1 {tvg}")
            break

    return extinf

def clean_extinf(line):
    return re.sub(r'\s*group-title="[^"]+"', '', line, flags=re.IGNORECASE)

def main():
    print("Downloading...")

    source1 = download(SOURCE1_URL)
    source2 = download(SOURCE2_URL)
    source3 = download(SOURCE3_URL)

    print("Parsing...")

    entries1 = parse_m3u(source1)
    entries2 = parse_m3u(source2)
    entries3 = parse_m3u(source3)

    print("Filtering...")

    filtered1 = filter_source1(entries1)
    filtered2 = filter_source2(entries2)
    filtered3 = filter_source3(entries3)

    merged = []

    for block in filtered1 + filtered2 + filtered3:
        if is_block_allowed(block) and remove_tagalized(block):
            merged.append(block)

    print(f"Total channels: {len(merged)}")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(HEADER + "\n")

        for block in merged:
            for idx, line in enumerate(block):

                # ✅ replacements
                line = line.replace("cg_hitsnow", "HITSNOW.sg@SD")
                line = line.replace("https://divign0fdw3sv.cloudfront.net/Images/ChannelLogo/contenthub/449_144.png", "https://images.now-tv.com/shares/channelPreview/img/en_hk/color/ch111_170_122")
                line = line.replace("https://uploads-ssl.webflow.com/64e961c3862892bff815289d/64f57100366fe5c8cb6088a7_logo_ext_web.png?fbclid=IwY2xjawGIHF9leHRuA2FlbQIxMAABHaW0_Y0A9XL4w1ZXDSwAZCAxe62ui1Oy3gU5wjykfHsZ0eCjzNxl05M0JQ_aem_NIH5vZtTty4_B8wy5fB2LA", "https://raw.githubusercontent.com/didikc/TV-Logo/main/logos/rockaction-ph.png")
                line = line.replace("https://divign0fdw3sv.cloudfront.net/Images/ChannelLogo/contenthub/450_144.png", "https://images.now-tv.com/shares/channelPreview/img/en_hk/color/ch112_170_122")
                line = line.replace("https://cdn.prod.website-files.com/67ad5259c6e804a40b4bae92/67ad5259c6e804a40b4bb0c1_logo_ent_red_web.png", "https://raw.githubusercontent.com/didikc/TV-Logo/main/logos/rockentertainment-ph.png")
                line = line.replace("https://i.imgur.com/t4HF5va.png", "https://images.now-tv.com/shares/channelPreview/img/en_hk/color/ch114_170_122")
                line = line.replace("https://divign0fdw3sv.cloudfront.net/Images/ChannelLogo/contenthub/337_144.png", "https://images.now-tv.com/shares/channelPreview/img/en_hk/color/ch113_170_122")

                if idx == 0:
                    line = clean_extinf(line)
                    line = inject_tvg(line)

                f.write(line + "\n")

    print("✅ Done: movies.m3u")

if __name__ == "__main__":
    main()
