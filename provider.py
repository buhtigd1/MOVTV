import requests
import re

# ✅ Sources
SOURCE1_URL = "https://raw.githubusercontent.com/apistech/project/refs/heads/main/IndihomeTV.m3u"
SOURCE3_URL = "https://raw.githubusercontent.com/buhtigd1/PTV2/main/pluto_us.m3u"
SOURCE4_URL = "https://raw.githubusercontent.com/buhtigd1/PTV/main/output/plutotv_us.m3u8"

OUTPUT_FILE = "movies.m3u"

HEADER = '#EXTM3U x-tvg-url="https://bit.ly/3THSiiN,https://raw.githubusercontent.com/matthuisman/i.mjh.nz/master/PlutoTV/us.xml.gz"'

# ✅ TVG mapping (only keep what’s relevant)
TVG_MAP = {
    "wedotv movies": 'tvg-id="64257#34496"',
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

# ✅ Source 1 filter (movies + AIRTEL)
def filter_source1(entries):
    result = []
    for block in entries:
        m = re.search(r'group-title="([^"]+)"', block[0], re.IGNORECASE)
        if m:
            group = m.group(1).lower()
            if "movie" in group or "airtel" in group:
                result.append(block)
    return result

# ✅ Source 3 filter
def filter_source3(entries):
    result = []
    for block in entries:
        m = re.search(r'group-title="([^"]+)"', block[0], re.IGNORECASE)
        if m and m.group(1).strip().lower() == "movies":
            result.append(block)
    return result

# ✅ Source 4 filter
def filter_source4(entries):
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
    source3 = download(SOURCE3_URL)
    source4 = download(SOURCE4_URL)

    print("Parsing...")

    entries1 = parse_m3u(source1)
    entries3 = parse_m3u(source3)
    entries4 = parse_m3u(source4)

    print("Filtering...")

    filtered1 = filter_source1(entries1)
    filtered3 = filter_source3(entries3)
    filtered4 = filter_source4(entries4)

    merged = []
    for block in filtered1 + filtered3 + filtered4:
        if is_block_allowed(block):
            merged.append(block)

    print(f"Total channels: {len(merged)}")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(HEADER + "\n")

        # ✅ Add Channels manually at the top
        f.write('#EXTINF:-1 tvg-id="661fca34414d94009d1206ec" ')
        f.write('tvg-logo="https://raw.githubusercontent.com/didikc/TV-Logo/main/logos/miramax.jpg" ,Miramax Movies Channel\n')
        f.write('https://linear-798.frequency.stream/dist/tcltv/798/hls/master/playlist.m3u8\n')
        f.write('https://linear-798.frequency.stream/mt/plex/798/hls/master/playlist_1920x1080.m3u8\n')
        f.write('#EXTINF:-1 tvg-id="Channel4.uk@UK" ')
        f.write('tvg-logo="https://www.netplus.ch/media/image/0/square/tv-logo-channel-4.jpg.webp" ,Channel 4\n')
        f.write('#KODIPROP:inputstream.adaptive.license_type=clearkey\n')
        f.write('#KODIPROP:inputstream.adaptive.license_key=0000000000000000000000000063340a:5ce85f1aa5771900b952f0ba58857d7a\n')
        f.write('https://olsp.live.dash.c4assets.com/dash_iso_sp_tl/live/channel(c4)/manifest.mpd\n')
        f.write('#EXTINF:-1 tvg-id="Film4.uk@SD" ')
        f.write('tvg-logo="https://www.netplus.ch/media/image/0/square/tv-logo-film-4.jpg.webp" ,Film4\n')
        f.write('#KODIPROP:inputstream.adaptive.license_type=clearkey\n')
        f.write('#KODIPROP:inputstream.adaptive.license_key=0000000000000000000000000066340a:627bcdc9e9556a74b05c5d311d8d2a61\n')
        f.write('https://olsp.live.dash.c4assets.com/dash_iso_sp_tl/live/channel(f4)/manifest.mpd\n')
        f.write('#EXTINF:-1 tvg-id="More4.uk@SD" ')
        f.write('tvg-logo="https://www.netplus.ch/media/image/0/square/tv-logo-more-4.jpg.webp" ,More4\n')
        f.write('#KODIPROP:inputstream.adaptive.license_type=clearkey\n')
        f.write('#KODIPROP:inputstream.adaptive.license_key=000000000000000000000000006d340a:efee11d60dd6a2afb6865fc141e1c4a0\n')
        f.write('https://olsp.live.dash.c4assets.com/dash_iso_sp_tl/live/channel(m4)/manifest.mpd\n')
        f.write('#EXTINF:-1 tvg-id="4seven.uk@SD" ')
        f.write('tvg-logo="https://upload.wikimedia.org/wikipedia/en/thumb/5/5e/4seven_logo_2018.svg/330px-4seven_logo_2018.svg.png" ,4seven\n')
        f.write('#KODIPROP:inputstream.adaptive.license_type=clearkey\n')
        f.write('#KODIPROP:inputstream.adaptive.license_key=0000000000000000000000000034730a:19bfb83e0e0f40f6eef4eccedbfa7bb8\n')
        f.write('https://olsp.live.dash.c4assets.com/dash_iso_sp_tl/live/channel(4s)/manifest.mpd\n')
        f.write('#EXTINF:-1 tvg-id="E4.uk@SD" ')
        f.write('tvg-logo="https://upload.wikimedia.org/wikipedia/en/thumb/1/18/E4_%28channel%29_logo.svg/250px-E4_%28channel%29_logo.svg.png" ,E4\n')
        f.write('#KODIPROP:inputstream.adaptive.license_type=clearkey\n')
        f.write('#KODIPROP:inputstream.adaptive.license_key=0000000000000000000000000065340a:88a5d26b2dc54896693dea815df7c592\n')
        f.write('https://olsp.live.dash.c4assets.com/dash_iso_sp_tl/live/channel(e4)/manifest.mpd\n')
        f.write('#EXTINF:-1 tvg-id="AXNWhite.us@Portugal" ')
        f.write('tvg-logo="https://i.postimg.cc/fLp6SK8w/ezgif-300b4feb0427483f.png" ,AXN White\n')
        f.write('#KODIPROP:inputstream.adaptive.license_type=clearkey\n')
        f.write('#KODIPROP:inputstream.adaptive.license_key={"keys":[{"kty":"oct","kid":"t3DVtLtrWU2vmFhFqumqXw","k":"sMtG0tMc8ES8c9tx6YZfbw"},{"kty":"oct","kid":"q_No7DBlMDMtV3H3nfgkwQ","k":"zcUkd_y0IGsEOnE6a_oRmQ"}]}\n')
        f.write('https://a164aivottlinear-a.akamaihd.net/OTTB/fra-nitro/live/clients/dash/enc/hlkbg1ngqb/out/v1/86088477f9f646e3ac7230fc23738e8a/cenc.mpd\n')

        # ✅ Write the rest of the merged channels
        for block in merged:
            for idx, line in enumerate(block):
                if idx == 0:
                    line = clean_extinf(line)
                    line = inject_tvg(line)
                f.write(line + "\n")

    print("✅ Done: movies.m3u")

if __name__ == "__main__":
    main()
