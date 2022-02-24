import pandas

from typing import Dict

RADIOCHARTS = [
    "data/charts/charts_radio_denmark_2017_2021.csv",
    "data/charts/charts_radio_finland_2017_2021.csv",
    "data/charts/charts_radio_norway_2017_2021.csv",
    "data/charts/charts_radio_sweden_2017_2021.csv",
]

SPOTIFYCHARTS = "data/charts/charts_spotify_allcountries_2017_2021.csv"


def filter_radio_charts() -> Dict[str, pandas.DataFrame]:
    """
    Read in weekly radio top charts and filter to the 10 most popular songs of
    each year in each country.
    """
    dfs_top10 = {}

    for filename in RADIOCHARTS:
        country = filename.split("_")[2]
        df = pandas.read_csv(filename)
        df["country"] = country.capitalize()
        dfs_top10[country] = df[df.position <= 10]

    for country, group in dfs_top10.items():
        topartists = group.groupby(["year", "artist", "title", "country"])["position"].count(
        ).reset_index().sort_values(by=["year", "position"], ascending=[True, False])
        topartists.rename(columns={"position": "weekcount"}, inplace=True)
        dfs_top10[country] = topartists

    for country in dfs_top10.keys():
        dfs_top10[country] = dfs_top10[country].groupby("year").head(10).reset_index(drop=True)

    return dfs_top10


def save_filtered_radio_charts() -> None:
    """
    Aggregate filtered radio charts into a single dataset and save to disk.
    """
    dfs_top10 = filter_radio_charts()
    final = pandas.concat(dfs_top10.values())
    final.sort_values(by=["year", "country", "weekcount"], ascending=[True, True, False], inplace=True)
    final.to_csv("data/top10/radio_charts.csv", index=False)


def filter_spotify_charts() -> pandas.DataFrame:
    """
    Read in weekly Spotify top charts and filter to the 10 most popular songs of
    each year in each country.
    """

    df = pandas.read_csv(SPOTIFYCHARTS)
    df_top10 = df[df.position <= 10]

    topartists = df_top10.groupby(["year", "artist", "title", "country"])["streams"].sum()
    topartists = topartists.reset_index().sort_values(by=["year", "country", "streams"], ascending=[True, True, False])

    topartists = topartists.groupby(["year", "country"]).head(10).reset_index(drop=True)

    return topartists


def save_filtered_spotify_charts() -> None:
    """Save filtered Spotify charts to disk."""
    final = filter_spotify_charts()
    final.sort_values(by=["year", "country", "streams"], ascending=[True, True, False], inplace=True)
    final.to_csv("data/top10/spotify_charts.csv", index=False)


if __name__ == "__main__":
    save_filtered_radio_charts()
    save_filtered_spotify_charts()
