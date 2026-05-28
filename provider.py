import requests
import re

INDIHOME_URL = "https://raw.githubusercontent.com/apistech/project/refs/heads/main/IndihomeTV.m3u"
CIGNAL_URL = "https://raw.githubusercontent.com/TakaMn/TakashiM3u/main/cignal.m3u"

OUTPUT_FILE = "movies.m3u"

HEADER = '#EXTM3U url-tvg="https://bit.ly/4a2SXO3" $BorpasFileFormat="1"'

CIGNAL_ALLOWED = [
    "Tap Movies","HBO","HBO Hits","HBO Family","HBO Signature",
    "Cinemax","AXN","Warner TV",
    "Rock Action","Rock Entertainment",
    "Hits HD","HITS Now","HITS Movies",
    "DreamWorks"
]

# ✅ TVG-ID MAP
TVG_MAP = {
    "HBO": 'tvg-id="HBOAsia.sg@SD"',
    "HBO Family": 'tvg-id="HBOFamilyAsia.sg@SD"',
    "HBO Hits": 'tvg-id="HBOHitsAsia.sg@SD"',
    "HBO Signature": 'tvg-id="HBOSignatureAsia.sg@SD"',
    "Cinemax": 'tvg-id="CinemaxAsia.sg@SD"',
    "AXN": 'tvg-id="AXNAsia.sg@SD"',
    "Warner TV": 'tvg-id="WarnerTVAsia.sg@SD"',
    "Tap Movies": 'tvg-id="TapMoviesAsia.sg@SD"',
    "Rock Action": 'tvg-id="RockActionAsia.sg@SD"',
    "Rock Entertainment": 'tvg-id="RockEntertainmentAsia.sg@SD"',
    "HITS Now": 'tvg-id="HitsNowAsia.sg@SD"',
    "HITS Movies": 'tvg-id="HitsMoviesAsia.sg@SD"',
    "Hits HD": 'tvg-id="HitsAsia.sg@SD"',
}

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
            i = j
        else:
            i += 1

    return entries


def filter_indihome(entries):
    result = []
    for block in entries:
        m = re.search(r'group-title="([^"]+)"', block[0], re.IGNORECASE)
        if m and "movie" in m.group(1).lower():
            result.append(block)
    return result


def filter_cignal(entries):
    result = []
    for block in entries:
        name = block[0].split(",", 1)[-1].lower()
        if any(ch in name for ch in CIGNAL_ALLOWED):
            result.append(block)
    return result


# ✅ Inject TVG-ID
def inject_tvg(extinf):
    name = extinf.split(",", 1)[-1].lower().strip()

    for key in sorted(TVG_MAP.keys(), key=len, reverse=True):
        if key in name:
            tvg = TVG_MAP[key]

            # remove existing tvg-id if any
            extinf = re.sub(r'\s*tvg-id="[^"]+"', '', extinf)

            # inject after #EXTINF:-1
            extinf = extinf.replace("#EXTINF:-1", f"#EXTINF:-1 {tvg}")

            break

    return extinf


def clean_extinf(line):
    # remove group-title
    line = re.sub(r'\s*group-title="[^"]+"', '', line, flags=re.IGNORECASE)
    return line


def main():
    print("Downloading...")

    indihome = requests.get(INDIHOME_URL).text
    cignal = requests.get(CIGNAL_URL).text

    print("Parsing...")

    ind_entries = parse_m3u(indihome)
    cig_entries = parse_m3u(cignal)

    print("Filtering...")

    ind_movies = filter_indihome(ind_entries)
    cig_selected = filter_cignal(cig_entries)

    merged = ind_movies + cig_selected

    print(f"Total channels: {len(merged)}")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(HEADER + "\n")

        for block in merged:
            for idx, line in enumerate(block):

                if idx == 0:
                    line = clean_extinf(line)

                    # ✅ apply tvg-id only to cignal channels
                    name = line.split(",", 1)[-1].lower()
                    if any(k in name for k in TVG_MAP):
                        line = inject_tvg(line)

                f.write(line + "\n")

    print("✅ Done: movies.m3u")


if __name__ == "__main__":
    main()
