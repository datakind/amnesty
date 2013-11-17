##
# Function to make a timeseries (to write either to a dataframe or a json)
#  from the csv file 
# 

import pandas as pd
import math
from collections import defaultdict

class CountryData:
    
    def __init__(self, lotus_dataframe):
        ''' take the lotus dataframe and make a dict of dataframes by country
        '''
        countries = lotus_dataframe['iso3'][ lotus_dataframe.iso3 != 'NA' ]
        countries = set( countries )
        self.countries = [ c for c in countries if not type(c)==float ]

        self.df = lotus_dataframe
    
    def get_timeseries(self, country):
        ''' get a pandas timeseries of the number of UA's in a country. 
            The country must be in ISO3 format, e.g. USA.
        '''
        # we'll keep a dictionary of counts of UA's per year
        year_counts = defaultdict(float)
        country_df = self.get_country_df( country )
        years = country_df['year']
        
        # count number of times each year is found in the list of years
        for year in years:
            if not math.isnan(year) and year > 1900:
                key = pd.datetime(int(year), 1, 1)
                year_counts[key] += 1.0
        
        # create a pandas timeseries of the counts per year
        timeseries = pd.TimeSeries(data = year_counts.values(), 
            index = year_counts.keys())

        return timeseries

    def get_json_ts(self, country):
        ''' Get a single country's timeseries in json format. Meant for use
            with get_all_countries_timeseries, which then is fed to d3 for 
            timeseries plotting.
            Result: (ex)  "USA" : { "actions" : [ {"year":2003,"count":23.0},
                {"year":2004,"count":10.0},... ] }
        '''        
        # grab pandas timeseries
        ts = self.get_timeseries( country )

        # build json string by appending successive data points
        json_string = ' "' + country + '" : { "actions" : [ '
        for I, timeIndex in enumerate(ts.index):

        	json_string += '{ "year":'+ str(timeIndex.year) + ',"count":' + str(ts[ timeIndex ]) + \
        	'} '
        	if I < len(ts) - 1:
                    json_string += ', '

        json_string += ' ] }'
        
        return json_string
    

    def get_country_df(self, country):
        ''' wrapper to get dataframe for a single country
        '''
        return self.df[ self.df['iso3'] == country ]
        
    def get_all_countries_timeseries(self): # (self, countries='All')
        ''' make a json string of timeseries for all countries based on 
            making json_timeseries with method self.get_json_ts( country )
        '''
        # build json string by appending individual json timeseries
        json_string = '{'
        for I, country in enumerate(self.countries):

        	ts_json = self.get_json_ts( country )
        	json_string += ts_json

        	if I < len(self.countries) - 1:
        		json_string += ' , '

        json_string += '}'

        return json_string

        
