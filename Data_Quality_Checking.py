#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 30 16:32:19 2020

@author: meerarakesh09
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def ReadData( fileName ):
    """This function takes a filename as input, and returns a dataframe with
    raw data read from that file in a Pandas DataFrame.  The DataFrame index
    should be the year, month and day of the observation.  DataFrame headers
    should be "Date", "Precip", "Max Temp", "Min Temp", "Wind Speed". Function
    returns the completed DataFrame, and a dictionary designed to contain all 
    missing value counts."""
    
    # define column names
    colNames = ['Date','Precip','Max Temp', 'Min Temp','Wind Speed']

    # open and read the file
    DataDF = pd.read_csv("DailyClimateData.txt",header=None, names=colNames,  
                         delimiter=r"\s+",parse_dates=[0])
    DataDF = DataDF.set_index('Date')
    DataDF['Wind Speed'] = DataDF['Wind Speed'].str.replace("`"," ").astype(float)
    
    # define and initialize the missing data dictionary
    ReplacedValuesDF = pd.DataFrame(0, index=["1. No Data"], columns=colNames[1:])
     
    return( DataDF, ReplacedValuesDF )
 
def Check01_RemoveNoDataValues( DataDF, ReplacedValuesDF ):
   
    # replace all -999 values to NaN
    DataDF = DataDF.replace(-999, np.NaN)
    #Record number of values replaced with the index "1. No Data"
    ReplacedValuesDF.loc['1. No Data',:]= DataDF.isna().sum()
    #return dataframe
    return( DataDF, ReplacedValuesDF )
    
def Check02_GrossErrors( DataDF, ReplacedValuesDF ):
   
 # define thresholds and apply to DF
    DataDF['Precip'][(DataDF['Precip']<0)|(DataDF['Precip']>25)] = np.NAN #Check Precip col
    DataDF['Max Temp'][(DataDF['Max Temp']<-25)|(DataDF['Max Temp']>35)] = np.NAN #Check Max temp col
    DataDF['Min Temp'][(DataDF['Min Temp']<-25)|(DataDF['Min Temp']>35)] = np.NAN #Check Min temp col
    DataDF['Wind Speed'][(DataDF['Wind Speed']< 0)|(DataDF['Wind Speed']>25)] = np.NAN #Check Wind temp col

    #record number of values relpaced for each data type in the df
    # replacedvaluesdf with index '2' Gross Error
    # sum NAN values and minus ReplacedValuesDF.loc['1 No Data', :]
    ReplacedValuesDF.loc["2. Gross Error", :] = DataDF.isna().sum() - ReplacedValuesDF.loc['1. No Data', :]
 
    # return df
    return( DataDF, ReplacedValuesDF )
    
    
def Check03_TmaxTminSwapped( DataDF, ReplacedValuesDF ):
    """This function checks for days when maximum air temperture is less than
    minimum air temperature, and swaps the values when found.  The function 
    returns modified DataFrames with data that has been fixed, and with counts 
    of how many times the fix has been applied."""
   # new variable set to zero 
    Tmax = 0
    Tmin = 0
    swap_val = 0 # make a counter to swap
    
    #checks that all Max Temp values are larger than Min temp values 
    #swap values when not true
    
    for i in range (len(DataDF)):
        if DataDF['Max Temp'][i] < DataDF['Min Temp'][i]: # Check if Min is larger than Max
            Tmax = DataDF['Min Temp'][i] #When condition is true assigns maxValue to Min temp 
            Tmin = DataDF['Max Temp'][i] #When ondition is true assigns minValue to Max temp             
            
            DataDF['Max Temp'][i] = Tmax #assign observation valaue
            DataDF['Min Temp'][i] = Tmin #assign observation values

            #print(DataDF['Max Temp'])
            
            swap_val = swap_val + 1 #adding to the counter
        #number of values replaced for each data type in the DataFrame 
        #ReplacedValuesDF with the index "3. Swapped"    
    ReplacedValuesDF.loc["3. Swapped", :] = [0,swap_val,swap_val,0]

    return( DataDF, ReplacedValuesDF )
    
