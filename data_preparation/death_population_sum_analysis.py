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
df_deaths = df_deaths.iloc[[0]]
print(df_deaths)

df_population = pd.read_csv('data/datasets/optional_original_sources/population_by_bundesland.csv', sep=';')
print(df_population.head())

df_population.drop(columns=[df_population.columns[-1]], inplace=True)

mean_population = df_population.set_index('Bundesland')
mean_population = mean_population.iloc[:, :-1].add(mean_population.iloc[:, 1:].values) / 2

mean_population.columns = [col.replace('01.01.', '') for col in mean_population.columns]
mean_population.drop(columns=[mean_population.columns[-1]], inplace=True)
print(mean_population)

df_deaths['Year'] = df_deaths['Datum'].str[:4]
df_deaths.columns = [col.replace('_Tote', '') for col in df_deaths.columns]
print(df_deaths.head())

for col in df_deaths.columns[1:10]:
    df_deaths[col] = df_deaths.apply(lambda row: row[col] / mean_population.at[col, row['Year']] * 1000, axis=1)
    
df_deaths.drop(columns=['Year', 'Datum'], inplace=True)

print(df_deaths.head())

df_deaths_per_1000_people = pd.melt(df_deaths, var_name='Bundesland', value_name='sum_deaths_per_1000_people')

print(df_deaths_per_1000_people.head())

filename = 'choropleth_deaths_per_1000_people_sum_sep_22.csv'

df_deaths_per_1000_people.to_csv(f'data/cleaned_csvs/{filename}', index=False, sep=';', quotechar='"', quoting=csv.QUOTE_ALL)

print("Done exporting file")
