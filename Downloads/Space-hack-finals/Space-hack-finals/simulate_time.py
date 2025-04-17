import json
from datetime import datetime, timedelta

# Load input.json
with open("placement_input.json", "r") as infile:
    data = json.load(infile)

items = data["items"]

def simulate_time_passage(items, num_days=1, items_used_per_day=None):
    today = datetime.strptime("2025-04-16", "%Y-%m-%d")  # Simulated today
    simulated_date = today + timedelta(days=num_days)
    
    used_today = []
    expired = []
    depleted = []

    for item in items:
        if item["expiryDate"] != "N/A":
            try:
                expiry = datetime.strptime(item["expiryDate"], "%Y-%m-%d")
                if expiry < simulated_date:
                    expired.append({"itemId": item["itemId"], "name": item["name"]})
            except:
                continue

        if items_used_per_day and item["itemId"] in items_used_per_day:
            item["usageLimit"] -= items_used_per_day[item["itemId"]]
            used_today.append({
                "itemId": item["itemId"],
                "name": item["name"],
                "remainingUses": item["usageLimit"]
            })
            if item["usageLimit"] <= 0:
                depleted.append({"itemId": item["itemId"], "name": item["name"]})

    return {
        "success": True,
        "newDate": simulated_date.strftime("%Y-%m-%d"),
        "changes": {
            "itemsUsed": used_today,
            "itemsExpired": expired,
            "itemsDepletedToday": depleted
        }
    }

# Example simulation
items_used_example = {
    items[0]["itemId"]: 1,
    items[1]["itemId"]: 3
}

result = simulate_time_passage(items, num_days=2, items_used_per_day=items_used_example)

# Save to output
with open("time_simulation_output.json", "w") as f:
    json.dump(result, f, indent=4)

print("✅ Time simulation complete. Output saved to time_simulation_output.json")
