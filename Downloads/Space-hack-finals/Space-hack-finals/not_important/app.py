import streamlit as st
import json
import os
import joblib
import pandas as pd
from placement_engine import place_items_with_ml
import datetime

# Load model
model = joblib.load("container_fit_model.pkl")

# Page config
st.set_page_config(page_title="Space Hack Placement Engine", layout="wide")
st.title("🚀 Space Hack: Smart Storage Placement Engine")

# File upload
uploaded_file = st.file_uploader("Upload placement_input.json", type="json")

if uploaded_file:
    data = json.load(uploaded_file)
    items = data["items"]
    containers = data["containers"]

    # Show uploaded input using expanders
    with st.expander("📦 Items to be Placed"):
        st.json(items)

    with st.expander("📂 Available Containers"):
        st.json(containers)

    # Run placement algorithm
    placements, rearrangements = place_items_with_ml(items, containers)

    # Save and structure placement output
    placement_output = {
        "success": True,
        "placements": placements,
        "rearrangements": rearrangements
    }

    with open("placement_output.json", "w") as f:
        json.dump(placement_output, f, indent=4)

    # Waste logic
    cutoff_date = "2025-06-01"
    waste_items = [
        item for item in items
        if item.get("expiryDate", "9999-12-31") < cutoff_date
    ]

    waste_output = {
        "wasteItems": waste_items,
        "note": "This is a simulated waste list. Replace with real expiry/use logic."
    }

    with open("waste_output.json", "w") as f:
        json.dump(waste_output, f, indent=4)

    # Summary
    st.info(f"📊 Summary: Total Items = {len(items)} | Placed = {len(placements)} | Waste = {len(waste_items)}")

    # Create layout columns
    col1, col2 = st.columns(2)

    # Placement Results
    with col1:
        st.subheader("📍 Placement Results")
        if placements:
            placement_df = pd.DataFrame(placements)
            st.dataframe(placement_df)
        else:
            st.warning("No placements were made.")

        st.download_button(
            label="📥 Download Placement Output",
            data=json.dumps(placement_output, indent=4),
            file_name="placement_output.json",
            mime="application/json"
        )

    # Waste Results
    with col2:
        st.subheader("🗑️ Waste Items (Before 2025-06-01)")
        if waste_items:
            waste_df = pd.DataFrame(waste_items)
            st.dataframe(waste_df)
        else:
            st.success("No waste items detected!")

        st.download_button(
            label="📥 Download Waste Output",
            data=json.dumps(waste_output, indent=4),
            file_name="waste_output.json",
            mime="application/json"
        )

    # Optional: Detailed placement view in expander
    with st.expander("🔍 Detailed Placements"):
        for item in placements:
            item_id = item.get("item_id", "Unknown")
            container_id = item.get("container_id", "Unknown")
            st.markdown(f"✅ **{item_id}** → Container: `{container_id}`")

    # Optional: Detailed waste view in expander
    if waste_items:
        with st.expander("⚠️ Waste Item Details"):
            for item in waste_items:
                item_id = item.get("item_id", "Unknown")
                expiry = item.get("expiryDate", "Unknown")
                st.markdown(f"⚠️ **{item_id}** expiring on `{expiry}`")
