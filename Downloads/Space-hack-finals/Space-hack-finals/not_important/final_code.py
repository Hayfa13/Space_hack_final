#!/usr/bin/env python
# coding: utf-8

# In[22]:


import os
import json
import pandas as pd
from itertools import permutations
import joblib
from datetime import datetime


# In[23]:


import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import joblib

# Simulate training data
num_samples = 1000
item_width = np.random.randint(5, 50, num_samples)
item_depth = np.random.randint(5, 50, num_samples)
item_height = np.random.randint(5, 50, num_samples)
priority = np.random.randint(1, 101, num_samples)

container_width = np.random.randint(50, 150, num_samples)
container_depth = np.random.randint(50, 150, num_samples)
container_height = np.random.randint(50, 150, num_samples)

success = (
    (item_width <= container_width) &
    (item_depth <= container_depth) &
    (item_height <= container_height)
).astype(int)

X = pd.DataFrame({
    'item_width': item_width,
    'item_depth': item_depth,
    'item_height': item_height,
    'priority': priority,
    'container_width': container_width,
    'container_depth': container_depth,
    'container_height': container_height
})
y = success

# Train the model
model = RandomForestClassifier()
model.fit(X, y)

# Save the model
joblib.dump(model, r"C:\Users\Hayfa\Documents\Space_hack_app\container_fit_model.pkl")
print("✅ New model trained and saved successfully.")


# In[24]:


exec(open("generate_samples.py").read())
exec(open("generate_containers.py").read())

# 🔁 Step 0: If placement_input.json doesn't exist, generate it from CSVs
if not os.path.exists("placement_input.json"):
    print("📂 placement_input.json not found. Creating from CSVs...")

    items_df = pd.read_csv("input_items.csv")
    containers_df = pd.read_csv("containers.csv")

    items = []
    for row in items_df.to_dict(orient="records"):
        items.append({
            "itemId": row["item_id"],
            "name": row["name"],
            "width": float(row["width_cm"]),
            "depth": float(row["depth_cm"]),
            "height": float(row["height_cm"]),
            "priority": int(row["priority"]),
            "expiryDate": row["expiry_date"],
            "usageLimit": int(row["usage_limit"]),
            "preferredZone": row["preferred_zone"]
        })

    containers = []
    for row in containers_df.to_dict(orient="records"):
        containers.append({
            "containerId": row["container_id"],
            "zone": row["zone"],
            "width": float(row["width_cm"]),
            "depth": float(row["depth_cm"]),
            "height": float(row["height_cm"])
        })

    with open("placement_input.json", "w") as f:
        json.dump({"items": items, "containers": containers}, f, indent=4)

    print("✅ placement_input.json created from CSVs.")


# In[25]:


# ✅ Step 1: Load input.json
with open("placement_input.json", "r") as infile:
    data = json.load(infile)

items = data["items"]
containers = data["containers"]


# In[26]:


def rotate_item(item):
    dims = (item['width'], item['depth'], item['height'])
    return list(set(permutations(dims)))


def overlaps(pos1, pos2):
    a_start, a_end = pos1
    b_start, b_end = pos2
    return not (
        a_end[0] <= b_start[0] or a_start[0] >= b_end[0] or
        a_end[1] <= b_start[1] or a_start[1] >= b_end[1] or
        a_end[2] <= b_start[2] or a_start[2] >= b_end[2]
    )


def fits_inside(box, container):
    _, end = box
    return (
        end[0] <= container['width'] and
        end[1] <= container['depth'] and
        end[2] <= container['height']
    )


# In[27]:


def find_free_position(container, used_positions, item):
    for rotation in rotate_item(item):
        w, d, h = rotation
        for x in range(0, container['width'] - w + 1, 5):
            for y in range(0, container['depth'] - d + 1, 5):
                for z in range(0, container['height'] - h + 1, 5):
                    start = (x, y, z)
                    end = (x + w, y + d, z + h)
                    box = (start, end)
                    if any(overlaps(box, used) for used in used_positions):
                        continue
                    if fits_inside(box, container):
                        return box
    return None


# In[28]:


import warnings
from sklearn.exceptions import InconsistentVersionWarning
warnings.filterwarnings("ignore", category=InconsistentVersionWarning)

model = joblib.load("container_fit_model.pkl")
import joblib
from tensorflow.keras.models import load_model
import numpy as np

# Load neural net model and scaler
nn_model = load_model("container_fit_nn_model.h5")
scaler = joblib.load("container_fit_nn_scaler.pkl")

def place_items_with_nn(items, containers):
    placements = []
    rearrangements = []
    used_space = {c['containerId']: [] for c in containers}

    items_sorted = sorted(items, key=lambda x: -x['priority'])

    for item in items_sorted:
        placed = False
        preferred = [c for c in containers if c['zone'] == item['preferredZone']]
        fallback = [c for c in containers if c['zone'] != item['preferredZone']]
        candidate_containers = preferred + fallback

        for container in candidate_containers:
            features = np.array([[
                item['width'], item['depth'], item['height'], item['priority'],
                container['width'], container['depth'], container['height']
            ]])
            features_scaled = scaler.transform(features)
            prediction = nn_model.predict(features_scaled, verbose=0)[0][0]

            if prediction >= 0.5:
                box = find_free_position(container, used_space[container['containerId']], item)
                if box:
                    used_space[container['containerId']].append(box)
                    placements.append({
                        "itemId": item['itemId'],
                        "containerId": container['containerId'],
                        "position": {
                            "startCoordinates": {
                                "width": box[0][0],
                                "depth": box[0][1],
                                "height": box[0][2]
                            },
                            "endCoordinates": {
                                "width": box[1][0],
                                "depth": box[1][1],
                                "height": box[1][2]
                            }
                        }
                    })
                    placed = True
                    break

        if not placed:
            print(f"[WARNING] No space or model rejected placement for item {item['itemId']}")

    return placements, rearrangements


placements, rearrangements = place_items_with_nn(items, containers)


# In[29]:


# ✅ Step 4: Save placement output
placement_output = {
    "success": True,
    "placements": placements,
    "rearrangements": rearrangements
}

with open("placement_output.json", "w") as outfile:
    json.dump(placement_output, outfile, indent=4)

print("✅ placement_output.json saved successfully.")

# ✅ Step 5: Waste detection logic
waste_items = []
for item in items:
    expiry = item["expiryDate"]
    if expiry != "N/A":
        try:
            expiry_date = datetime.strptime(expiry, "%Y-%m-%d")
            if expiry_date < datetime(2025, 6, 1):
                waste_items.append(item)
        except:
            continue

waste_output = {
    "wasteItems": waste_items,
    "note": "Items with expiryDate before 2025-06-01 considered waste."
}

with open("waste_output.json", "w") as wastefile:
    json.dump(waste_output, wastefile, indent=4)

print("✅ waste_output.json saved successfully.")





