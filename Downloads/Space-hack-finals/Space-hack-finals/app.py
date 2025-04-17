import streamlit as st
import time
from streamlit_autorefresh import st_autorefresh
import json
import pandas as pd
from datetime import datetime
import streamlit.components.v1 as components


# Page Configuration
st.set_page_config(
    layout="wide", 
    page_title="ISS Cargo Dashboard", 
    page_icon="🌌",
    initial_sidebar_state="expanded"
)

# Load Data
with open("placement_input.json") as f:
    data = json.load(f)
items = data["items"]
containers = data["containers"]

with open("waste_output.json") as f:
    waste_data = json.load(f)

with open("placement_output.json") as f:
    placement_output = json.load(f)

# Custom CSS for professional appearance
st.markdown("""
<style>
    :root {
        --primary: #1a237e;
        --secondary: #283593;
        --accent: #3949ab;
        --background: #f8f9fa;
        --card: #ffffff;
        --text: #212529;
        --success: #28a745;
        --warning: #ffc107;
        --danger: #dc3545;
    }
    
    .main {
        background-color: var(--background);
    }
    
    .sidebar .sidebar-content {
        background-color: var(--primary) !important;
        color: white !important;
    }
    
    .sidebar .sidebar-content .stRadio label {
        color: white !important;
    }
    
    .sidebar .sidebar-content .stRadio div[role="radiogroup"] > label {
        padding: 10px 15px;
        border-radius: 5px;
        margin: 5px 0;
        transition: all 0.3s ease;
    }
    
    .sidebar .sidebar-content .stRadio div[role="radiogroup"] > label:hover {
        background-color: var(--secondary);
    }
    
    .sidebar .sidebar-content .stRadio div[role="radiogroup"] > label[data-baseweb="radio"]:has(input:checked) {
        background-color: var(--accent);
        font-weight: 500;
    }
    
    h1, h2, h3, h4, h5, h6 {
        color: var(--primary);
        font-weight: 600;
    }
    
    .stButton>button {
        background-color: var(--accent);
        color: white;
        border: none;
        padding: 10px 24px;
        border-radius: 4px;
        font-weight: 500;
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .stButton>button:hover {
        background-color: var(--secondary);
        transform: translateY(-1px);
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    .stDataFrame {
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    .stAlert {
        border-radius: 8px;
    }
    
    .card {
        background-color: var(--card);
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    .metric-card {
        background-color: var(--card);
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        text-align: center;
    }
    
    .metric-value {
        font-size: 24px;
        font-weight: 700;
        color: var(--primary);
    }
    
    .metric-label {
        font-size: 14px;
        color: var(--text);
        opacity: 0.8;
    }
    
    .icon {
        font-size: 24px;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar - Enhanced with professional styling and visible content
with st.sidebar:
    st.markdown("""
    <div style="padding: 15px 0 25px 0; border-bottom: 1px solid rgba(0,0,0,0.1); margin-bottom: 20px;">
        <h1 style="color: black; margin: 0; font-size: 24px;">🌌 ISS Cargo Dashboard</h1>
        <p style="color: rgba(0,0,0,0.7); margin: 5px 0 0 0; font-size: 14px;">Advanced Cargo Management System</p>
    </div>
    """, unsafe_allow_html=True)

    section = st.radio(
        "Navigation",
        [
            "Overview",
            "Items & Containers",
            "Run Placement",
            "3D Visualization",
            "Waste Detection",
            "Simulate Time",
            "Search Item",
            "Export & Logs"
        ],
        label_visibility="collapsed"
    )
    
    st.markdown("""
    <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid rgba(255,255,255,0.1);">
        <p style="color: rgba(255,255,255,0.6); font-size: 12px; margin: 0;">ISS Cargo Dashboard v2.1</p>
        <p style="color: rgba(255,255,255,0.6); font-size: 12px; margin: 0;">Last updated: {}</p>
    </div>
    """.format(datetime.now().strftime("%Y-%m-%d")), unsafe_allow_html=True)

#Overview
if section == "Overview":
    st.title("ISS Cargo Optimization Dashboard")

    components.html("""
        <html>
        <head>
            <style>
                .typing-box {
                    font-size: 16px;
                    color: #333;
                    font-family: 'Courier New', Courier, monospace;
                    line-height: 1.6;
                    white-space: pre-wrap;
                    min-height: 100px;
                    padding-bottom: 20px;
                }
            </style>
        </head>
        <body>
            <div class="typing-box" id="typed-output"></div>

            <script>
                const text = "🚀 Welcome to the International Space Station Cargo Management System. This dashboard provides comprehensive tools for organizing, tracking, and optimizing cargo placement aboard the ISS.";
                let i = 0;
                function typeWriter() {
                    if (i < text.length) {
                        document.getElementById("typed-output").innerHTML += text.charAt(i);
                        i++;
                        setTimeout(typeWriter, 30);
                    }
                }
                window.onload = typeWriter;
            </script>
        </body>
        </html>
    """, height=100)
    



    
    # Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div class="icon">📦</div>
            <div class="metric-value">{}</div>
            <div class="metric-label">Total Items</div>
        </div>
        """.format(len(items)), unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="metric-card">
            <div class="icon">🗄️</div>
            <div class="metric-value">{}</div>
            <div class="metric-label">Containers</div>
        </div>
        """.format(len(containers)), unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="metric-card">
            <div class="icon">🧹</div>
            <div class="metric-value">{}</div>
            <div class="metric-label">Waste Items</div>
        </div>
        """.format(len(waste_data.get("wasteItems", []))), unsafe_allow_html=True)
    with col4:
        st.markdown("""
        <div class="metric-card">
            <div class="icon">✅</div>
            <div class="metric-value">{}</div>
            <div class="metric-label">Placements</div>
        </div>
        """.format(len(placement_output.get("placements", []))), unsafe_allow_html=True)
    
    # Features Section
    st.subheader("Dashboard Features")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="card">
            <h4>🚀 Cargo Management</h4>
            <ul style="padding-left: 20px;">
                <li>View all items and containers</li>
                <li>Smart placement algorithm</li>
                <li>3D visualization of cargo</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="card">
            <h4>🛠️ System Utilities</h4>
            <ul style="padding-left: 20px;">
                <li>Time simulation tools</li>
                <li>Advanced search functionality</li>
                <li>Data export capabilities</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

