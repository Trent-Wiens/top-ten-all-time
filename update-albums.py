import pandas as pd

# Load CSV file
df = pd.read_csv("albums.csv")

# Convert to JSON
df.to_json("albums.json", orient="records")

print("JSON file created: albums.json")
