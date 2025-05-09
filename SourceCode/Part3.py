import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans 
from sklearn.metrics import silhouette_score 
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA 
import os

## Data processing

df = pd.read_csv(os.path.join("SourceCode","results.csv"))

# Split the Age column into Year and Day, then calculate the age in years
df[['Year', 'Day']] = df['Age'].str.split('-', expand = True).astype(int)
df['Age'] = (df['Year'] + df['Day'] / 365).round(2)
df.drop(columns = ['Year', 'Day'], inplace = True) 

# Select numerical columns and handle missing values
cols = df.columns[4:] 
df.replace("N/a", np.nan, inplace = True) # Replace "N/a" with NaN
data = df[cols].apply(pd.to_numeric, errors = 'coerce') # Convert to numeric, if conversion fails, return NaN

data = data.fillna(data.mean()) # Replace NaN with the column's mean value


## Data clustering

# Standardize the data
scaler = StandardScaler() 
data = scaler.fit_transform(data) 

inertias = [] # Within-cluster distances
silhouette_scores = [] # Similarity scores

for k in range(2, 30):
    kmeans = KMeans(n_clusters = k, random_state = 0) # Initialize the KMeans model
    kmeans.fit(data) # Perform data clustering
    inertias.append(kmeans.inertia_) # Save within-cluster distances
    silhouette_scores.append(silhouette_score(data, kmeans.labels_)) # Calculate similarity scores

# Elbow plot
plt.figure(figsize = (10, 6))
plt.plot(range(2, 30), inertias, marker = 'o') 
plt.grid(True)
plt.title("Elbow method")
plt.xlabel("Number of clusters")
plt.ylabel("Inertia")
elbow_plot_path = os.path.join("SourceCode", "elbow_plot.png") 
plt.savefig(elbow_plot_path, dpi = 300, bbox_inches = "tight")
plt.show()

# Silhouette plot
plt.figure(figsize = (10, 6))
plt.plot(range(2, 30), silhouette_scores, marker = 'o')
plt.grid(True)
plt.title("Silhouette method")
plt.xlabel("Number of clusters")
plt.ylabel("Silhouette Score")
silhouette_plot_path = os.path.join("SourceCode", "silhouette_plot.png")  
plt.savefig(silhouette_plot_path, dpi = 300, bbox_inches = "tight")
plt.show()


k_optimal = 8 # Optimal number of clusters
# Reason for choosing k_optimal = 8:
# - Elbow plot: after k = 8, the graph starts to decrease more slowly,
# indicating that increasing the number of clusters beyond this point does not significantly reduce inertia
# - Silhouette plot: although the highest points are at k = 2 and k = 3, 
# k = 8 still has an acceptable value and allows for more detailed data segmentation
# => k = 8 is a balance between reasonable clustering and desired level of detail

kmeans = KMeans(n_clusters = k_optimal, random_state = 0) # Initialize the KMeans model
kmeans.fit(data) # Perform data clustering


## Use PCA to reduce the dimensionality of the data to 2 dimensions

pca = PCA(n_components = 2, random_state = 0) # Reduce the dimensionality of the data
pca_data = pca.fit_transform(data) # Reduce the dimensionality of the data  

plt.figure(figsize = (10, 6))
plt.scatter(pca_data[:, 0], pca_data[:, 1], c = kmeans.labels_, cmap = 'viridis')
plt.title("KMeans Clustering")
plt.colorbar(label="Cluster")
plt.xlabel("Feature 1")
plt.ylabel("Feature 2")
kmeans_plot_path = os.path.join("SourceCode", "kmeans_clustering.png")
plt.savefig(kmeans_plot_path, dpi = 300, bbox_inches = "tight")
plt.show()