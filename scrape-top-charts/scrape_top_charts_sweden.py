import bs4
import datetime
import pandas
import requests

from typing import NamedTuple

BASE_URL = "https://sverigesradio.se/topplista.aspx?programid=2023&date="


class SongInfo(NamedTuple):
    position: int
    artist: str
    title: str


def convert_weeknumber_to_datetime_str(year: int, week: int) -> str:
    # Converts given year and week into a datetime.datetime object
    # pointing to the Sunday of that specific week.
    sunday = datetime.datetime.strptime(f"{year}-{week:02}-0", "%Y-%U-%w")
    return sunday.strftime("%Y-%m-%d")


def get_song_info(elements: bs4.element.Tag) -> SongInfo:
    position = elements.find(class_="track__ranking-current").contents[0].strip()
    artist_title = (elements.find(class_="track-title") or elements.find(class_="track__title"))
    artist, title = map(str.strip, artist_title.contents[0].split(" - "))
    return SongInfo(position, artist, title)


def extract_weekly_chart(year: int, week: int) -> pandas.DataFrame:
    urltoken = convert_weeknumber_to_datetime_str(year, week)
    week_url = f"{BASE_URL}{urltoken}"
    page = requests.get(week_url)
    # Get elements of tag list at odd positions since the website puts a `\n` between them
    weekly_chart = bs4.BeautifulSoup(page.content, "html.parser").ul.li.ul.contents[1::2]
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
    df.to_csv("data/charts/charts_radio_sweden_2017_2021.csv", index=False)
