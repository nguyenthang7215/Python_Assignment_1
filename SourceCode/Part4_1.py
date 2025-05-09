import pandas as pd 
from bs4 import BeautifulSoup 
from selenium import webdriver
import time
from rapidfuzz import process, fuzz
import os 


## 4.1. Collect player transfer values for the 2024-2025 season. Only collect for the players 
# whose playing time is greater than 900 minutes

url = "https://www.footballtransfers.com/us/values/players/most-valuable-soccer-players/playing-in-uk-premier-league"

driver = webdriver.Chrome()

players_data = [] # Store data

for i in range(1, 23): # Get data from all 22 pages
    url_tmp = url
    if i != 1: 
        url_tmp += "/" + str(i) 
    
    driver.get(url_tmp) # Open the webpage
    time.sleep(3) 
    
    html = driver.page_source # Get the entire HTML source of the current page
    soup = BeautifulSoup(html, "html.parser") 
    
    table = soup.find("table", class_ = "table table-hover no-cursor table-striped leaguetable mvp-table mb-0") # Find the table using its class
    
    if table: 
        
        rows = table.find_all("tr") 
        for row in rows: 
            cols = row.find_all("td") 
            
            if cols: 
                # Get the player's name
                player_name = cols[2].find("a").text.strip() # Found in the <a> tag
                
                # Get the team name
                team_col = cols[4].find("span", class_ = "td-team__teamname") # The <span> tag contains the team name
                team_name = team_col.text.strip() if team_col else "Unknown" 
                
                # Get the player's value
                value = cols[-1].text.strip() 
                
                # Add the data to the list
                players_data.append({"Player": player_name, "Team": team_name, "Value": value}) 
    
    
driver.quit() # Close all browser windows
players_value = pd.DataFrame(players_data) # Convert the list to a DataFrame


df = pd.read_csv(os.path.join("SourceCode","results.csv"))

cols = ["Player", "Nation", "Squad", "Pos", "Age", "Min"]
players_900mins = df[df["Min"] > 900][cols].reset_index(drop = True) # Players who played more than 900 minutes

# Create a new column "Value" in players_900mins to store the player's value
players_900mins["Value"] = None

for index, row in players_900mins.iterrows(): # Iterate through each row in players_900mins
    
    # Get the player's name
    player_name = row["Player"]  
    
    # Find the closest matching player in players_value
    match = process.extractOne(player_name, players_value["Player"], scorer = fuzz.token_sort_ratio) # Fuzzy match player names
    
    if match and match[1] > 80:  # Similarity threshold > 80%, match[1]: Similarity score (0-100)
        
        matched_player = match[0]  # Matched player name
        
        value = players_value.loc[players_value["Player"] == matched_player, "Value"].values[0] # Get the value from players_value
        # After filtering rows, only take the "Value" column, convert it to a 1D array, and get the first element
        
        players_900mins.at[index, "Value"] = value  # Assign the value to the "Value" column


players_900mins.dropna(inplace = True) # Remove rows with null values in the "Value" column

players_900mins.reset_index(drop = True, inplace = True) # Reset the index

csv_path = os.path.join("SourceCode", "players_900mins_value.csv")
players_900mins.to_csv(csv_path, index = False)