import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json
import os
import random

from PIL import Image

def get_average_color(image_path):
    """Returns the average color of an image as an (R, G, B) tuple."""
    try:
        img = Image.open(image_path)
        img = img.resize((50, 50))  # Resize to speed up processing
        pixels = np.array(img)
        avg_color = pixels.mean(axis=(0, 1))  # Average across width & height
        return tuple(avg_color[:3].astype(int))  # Convert to (R, G, B)
    except Exception as e:
        print(f"Error processing {image_path}: {e}")
        return (100, 100, 255)  # Default color (blue) if error occurs

# Set up the radar plot categories
CATEGORIES = ["Lyrics", "Vibes", "Production", "Cohesiveness", "Emotional Impact", "Creativity"]

# Ensure output folders exist
os.makedirs("radar_plots", exist_ok=True)

def generate_radar_plot(album_name, scores, cover_url):
    """Creates and saves a radar plot for an album."""
    num_vars = len(CATEGORIES)

    # Compute the angle for each category
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    angles = [a + (np.pi / num_vars) for a in angles]  # Rotate so a point is at the bottom
    angles += angles[:1]  # Close the radar shape
    scores += scores[:1]  # Close the radar shape
    
    avg_color = get_average_color(cover_url)
    fill_color = (avg_color[0] / 255, avg_color[1] / 255, avg_color[2] / 255, 0.4)  # RGBA with transparency
    line_color = (avg_color[0] / 255, avg_color[1] / 255, avg_color[2] / 255, 1)  # Full opacity for lines
            
    # Create figure
    fig, ax = plt.subplots(figsize=(4, 4), subplot_kw=dict(polar=True))
    
    # Draw hexagonal grid manually
    for i in np.linspace(5, 1.0, 5):  # Five grid levels
        hexagon = [i] * num_vars + [i]  # Close the shape
        ax.plot(angles, hexagon, linestyle="solid", color="black", alpha=1)
        
    ax.fill(angles, scores, color=fill_color)  # Fill with transparency
    ax.plot(angles, scores, color=line_color, linewidth=2)  # Outline
    
    for index, angle in enumerate(angles):
        if 0 < angle < 1:
            angles[index] = angle + .25
        elif 2 < angle < 3:
            angles[index] = angle - .25 
        elif 3 < angle < 4:
            angles[index] = angle + .25
        elif 5 < angle < 6:
            angles[index] = angle - .25
    # Labels
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(CATEGORIES, fontsize=15, fontdict={'fontweight': 'normal', 'family': 'serif'})


    ax.set_yticklabels([])
    ax.spines["polar"].set_visible(False)  # Remove outer circle
    ax.grid(False)  # Remove grid lines    

    # Save the figure
    safe_name = album_name.replace(" ", "_").replace("/", "_")  # Ensure safe filenames
    plot_path = f"radar_plots/{safe_name}.png"
    
    # Make figure background transparent
    # fig.patch.set_alpha(0)
    # ax.set_facecolor((1, 1, 1, 0))  # Set axes background to transparent

    # Save the figure with a transparent background
    # plt.savefig(plot_path, bbox_inches='tight', dpi=100, transparent=True)
        
    plt.savefig(plot_path, bbox_inches='tight', dpi=100)
    plt.close()
    
    return plot_path

# Load CSV
csv_file = "albums.csv"  # Change if needed
df = pd.read_csv(csv_file)

# Process each album
albums_data = []
for _, row in df.iterrows():
    album_name_no_spaces = row["Album Name"].replace(" ", "")
    cover_path = f"img/{album_name_no_spaces}.jpg"
    album_info = {
        "Album Name": row["Album Name"],
        "Artist": row["Artist"],
        "Cover Path": cover_path,  # Include the local file path instead of the URL
        "Sum": row["Sum"],
        "Spotify Link": row["Spotify Link"],
        "Apple Music Link": row["Apple Music Link"],
    }

    # Extract and normalize scores (0-10 scale)
    scores = [row[col] if pd.notna(row[col]) else 5 for col in CATEGORIES]
    # scores = [min(max(score, 0), 10) / 10.0 for score in scores]  # Normalize 0-10 to 0-1
    
    # Generate radar plot and store its path
    album_info["Radar Plot"] = generate_radar_plot(row["Album Name"], scores, cover_path)

    albums_data.append(album_info)

# Sort albums by "Sum" in descending order (highest rated first)
df = df.sort_values(by="Sum", ascending=False)

# Save JSON
with open("albums.json", "w") as json_file:
    json.dump(albums_data, json_file, indent=4)

print("✅ JSON file and radar plots generated successfully!")
