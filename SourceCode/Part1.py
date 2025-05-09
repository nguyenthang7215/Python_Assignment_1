from selenium import webdriver 
from bs4 import BeautifulSoup
import pandas as pd
import time
from io import StringIO
import os

driver = webdriver.Chrome() 

## Get the fbref page containing detailed player statistics

# Get the links to the statistical tables
links = { 
    "stats_standard" : "https://fbref.com/en/comps/9/stats/Premier-League-Stats",
    "stats_keeper" : "https://fbref.com/en/comps/9/keepers/Premier-League-Stats",
    "stats_shooting" : "https://fbref.com/en/comps/9/shooting/Premier-League-Stats",
    "stats_passing" : "https://fbref.com/en/comps/9/passing/Premier-League-Stats", 
    "stats_gca" : "https://fbref.com/en/comps/9/gca/Premier-League-Stats",
    "stats_defense" : "https://fbref.com/en/comps/9/defense/Premier-League-Stats",
    "stats_possession" : "https://fbref.com/en/comps/9/possession/Premier-League-Stats",
    "stats_misc" : "https://fbref.com/en/comps/9/misc/Premier-League-Stats"
    }


## Use BeautifulSoup to parse HTML + Pandas to extract data

data = {} # Store data

for id, link in links.items() : 
    driver.get(link) # Open the web page
    time.sleep(3)
    
    html = driver.page_source # Get the entire HTML source of the current page
    soup = BeautifulSoup(html, "html.parser") 
    
    table = soup.find("table", {"id" : id}) # Find the table using its id
    
    if table : 
        df = pd.read_html(StringIO(str(table)), header = 1)[0] 
        # Convert the table to a DataFrame, get the first table, header=1 skips the unnecessary first row

        df.drop(df.columns[0], axis = 1, inplace = True) # Delete the first column
        
        data[id] = df # Store the DataFrame in the data dictionary

driver.quit() # Close all web browsers


## Extract data according to requirements

df_result = data["stats_standard"] # Use the stats_standard table as the main table

# Combine the remaining tables into df_result
for id, df_tmp in data.items():
    if id != "stats_standard":
        # Remove the duplicate Player column like on the website
        df_tmp = df_tmp[ df_tmp['Player'] != 'Player' ] 
        
         # Rename columns, avoiding column name conflicts
        df_tmp = df_tmp.rename(columns = lambda x : x if x in ["Player", "Nation", "Squad", "Pos"] else f"{id}_{x}")
        
        # Merge the data into df_result
        df_result = pd.merge(df_result, df_tmp, on = ["Player", "Nation", "Squad", "Pos"], how = "left")


# 78 main columns
columns_to_keep = [ 
        ## Standard: 
        "Player", "Nation", "Squad", "Pos", "Age",            
        # Playing Time : matches played, starts, minutes 
        "MP", "Starts", "Min",
        # Performance : goals, assists, yellow cards, red cards 
        "Gls", "Ast", "CrdY", "CrdR",
        # Expected: expected goals (xG), expedted Assist Goals (xAG) 
        "xG", "xAG",
        # Progression: PrgC, PrgP, Prg 
        "PrgC", "PrgP", "PrgR",
        # Per 90 minutes: Gls, Ast, xG, xGA 
        "Gls.1", "Ast.1", "xG.1", "xAG.1",
    
        ## Goalkeeping: 
        # Performance: goals against per 90mins (GA90), Save%, CS% 
        # Penalty Kicks: penalty kicks Save% 
        "stats_keeper_GA90", "stats_keeper_Save%", "stats_keeper_CS%", 
        "stats_keeper_Save%.1",  
         
        ## Shooting: 
        # Standard: shoots on target percentage (SoT%), Shoot on Target per 90min (SoT/90),
        # goals/shot (G/sh), average shoot distance (Dist) 
        "stats_shooting_SoT%", "stats_shooting_SoT/90", "stats_shooting_G/Sh", "stats_shooting_Dist",
        
        ## Passing:
        # Total: passes completed (Cmp),Pass completion (Cmp%), progressive
        # passing distance (TotDist) 
        # Short: Pass completion (Cmp%),
        # Medium: Pass completion (Cmp%),
        # Long: Pass completion (Cmp%),
        # Expected: key passes (KP), pass into final third (1/3), pass into penalty
        # area (PPA), CrsPA, PrgP
        "stats_passing_Cmp", "stats_passing_Cmp%", "stats_passing_TotDist", 
        "stats_passing_Cmp%.1", 
        "stats_passing_Cmp%.2", 
        "stats_passing_Cmp%.3", 
        "stats_passing_KP", "stats_passing_1/3", "stats_passing_PPA", "stats_passing_CrsPA", "stats_passing_PrgP", 
        
        ## Goal and Shot Creation:
        # SCA: SCA, SCA90
        # GCA: GCA, GCA90
        "stats_gca_SCA", "stats_gca_SCA90",
        "stats_gca_GCA", "stats_gca_GCA90",
        
        ## Defensive Actions:
        # Tackles: Tkl, TklW
        # Challenges: Att, Lost
        # Blocks: Blocks, Sh, Pass, Int
        "stats_defense_Tkl", "stats_defense_TklW",
        "stats_defense_Att", "stats_defense_Lost",
        "stats_defense_Blocks", "stats_defense_Sh", "stats_defense_Pass", "stats_defense_Int",
        
        ## Possession:
        # Touches: Touches, Def Pen, Def 3rd, Mid 3rd, Att 3rd, Att Pen
        # Take-Ons: Att, Succ%, Tkld%
        # Carries: Carries, ProDist, ProgC, 1/3, CPA, Mis, Dis
        # Receiving: Rec, PrgR
        "stats_possession_Touches", "stats_possession_Def Pen", "stats_possession_Def 3rd",
        "stats_possession_Mid 3rd", "stats_possession_Att 3rd", "stats_possession_Att Pen",
        "stats_possession_Att", "stats_possession_Succ%", "stats_possession_Tkld%",
        "stats_possession_Carries", "stats_possession_PrgDist", "stats_possession_PrgC",
        "stats_possession_1/3", "stats_possession_CPA", "stats_possession_Mis", "stats_possession_Dis",
        "stats_possession_Rec", "stats_possession_PrgR",
        
        ## Miscellaneous Stats:
        # Performance: Fls, Fld, Off, Crs, Recov
        # Aerial Duels: Won, Lost, Won%
        "stats_misc_Fls", "stats_misc_Fld", "stats_misc_Off", "stats_misc_Crs", "stats_misc_Recov",
        "stats_misc_Won", "stats_misc_Lost", "stats_misc_Won%",
                   ] 

## Filter players, rename, sort

df_result = df_result[columns_to_keep] # Select the main columns

# Fill empty cells with N/a
df_result = df_result.fillna("N/a") 

# Get the capitalized country name
df_result["Nation"] = df_result["Nation"].str.split().str[-1] 

# Convert the Min column to numeric
df_result["Min"] = pd.to_numeric(df_result["Min"], errors = "coerce") # Convert to numeric, if it fails, convert to NaN

# Filter players who played more than 90 minutes
df_result = df_result[df_result["Min"] > 90]

# Sort by player name
df_result = df_result.sort_values(by = ["Player"])

# print(df_result.shape) # Size of the DataFrame (number of rows, number of columns) (494, 78)


## Save the data to a csv file
csv_path = os.path.join("SourceCode", "results.csv")
df_result.to_csv(csv_path, index = False) 