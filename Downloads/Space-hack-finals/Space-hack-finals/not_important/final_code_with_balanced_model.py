#!/usr/bin/env python
# coding: utf-8

import os
import json
import pandas as pd
from itertools import permutations
import joblib
from datetime import datetime
import numpy as np
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.exceptions import InconsistentVersionWarning
import warnings

warnings.filterwarnings("ignore", category=InconsistentVersionWarning)

# Phase 1: Train a Balanced ML Model with XGBoost
def generate_large_sample_and_balance():
    N = 50000
    iw = np.random.randint(5, 50, N)
    id_ = np.random.randint(5, 50, N)
    ih = np.random.randint(5, 50, N)
    cw = np.random.randint(50, 150, N)
    cd = np.random.randint(50, 150, N)
    ch = np.random.randint(50, 150, N)
    im = (iw * id_ * ih) / 2000 + np.random.uniform(0.1, 5.0, N)
    prio = np.random.randint(1, 101, N)
    zone_match = np.random.randint(0, 2, N)
    label = ((iw <= cw) & (id_ <= cd) & (ih <= ch)).astype(int)

    df = pd.DataFrame({
        'item_width': iw,
        'item_depth': id_,
        'item_height': ih,
        'item_mass': im,
        'priority': prio,
        'preferred_zone_match': zone_match,
        'container_width': cw,
        'container_depth': cd,
        'container_height': ch,
        'label': label
    })

    df_0 = df[df.label == 0].sample(2500, random_state=42)
    df_1 = df[df.label == 1].sample(2500, random_state=42)
    return pd.concat([df_0, df_1]).sample(frac=1).reset_index(drop=True)

df_balanced = generate_large_sample_and_balance()
X = df_balanced.drop("label", axis=1)
y = df_balanced["label"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = XGBClassifier(use_label_encoder=False, eval_metric="logloss")
model.fit(X_train, y_train)
joblib.dump(model, "container_fit_model.pkl")
print("✅ New ML model trained and saved.")

# Phase 2: Generate Inputs from CSVs
exec(open("generate_samples.py").read())
exec(open("generate_containers.py").read())

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

with open("placement_input.json", "r") as infile:
    data = json.load(infile)

items = data["items"]
containers = data["containers"]

# Placement Logic Functions
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

model = joblib.load("container_fit_model.pkl")

def place_items_with_ml(items, containers):
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
            features = [[
                item['width'], item['depth'], item['height'], 
                (item['width'] * item['depth'] * item['height']) / 2000,
                item['priority'], 1,  # zone match = 1 for simplicity
                container['width'], container['depth'], container['height']
            ]]
            prediction = model.predict(features)[0]
            if prediction == 1:
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

placements, rearrangements = place_items_with_ml(items, containers)

with open("placement_output.json", "w") as outfile:
    json.dump({"success": True, "placements": placements, "rearrangements": rearrangements}, outfile, indent=4)

print("✅ placement_output.json saved successfully.")

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
