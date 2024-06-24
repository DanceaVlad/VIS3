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

def cap_extreme_values(df, col, lower_percentile=1, upper_percentile=99):
    # Calculate percentiles
    lower_cap = df[col].quantile(lower_percentile / 100)
    upper_cap = df[col].quantile(upper_percentile / 100)
    
    # Apply caps
    df[col] = df[col].clip(lower=lower_cap, upper=upper_cap)


# TODO maybe compare this with original sources
    
df = pd.read_csv('data/datasets/austriadata.csv', sep=',')

print(df.columns)
print(df.head())

df_tests = df[['Datum', 'Wien_Tests', 'Burgenland_Tests', 'Niederösterreich_Tests', 'Oberösterreich_Tests', 'Salzburg_Tests', 'Steiermark_Tests', 'Tirol_Tests', 'Vorarlberg_Tests', 'Kärnten_Tests']]
df_tests = df_tests.dropna()

print(df_tests.head())

df_tests['Datum'] = pd.to_datetime(df_tests['Datum'])
df_tests = df_tests.sort_values(by='Datum', ascending=False)

# There are Ns in the dataset, which denote missing values. We will replace them with NaNs
for col in df_tests.columns[1:]:
    df_tests[col] = pd.to_numeric(df_tests[col], errors='coerce')
    
for col in df_tests.columns[1:]: # excluding 'Datum'
    for i in df_tests.index:
        if pd.isna(df_tests.at[i, col]):  # Check if the value is NaN
            # Get previous and next non-NaN values
            prev_val = df_tests[col][:i].dropna().last_valid_index()
            next_val = df_tests[col][i+1:].dropna().first_valid_index()
            
            values_to_mean = []
            if prev_val is not None:
                values_to_mean.append(df_tests.at[prev_val, col])
            if next_val is not None:
                values_to_mean.append(df_tests.at[next_val, col])
            
            # Calculate mean if there are values to average
            if values_to_mean:
                df_tests.at[i, col] = np.mean(values_to_mean)

df_tests['days_since_last_measurement'] = (df_tests['Datum'] - df_tests['Datum'].shift(-1)).dt.days

print(df_tests.head())

temp_df = df_tests.copy()

for col in df_tests.columns[1:-1]:
    temp_df[col] = (df_tests[col] - df_tests[col].shift(-1)) / df_tests['days_since_last_measurement']
    
df_tests.update(temp_df)

df_tests.drop(columns=['days_since_last_measurement'], inplace=True)
    
df_tests.fillna(0, inplace=True)

print(df_tests.head())

df_population = pd.read_csv('data/datasets/optional_original_sources/population_by_bundesland.csv', sep=';')
print(df_population.head())

df_population.drop(columns=[df_population.columns[-1]], inplace=True)

mean_population = df_population.set_index('Bundesland')
mean_population = mean_population.iloc[:, :-1].add(mean_population.iloc[:, 1:].values) / 2

mean_population.columns = [col.replace('01.01.', '') for col in mean_population.columns]
mean_population.drop(columns=[mean_population.columns[-1]], inplace=True)
print(mean_population)

df_tests['Year'] = str(df_tests['Datum'].get(0).year)
df_tests.columns = [col.replace('_Tests', '') for col in df_tests.columns]
print(df_tests.head())

for col in df_tests.columns[1:-1]:
    df_tests[col] = df_tests.apply(lambda row: row[col] / mean_population.at[col, row['Year']] * 1000, axis=1)
    df_tests[col] = np.where(df_tests[col] < 0, 0, df_tests[col])
    
df_tests.drop(columns=['Year'], inplace=True)
    
print(df_tests.head())

for col in df_tests.columns[1:]:
    cap_extreme_values(df_tests, col)

for col in df_tests.columns[1:]:
    df_to_export = df_tests[['Datum', col]]
    filename = convert_umlauts(f'daily_tests_per_1000_people_non-cumulative_{col}.csv')
    df_to_export.to_csv(f'data/cleaned_csvs/{filename}', index=False, sep=';', quotechar='"', quoting=csv.QUOTE_ALL)

print("Done exporting files")