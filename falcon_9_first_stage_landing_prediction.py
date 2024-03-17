# -*- coding: utf-8 -*-
"""Falcon 9 first stage Landing Prediction.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1V486Gqjve6WPLEVqhs4EKtZrS4Xq-C9L
"""

# Requests allows us to make HTTP requests which we will use to get data from an API
import requests
# Pandas is a software library written for the Python programming language for data manipulation and analysis.
import pandas as pd
# NumPy is a library for the Python programming language, adding support for large, multi-dimensional arrays and matrices, along with a large collection of high-level mathematical functions to operate on these arrays
import numpy as np
# Datetime is a library that allows us to represent dates
import datetime

# Setting this option will print all columns of a dataframe
pd.set_option('display.max_columns', None)
# Setting this option will print all of the data in a feature
pd.set_option('display.max_colwidth', None)

# Takes the dataset and uses the rocket column to call the API and append the data to the list
def getBoosterVersion(data):
    for x in data['rocket']:
       if x:
        response = requests.get("https://api.spacexdata.com/v4/rockets/"+str(x)).json()
        BoosterVersion.append(response['name'])

# Takes the dataset and uses the launchpad column to call the API and append the data to the list
def getLaunchSite(data):
    for x in data['launchpad']:
       if x:
         response = requests.get("https://api.spacexdata.com/v4/launchpads/"+str(x)).json()
         Longitude.append(response['longitude'])
         Latitude.append(response['latitude'])
         LaunchSite.append(response['name'])

# Takes the dataset and uses the payloads column to call the API and append the data to the lists
def getPayloadData(data):
    for load in data['payloads']:
       if load:
        response = requests.get("https://api.spacexdata.com/v4/payloads/"+load).json()
        PayloadMass.append(response['mass_kg'])
        Orbit.append(response['orbit'])

# Takes the dataset and uses the cores column to call the API and append the data to the lists
def getCoreData(data):
    for core in data['cores']:
            if core['core'] != None:
                response = requests.get("https://api.spacexdata.com/v4/cores/"+core['core']).json()
                Block.append(response['block'])
                ReusedCount.append(response['reuse_count'])
                Serial.append(response['serial'])
            else:
                Block.append(None)
                ReusedCount.append(None)
                Serial.append(None)
            Outcome.append(str(core['landing_success'])+' '+str(core['landing_type']))
            Flights.append(core['flight'])
            GridFins.append(core['gridfins'])
            Reused.append(core['reused'])
            Legs.append(core['legs'])
            LandingPad.append(core['landpad'])

spacex_url="https://api.spacexdata.com/v4/launches/past"

response = requests.get(spacex_url)

print(response.content)

static_json_url='https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DS0321EN-SkillsNetwork/datasets/API_call_spacex_api.json'

response.status_code

# Use json_normalize meethod to convert the json result into a dataframe
import pandas as pd

normalized = response.json()

# Convert the JSON data to a Pandas DataFrame
data = pd.json_normalize(normalized)

data.head()

# Lets take a subset of our dataframe keeping only the features we want and the flight number, and date_utc.
data = data[['rocket', 'payloads', 'launchpad', 'cores', 'flight_number', 'date_utc']]

# We will remove rows with multiple cores because those are falcon rockets with 2 extra rocket boosters and rows that have multiple payloads in a single rocket.
data = data[data['cores'].map(len)==1]
data = data[data['payloads'].map(len)==1]

# Since payloads and cores are lists of size 1 we will also extract the single value in the list and replace the feature.
data['cores'] = data['cores'].map(lambda x : x[0])
data['payloads'] = data['payloads'].map(lambda x : x[0])

# We also want to convert the date_utc to a datetime datatype and then extracting the date leaving the time
data['date'] = pd.to_datetime(data['date_utc']).dt.date

# Using the date we will restrict the dates of the launches
data = data[data['date'] <= datetime.date(2020, 11, 13)]

#Global variables
BoosterVersion = []
PayloadMass = []
Orbit = []
LaunchSite = []
Outcome = []
Flights = []
GridFins = []
Reused = []
Legs = []
LandingPad = []
Block = []
ReusedCount = []
Serial = []
Longitude = []
Latitude = []

