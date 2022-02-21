import bs4
import pandas
import requests

from typing import NamedTuple

BASE_URL = "http://hitlisten.nu/default.asp?w={}&y={}&list=t40"


class SongInfo(NamedTuple):
    position: int
    artist: str
    title: str


def get_song_info(elements: bs4.element.Tag) -> SongInfo:
    position = int(elements.find(id=["denneugeny", "denneuge","denneugere"]).contents[0])
    artist = elements.find(id="artistnavn").contents[0].strip()
    title = elements.find(id="titel").contents[0].strip()
    return SongInfo(position, artist, title)


def extract_weekly_chart(year: int, week: int) -> pandas.DataFrame:
    week_url = BASE_URL.format(f"{week:02}", year)
    page = requests.get(week_url)

    weekly_chart = bs4.BeautifulSoup(page.content, "html.parser").find_all(id="linien")

    info = [get_song_info(elements) for elements in weekly_chart]

    df = pandas.DataFrame(info)
    df["year"] = year
    df["week"] = week
    return df


def create_dataset() -> pandas.DataFrame:
    dfs = []
    for year in range(2017, 2022):
        for week in range(1, 53):
            print(f"{year}-{week}")
            dfs.append(extract_weekly_chart(year, week))
    return pandas.concat(dfs)


if __name__ == "__main__":
    df = create_dataset()
    df.to_csv("data/charts_radio_denmark_2017_2021.csv", index=False)
