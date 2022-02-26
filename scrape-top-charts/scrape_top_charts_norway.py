import bs4
import pandas
import requests

from typing import NamedTuple

BASE_URL = "https://topplista.no/charts/singles/"


class SongInfo(NamedTuple):
    position: int
    artist: str
    title: str


def get_song_info(elements: bs4.element.ResultSet) -> SongInfo:
    artist = elements[4].span.a.contents[0]
    position = int(elements[0].contents.pop())
    title = elements[4].contents[0]
    return SongInfo(position, artist, title)


def extract_weekly_chart(year: int, week: int) -> pandas.DataFrame:
    week_url = f"{BASE_URL}{year}-w{week:02}"
    page = requests.get(week_url)
    weekly_chart = bs4.BeautifulSoup(page.content, "html.parser").table.tbody
    rows = weekly_chart.find_all("tr")
    info = [get_song_info(row.find_all("td")) for row in rows]
    df = pandas.DataFrame(info)
    df["year"] = year
    df["week"] = week
    return df


def create_dataset() -> pandas.DataFrame:
    dfs = []
    for year in range(2017, 2022):
        for week in range(1, 53):
            dfs.append(extract_weekly_chart(year, week))
    return pandas.concat(dfs)


if __name__ == "__main__":
    df = create_dataset()
    df = df.reindex(sorted(df.columns), axis=1)  # Order columns alphabetically
    df.to_csv("data/charts/charts_radio_norway_2017_2021.csv", index=False)
