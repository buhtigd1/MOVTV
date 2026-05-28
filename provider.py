import requests
import re

SOURCE1_URL = "https://raw.githubusercontent.com/apistech/project/refs/heads/main/IndihomeTV.m3u"
SOURCE2_URL = "https://raw.githubusercontent.com/TakaMn/TakashiM3u/main/cignal.m3u"

OUTPUT_FILE = "movies.m3u"

HEADER = '#EXTM3U url-tvg="https://bit.ly/4a2SXO3" $BorpasFileFormat="1"'
HEADERS = {"User-Agent": "Mozilla/5.0"}


# ✅ Allowed channels (Cignal)
SOURCE2_ALLOWED = [
    "hbo","hbohits","hbofamily","hbosignature",
    "cinemax","axn","warner",
    "tapmovies","rockaction","rockentertainment",
    "hits","dreamworks"
]


# ✅ TVG MAP
TVG_MAP = {
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
    "hits": 'tvg-id="HitsAsia.sg@SD"',
    "dreamworks": 'tvg-id="DreamWorksAsia.sg@SD"',

    # Source1
    "ccm": 'tvg-id="CelestialClassicMovies.id@SD"',
    "celestial movies": 'tvg-id="CelestialMoviesIndonesia.id@SD"',
    "galaxy premium": 'tvg-id="GalaxyPremium.id@SD"',
    "galaxy": 'tvg-id="Galaxy.id@SD"',
    "imc": 'tvg-id="IMC.id@SD"',
    "thrill": 'tvg-id="Thrill.hk@SD"',
    "studio universal": 'tvg-id="StudioUniversalLatinAmerica.us@Brazil"',
    "tvn movies": 'tvg-id="tvNMoviesAsia.hk@SD"',
    "zee bioskop": 'tvg-id="ZeeBioskop.id@SD"',
}


# -----------------------------

def normalize(name):
    return re.sub(r'[^a-z0-9]', '', name.lower())


def clean_name(name):
    name = name.lower()
