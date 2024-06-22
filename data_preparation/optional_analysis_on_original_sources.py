import datetime
import numpy as np
import pandas as pd


tests_file_name = 'data/datasets/timeline-faelle-bundeslaender.csv'
deaths_file_name = 'data/datasets/OGD_gest_kalwo_GEST_KALWOCHE_100.csv'
    
df_tests = pd.read_csv(tests_file_name, sep=';')
df_deaths = pd.read_csv(deaths_file_name, sep=';')
    
# print the first few rows of the dataframes
# print(df_tests.head())
# print(df_deaths.head())
    
# rename columns in test dataframe
df_deaths = df_deaths.rename(columns={"C-KALWOCHE-0": "cal_week", "C-B00-0": "state", "C-C11-0": "gender", "F-ANZ-1": "counts" })
# print(df_deaths.head())
    
# name of states
# print(df_tests["Name"].unique())
    
# rename states
df_tests["Name"] = df_tests["Name"].replace({"Kärnten" : "Kaernten", "Niederösterreich" : "Niederoesterreich", "Oberösterreich" : "Oberoesterreich", "Österreich" : "Oesterreich"})
# print(df_tests["Name"].unique())
# print(df_tests.head())
    
# check that the sum of tests equals the total number of tests
violating_rows = df_tests[df_tests["TestungenPCR"] + df_tests["TestungenAntigen"] != df_tests["Testungen"]]
# print(violating_rows)
# looks good

df_deaths['year'] = [d.split("-")[1][:4] for d in df_deaths['cal_week']]
df_deaths['cal_week'] = [d.split("-")[1][4:] for d in df_deaths['cal_week']]
df_deaths['formatted_date'] = df_deaths.year.astype(str)  + df_deaths.cal_week.astype(str) + '0'
df_deaths['date'] = pd.to_datetime(df_deaths['formatted_date'], format='%Y%W%w')

df_deaths['conv_date']= df_deaths.date.map(datetime.datetime.toordinal)
print(df_deaths.head())


# TODO use ids to merge dataframes


# get rid of ids of states (identified by names)
df_tests.drop(columns=["BundeslandID"], inplace=True)
print(df_tests.head())