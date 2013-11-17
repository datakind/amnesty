''' Script for building timeseries json for all countries to be used with d3.
    Author: Matt Turner (maturner01@gmail.com)
'''
import pandas as pd
from make_country_timeseries import CountryData

# import lotus csv as dataframe
df = pd.read_csv('lotus_database_w_iso3.csv')

# create CountryData object
country_data = CountryData( df )

# create json string of all nation's UA counts by year
world_json = country_data.get_all_countries_timeseries()

# write json to file
f = open( 'ts_json.json', 'w' )
f.write( world_json )
f.close()


