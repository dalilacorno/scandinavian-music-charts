import bs4
import datetime
import pandas
import requests

from pycountry import countries
from typing import NamedTuple

BASE_URL = "https://spotifycharts.com/regional/{country}/weekly/{daterange}"

COUNTRIES = {
    countries.get(name="Denmark").alpha_2.lower(): "Denmark",
    countries.get(name="Finland").alpha_2.lower(): "Finland",
    countries.get(name="Iceland").alpha_2.lower(): "Iceland",
    countries.get(name="Norway").alpha_2.lower(): "Norway",
    countries.get(name="Sweden").alpha_2.lower(): "Sweden",
}

# Headers dict to use when requesting pages from spotifycharts.com
HEADERS = {
    "User-agent": "Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0"
}


class SongInfo(NamedTuple):
    position: int
    artist: str
    title: str
    streams: int


def get_song_info(row: bs4.element.Tag) -> SongInfo:
    position = int(row.find(class_="chart-table-position").contents[0])
    artist_contents = row.find(class_="chart-table-track").span.contents
    artist = artist_contents[0].lstrip("by ") if artist_contents else None
    title_contents = row.find(class_="chart-table-track").strong.contents
    title = title_contents[0] if title_contents else None
    streams = int(row.find(class_="chart-table-streams").contents[0].replace(",", ""))
    return SongInfo(position, artist, title, streams)


def generate_url_tokens() -> str:
    tokens = []
    startdate = datetime.date(2016, 12, 30)
    enddate = datetime.date(2021, 12, 31)
    # The daterange in the Spotify website contains two consecutive fridays,
    # e.g. 2021-12-31--2022-01-07
    while startdate < enddate:
        nextdate = startdate + datetime.timedelta(7)
        tokens.append(f'{startdate.strftime("%Y-%m-%d")}--{nextdate.strftime("%Y-%m-%d")}')
        startdate = nextdate
    return tokens


def extract_weekly_chart(country_code: str, daterange: str) -> pandas.DataFrame:
    week_url = BASE_URL.format(country=country_code, daterange=daterange)
    page = requests.get(week_url, headers=HEADERS)

    rows = bs4.BeautifulSoup(page.content, "html.parser").table.tbody.find_all("tr")
    info = [get_song_info(row) for row in rows]

    year = datetime.datetime.strptime(daterange.split("--")[0], "%Y-%m-%d").year

    df = pandas.DataFrame(info)
    df["daterange"] = daterange
    df["year"] = year
    df["country"] = COUNTRIES[country_code]
    return df


def create_dataset() -> pandas.DataFrame:
    dfs = []
    for country_code in COUNTRIES.keys():
        for daterange in generate_url_tokens():
            print(f"{country_code}: {daterange}")
            dfs.append(extract_weekly_chart(country_code, daterange))
    return pandas.concat(dfs)


if __name__ == "__main__":
    df = create_dataset()
    # Some songs are on the Spotify top charts, but have been removed from
    # Spotify. Their name and/or title will be null.
    df = df.dropna()
    # There is a trailing last week of 2016 due to how Spotify handles the string
    # of the week in the website URL
    df = df[df.year > 2016]
    df.to_csv("data/charts/charts_spotify_allcountries_2017_2021.csv", index=False)
