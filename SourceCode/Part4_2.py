import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split 
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import os

## 4.2. Propose a method for estimating player values. How do you select features and model?

data1 = pd.read_csv(os.path.join("SourceCode","results.csv"))
data2 = pd.read_csv(os.path.join("SourceCode","players_900mins_value.csv"))

df = pd.merge(data1, data2[["Player", "Value"]], on = "Player", how = "left") # Merge two tables

df = df[df["Min"] > 900] # Select players with > 900 minutes

# Split the Age column into Year and Day, then calculate the age in years
df[['Year', 'Day']] = df['Age'].str.split('-', expand = True).astype(int)
df['Age'] = (df['Year'] + df['Day'] / 365).round(2)
df.drop(columns = ['Year', 'Day'], inplace = True) 

# Remove characters in Value and convert to float
df["Value"] = df["Value"].str.replace("€", "").str.replace("M", "").astype(float)

df.replace("N/a", np.nan, inplace = True) # Replace "N/a" with NaN
df.reset_index(drop = True, inplace = True)

# Remove unnecessary columns
df = df.drop(["Player", "Nation", "Squad", "Pos", "stats_keeper_GA90",
            "stats_keeper_Save%", "stats_keeper_CS%", "stats_keeper_Save%.1"], axis = 1)

# Convert all columns to numeric, replace missing values with the mean
df = df.apply(pd.to_numeric, errors = 'coerce') 
df = df.fillna(df.mean())

# Calculate the full correlation matrix
corr_matrix = df.corr().abs()

# Get correlation with Value
value_corr = corr_matrix["Value"]

# Select columns with correlation > 0.3
selected_features = value_corr[value_corr > 0.3].index.tolist()

# Recalculate the correlation matrix for these columns
corr_selected = df[selected_features].corr().abs()

# Extract the upper triangle of the matrix
upper = corr_selected.where(np.triu(np.ones(corr_selected.shape), k = 1).astype(bool))

# Find columns with multicollinearity > 0.9
to_drop = []
for column in upper.columns:
    high_corr = upper[column][upper[column] > 0.9]
    for idx in high_corr.index:
        # Keep the column with higher correlation with Value
        if value_corr[column] > value_corr[idx]:
            to_drop.append(idx)
        else:
            to_drop.append(column)

# Remove duplicate columns
to_drop = list(set(to_drop))

# Final list of features to keep
final_features = [col for col in selected_features if col not in to_drop]

# Plot the heatmap of correlations between variables after multicollinearity treatment
plt.figure(figsize = (12, 10))
sns.heatmap(df[final_features].corr(), annot = True, fmt = ".2f", cmap = "coolwarm")  
plt.title("Correlation heatmap between variables after multicollinearity treatment")
heatmap_path = os.path.join("SourceCode", "heatmap_of_correlations.png")
plt.savefig(heatmap_path, dpi = 300, bbox_inches = "tight")
plt.show()

feature_data = df[final_features].drop(columns = "Value")

# Standardize the data
sc = StandardScaler() 
X = sc.fit_transform(feature_data)

Y = df["Value"]

# Train and test split (80% train, 20% test)
X_train, X_test, Y_train, Y_test = train_test_split(X, Y, train_size = 0.8, test_size = 0.2, random_state = 29)

# Use Linear Regression
dt_model = LinearRegression()

dt_model.fit(X_train, Y_train)

Y_pred = dt_model.predict(X_test)

csv_path = os.path.join("SourceCode", "train_model.csv")
pd.DataFrame({"Actual Value Y": Y_test, "Predicted Values Y_test": Y_pred}).to_csv(csv_path)

# Calculate evaluation metrics
mae = mean_absolute_error(Y_test, Y_pred)
mse = mean_squared_error(Y_test, Y_pred)
r2 = r2_score(Y_test, Y_pred)

print(f"Mean Absolute Error (MAE): {mae}") 
print(f"Mean Squared Error (MSE): {mse}") 
print(f"R² Score: {r2}") 

# Output:
# Mean Absolute Error (MAE): 11.904445815556226
# Mean Squared Error (MSE): 227.40318403347462
# R² Score: 0.6553717047107084