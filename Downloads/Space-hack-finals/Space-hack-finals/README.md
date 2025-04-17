# 🛰️ Space Cargo Optimization Engine

Welcome to our submission for the Space Hack 2025 challenge! This project is a fully automated **space cargo storage and management system** that uses Machine Learning, API design, and a beautiful frontend to help astronauts efficiently plan, place, retrieve, and dispose of cargo items onboard a space station.

---

## 🚀 Features

 **ML-based placement recommendations**  
 **Real-time waste detection** (expiry & usage)  
 **Streamlit UI** for quick interaction  
 **FastAPI backend** with RESTful APIs (runs on port 8000)  
 **Time simulation** and logging support  
 **Fully Dockerized** using Ubuntu 22.04  

---

## 🗂️ Project Structure

```
space-cargo-optimizer/
├── app.py                      ← Streamlit frontend
├── main_api.py                ← FastAPI backend (entrypoint for Docker)
├── placement_engine.py        ← ML-based logic engine
├── container_fit_model.pkl    ← Trained ML model (RandomForest)
├── requirements.txt           ← Python dependencies
├── Dockerfile                 ← For Docker deployment
├── input_items.csv            ← Sample item data
├── containers.csv             ← Sample container data
├── placement_input.json       ← Full input file (items + containers)
├── placement_output.json      ← Output after placement
├── waste_output.json          ← Waste items
├── generate_samples.py        ← CSV item generator
├── generate_containers.py     ← CSV container generator
├── sample_data.py             ← Dict of item types & zones
└── README.md                  ← This file
```

---

##  Core Functionality

### 1.  Placement Recommendations
- ML model checks if item fits container
- Priority-aware placement in preferred zones
- If full, tries rearrangement (fallback container)

### 2.  Item Search & Retrieval
- `/api/search`: Search by ID or name
- `/api/retrieve`: Retrieve item (usage decreases)
- `/api/place`: Re-place an item in a new container

### 3.  Waste Management
- `/api/waste/identify`: Detects expired / used-up items
- `/api/waste/return-plan`: Suggests items to move for disposal
- `/api/waste/complete-undocking`: Clears waste items

### 4.  Time Simulation
- `/api/simulate/day`: Fast-forward by days to simulate expiry & depletion

### 5.  Import & Export APIs
- `/api/import/items`, `/api/import/containers`: Upload CSVs
- `/api/export/arrangement`: Export final placements as CSV

### 6.  Logging API
- `/api/logs`: View all actions (retrieval, placement, disposal)

---

##  API Server Setup

###  Local Run (without Docker)
```bash
pip install -r requirements.txt
uvicorn main_api:app --host 0.0.0.0 --port 8000 --reload
```
Then visit: [http://localhost:8000/docs](http://localhost:8000/docs)

###  Docker Setup
```bash
docker build -t space-cargo .
docker run -p 8000:8000 space-cargo
```

---

##  Streamlit App (Frontend)
```bash
streamlit run app.py
```
Then go to: [http://localhost:8501](http://localhost:8501)

Upload `placement_input.json` and instantly view:
-  Placement Results
-  Waste Items
-  Download output JSONs

---

##  Machine Learning
We trained a `RandomForestClassifier` using 1000+ samples of:
- Item dimensions & priority
- Container dimensions

Output: 1 (fits) or 0 (doesn’t fit). Model is saved as `container_fit_model.pkl`.

---

##  Sample Test Case

### Input JSON:
```json
{
  "items": [
    {
      "itemId": "001",
      "name": "Food Packet",
      "width": 10,
      "depth": 10,
      "height": 20,
      "priority": 80,
      "expiryDate": "2025-05-20",
      "usageLimit": 30,
      "preferredZone": "Crew Quarters"
    }
  ],
  "containers": [
    {
      "containerId": "contA",
      "zone": "Crew Quarters",
      "width": 100,
      "depth": 85,
      "height": 200
    }
  ]
}
```

---

## ✨ Team
**Built by Nidhi Shakhapur, Hayfa F and Shaurya Sorayan**

If you have any questions or want to collaborate further, feel free to reach out! 🚀

