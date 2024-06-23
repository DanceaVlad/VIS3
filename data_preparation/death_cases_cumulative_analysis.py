import pandas as pd
import csv
import unicodedata


# Function to convert umlauts and special characters in filenames
def convert_umlauts(filename):
    umlauts = {
        'Ä': 'Ae', 'Ö': 'Oe', 'Ü': 'Ue', 'ä': 'ae', 'ö': 'oe', 'ü': 'ue', 'ß': 'ss'
    }
    for umlaut, replacement in umlauts.items():
        filename = filename.replace(umlaut, replacement)
    filename = unicodedata.normalize('NFKD', filename).encode('ASCII', 'ignore').decode('utf-8')
    return filename


# TODO maybe compare this with original sources
    
df = pd.read_csv('data/datasets/austriadata.csv', sep=',')

print(df.columns)
print(df.head())

df_deaths = df[['Datum', 'Wien_Tote', 'Burgenland_Tote', 'Niederösterreich_Tote', 'Oberösterreich_Tote', 'Salzburg_Tote', 'Steiermark_Tote', 'Tirol_Tote', 'Vorarlberg_Tote', 'Kärnten_Tote']]
print(df_deaths.head())

df_deaths = df_deaths.dropna()

df_cases = df[['Datum', 'Wien', 'Burgenland', 'Niederösterreich', 'Oberösterreich', 'Salzburg', 'Steiermark', 'Tirol', 'Vorarlberg', 'Kärnten']]
print(df_cases.head())

df_cases = df_cases.dropna()

df_deaths.columns = [col.replace('_Tote', '') for col in df_deaths.columns]
print(df_deaths.head())

for col in df_deaths.columns[1:]:
    df_deaths[col] = df_deaths.apply(lambda row: (row[col] / df_cases.loc[df_cases['Datum'] == row['Datum'], col].values[0] * 1000) if df_cases.loc[df_cases['Datum'] == row['Datum'], col].values[0] != 0 else 0, axis=1)
    
print(df_deaths.head())

for col in df_deaths.columns[1:]:
    df_to_export = df_deaths[['Datum', col]]
    filename = convert_umlauts(f'deaths_per_1000_cases_cumulative_{col}.csv')
    df_to_export.to_csv(f'data/cleaned_csvs/{filename}', index=False, sep=';', quotechar='"', quoting=csv.QUOTE_ALL)

print("Done exporting files")

# actually a delayed impact of positive cases on deaths, but does not matter for now