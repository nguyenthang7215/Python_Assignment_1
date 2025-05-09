import pandas as pd 
import matplotlib.pyplot as plt
import os

## Data processing

df = pd.read_csv(os.path.join("SourceCode","results.csv"))

# Split the Age column into Year and Day, then calculate the age in years
df[['Year', 'Day']] = df['Age'].str.split('-', expand = True).astype(int)
df['Age'] = (df['Year'] + df['Day'] / 365).round(2)
df.drop(columns=['Year', 'Day'], inplace = True) 


## Find the 3 highest and 3 lowest scores for each statistic

top_3_path = os.path.join("SourceCode", "top_3.txt") 
with open(top_3_path, "w", encoding = "utf-8") as f : 
    for col in df.columns[4:] : 
        # Convert the column to numeric and round to 2 decimal places
        # If conversion fails, replace with NaN
        df[col] = pd.to_numeric(df[col], errors = "coerce").round(2) 
        
        f.write(f"------------ Statistics for {col} ------------ \n")
        
        # Find the 3 highest scores
        f.write(f"3 highest scores :  \n")
        f.write( df.nlargest(3, col)[["Player", "Nation", "Squad", "Pos", col]].to_string(index = False) )
        
        # Find the 3 lowest scores
        f.write(f"\n3 lowest scores : \n")
        f.write( df.nsmallest(3, col)[["Player", "Nation", "Squad", "Pos", col]].to_string(index = False) )

        f.write("\n\n")
        
        
## Find the median for each statistic. Calculate the mean and standard deviation
# for each statistic across all players and for each team    

# Select the columns to calculate statistics
cols = df.columns[4:]

# Calculate median, mean, std for each team
team = df.groupby("Squad")[cols].agg(["median", "mean", "std"]).round(2)
team.columns = [f"{stat.capitalize()} of {name}" for name, stat in team.columns] # Convert multi-index to simple column names 
team.reset_index(inplace = True)

# Calculate median, mean, std for all  
median = df[cols].median().round(2)
mean = df[cols].mean().round(2)
std = df[cols].std().round(2)

# Creare a new row for the overall statistics
row = {"Squad" : "all"}
for col in cols:
    row[f"Median of {col}"] = median[col]
    row[f"Mean of {col}"] = mean[col]
    row[f"Std of {col}"] = std[col]

df_all = pd.DataFrame([row])

# Add the overall statistics to the team DataFrame
table = pd.concat([df_all, team], ignore_index = True)

csv_path = os.path.join("SourceCode", "results2.csv") 
table.to_csv(csv_path, index = True)


## Plot a histogram showing the distribution of each statistic 
# for all players in the league and each team

# 3 statistics for attacking : goals, assists, goals/shot : stats_shooting_sG/sh
attack_cols = ["Gls", "Ast", "stats_shooting_G/Sh"]

# 3 statistics for defending : Tackles: stats_defense_Tkl, stats_defense_TklW. Blocks : stats_defense_Blocks
defense_cols = ["stats_defense_Tkl", "stats_defense_TklW", "stats_defense_Blocks"]

# Histogram for all players
for col in attack_cols + defense_cols : 
    plt.figure(figsize = (10, 6)) # Set figure size
    plt.hist(df[col], color = "skyblue", bins = 20, alpha = 1, edgecolor = "black") # Create histogram
    plt.title(f"Histogram of {col} for all players") # Set title
    plt.xlabel(col) # Set x-axis label
    plt.ylabel("Frequency") # Set y-axis label
    safe_col = col.replace("/", "_") # Replace invalid characters in column names
    histogram_path = os.path.join("SourceCode", f"histogram_all_{safe_col}.png")
    plt.savefig(histogram_path, dpi = 300, bbox_inches = "tight")  # Save the plot
    plt.show()
    
# Histogram for each teams
for col in attack_cols + defense_cols : 
    for team in df["Squad"].unique() : # Get unique values in the Squad column
        plt.figure(figsize = (10, 6))
        plt.hist(df[df["Squad"] == team][col], color = "blue", bins = 20, alpha = 0.5, edgecolor = "black")
        plt.title(f"Histogram of {col} for team {team}")
        plt.xlabel(col) 
        plt.ylabel("Frequency") 
        safe_col = col.replace("/", "_")  # Replace invalid characters in column names
        safe_team = team.replace("/", "_")  # Replace invalid characters in team names
        histogram_team_path = os.path.join("SourceCode", f"histogram_{safe_team}_{safe_col}.png")
        plt.savefig(histogram_team_path, dpi = 300, bbox_inches = "tight")
        plt.show()


## Identify the team with the highest scores for each statistic

table.drop(index = 0, inplace = True) # Remove the first row which is the overall stats for "all"

Count = {} # Count the occurrences of teams to print the best-performing team

for col in df.columns[4:] : 
    mean_name = "Mean of " + col # Column name for mean
    # Find the team with the highest value using the index of the max value in the column
    max_team = table.loc[table[mean_name].idxmax(), "Squad"]
    max_value = table[mean_name].max() # Get the maximum value
    # Count occurrences
    if max_team not in Count : 
        Count[max_team] = 1 
    else : 
        Count[max_team] += 1
    print(f"The team with the highest {mean_name} is {max_team} with a value of {max_value}") 
    
Max_value = max(Count.values()) # Find the highest occurrence count
Max_team = [team for team, count in Count.items() if count == Max_value] # Find the teams with the highest occurrence count

print(f"The team with the highest scores for each statistic is {", ".join(Max_team)} with {Max_value} statistics") 