import geopandas as gpd
import folium
import pandas as pd
import matplotlib.pyplot as plt
ruta_path="shapefiles/ICA/11_ICA_SectoresEstadisticos.shp"

# Cargar los shapefiles
gdf = gpd.read_file(ruta_path)


dep='ICA'
pro='NASCA'
dist='NASCA'
sec='POROMA'
gdfnuevo= gdf[
    (gdf["NOMBDEP"] == dep) &
    (gdf["NOMBPROV"] == pro) &
    (gdf["NOMBDIST"] == dist) &
    (gdf["NOM_SE"] == sec)
]
print(gdfnuevo)
