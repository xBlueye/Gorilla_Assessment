# -*- coding: utf-8 -*-
"""
Created on Tue Aug  9 17:45:32 2022

@author: akapi
"""

import pandas as pd
import numpy as np
import random
import datetime
import time
# Load the datasheets
meter_list = pd.read_excel('./gorilla_test_data.xlsx',sheet_name='meter_list')
forecast_table = pd.read_excel('./gorilla_test_data.xlsx',sheet_name='forecast_table')
rate_table = pd.read_excel('./gorilla_test_data.xlsx',sheet_name='rate_table')
# 1)
# Function for the Total Estimated Consumption and Total Cost
def calc_cost(meter_input,forecast_input):
    
    meter_id = meter_input['meter_id']
    aq_kwh = meter_input['aq_kwh']
    exit_zone = meter_input['exit_zone']
    # Variable initialization
    TEC = 0
    TC = 0
    forecast_filter = pd.DataFrame()
    rate_filter = pd.DataFrame()
    
    # Choose the right AQ band
    if aq_kwh < 73200:
        rate_filter = rate_filter.append(rate_table[(rate_table['aq_min_kwh'] == 0) & (rate_table['exit_zone'] == exit_zone)])
    elif aq_kwh < 732000:
        rate_filter = rate_filter.append(rate_table[(rate_table['aq_min_kwh'] == 73200) & (rate_table['exit_zone'] == exit_zone)])
    else:
        rate_filter = rate_filter.append(rate_table[(rate_table['aq_min_kwh'] == 732000) & (rate_table['exit_zone'] == exit_zone)])
        
    # We only need 1 meter ID so there is no need to check the other ones    
    forecast_filter = forecast_filter.append(forecast_input[(forecast_input['meter_id'] == meter_id)])
    
    #print(forecast_filter) 
    #print(rate_filter) 
    
    # A step variable used to pick the right rate
    step = 0
    # Calculate the cost and consumption over the full forecast period
    for i in range(len(forecast_filter)):
        # The rates are updated on the 1st of April and October. When the date of today's forecast is equal to the next update 
        # date , we increase the step variable to use the rate for the appropriate date.
        if step != len(rate_filter) - 1:
            if (forecast_filter.loc[forecast_filter.index[i],'date'] >= rate_filter.loc[rate_filter.index[step+1],'date']):
                step += 1        
        # Total cost is the sum of all the daily costs, calculated by multiplying the forecast for a day with the rate for that day in p
        TC += np.multiply(forecast_filter.loc[forecast_filter.index[i],'kwh'] , rate_filter.loc[rate_filter.index[step],'rate_p_per_kwh'])
    # Rounded tot 2 decimals and converted to pounds
    #print(TEC,TC)
    TEC = np.sum(forecast_filter.loc[:,'kwh'])
    TC = float('{:.2f}'.format(TC / 100))
    #print(TC,round(TEC))
    # The function output is a DataFrame with proper column names.
    return pd.DataFrame([[meter_id,round(TEC),TC]],columns=('meter_id','total_esimated_consumption','total_cost')) 

# 2)
# Function to generate a random meter list

def gen_meter_list(N):

    new_meter_list = pd.DataFrame(columns=('meter_id','aq_kwh','exit_zone'))
    zones = list(set(rate_table.loc[:,'exit_zone'])) # look for unique exit zone names
    #print(zones)
    for n in range(N):
        meter_id = ''
        aq_kwh = 0
        exit_zone = ''
        for i in range(8):  # Generate a random 8 digit ID starting with a non 0 digit
            if i == 0:
                meter_id = meter_id + (str(random.randint(1, 9)))
            else:
                meter_id = meter_id + (str(random.randint(0, 9)))
        
        aq_kwh = random.randint(0, 1000000)  # Generate a random int between 0 and 1 000 000 to be used as AQ
        exit_zone = random.choice(zones)    # Randomly assign the exit zone 
        new_meter_list.loc[n] = [meter_id,aq_kwh,exit_zone] # Add a generated row to a dataframe
        #print(new_meter_list)
        
    return new_meter_list

# 3)
# Function to generate mock consumption data given a meter_list, start date and duration.
def gen_forecast_table(meter_input,start_date,duration):
    new_forecast_table = pd.DataFrame(columns=('meter_id','date','kwh'))
    for i in range(len(meter_input)):
        for j in range(duration):
            new_forecast_table.loc[j + i*duration] = [meter_input.loc[meter_input.index[i],'meter_id'],
                                                       (start_date + datetime.timedelta(days=j)),
                                                       random.uniform(forecast_table['kwh'].min(), forecast_table['kwh'].max())]
    return new_forecast_table

tick = time.time()
out = pd.DataFrame(columns=('meter_id','total_esimated_consumption','total_cost'))
for x in range(len(meter_list)):
    out = out.append(calc_cost(meter_list.loc[meter_list.index[x],:],forecast_table),ignore_index= True)
#print(out)
tock = time.time()  
print('elapsed time for processing original data: {}'.format(tock - tick)) 

tick = time.time()
out = pd.DataFrame(columns=('meter_id','total_esimated_consumption','total_cost'))
new_meter_list = gen_meter_list(853).astype({'meter_id' : 'int64', 'aq_kwh' : 'int64'})
new_forecast_table = gen_forecast_table(new_meter_list, datetime.datetime(2020, 6, 2), 4)
tock = time.time()  
print('elapsed time for generating mock dataset: {}'.format(tock - tick)) 

tick = time.time()
for x in range(len(new_meter_list)):
    out = out.append(calc_cost(new_meter_list.loc[new_meter_list.index[x],:],new_forecast_table),ignore_index= True)
#print(out)   
tock = time.time()  
print('elapsed time for processing dataset: {}'.format(tock - tick)) 


