import pandas as pd
import numpy as np

if __name__ == "__main__":
    # Load News
    ffm_df = pd.read_csv(r"../out/Polizeiberichte_raw_full_00_19.csv", sep=";", header="infer")
    # Insert index in new column
    ffm_df['level_0'] = ffm_df.index
    # Split rows if a certain pattern occurs into new rows
    s = ffm_df['Hauptartikel'].str.split(r'\d\d\d\d\d\d\s\-\s\d\d\d\d').apply(pd.Series, 1).stack()
    splitrows = pd.DataFrame(s)
    splitrows.columns = ["News"]
    # reset index
    splitrows = splitrows.reset_index()
    # join original news dataframe back to get timestamp foe each news
    merged = splitrows.merge(right=ffm_df, how="inner", on="level_0")
    # replace empty news with nan
    merged[merged['News'] == ' '] = np.nan
    # drop empty news rows
    merged = merged.dropna(subset=['News'])
    # there are basically two news formats
    # classify as old if certain pattern appears at the start of a news article
    merged["Old"] = merged["Hauptartikel"].str[:30].str.contains(r'\d\d\d\d\d\d\s\-\s\d\d\d\d')
    # Split in old and new dataframe
    merged_old = merged[merged["Old"] == True]
    merged_new = merged[merged["Old"] == False]
    # replace \xa0 with whitespace
    merged_old["News"] = merged_old["News"].str.replace(u'\xa0', u' ')
    # remove whitespace from start
    merged_old["News"] = merged_old["News"].str.strip()
    # split if 4 whitespace in a row appear, usually this is the end of the headline
    merged_old["Ueberschrift"] = merged_old["News"].str.split("    ").str[0]
    # if the headline is longer than 150 characters it probably has not worked and it returned the whole article
    # in this case return an empty headline
    merged_old["Ueberschrift"] = merged_old["Ueberschrift"].apply(lambda x: x if len(x) <= 150 else "")
    # remove the headline from the news
    merged_old["News"] = [e.replace(k, '') for e, k in
                          zip(merged_old["News"].astype('str'), merged_old["Ueberschrift"].astype('str'))]
    # Add "POL-F: " at the start for uniformity
    merged_old["Hauptartikel"] = "POL-F: " + merged_old["Hauptartikel"]
    # concatenate old and new dataframe together
    merged = pd.concat([merged_new, merged_old])
    # drop unnecessary columns
    merged.drop(['Hauptartikel', "level_0", "level_1"], axis=1, inplace=True)
    # rename news to Hauptartikel
    merged.rename(columns={'News': 'Hauptartikel'}, inplace=True)
    # format timestamp column
    merged['Timestamp'] = pd.to_datetime(merged['Timestamp'], format='%d.%m.%Y – %H:%M')
    # extract year
    merged["Year"] = merged['Timestamp'].dt.year
    # save file per year to get smaller files
    for i, (name, group) in enumerate(merged.groupby('Year')):
        group.to_csv(r"../out/ffm_news{}.csv".format(i),
                     sep=";",
                     encoding="UTF-8",
                     header=True,
                     quotechar='"',
                     index=False)