BoosterVersion

# Call getBoosterVersion
getBoosterVersion(data)

BoosterVersion[0:5]

# Call getLaunchSite
getLaunchSite(data)

LaunchSite[0:5]

# Call getPayloadData
getPayloadData(data)

# Call getCoreData
getCoreData(data)

launch_dict = {'FlightNumber': list(data['flight_number']),
'Date': list(data['date']),
'BoosterVersion':BoosterVersion,
'PayloadMass':PayloadMass,
'Orbit':Orbit,
'LaunchSite':LaunchSite,
'Outcome':Outcome,
'Flights':Flights,
'GridFins':GridFins,
'Reused':Reused,
'Legs':Legs,
'LandingPad':LandingPad,
'Block':Block,
'ReusedCount':ReusedCount,
'Serial':Serial,
'Longitude': Longitude,
'Latitude': Latitude}

# Create a data from launch_dict

launch_df = pd.DataFrame(launch_dict)

launch_df.head()

# Filter the data DataFrame to keep only Falcon 9 launches
data_falcon9 = launch_df[launch_df['BoosterVersion'] != 'Falcon 1']

data_falcon9.head()

data_falcon9.loc[:,'FlightNumber'] = list(range(1, data_falcon9.shape[0]+1))
data_falcon9

data_falcon9.describe().T

data_falcon9.isnull().sum()

duplicated = data_falcon9[data_falcon9.duplicated(keep=False)] #for clean dataset we should firstly check if there exist duplicated values. If yes we should drop them.
duplicated

# Identify numerical features
numerical_features = data_falcon9.select_dtypes(include=['float64', 'int64']).columns
print(numerical_features)

# Fill missing values in numerical columns
for i in numerical_features:
    data_falcon9[i].fillna(value=data_falcon9[i].mean(), inplace=True)

data_falcon9.head()

data_falcon9.to_csv('dataset_part_1.csv', index=False)

"""Web scrap Falcon 9 launch records with BeautifulSoup:

Extract a Falcon 9 launch records HTML table from Wikipedia
Parse the table and convert it into a Pandas data frame
"""

!pip3 install beautifulsoup4
!pip3 install requests

import sys

import requests
from bs4 import BeautifulSoup
import re
import unicodedata
import pandas as pd

def date_time(table_cells):
    """
    This function returns the data and time from the HTML table cell
    Input: the  element of a table data cell extracts extra row
    """
    return [data_time.strip() for data_time in list(table_cells.strings)][0:2]

def booster_version(table_cells):
    """
    This function returns the booster version from the HTML  table cell
    Input: the  element of a table data cell extracts extra row
    """
    out=''.join([booster_version for i,booster_version in enumerate( table_cells.strings) if i%2==0][0:-1])
    return out

def landing_status(table_cells):
    """
    This function returns the landing status from the HTML table cell
    Input: the  element of a table data cell extracts extra row
    """
    out=[i for i in table_cells.strings][0]
    return out


def get_mass(table_cells):
    mass=unicodedata.normalize("NFKD", table_cells.text).strip()
    if mass:
        mass.find("kg")
        new_mass=mass[0:mass.find("kg")+2]
    else:
        new_mass=0
    return new_mass


def extract_column_from_header(row):
    """
    This function returns the landing status from the HTML table cell
    Input: the  element of a table data cell extracts extra row
    """
    if (row.br):
        row.br.extract()
    if row.a:
        row.a.extract()
    if row.sup:
        row.sup.extract()

    colunm_name = ' '.join(row.contents)

    # Filter the digit and empty names
    if not(colunm_name.strip().isdigit()):
        colunm_name = colunm_name.strip()
        return colunm_name

"""Scrape the data from a snapshot of the List of Falcon 9 and Falcon Heavy launches Wikipage updated on 9th June 2021"""

static_url = "https://en.wikipedia.org/w/index.php?title=List_of_Falcon_9_and_Falcon_Heavy_launches&oldid=1027686922"

response2 = requests.get(static_url)

# Check if the request was successful
if response2.status_code == 200:
    # Create a BeautifulSoup object from the response text content
    soup = BeautifulSoup(response2.text, 'html.parser')
    print("BeautifulSoup object created successfully.")
