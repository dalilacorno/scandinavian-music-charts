import os

import numpy
import pandas

from matplotlib import pyplot
from matplotlib.patches import Patch

from typing import Dict, Iterable, List, Tuple


LANGUAGE_COUNTS = Dict[str, List[int]]

LANGUAGE_COLORS = {
    "Danish": "tab:red",
    "English": "tab:olive",
    "Finnish": "tab:blue",
    "Norwegian": "tab:purple",
    "Swedish": "tab:orange",
    "Icelandic": "tab:cyan",
    "Other": "lightgrey",
}


def get_lang(language: str, iterable: Iterable[str]) -> str:
    for item in iterable:
        if item in language:
            return item


def create_dataset_for_vis() -> Dict[int, Tuple[LANGUAGE_COUNTS, LANGUAGE_COUNTS]]:
    dfs = {}
    basepath = "../scrape-top-charts/data/labelled-manual"
    for filename in os.listdir(basepath):
        name = filename.split("_")[0]
        dfs[name] = pandas.read_csv(os.path.join(basepath, filename))

    spotify_years = {}
    for label, group in dfs["spotify"].groupby("year"):
        spotify_years[label] = group

    radio_years = {}
    for label, group in dfs["radio"].groupby("year"):
        radio_years[label] = group

    radio_agg = {}
    for year, df in radio_years.items():
        radio_agg[year] = df.groupby(["country", "language"])["weekcount"].count().reset_index()

    spotify_agg = {}
    for year, df in spotify_years.items():
        spotify_agg[year] = df.groupby(["country", "language"])["streams"].count().reset_index()

    dfs_agg = {
        year: (radio, spotify)
        for year, radio, spotify
        in zip(radio_agg.keys(), radio_agg.values(), spotify_agg.values())
    }

    stacked_bars = {}
    for year, (radio, spotify) in dfs_agg.items():
        stacked_bars_radio = pandas.crosstab(
            radio.country, radio.language, values=radio["weekcount"],
            aggfunc=lambda x: x.apply(pandas.to_numeric, errors="ignore"))
        stacked_bars_radio = stacked_bars_radio.apply(lambda x: x.fillna(0))

        stacked_bars_spotify = pandas.crosstab(
            spotify.country, spotify.language, values=spotify["streams"],
            aggfunc=lambda x: x.apply(pandas.to_numeric, errors="ignore"))
        stacked_bars_spotify = stacked_bars_spotify.apply(lambda x: x.fillna(0))
        stacked_bars_spotify = stacked_bars_spotify.reindex(["Denmark", "Finland", "Norway", "Sweden", "Iceland"])

        stacked_bars[year] = (stacked_bars_radio, stacked_bars_spotify)

    lang_countries = {}
    for year, (radio, spotify) in stacked_bars.items():
        radio_langs = {}
        for column in radio.columns:
            radio_langs[column] = radio[column].to_list()

        spotify_langs = {}
        for column in spotify.columns:
            spotify_langs[column] = spotify[column].to_list()

        lang_countries[year] = (radio_langs, spotify_langs)

    return lang_countries


def plot(dataset: Dict[int, Tuple[LANGUAGE_COUNTS, LANGUAGE_COUNTS]]) -> None:
    fig, axes = pyplot.subplots(5, 2, figsize=(13, 15))
    ax_years = {year: (ax_radio, ax_spoti) for year, (ax_radio, ax_spoti) in zip(dataset.keys(), axes)}

    textbox_props = dict(boxstyle='round', facecolor='white', alpha=0.5)

    radio_labels = ["Denmark", "Finland", "Norway", "Sweden"]
    spotify_labels = radio_labels + ["Iceland"]

    radio_xvals = numpy.arange(len(radio_labels))
    spotify_xvals = numpy.arange(len(spotify_labels))

    for year in ax_years.keys():
        ax_radio, ax_spotify = ax_years[year]

        radio_langs, spotify_langs = dataset[year]

        width = 0.15

        radio_others, spotify_others = 0, 0

        radio_agg_bars = [0] * 4
        spotify_agg_bars = [0] * 5

        # Plot radio
        for language in radio_langs.keys():
            if language == "English":
                ax_radio.bar(radio_xvals-width, radio_langs[language], width,
                             label=language, color=LANGUAGE_COLORS[language])
            elif language in LANGUAGE_COLORS.keys():
                ax_radio.bar(radio_xvals, radio_langs[language], width, label=language,
                             bottom=radio_agg_bars, color=LANGUAGE_COLORS[language])
                radio_agg_bars = numpy.add(radio_agg_bars, radio_langs[language])
            else:
                otherlang = "Other"
                ax_radio.bar(radio_xvals+width, radio_langs[language], width,
                             label=otherlang if radio_others == 0 else "", color=LANGUAGE_COLORS[otherlang])
                radio_others += 1

        # Plot spotify
        for language in spotify_langs.keys():
            if language == "English":
                ax_spotify.bar(spotify_xvals-width, spotify_langs[language],
                               width, label=language, color=LANGUAGE_COLORS[language])
            elif language in LANGUAGE_COLORS.keys():
                ax_spotify.bar(spotify_xvals, spotify_langs[language], width, label=language,
                               bottom=spotify_agg_bars, color=LANGUAGE_COLORS[language])
                spotify_agg_bars = numpy.add(spotify_agg_bars, spotify_langs[language])
            else:
                otherlang = "Other"
                ax_spotify.bar(spotify_xvals+width, spotify_langs[language], width,
                               label=otherlang if spotify_others == 0 else "", color=LANGUAGE_COLORS[otherlang])
                spotify_others += 1

        ax_radio.set_xticks(radio_xvals, radio_labels, fontsize=14)
        ax_spotify.set_xticks(spotify_xvals, spotify_labels, fontsize=14)

        ax_radio.set_yticks([0, 5, 10])
        ax_spotify.set_yticks([0, 5, 10])

        ax_radio.text(0.02, 0.9, f"{year} - Radio", transform=ax_radio.transAxes, bbox=textbox_props, fontsize=12)
        ax_spotify.text(0.02, 0.9, f"{year} - Spotify", transform=ax_spotify.transAxes, bbox=textbox_props, fontsize=12)

    legend_items = [Patch(facecolor=value, label=key) for key, value in LANGUAGE_COLORS.items()]
    fig.legend(handles=legend_items, loc="lower center", ncol=4, fontsize=14)
    fig.savefig("visualize_top_charts.png")


if __name__ == "__main__":
    dataset = create_dataset_for_vis()
    plot(dataset)
