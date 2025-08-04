
import streamlit as st
import pandas as pd
from datetime import datetime
from math import radians, cos, sin, asin, sqrt

# Mock reload data
mock_data = pd.DataFrame([
    {"Load ID": "RL1001", "Pickup Zip": "36602", "Pickup City": "Mobile, AL", "Delivery City": "Atlanta, GA", "Broker": "ABC Logistics", "Broker Email": "broker1@example.com", "Broker Phone": "555-123-4567", "Miles": 345},
    {"Load ID": "RL1002", "Pickup Zip": "36532", "Pickup City": "Fairhope, AL", "Delivery City": "Savannah, GA", "Broker": "XYZ Freight", "Broker Email": "broker2@example.com", "Broker Phone": "555-987-6543", "Miles": 420},
    {"Load ID": "RL1003", "Pickup Zip": "36603", "Pickup City": "Mobile, AL", "Delivery City": "Birmingham, AL", "Broker": "Delta Carriers", "Broker Email": "broker3@example.com", "Broker Phone": "555-654-3210", "Miles": 260},
])

# Zip code to lat/lon mapping for demo
zip_latlon = {
    "36602": (30.6944, -88.0431),
    "36532": (30.5224, -87.9036),
    "36603": (30.6834, -88.0431),
    "30301": (33.7490, -84.3880),  # Atlanta
    "31401": (32.0809, -81.0912),  # Savannah
    "35203": (33.5186, -86.8104),  # Birmingham
}

def haversine(lon1, lat1, lon2, lat2):
    # Calculate the great circle distance in miles
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    return 3956 * c

def find_matches(truck_zip, max_radius):
    if truck_zip not in zip_latlon:
        return pd.DataFrame()
    lat1, lon1 = zip_latlon[truck_zip]
    matches = []
    for _, row in mock_data.iterrows():
        pickup_zip = row["Pickup Zip"]
        if pickup_zip in zip_latlon:
            lat2, lon2 = zip_latlon[pickup_zip]
            distance = haversine(lon1, lat1, lon2, lat2)
            if distance <= max_radius:
                row = row.copy()
                row["Deadhead (mi)"] = round(distance, 1)
                matches.append(row)
    return pd.DataFrame(matches)

# Streamlit UI
st.title("BBE Load Match Dashboard")

with st.form("truck_entry_form"):
    truck_id = st.text_input("Truck ID")
    delivery_zip = st.text_input("Delivery Zip Code")
    delivery_date = st.date_input("Expected Delivery Date", datetime.today())
    submitted = st.form_submit_button("Submit")

if submitted:
    st.success(f"Submitted truck {truck_id} for delivery in ZIP {delivery_zip} on {delivery_date}")

    search_radius = 100
    max_radius = 300
    match_df = find_matches(delivery_zip, search_radius)

    while match_df.empty and search_radius < max_radius:
        search_radius += 50
        match_df = find_matches(delivery_zip, search_radius)

    if not match_df.empty:
        st.subheader(f"Reload Matches (within {search_radius} miles)")
        for i, row in match_df.iterrows():
            with st.expander(f"Load {row['Load ID']}"):
                st.write(f"Pickup: {row['Pickup City']}  
Delivery: {row['Delivery City']}")
                st.write(f"Broker: {row['Broker']}")
                st.write(f"Deadhead: {row['Deadhead (mi)']} mi")
                st.markdown(f"[📧 Email Broker](mailto:{row['Broker Email']})")
                st.markdown(f"[📞 Call Broker](tel:{row['Broker Phone']})")
                booked = st.toggle(f"Booked - {row['Load ID']}", key=row['Load ID'])
    else:
        st.warning(f"No loads found within {max_radius} miles.")
