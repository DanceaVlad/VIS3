import datetime
import numpy as np
import pandas as pd


tests_file_name = 'data/timeline-faelle-bundeslaender.csv'
deaths_file_name = 'data/OGD_gest_kalwo_GEST_KALWOCHE_100.csv'

df_tests = pd.read_csv(tests_file_name, sep=';')  
df_deaths = pd.read_csv(deaths_file_name, sep=';')

print(df_tests.head())

