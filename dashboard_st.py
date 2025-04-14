import streamlit as st

import pandas as pd
import geopandas as gpd

import folium
from streamlit_folium import st_folium
import branca

import numpy as np
import math

st.set_page_config(
     page_title="Grants to Local Government",
     page_icon="./Data/Assets/alga.png",
     layout="wide"
     )

# Read in data

@st.cache_data
def read_map():
    return gpd.read_file("./Data/Working Data/Grants Councils.geojson")

@st.cache_data
def read_uninc():
    return gpd.read_file("./Data/Working Data/Unincorp.geojson")

grants = read_map()

st.write(len(grants), "grants to local government")

uninc = read_uninc()

dates = grants["Approval Date"].unique()
dates = dates[dates.argsort()]
dates = list(dates)

start_date = dates[0].strftime('%b %Y')
end_date = dates[-1].strftime('%b %Y')

dates = [date.strftime('%d %b %Y') for date in dates]

# Define page structure

map, filt = st.columns([5, 4], border=True)

# Define functions

def plot_map(filtered):
    m = folium.Map(location = [-25.947028, 133.209639], tiles="CartoDB.Voyager", zoom_start=4.2)

    temp = gpd.GeoDataFrame(filtered.groupby(["Assigned LGA", "geometry"]).agg({"Value (AUD)": "sum"}).reset_index())
    temp["Value (AUD)"] = temp["Value (AUD)"] / 1000
    temp["Value (AUD)"] = temp["Value (AUD)"].apply(lambda x: round(x, 2))

    colormap = branca.colormap.LinearColormap(colors=['#85C0BD',
         '#659ca0',
         '#457883',
         '#255466',
         '#062E4A'], vmin=temp["Value (AUD)"].min(), vmax=temp["Value (AUD)"].max(), max_labels=5)
    #colormap = branca.colormap.linear.Spectral_07.scale(temp["Value (AUD)"].min(), temp["Value (AUD)"].max(), max_labels=5)
    colormap.caption = "Total Grant Value ($'000)"
    colormap.add_to(m)


    m = temp.explore(
         column = "Value (AUD)",
         m = m,
         cmap = colormap,
         tooltip_kwds={
              #"fields": ["Assigned LGA", "Value (AUD)"],
              "aliases": ["Local Government Area", "Total Grant Value ($'000)"]              
         }
    )

    uninc_layer = folium.GeoJson(
        uninc,
        name = "Unincorporated Areas",
        tooltip = "Unincorporated area",
        style_function = lambda x: {
            "color": "black",
            "fillColor": "black",
            "fillOpacity": 0.7,
            "weight": 1
        }
    )
    uninc_layer.add_to(m)

    return m

with st.sidebar:
    st.markdown("### Grants to Local Government")
    st.markdown(f"#### {start_date} to {end_date}")
    st.markdown("Use the sidebar to filter the data.")

    agency = st.multiselect("Agency", grants["Agency"].unique())
    if len(agency) == 0:
        agency = grants["Agency"].unique()

    competitive = st.multiselect("Selection Process", grants["Selection Process"].unique())
    if len(competitive) == 0:
        competitive = grants["Selection Process"].unique()

    category = st.multiselect("Category", grants["Category"].unique())
    if len(category) == 0:
        category = grants["Category"].unique()

    program = st.multiselect("Grant Program", grants["Grant Program"].unique())
    if len(program) == 0:
        program = grants["Grant Program"].unique()

    start_date, end_date = st.select_slider("Approval Date", options=dates, value=(dates[0], dates[-1]))


    st.markdown("Compiled from data released by GrantConnect under a Creative Commons license [(CC BY 3.0 AU)](https://creativecommons.org/licenses/by/3.0/au/deed.en).")
    st.info("""
    - GrantConnect materials are released by the Department of Finance
    - GrantConnect materials are subject to change and should be verified on the GrantConnect website to ensure the information is up to date and correct: www.grants.gov.au
                """,)  

filtered = grants[
            (grants["Agency"].isin(agency)) &
            (grants["Selection Process"].isin(competitive)) &
            (grants["Category"].isin(category)) &
            (grants["Grant Program"].isin(program)) &
            (grants["Approval Date"] >= pd.to_datetime(start_date)) &
            (grants["Approval Date"] <= pd.to_datetime(end_date))
        ]
if len(filtered) == 0:
                st.error("No data available for the selected filters.")

else:
    m = plot_map(filtered)

    with map:
        lga = st_folium(m, use_container_width=True, return_on_hover=False, returned_objects = ["last_active_drawing"])["last_active_drawing"]
    
    with filt:
        if lga:
            if "Assigned LGA" in lga['properties'].keys():
                st.markdown(f"### {lga['properties']['Assigned LGA']}")

                filtered_lga = filtered[filtered["Assigned LGA"] == lga["properties"]["Assigned LGA"]][['Agency', 'Value (AUD)', 'Parent GA ID',
                                        'GA ID', 'GO ID', 'Status', 'Grant Program', 'Approval Date', 'Start Date', 'End Date', 'Variation Value (AUD)',
                                        'One-off/Ad hoc', 'Selection Process', 'Category']].reset_index(drop=True)
                
                st.metric("Total Value of Grants", f'$ {str("{:,}".format(round(filtered_lga["Value (AUD)"].sum(), 2)))}')
            
                st.dataframe(pd.DataFrame(filtered_lga).sort_values(by="Value (AUD)", ascending=True).reset_index(drop=True))


    with st.expander("Detailed Dataset"):
        st.dataframe(filtered[['Agency', 'Value (AUD)', 'Parent GA ID', 'Assigned LGA',
                                        'GA ID', 'GO ID', 'Status', 'Grant Program', 'Approval Date', 'Start Date', 'End Date', 'Variation Value (AUD)',
                                        'One-off/Ad hoc', 'Selection Process', 'Category']].reset_index(drop=True))