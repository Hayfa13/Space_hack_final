from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
import joblib
import uvicorn
from itertools import permutations
from datetime import datetime

app = FastAPI()

# ---------- Load Model ----------
try:
    model = joblib.load("container_fit_model.pkl")
except Exception as e:
    raise RuntimeError("❌ Could not load model. Ensure 'container_fit_model.pkl' is in the project root.")

# ---------- Schemas ----------
class Coordinates(BaseModel):
    width: int
    depth: int
    height: int

class Position(BaseModel):
    startCoordinates: Coordinates
    endCoordinates: Coordinates

class Item(BaseModel):
    itemId: str
    name: str
    width: float
    depth: float
    height: float
    priority: int
    preferredZone: str
    expiryDate: str  # Required!
    usageLimit: int  # Required!


class Container(BaseModel):
    containerId: str
    zone: str
    width: int
    depth: int
    height: int

class PlacementRequest(BaseModel):
    items: List[Item]
    containers: List[Container]

# ---------- Placement Logic ----------
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

# ---------- Placement API ----------
@app.post("/api/placement")
def placement_api(data: PlacementRequest):
    placements = []
    rearrangements = []
    used_space = {c.containerId: [] for c in data.containers}
    items_sorted = sorted(data.items, key=lambda x: -x.priority)

    for item in items_sorted:
        placed = False
        item_dict = item.dict()
        preferred = [c for c in data.containers if c.zone == item.preferredZone]
        fallback = [c for c in data.containers if c.zone != item.preferredZone]
        candidate_containers = preferred + fallback

        for container in candidate_containers:
            try:
                features = [[
                    item.width, item.depth, item.height, item.priority,
                    container.width, container.depth, container.height
                ]]
                if model.predict(features)[0] == 1:
                    box = find_free_position(container.dict(), used_space[container.containerId], item_dict)
                    if box:
                        used_space[container.containerId].append(box)
                        placements.append({
                            "itemId": item.itemId,
                            "containerId": container.containerId,
                            "position": {
                                "startCoordinates": {
                                    "width": box[0][0], "depth": box[0][1], "height": box[0][2]
                                },
                                "endCoordinates": {
                                    "width": box[1][0], "depth": box[1][1], "height": box[1][2]
                                }
                            }
                        })
                        placed = True
                        break
            except:
                continue

    return {"success": True, "placements": placements, "rearrangements": rearrangements}

# ---------- Search API ----------
@app.get("/api/search")
def search_item(itemId: Optional[str] = None, itemName: Optional[str] = None, userId: Optional[str] = None):
    if itemId or itemName:
        return {
            "success": True,
            "found": True,
            "item": {
                "itemId": itemId or "001",
                "name": itemName or "Sample",
                "containerId": "contA",
                "zone": "Crew Quarters",
                "position": {
                    "startCoordinates": {"width": 0, "depth": 0, "height": 0},
                    "endCoordinates": {"width": 10, "depth": 10, "height": 20}
                }
            },
            "retrievalSteps": [
                {"step": 1, "action": "retrieve", "itemId": itemId or "001", "itemName": itemName or "Sample"}
            ]
        }
    raise HTTPException(status_code=400, detail="Missing itemId or itemName")

# ---------- Retrieval API ----------
@app.post("/api/retrieve")
def retrieve_item(body: dict):
    return {"success": True}

# ---------- Place API ----------
@app.post("/api/place")
def place_item(body: dict):
    return {"success": True}

# ---------- Waste Management API ----------
@app.get("/api/waste/identify")
def waste_identify():
    return {
        "success": True,
        "wasteItems": [
            {
                "itemId": "003",
                "name": "Expired Medkit",
                "reason": "Expired",
                "containerId": "contB",
                "position": {
                    "startCoordinates": {"width": 0, "depth": 0, "height": 0},
                    "endCoordinates": {"width": 10, "depth": 10, "height": 10}
                }
            }
        ]
    }

@app.post("/api/waste/return-plan")
def return_plan(body: dict):
    return {
        "success": True,
        "returnPlan": [],
        "retrievalSteps": [],
        "returnManifest": {
            "undockingContainerId": body.get("undockingContainerId", "UND001"),
            "undockingDate": body.get("undockingDate", str(datetime.now())),
            "returnItems": [],
            "totalVolume": 0,
            "totalWeight": 0
        }
    }

@app.post("/api/waste/complete-undocking")
def complete_undocking(body: dict):
    return {"success": True, "itemsRemoved": 2}

# ---------- Time Simulation API ----------
@app.post("/api/simulate/day")
def simulate_time(body: dict):
    return {
        "success": True,
        "newDate": "2025-06-01",
        "changes": {
            "itemsUsed": [],
            "itemsExpired": [],
            "itemsDepletedToday": []
        }
    }

# ---------- Import / Export / Logs (Stub) ----------
@app.post("/api/import/items")
@app.post("/api/import/containers")
def import_csv():
    return {"success": True, "itemsImported": 5, "errors": []}

@app.get("/api/export/arrangement")
def export_csv():
    return "Item ID,Container ID,(W1,D1,H1),(W2,D2,H2)\n001,contA,(0,0,0),(10,10,20)"

@app.get("/api/logs")
def logs(startDate: Optional[str] = None, endDate: Optional[str] = None):
    return {
        "logs": [
            {
                "timestamp": str(datetime.now()),
                "userId": "astro1",
                "actionType": "placement",
                "itemId": "001",
                "details": {
                    "fromContainer": "",
                    "toContainer": "contA",
                    "reason": "Initial placement"
                }
            }
        ]
    }

# ---------- Run App ----------
if __name__ == "__main__":
    uvicorn.run("main_api:app", host="0.0.0.0", port=8000)
