#!/usr/bin/env python3

# This is from a tutorial located at
# http://blog.kaggle.com/2017/01/31/scraping-for-craft-beers-a-dataset-creation-tutorial/

# data from this url
# http://www.craftcans.com/db.php?search=all&sort=beerid&ord=desc&view=text

from urllib.request import urlopen
 
from bs4 import BeautifulSoup
import pandas as pd
import re
import csv

# Determines if a table_row is a beer entry
def is_beer_entry(table_row):
    row_cells = table_row.findAll("td")
    beer_id = get_beer_id(row_cells[0].text)
    return ( len(row_cells) == 8 and beer_id )
 
# Return the beer entry numerical identifier from the "Entry" column.
def get_beer_id(cell_value):
    match = re.match("^(\d{1,4})\.$", cell_value)
    if match is None or len(match.groups()) != 1:
        return None
    return int(match.group(1))
        
def get_all_beers(html_soup):

    # I got rid of variable which was just holding results of findall("tr"),
    # got rid of an else, and turned this into a generator
    for table_row in html_soup.findAll("tr"):
        if not is_beer_entry(table_row):
            continue
        
        row_cells = table_row.findAll("td")
        beer_entry = {
            "id": get_beer_id(row_cells[0].text),
            "name": row_cells[1].text,
            "brewery_name": row_cells[2].text,
            "brewery_location": row_cells[3].text,
            "style": row_cells[4].text,
            "size": row_cells[5].text,
            "abv": row_cells[6].text,    
            "ibu": row_cells[7].text
        }

        yield beer_entry
        
def stringPrctToFloat(value):
    try:
        return float(value.strip('%')) / 100
    except ValueError:
        return None
        
def stringToInt(value):
    try:
        return int(value)
    except ValueError:
        return None

    
# To be polite.  I'm going to dump this data into a csv and have 
# subsequent runs read it from there
# url = "http://craftcans.com/db.php?search=all&sort=beerid&ord=desc&view=text"
# html = urlopen(url)
# html_soup = BeautifulSoup(html, 'html.parser')

csvFile = 'beerData.csv'

# with open(csvFile, 'w') as outFile:
    # writer = None
    # for i, beer in enumerate(get_all_beers(html_soup)):
        # if i == 0:
            # writer = csv.DictWriter(
                # outFile,
                # fieldnames=list(beer.keys()))
            # writer.writeheader()
        # writer.writerow(beer)
        
df = pd.read_csv(csvFile)

breweries = df[["brewery_location", "brewery_name"]]
breweries = breweries.drop_duplicates()

# After drop_duplicates the indices in brewery are the index values for
# the first occurence of each brewery. i.e. 0, 6, 19, 24, 30, etc.  
# reset_index(drop=True) gives you a basic 1, 2, 3, ... index
breweries = breweries.reset_index(drop=True)

# Copy index into a column
breweries["id"] = breweries.index

# Join the two data frames
beers = pd.merge(
    df,
    breweries,
    left_on=["brewery_name", "brewery_location"],
    right_on=["brewery_name", "brewery_location"],
    sort=True,  # sort according to join columns
    # suffixes to add to disambiguate column names (the id columns from the
    # two dataframes in this case
    suffixes=('_beer', '_brewery') 
)

# Extract certain columns
beers = beers[["abv", "ibu", "id_beer", "name", "size", "style", "id_brewery"]]

# rename the 
beers.rename(
    inplace=True, 
    columns={
        "id_beer": "id",
        "id_brewery": "brewery_id"
    }
)

# Split the brewery_location column in two and create two new columns
breweries["city"] = breweries["brewery_location"].apply(
    lambda location: location.split(",")[0])
breweries["state"] = breweries["brewery_location"].apply(
    lambda location: location.split(",")[1])

# Drop brewery_location column.  Rename brewery_name to name 
breweries = breweries[["brewery_name", "city", "state"]]
breweries.rename(inplace=True, columns={"brewery_name": "name"})


beers['abv'] = beers['abv'].apply(stringPrctToFloat)
beers['ibu'] = beers['ibu'].apply(stringToInt)














