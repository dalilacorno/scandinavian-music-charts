import pandas
import os

from functools import lru_cache
from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException
from lyricsgenius import Genius
from pycountry import languages
from requests.exceptions import Timeout

FILENAMES = [os.path.join("data/top10", filename) for filename in os.listdir("data/top10")]

# Need to provide a Genius access token for this to work
# GENIUS = Genius(..., timeout=20, retries=5, sleep_time=1)
GENIUS = None


@lru_cache(maxsize=None)
def detect_song_language(artist: str, title: str) -> str:
    try:
        song = GENIUS.search_song(title, artist)
        todetect = song.lyrics if song is not None and song.lyrics is not None else title.lower()
        detected = detect(todetect)
        return languages.get(alpha_2=detected).name
    except LangDetectException:
        print(f"Cannot detect language for song {title} by {artist}")
        return "LangDetectException"
    except Timeout:
        print(f"Connection timeout while processing song {title} by {artist}")
        return "Timeout"


def amend_song_language(artist: str, title: str, language: str) -> str:
    if language == "Timeout":
        return detect_song_language(artist, title)
    else:
        print(f"No amend needed: {title} by {artist}")
        return language


if __name__ == "__main__":
    for filename in FILENAMES:
        df = pandas.read_csv(filename)
        df["language"] = df.apply(lambda df: detect_song_language(df.artist, df.title), axis=1)
        df.to_csv(os.path.join("data/labelled-automated", os.path.basename(filename)), index=False)

    print(detect_song_language.cache_info())
