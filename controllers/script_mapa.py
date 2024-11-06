import geopandas as gpd
import folium
from shapely.geometry import Point
import os
import datetime
import simplekml
from controllers.Model import RutaShape

#Transformar coordenadas en formato decimal a grados,minutos y segundos
def decimal_a_gms(decimal):
    grados = int(decimal)
    minutos_dec = abs((decimal - grados) * 60)
    minutos = int(minutos_dec)
    segundos = (minutos_dec - minutos) * 60
    segundos=round(segundos,2)
    
    # Añadir cero a la izquierda en minutos si es necesario
    if minutos < 10:
        minutos_str = f"0{minutos}"
    else:
        minutos_str = str(minutos)

    # Añadir cero a la izquierda en segundos si es necesario
    if segundos < 10:
        seg="{:.2f}".format(segundos)
        segundos_str = f"0{seg}"
    else:
        segundos_str = "{:.2f}".format(segundos)
    
    return grados, minutos_str, segundos_str

# Función para determinar la dirección
def determinar_direccion(grados, latitud=True):
    if latitud:
        return 'N' if grados >= 0 else 'S'
    else:
        return 'E' if grados >= 0 else 'W'

def GeneradorHmtl_mapa(dep, prov, distr, sect, dicPuntos):
    shapefile_dir=RutaShape(dep)
    shapefile_path = os.path.join(shapefile_dir[0])
    if not os.path.exists(shapefile_path):
        print("Contenido de la carpeta 'shape':", os.listdir('shape'))
        raise ValueError(f"No se encontraron archivos en la ruta '{shapefile_path}'")
    
    shape_sector = gpd.read_file(shapefile_path)

    # Imprimir los tipos de datos de las columnas para depuración
    print(f"Column types in shapefile: {shape_sector.dtypes}")

    # Convertir cualquier campo de tipo Timestamp a cadena
    for col in shape_sector.columns:
        if 'datetime64' in str(shape_sector[col].dtype):
            shape_sector[col] = shape_sector[col].astype(str)

    # Filtrar el shapefile por departamento, provincia y distrito
    mapa = shape_sector[
        (shape_sector['NOMBDEP'] == dep) &
        (shape_sector['NOMBPROV'] == prov) &
        (shape_sector['NOMBDIST'] == distr) &
        (shape_sector['NOM_SE'] == sect)
    ]

    # Asegurarse de que el filtro no devuelve un NoneType
    if mapa.empty:
        raise ValueError(f"No se encontraron datos para {dep}, {prov}, {distr}")

    puntos = [Point(coords) for coords in dicPuntos.values()]
    gdf_puntos = gpd.GeoDataFrame(list(dicPuntos.keys()), geometry=puntos, crs="EPSG:4326")

    map_center = [gdf_puntos.geometry.y.mean(), gdf_puntos.geometry.x.mean()]
    m = folium.Map(location=map_center, zoom_start=14)

    mapbox_api_key = 'pk.eyJ1IjoiZW5yaXF1ZXNhbmRvdmFsIiwiYSI6ImNseWhxZmU2NTA3NjkybW9mbWxzZXpmdGQifQ.c1uvRvMYZyEaLaCqYioUmw'
    # Añadir capas de mapas utilizando Mapbox
    folium.TileLayer(
        tiles=f'https://api.mapbox.com/styles/v1/mapbox/streets-v11/tiles/256/{{z}}/{{x}}/{{y}}@2x?access_token={mapbox_api_key}',
        attr='Map data © <a href="https://www.mapbox.com/">Mapbox</a>',
        name='Mapa Estándar'
    ).add_to(m)
    
    folium.TileLayer(
        tiles=f'https://api.mapbox.com/styles/v1/mapbox/satellite-v9/tiles/256/{{z}}/{{x}}/{{y}}@2x?access_token={mapbox_api_key}',
        attr='Map data © <a href="https://www.mapbox.com/">Mapbox</a>',
        name='Vista Satelital'
    ).add_to(m)
    
    folium.TileLayer(
        tiles=f'https://api.mapbox.com/styles/v1/mapbox/satellite-streets-v11/tiles/256/{{z}}/{{x}}/{{y}}@2x?access_token={mapbox_api_key}',
        attr='Map data © <a href="https://www.mapbox.com/">Mapbox</a>',
        name='Híbrido'
    ).add_to(m)

    folium.GeoJson(
        mapa,name='Sector Estadistico',
        style_function=lambda feature: {
            'fillColor': '#ADD8E6',  # Azul claro
            'weight': 2,             # Grosor del borde
            'fillOpacity': 0.6       # Opacidad del relleno
        }
    ).add_to(m)

    for punto, coord in dicPuntos.items():
        folium.Marker(location=[coord[1], coord[0]], popup=punto, icon=folium.Icon(color='red')).add_to(m)

    # Añadir leyenda
    legend_html = '''
    <div style="position: fixed; 
    top: 468px; left: 7px; width: 300px; height: 100px; 
    background-color: white; z-index:9999; font-size:11px;
    border:2px solid grey; padding: 10px;">
    <div style="background-color: red; font-size:14px;color:white;padding: 5px;">
    <strong>LEYENDA</strong>
    </div>
    <i class="fa fa-map-marker fa-2x" style="color:red"></i> Puntos<br>
    <svg width="24" height="24"><rect width="24" height="24" style="fill:#ADD8E6;stroke-width:1;stroke:rgb(0,0,0)" /></svg> Sector Estadistico<br>
    </div>
     '''
    m.get_root().html.add_child(folium.Element(legend_html))

    # Añadir cuadro "Datos del sector Estadístico"
    datos_sector = f'''
    <div style="position: fixed; 
    top: 80px; left: 7px; width: 300px; height: 120px; 
    background-color: white; z-index:9999; font-size:11px;
    border:2px solid grey; padding: 10px;">
    <div style="background-color: red; font-size:14px;color:white;padding: 5px;">
    <strong>DATOS DEL SECTOR ESTADÍSTICO</strong>
    </div>
    Departamento: {dep}<br>
    Provincia: {prov}<br>
    Distrito: {distr}<br>
    Sector Estadístico: {sect}<br>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(datos_sector))

    # Añadir cuadro "Cuadro de Coordenadas"
    coordenadas = '''
    <div style="position: fixed; top: 200px; left: 7px; width: 300px; height: 268px; 
    background-color: white; z-index: 9999; font-size: 11px; border: 2px solid grey; padding: 10px;">
    <div style="background-color: red; font-size: 14px; color: white; padding: 5px;">
    <strong>CUADRO DE COORDENADAS</strong>
    </div>
    <table style="width: 100%;">
    <tr>
    <th style="text-align: center; padding-right: 10px;">Puntos</th>
    <th style="text-align: center; padding-right: 10px;">Longitud</th>
    <th style="text-align: center;">Latitud</th>
    </tr>
    '''
    # Iterar sobre los puntos y coordenadas
    for punto, coord in dicPuntos.items():
        # Conversión de longitud
        grados_lon, minutos_lon, segundos_lon = decimal_a_gms(coord[0])
        # Conversión de latitud
        grados_lat, minutos_lat, segundos_lat = decimal_a_gms(coord[1])
        # Direcciones
        direccion_lon = determinar_direccion(grados_lon, latitud=False)
        direccion_lat = determinar_direccion(grados_lat, latitud=True)

        # Ajustar grados para dirección negativa
        grados_lon = abs(grados_lon)
        grados_lat = abs(grados_lat)

        longitud=f"{grados_lon}°{minutos_lon}'{segundos_lon}\" {direccion_lon}"
        latitud=f"{grados_lat}°{minutos_lat}'{segundos_lat}\" {direccion_lat}"
        coordenadas += f'<tr><td>{punto}</td><td>{longitud}</td><td>{latitud}</td></tr>'
    coordenadas += '</table></div>'
    # Añadir el cuadro de coordenadas al mapa folium
    m.get_root().html.add_child(folium.Element(coordenadas))

    folium.LayerControl().add_to(m)

    now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    url_mapa = f"{dep}_{prov}_{distr}_{now}.html"
    filepath = os.path.join("static", url_mapa)
    m.save(filepath)

    # Crear archivo KML
    kml = simplekml.Kml()

    # Añadir puntos al KML
    for punto, coord in dicPuntos.items():
        kml.newpoint(name=punto, coords=[(coord[0], coord[1])])

    # Añadir geometrías del shapefile al KML
    for _, row in mapa.iterrows():
        if row.geometry.geom_type == 'Polygon':
            pol = kml.newpolygon(name=row['NOM_SE'], outerboundaryis=list(row.geometry.exterior.coords))
        elif row.geometry.geom_type == 'MultiPolygon':
            for poly in row.geometry:
                pol = kml.newpolygon(name=row['NOM_SE'], outerboundaryis=list(poly.exterior.coords))

    kml_filepath = os.path.join("static", f"{dep}_{prov}_{distr}_{now}.kml")
    kml.save(kml_filepath)

    return filepath,kml_filepath