def Check04_TmaxTminRange( DataDF, ReplacedValuesDF ):
    """This function checks for days when maximum air temperture minus 
    minimum air temperature exceeds a maximum range, and replaces both values 
    with NaNs when found.  The function returns modified DataFrames with data 
    that has been checked, and with counts of how many days of data have been 
    removed through the process."""
    
   # new variable set to zero 
    range =0
    for i, row in DataDF.iterrows():
         if (row['Max Temp'] - row['Min Temp'])>25:
             DataDF.loc[i,['Max Temp','Min Temp']] = np.NaN  #to replace both temps to NaN
             range = range + 1 
    ReplacedValuesDF.loc["4. Range Fail", :] = [0,range,range,0]
    return( DataDF, ReplacedValuesDF )   

# the following condition checks whether we are running as a script, in which 
# case run the test code, otherwise functions are being imported so do not.
# put the main routines from your code after this conditional check.

if __name__ == '__main__':

    fileName = "DataQualityChecking.txt"
    DataDF, ReplacedValuesDF = ReadData(fileName)
    rawdata = DataDF.copy() #copy original data
    
    print("\nRaw data.....\n", DataDF.describe())
    
    DataDF, ReplacedValuesDF = Check01_RemoveNoDataValues( DataDF, ReplacedValuesDF ) 
    print("\nMissing values removed.....\n", DataDF.describe())
    
    
    DataDF, ReplacedValuesDF = Check02_GrossErrors( DataDF, ReplacedValuesDF )
    print("\nCheck for gross errors complete.....\n", DataDF.describe())
   
    
    DataDF, ReplacedValuesDF = Check03_TmaxTminSwapped( DataDF, ReplacedValuesDF )
    print("\nCheck for swapped temperatures complete.....\n", DataDF.describe())
    
    
    DataDF, ReplacedValuesDF = Check04_TmaxTminRange( DataDF, ReplacedValuesDF )
    print("\nAll processing finished.....\n", DataDF.describe())
    print("\nFinal changed values counts.....\n", ReplacedValuesDF)
    
    #plotting all the variables showing before and after data checking
    
    #plot for precipitation
    rawdata['Precip'].plot(color='red', label='Before checking', linewidth=1) 
    DataDF['Precip'].plot(figsize = (6,4), label = 'After checking', linewidth=1)
    plt.title("Precipitation before and after data checking")
    plt.legend()
    plt.xlabel('Date')
    plt.ylabel('Precipitation (mm)')
    plt.savefig('Precipitation.png')# save plot
    plt.show()#display plot
    plt.close()#display plot
    
    #plot for Maximum temperature
    rawdata['Max Temp'].plot(color='red', label='Before checking', linewidth=1)
    DataDF['Max Temp'].plot(figsize = (6,4), label = 'After checking', linewidth=1)
    plt.title("Maximum Temperature before and after data checking")
    plt.legend()
    plt.xlabel('Date')
    plt.ylabel('Maximum Temperature')
    plt.savefig('Max Temp.png')# save plot
    plt.show() #display plot
    plt.close() #close plot
    
    #plot for Minimum temperature
    rawdata['Min Temp'].plot(color='red', label='Before checking', linewidth=1)
    DataDF['Min Temp'].plot(figsize = (6,4), label = 'After checking', linewidth=1)
    plt.title("Minimum Tempearture before and after checking")
    plt.legend()
    plt.xlabel('Date')
    plt.ylabel('Minimum Temperature')
    plt.savefig('Min Temp.png')# save plot
    plt.show()#display plot
    plt.close() #close plot
    
    #plot for wind speed
    rawdata['Wind Speed'].plot(color='red', label='Before checking', linewidth=1)
    DataDF['Wind Speed'].plot(figsize = (6,4), label = 'After checking', linewidth=1)
    plt.title("Wind speed before and after checking")
    plt.legend()
    plt.xlabel('Date')
    plt.ylabel('Wind Speed')
    plt.savefig('windspeed.png')# save plot
    plt.show()#display plot
    plt.close() #close plot
    