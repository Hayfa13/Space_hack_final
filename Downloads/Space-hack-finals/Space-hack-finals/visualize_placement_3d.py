import json
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import streamlit as st

def draw_box(ax, start, end, label, color='skyblue'):
    x, y, z = start['width'], start['depth'], start['height']
    dx = end['width'] - x
    dy = end['depth'] - y
    dz = end['height'] - z

    # Define the 6 faces of the box
    verts = [
        [(x, y, z), (x + dx, y, z), (x + dx, y + dy, z), (x, y + dy, z)],  # Bottom face
        [(x, y, z + dz), (x + dx, y, z + dz), (x + dx, y + dy, z + dz), (x, y + dy, z + dz)],  # Top face
        [(x, y, z), (x + dx, y, z), (x + dx, y, z + dz), (x, y, z + dz)],  # Front face
        [(x + dx, y, z), (x + dx, y + dy, z), (x + dx, y + dy, z + dz), (x + dx, y, z + dz)],  # Right face
        [(x + dx, y + dy, z), (x, y + dy, z), (x, y + dy, z + dz), (x + dx, y + dy, z + dz)],  # Top face
        [(x, y + dy, z), (x, y, z), (x, y, z + dz), (x, y + dy, z + dz)],  # Left face
    ]

    # Create the box using Poly3DCollection
    box = Poly3DCollection(verts, alpha=0.5, facecolor=color, edgecolor='black')
    ax.add_collection3d(box)
    
    # Add text inside the box (at the center of the box)
    ax.text(x + dx / 2, y + dy / 2, z + dz / 2, label, color='black', fontsize=8, ha='center')
    
    # Add label above the box
    ax.text(
        x + dx / 2, y + dy / 2, z + dz + 3,  # Position the label *above* the box
        label,
        color='black',
        fontsize=9,
        ha='center',
        va='bottom',
        zorder=10
    )

def visualize_placement(json_file):
    # Load data from the JSON file
    with open(json_file, 'r') as f:
        data = json.load(f)

    # Create the figure for 3D plotting using PyPlot interface
    fig = plt.figure(figsize=(14, 8))
    ax = fig.add_subplot(111, projection='3d')

    placements = data.get('placements', [])
    id_to_name = {item['itemId']: item['name'] for item in data.get('items', [])}  # Mapping item ID to name

    # Draw a box for each item in the placements data
    for item in placements:
        start = item['position']['startCoordinates']
        end = item['position']['endCoordinates']
        item_id = item['itemId']
        name = id_to_name.get(item_id, "")  # Fallback in case the name is missing
        label = f"{item_id}\n{name}"  # Combine item ID and name for the label
        draw_box(ax, start, end, label)

    # Label the axes and set a title for the plot
    ax.set_xlabel('Width')
    ax.set_ylabel('Depth')
    ax.set_zlabel('Height')
    ax.set_title('3D Cargo Placement Visualization')

    # Tight layout to ensure the plot elements fit well
    plt.tight_layout()

    # Render the plot in Streamlit
    st.pyplot(fig)

# Call the function with the JSON data file
visualize_placement('placement_output.json')
