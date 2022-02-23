import pandas


def merge_language_into_dataset() -> None:
    df_official = pandas.read_csv("data/eurovision_songs_official.csv")
    df_official.sort_values(by=["year", "country"], inplace=True)
    df_official.reset_index(drop=True, inplace=True)

    df_esc = pandas.read_csv("data/eurovision_songs_esc.csv")
    df_esc.sort_values(by=["year", "country"], inplace=True)
    df_esc.reset_index(drop=True, inplace=True)

    df_official["lowertitle"] = df_official.title.apply(str.lower)
    df_esc["lowertitle"] = df_esc.title.apply(str.lower)

    merged = pandas.merge(df_official, df_esc, on=["country", "lowertitle", "year"], how="left")

    # Adjust column name, remove extra column and reorder columns alphabetically
    merged.rename(columns={"artist_x": "artist", "title_x": "title"}, inplace=True)
    merged.drop(["artist_y", "title_y", "lowertitle"], axis=1, inplace=True)
    merged = merged.reindex(sorted(merged.columns), axis=1)

    merged.to_csv("data/eurovision_songs_merged.csv", index=False)


if __name__ == "__main__":
    merge_language_into_dataset()
