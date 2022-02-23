import bs4
import pandas
import requests

from typing import NamedTuple, Optional, Tuple

BASE_URL = "https://eurovision.tv/events"

# Headers dict to use when requesting pages from spotifycharts.com
HEADERS = {
    "User-agent": "Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0"
}


def gather_events_url() -> list:
    page = requests.get(BASE_URL, headers=HEADERS)
    soup = bs4.BeautifulSoup(page.content, "html.parser")
    events = soup.find(class_="flex flex-wrap").find_all("div", class_="w-full md:w-1/3 xl:w-1/4 bg-white")
    return [event.find("a", href=True)["href"] for event in events][1:]  # Skip 2022


class SongInfo(NamedTuple):
    artist: str
    country: str
    title: str
    place_final: Optional[int]
    points_final: Optional[int]


def get_participant_info(participant: bs4.element.Tag) -> Tuple[str, str, str]:

    artist = participant.find("h4", {"data-card-title": ""}).text.strip()
    country = participant.find(class_="space-x-1").text.strip()
    title = participant.find("div", class_="text-base").text.strip()

    return artist, country, title


def get_final_info_if_present(artist: str, title: str, final_rows: bs4.element.ResultSet) -> Tuple[Optional[int], Optional[int]]:
    artist_col = 2
    title_col = 3
    points_col = 4
    place_col = 5

    for row in final_rows:
        elements = row.find_all("td")
        rowartist = elements[artist_col].text.strip()
        rowtitle = elements[title_col].span.text.strip()
        if rowartist == artist and rowtitle == title:
            rowplace = elements[place_col].text.strip()[:-2]  # Remove suffixes like 'st', 'nd', 'th'
            rowpoints = int(elements[points_col].text.strip()) if elements[points_col].text.strip() != "—" else 0
            return rowplace, rowpoints

    return None, None


def extract_songinfo_from(url: str) -> pandas.DataFrame:
    year = int(url.split("-")[-1])
    if year < 2004:
        final_url = f"{url}/final"
    else:
        final_url = f"{url}/grand-final"

    participants_url = f"{url}/participants"
    participants_page = requests.get(participants_url, headers=HEADERS)

    participants = bs4.BeautifulSoup(participants_page.content, "html.parser").find(
        class_="flex flex-wrap").find_all(class_="pointer-events-none")

    participants_info = [get_participant_info(participant) for participant in participants]

    final_page = requests.get(final_url, headers=HEADERS)
    final_rows = bs4.BeautifulSoup(final_page.content, "html.parser").table.tbody.find_all("tr")

    final_info = [get_final_info_if_present(artist, title, final_rows) for (artist, _, title) in participants_info]

    info = [SongInfo(artist, country, title, place_final, points_final)
            for (artist, country, title), (place_final, points_final) in zip(participants_info, final_info)]

    df = pandas.DataFrame(info)
    df["year"] = year
    return df


def create_dataset() -> pandas.DataFrame:
    dfs = []
    for url in gather_events_url():
        print(url)
        if url == "https://eurovision.tv/event/london-1963":
            continue
        df = extract_songinfo_from(url)
        dfs.append(df)
    return pandas.concat(dfs)

def save_specific_year(url: str) -> None:
    df = extract_songinfo_from(url)
    year = int(url.split("-")[-1])
    df.to_csv(f"data/eurovision_songs_official_{year}.csv")


if __name__ == "__main__":
    df = create_dataset()
    df.to_csv("data/eurovision_songs_official.csv", index=False)
