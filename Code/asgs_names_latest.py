import geopandas as gpd
import pandas as pd

lgas = gpd.read_file("./Data/Working Data/LGA_2024_AUST_GDA2020.zip")
council_names = pd.read_csv("./Data/Working Data/ALGA Mail List.csv", encoding="latin1")

grants = pd.read_csv("./Data/Grants_Councils_latest.csv")

geometry = lgas[["LGA_CODE24", "geometry"]]

lgas = pd.DataFrame(lgas.drop(columns=["geometry"]))

lgas = lgas[~lgas["LGA_NAME24"].str.contains(r"Unincorporated|Offshore|No usual address|Outside Australia|Unincorp. Other Territories")]

council_names.dropna(subset="COUNCIL", inplace=True)

lgas["Council Name"] = lgas["LGA_NAME24"].apply(lambda x: [i for i in council_names["COUNCIL"] if x in i])
lgas["Council Name"] = lgas["Council Name"].apply(lambda x: x[0] if len(x) == 1 else x)

replace_dict = {
    "Anangu Pitjantjatjara Yankunytjatjara" : pd.NA, # HAS TO BE REPLACED
    "Augusta Margaret River" : "Shire of Augusta-Margaret River",
    "Bayside (NSW)" : "Bayside Council",
    "Bayside (Vic.)" : "Bayside City Council",
    "Blackall Tambo" : "Blackall-Tambo Regional Council",
    "Campbelltown (NSW)" : "Campbelltown City Council",
    "Campbelltown (SA)" : "Campbelltown City Council (SA)",
    "Central Coast (NSW)" : "Central Coast Council",
    "Central Coast (Tas.)" : "Central Coast Council (Tas.)",
    "Central Highlands (Qld)" : "Central Highlands Regional Council",
    "Central Highlands (Tas.)" : "Central Highlands Council",
    "Cocos Islands" : "Shire of Cocos (Keeling) Islands",
    "Darwin Waterfront Precinct" : "City of Darwin",
    "Derby-West Kimberley" : "Shire of Derby/West Kimberley",
    "Flinders (Qld)" : "Flinders Shire Council",
    "Flinders (Tas.)": "Flinders Council",
    "Glamorgan-Spring Bay": "Glamorgan Spring Bay Council",
    "Hunters Hill" : "Hunter's Hill Council",
    "Kingston (SA)" : "Kingston District Council",
    "Kingston (Vic.)" : "City of Kingston",
    "Latrobe (Tas.)" : "Latrobe Council",
    "Latrobe (Vic.)" : "Latrobe City Council",
    "Maralinga Tjarutja" : pd.NA, # HAS TO BE REPLACED
    "Mid-Coast" : "Mid Coast Council",
    "Mount Marshall" : "Shire of Mt Marshall",
    "Nambucca Valley" : "Nambucca Shire Council",
    "Roxby Downs" : "Roxby Council",
    "Serpentine-Jarrahdale" : "Shire of Serpentine Jarrahdale",
    "Waratah-Wynyard" : "Waratah - Wynyard Council",
    "Weipa" : "Weipa Town Authority"
}

lgas.loc[lgas["LGA_NAME24"].isin(replace_dict.keys()), "Council Name"] = lgas.loc[lgas["LGA_NAME24"].isin(replace_dict.keys()), "LGA_NAME24"].apply(lambda x: replace_dict[x])

lgas = lgas[lgas["Council Name"].notna()]

lgas["Council Name"] = lgas["Council Name"].apply(lambda x: [i for i in x if i not in lgas["Council Name"].values][0] if type(x) == list else x)

lgas["LGA_CODE24"] = lgas["LGA_CODE24"].astype(str)

lgas = lgas.merge(geometry, on="LGA_CODE24")

grants.loc[(grants["Recipient State/Territory"] == "TAS") & (grants["Assigned LGA"] == "Central Coast Council"), "Assigned LGA"] = "Central Coast Council (Tas.)"

grants_geo = gpd.GeoDataFrame(lgas.merge(grants, left_on="Council Name", right_on="Assigned LGA"))

grants_geo.geometry = grants_geo.geometry.set_precision(grid_size=0.01)

grants_archive = gpd.read_file("./Data/Working Data/Grants Councils.geojson")

grants_archive = pd.concat([grants_archive, grants_geo])

grants_archive.to_file("./Data/Working Data/Grants Councils.geojson", driver="GeoJSON")