else:
    print("Failed to retrieve data from the URL.")

# Use soup.title attribute
title_element = soup.title

# Print the text inside the <title> tag
print(title_element.text)

"""Extract all column/variable names from the HTML table header"""

# Use the find_all function in the BeautifulSoup object, with element type `table`

html_tables = soup.find_all('table')

# Let's print the third table and check its content
first_launch_table = html_tables[2]
print(first_launch_table)

""" we just need to iterate through the <th> elements and apply the provided extract_column_from_header() to extract column name one by one."""

column_names = []

# Apply find_all() function with 'th' element on first_launch_table
first_launch_table_th = first_launch_table.find_all('th')

# Iterate each th element and apply the provided extract_column_from_header() to get a column name
for th in first_launch_table_th:
    column_name = extract_column_from_header(th)
    # Append the Non-empty column name (`if name is not None and len(name) > 0`) into a list called column_names
    if (column_name != None and len(column_name) > 0):
      column_names.append(column_name)


      # if column_name:
      #   column_names.append(column_name)

print(column_names)

"""Create a data frame by parsing the launch HTML tables"""

launch_dict= dict.fromkeys(column_names)

# Remove an irrelvant column
del launch_dict['Date and time ( )']

# Let's initial the launch_dict with each value to be an empty list
launch_dict['Flight No.'] = []
launch_dict['Launch site'] = []
launch_dict['Payload'] = []
launch_dict['Payload mass'] = []
launch_dict['Orbit'] = []
launch_dict['Customer'] = []
launch_dict['Launch outcome'] = []
# Added some new columns
launch_dict['Version Booster']=[]
launch_dict['Booster landing']=[]
launch_dict['Date']=[]
launch_dict['Time']=[]

"""Next, we just need to fill up the launch_dict with launch records extracted from table rows.

Usually, HTML tables in Wiki pages are likely to contain unexpected annotations and other types of noises, such as reference links B0004.1[8], missing values N/A [e], inconsistent formatting, etc.
"""

extracted_row = 0
#Extract each table
for table_number,table in enumerate(soup.find_all('table',"wikitable plainrowheaders collapsible")):
   # get table row
    for rows in table.find_all("tr"):
        #check to see if first table heading is as number corresponding to launch a number
        if rows.th:
            if rows.th.string:
                flight_number=rows.th.string.strip()
                flag=flight_number.isdigit()
        else:
            flag=False
        #get table element
        row=rows.find_all('td')
        #if it is number save cells in a dictonary
        if flag:
            extracted_row += 1
            # Flight Number value
            flight_number = launch_dict['Flight No.']
            print(flight_number)
            datatimelist=date_time(row[0])

            # Date value
            date = launch_dict['Date']
            date = datatimelist[0].strip(',')
            print(date)

            # Time value
            time = launch_dict['Time']
            time = datatimelist[1]
            print(time)

            # Booster version
            bv = launch_dict['Version Booster']
            bv=booster_version(row[1])
            if not(bv):
                bv=row[1].a.string
            print(bv)

            # Launch Site
            launch_site = row[2].a.string
            launch_dict['Launch Site'] = launch_site
            print(launch_site)

            # Payload
            payload = row[3].a.string
            launch_dict['Payload'] = payload

            # Payload Mass
            payload_mass = get_mass(row[4])
            launch_dict['Payload mass'] = payload_mass

            # Orbit
            orbit = row[5].a.string
            launch_dict['Orbit'] = orbit

            # Customer
            customer_element = row[6].a
            if customer_element:
              customer = customer_element.string
              launch_dict['Customer'] = customer
            else:
              launch_dict['Customer'] = None  # Or any default value you prefer



            # Launch outcome
            launch_outcome = list(row[7].strings)[0]
            launch_dict['Launch outcome'] = launch_outcome

            # Booster landing
            booster_landing = landing_status(row[8])
            launch_dict['Booster landing'] = booster_landing

df= pd.DataFrame({ key:pd.Series(value) for key, value in launch_dict.items() })

df.to_csv('spacex_web_scraped.csv', index=False)

df