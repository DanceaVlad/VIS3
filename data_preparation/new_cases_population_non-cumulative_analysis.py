import pandas as pd
import numpy as np
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

df_cases = df[['Datum', 'Wien', 'Burgenland', 'Niederösterreich', 'Oberösterreich', 'Salzburg', 'Steiermark', 'Tirol', 'Vorarlberg', 'Kärnten']]
df_cases = df_cases.dropna()

print(df_cases.head())

df_cases['Datum'] = pd.to_datetime(df_cases['Datum'])
df_cases = df_cases.sort_values(by='Datum', ascending=False)

df_cases['days_since_last_measurement'] = (df_cases['Datum'] - df_cases['Datum'].shift(-1)).dt.days

print(df_cases.head())

temp_df = df_cases.copy()

for col in df_cases.columns[1:-1]:
    temp_df[col] = (df_cases[col] - df_cases[col].shift(-1)) / df_cases['days_since_last_measurement']
    
df_cases.update(temp_df)

df_cases.drop(columns=['days_since_last_measurement'], inplace=True)
    
df_cases.fillna(0, inplace=True)

print(df_cases.head())

df_population = pd.read_csv('data/datasets/optional_original_sources/population_by_bundesland.csv', sep=';')
print(df_population.head())

df_population.drop(columns=[df_population.columns[-1]], inplace=True)

mean_population = df_population.set_index('Bundesland')
mean_population = mean_population.iloc[:, :-1].add(mean_population.iloc[:, 1:].values) / 2

mean_population.columns = [col.replace('01.01.', '') for col in mean_population.columns]
mean_population.drop(columns=[mean_population.columns[-1]], inplace=True)
print(mean_population)

df_cases['Year'] = str(df_cases['Datum'].get(0).year)
print(df_cases.head())

for col in df_cases.columns[1:-1]:
    df_cases[col] = df_cases.apply(lambda row: row[col] / mean_population.at[col, row['Year']] * 1000, axis=1)
    df_cases[col] = np.where(df_cases[col] < 0, 0, df_cases[col])
    
df_cases.drop(columns=['Year'], inplace=True)
    
print(df_cases.head())

for col in df_cases.columns[1:]:
    df_to_export = df_cases[['Datum', col]]
    filename = convert_umlauts(f'daily_new_cases_per_1000_people_non-cumulative_{col}.csv')
    df_to_export.to_csv(f'data/cleaned_csvs/{filename}', index=False, sep=';', quotechar='"', quoting=csv.QUOTE_ALL)

print("Done exporting files")