import bs4
import pandas
import requests

from typing import NamedTuple, Optional

BASE_URL = "https://www.esc-history.com/entries.asp?start="


class SongInfo(NamedTuple):
    artist: str
    country: str
    language: str
    title: str
    year: int


def get_song_info(row: bs4.element.Tag) -> Optional[SongInfo]:
    elements = row.find_all("td")
    year_col = 1
    country_col = 3
    artist_col = 4
    title_col = 5
    details_col = 8

    detail_url = elements[details_col].find("a", href=True)["href"]
    detail_page = requests.get("https://www.esc-history.com/"+detail_url)
    if detail_page.status_code == 404:
        # No details about this song, something weird going on
        return None

    detail_soup = bs4.BeautifulSoup(detail_page.content, 'html.parser')
    section = detail_soup.find("section", id="middle-col")
    strippedstrings = list(section.stripped_strings)
    langind = strippedstrings.index("Language") + 1

    artist = elements[artist_col].text.strip()
    country = elements[country_col].a.text
    language = strippedstrings[langind].strip(":\t")
    title = elements[title_col].text.strip()
    year = int(elements[year_col].a.text)

    return SongInfo(artist, country, language, title, year)


def extract_songinfo_from(url: str) -> pandas.DataFrame:
    page = requests.get(url)

    # First row is always spurious
    rows = bs4.BeautifulSoup(page.content, "html.parser").table.tbody.find_all("tr")[1:]

    info = [get_song_info(row) for row in rows]
    info = [song for song in info if song is not None]

    df = pandas.DataFrame(info)
    return df


def create_dataset() -> pandas.DataFrame:
    dfs = []
    for startn in range(1, 1352, 30):
        print(f"Gathering page {startn}")
        url = f"{BASE_URL}{startn}"
        df = extract_songinfo_from(url)
        dfs.append(df)
    return pandas.concat(dfs)


if __name__ == "__main__":
    df = create_dataset()
    df.to_csv("data/eurovision_songs_esc.csv", index=False)
