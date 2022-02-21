import bs4
import pandas
import requests

from typing import NamedTuple

BASE_URL = "https://www.ifpi.fi/lista/singlet"


class SongInfo(NamedTuple):
    position: int
    artist: str
    title: str


def get_song_info(elements: bs4.element.Tag) -> SongInfo:
    position = int(elements.find(class_="chart-position").contents[0].rstrip("."))
    artist = elements.find(class_="chart-artist").contents[0]
    title = elements.find(class_="chart-title").contents[0]
    return SongInfo(position, artist, title)


def extract_weekly_chart(year: int, week: int) -> pandas.DataFrame:
    week_url = f"{BASE_URL}/{year}/{week:02}"
    page = requests.get(week_url)

    weekly_chart = bs4.BeautifulSoup(page.content, "html.parser").find_all(class_="chart-row")

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
    df.to_csv("data/charts_radio_finland_2017_2021.csv", index=False)