elif section == "Items & Containers":
    st.title("Cargo Inventory Management")
    st.markdown("""
    <div class="card">
        <p>Comprehensive overview of all cargo items and storage containers aboard the ISS.</p>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📦 Items Inventory", "🗄️ Containers"])
    
    with tab1:
        st.subheader("Item Inventory")
        st.dataframe(
            pd.DataFrame(items), 
            use_container_width=True,
            height=600
        )
    
    with tab2:
        st.subheader("Storage Containers")
        st.dataframe(
            pd.DataFrame(containers), 
            use_container_width=True,
            height=600
        )

elif section == "Run Placement":
    st.title("Cargo Placement Optimization")
    
    if placement_output["success"]:
        st.success("Placement algorithm executed successfully.", icon="✅")
        st.markdown("""
        <div class="card">
            <p>The following placements have been calculated by the optimization algorithm:</p>
        </div>
        """, unsafe_allow_html=True)
        
        df = pd.DataFrame(placement_output["placements"])
        st.dataframe(
            df, 
            use_container_width=True,
            height=600
        )
    else:
        st.error("Placement algorithm failed to execute.", icon="❌")

elif section == "3D Visualization":
    st.title("3D Cargo Visualization")
    st.markdown("""
    <div class="card">
        <p>Interactive 3D representation of cargo placement within ISS storage containers.</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("Launch 3D Visualization", key="3d_visualization"):
        from visualize_placement_3d import visualize_placement
        visualize_placement("placement_output.json")

elif section == "Waste Detection":
    st.title("Waste & Expired Items")
    
    if waste_data["wasteItems"]:
        st.warning(f"Detected {len(waste_data['wasteItems'])} waste/expired items requiring attention.", icon="⚠️")
        st.markdown("""
        <div class="card">
            <p>{}</p>
        </div>
        """.format(waste_data["note"]), unsafe_allow_html=True)
        
        st.subheader("Waste Items List")
        df_waste = pd.DataFrame(waste_data["wasteItems"])
        st.dataframe(
            df_waste, 
            use_container_width=True,
            height=400
        )
    else:
        st.success("No expired or waste items detected in current inventory.", icon="✅")

elif section == "Simulate Time":
    st.title("Time Simulation")
    st.markdown("""
    <div class="card">
        <p>Simulate the passage of time to predict cargo changes, expiration dates, and resource consumption.</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.expander("⚙️ Simulation Parameters", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            num_days = st.number_input(
                "Days to simulate", 
                min_value=1, 
                max_value=365, 
                value=7,
                help="Number of days to advance the simulation"
            )
        with col2:
            st.markdown("**Current Date**")
            st.markdown(f"`{datetime.now().strftime('%Y-%m-%d')}`")
        
        st.markdown("**Item Usage Rates**")
        usage_text = st.text_area(
            "Specify daily item usage (format: itemID:quantity)", 
            value="",
            placeholder="item001:2\nitem005:1",
            help="Enter one item per line in format ID:quantity"
        )
    
    items_used_dict = {}
    if usage_text.strip():
        try:
            for line in usage_text.strip().splitlines():
                item_id, count = line.split(":")
                items_used_dict[item_id.strip()] = int(count.strip())
        except Exception as e:
            st.error(f"Invalid format: {e}. Please use 'itemID:quantity' format.")
    
    if st.button("Run Time Simulation", key="time_sim"):
        from simulate_time import simulate_time_passage
        with st.spinner("Running simulation..."):
            result = simulate_time_passage(
                items, 
                num_days=num_days, 
                items_used_per_day=items_used_dict
            )
        
        st.success("Simulation completed successfully!")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            <div class="card">
                <h4>Simulation Results</h4>
                <p><strong>New Date:</strong> {}</p>
            </div>
            """.format(result['newDate']), unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="card">
                <h4>Changes Summary</h4>
                <p>{} items modified</p>
                <p>{} items expired</p>
            </div>
            """.format(
                len(result["changes"]),
                sum(1 for change in result["changes"] if change.get("expired", False))
            ), unsafe_allow_html=True)
        
        st.subheader("Detailed Changes")
        st.json(result["changes"])

elif section == "Search Item":
    st.title("Cargo Search")
    st.markdown("""
    <div class="card">
        <p>Locate specific items in the ISS inventory using ID, name, or other attributes.</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("search_form"):
        col1, col2 = st.columns(2)
        with col1:
            item_id = st.text_input("Item ID")
        with col2:
            item_name = st.text_input("Item Name")
        
        search_submitted = st.form_submit_button("Search Inventory")
    
    if search_submitted:
        results = [
            item for item in items 
            if (not item_id or item_id.lower() in item['itemId'].lower()) and 
               (not item_name or item_name.lower() in item['name'].lower())
        ]
        
        if results:
            st.success(f"Found {len(results)} matching item(s)")
            
            for item in results:
                with st.expander(f"📦 {item['itemId']} - {item['name']}", expanded=False):
                    st.json(item)
        else:
            st.warning("No items matched your search criteria.")

elif section == "Export & Logs":
    st.title("Data Export & System Logs")
    
    tab1, tab2 = st.tabs(["📤 Data Export", "📜 System Logs"])
    
    with tab1:
        st.subheader("Export Cargo Data")
        st.markdown("""
        <div class="card">
            <p>Download current cargo arrangements and inventory data in various formats.</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Placement Data**")
            if st.button("Export as CSV"):
                df = pd.DataFrame(placement_output["placements"])
                csv = df.to_csv(index=False)
                st.download_button(
                    "Download CSV",
                    csv,
                    file_name="iss_placement_data.csv",
                    mime="text/csv"
                )
            
            if st.button("Export as JSON"):
                json_data = json.dumps(placement_output, indent=2)
                st.download_button(
                    "Download JSON",
                    json_data,
                    file_name="iss_placement_data.json",
                    mime="application/json"
                )
        
        with col2:
            st.markdown("**Inventory Data**")
            if st.button("Export Inventory as CSV"):
                df = pd.DataFrame(items)
                csv = df.to_csv(index=False)
                st.download_button(
                    "Download CSV",
                    csv,
                    file_name="iss_inventory_data.csv",
                    mime="text/csv"
                )
    
    with tab2:
        st.subheader("System Logs")
        st.markdown("""
        <div class="card">
            <p>View system operation logs and historical data.</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Refresh Logs"):
            logs = {
                "Log 1": "System initialized at {}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                "Log 2": "Placement algorithm executed",
                "Log 3": "Waste detection completed",
                "Log 4": "User accessed search functionality"
            }
            st.json(logs)