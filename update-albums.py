import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json
import os

# Set up the radar plot categories
CATEGORIES = ["Lyrical Wit", "Lyrical Depth", "Production", "Cohesiveness", "Emotional Impact", "Creativity"]

# Ensure output folders exist
os.makedirs("radar_plots", exist_ok=True)

def generate_radar_plot(album_name, scores):
    """Creates and saves a radar plot for an album."""
    num_vars = len(CATEGORIES)

    # Compute the angle for each category
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    scores += scores[:1]  # Close the radar shape
    angles += angles[:1]  # Close the radar shape

    # Create figure
    fig, ax = plt.subplots(figsize=(4, 4), subplot_kw=dict(polar=True))
    ax.fill(angles, scores, color='blue', alpha=0.25)
    ax.plot(angles, scores, color='blue', linewidth=2)

    # Labels
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(CATEGORIES, fontsize=8)
    ax.set_yticklabels([])
    ax.grid(True)

    # Save the figure
    safe_name = album_name.replace(" ", "_").replace("/", "_")  # Ensure safe filenames
    plot_path = f"radar_plots/{safe_name}.png"
    plt.savefig(plot_path, bbox_inches='tight', dpi=100)
    plt.close()
    
    return plot_path

# Load CSV
csv_file = "albums.csv"  # Change if needed
df = pd.read_csv(csv_file)

# Process each album
albums_data = []
for _, row in df.iterrows():
    album_info = {
        "Album Name": row["Album Name"],
        "Artist": row["Artist"],
        "Cover URL": row["Cover URL"],
        "Spotify Link": row["Spotify Link"],
        "Apple Music Link": row["Apple Music Link"],
    }

    # Extract and normalize scores (0-10 scale)
    scores = [row[col] if pd.notna(row[col]) else 5 for col in CATEGORIES]
    scores = [min(max(score, 0), 10) / 10.0 for score in scores]  # Normalize 0-10 to 0-1
    
    # Generate radar plot and store its path
    album_info["Radar Plot"] = generate_radar_plot(row["Album Name"], scores)

    albums_data.append(album_info)

# Save JSON
with open("albums.json", "w") as json_file:
    json.dump(albums_data, json_file, indent=4)

print("✅ JSON file and radar plots generated successfully!")
