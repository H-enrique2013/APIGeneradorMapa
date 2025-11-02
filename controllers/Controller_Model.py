#!/usr/bin/env python
# coding: utf-8

# In[18]:
import geopandas as gpd
import numpy as np
import pandas as pd
from controllers.Model import RutaShape
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from shapely.geometry import MultiLineString,Point
import pyproj,sys
import folium
#Calculo de la distancia basada en el elipsoide de WGS84
geod = pyproj.Geod(ellps="WGS84")
import datetime
import os
import simplekml
from pathlib import Path
# In[1]:


#Función importar Mapas(Sector Estadístico y Agrícola)
def ImportData(dep,prov,distr,sec_est):
    lista_shape=RutaShape(dep,prov,distr)
    path_map=os.path.join(lista_shape[0])
    if not os.path.exists(path_map):
        print("Contenido de la carpeta 'shape':", os.listdir('shape'))
        raise ValueError(f"No se encontraron archivos en la ruta '{path_map}'")
    
    path_map1=os.path.join(lista_shape[1])
    if not os.path.exists(path_map1):
        raise ValueError(f"No se encontraron archivos en la ruta '{path_map1}'")

    shape_sector=gpd.read_file(path_map)
    shape_agricola=gpd.read_file(path_map1)
    map1=shape_sector[(shape_sector['NOMBDEP']==dep)&(shape_sector['NOMBPROV']==prov)&(shape_sector['NOMBDIST']==distr)
    & (shape_sector['NOM_SE']==sec_est)]
    map2=shape_agricola[(shape_agricola['NOMBDEP']==dep)&(shape_agricola['NOMBPROV']==prov)&(shape_agricola['NOMBDIST']==distr)
    & (shape_agricola['NOM_SE']==sec_est)]
    return map1,map2
def ImportDataSectorNULL(dep,prov,distr):
    lista_shape=RutaShape(dep,prov,distr)
    path_map=os.path.join(lista_shape[0])
    
    if not os.path.exists(path_map):
        raise ValueError(f"No se encontraron archivos de shapefile para Sector Est. en '{path_map}'")
    
    path_map1=os.path.join(lista_shape[1])

    if not os.path.exists(path_map1):
        raise ValueError(f"No se encontraron archivos de shapefile para Sector Agricola. en '{path_map1}'")

    shape_sector=gpd.read_file(path_map)
    shape_agricola=gpd.read_file(path_map1)

    map1=shape_sector[(shape_sector['NOMBDEP']==dep)&(shape_sector['NOMBPROV']==prov)&(shape_sector['NOMBDIST']==distr)]
    map2=shape_agricola[(shape_sector['NOMBDEP']==dep)&(shape_agricola['NOMBPROV']==prov)&(shape_agricola['NOMBDIST']==distr)]
    #print(map1)
    return map1,map2


# In[20]:


#Agrupando en listas las coordenadas
def CalculoListaCoordenadas(map):
    #Division de los polígonos
    exploded =map.explode(ignore_index=True)
    lista=[]
    listaor_x=[]
    listaor_y=[]
    for i in range(len(exploded)):
        dxy=[]
        df = exploded.filter(items=[i],axis=0)
        df1=df.loc[i,'geometry']
        x0,y0,x1,y1 = df1.bounds
        dxy=[[x0,x1],[y0,y1]]
        lista.append(dxy)

    for i in lista:
        listaor_x.append(i[0])
        listaor_y.append(i[1])
    #Creando los DataFrame y ordenando de menor a mayor los ejes
    df_x=pd.DataFrame(listaor_x,columns=['Xmin','Xmax'])
    df_y=pd.DataFrame(listaor_y,columns=['Ymin','Ymax'])
    df_orden_x=df_x.sort_values(by=['Xmin'])
    df_orden_y=df_y.sort_values('Ymin')
    return  (df_orden_x,df_orden_y)

# In[21]:
#Funcion para unir los puntos de cada poligono y eliminando los espacios que no contienen sector agrícola.
def CalculoLineaBase(df_orden,mapa,r):
    lista_xy=df_orden.to_numpy().tolist()
    puntos=[]
    n_poligonos=len(lista_xy)
    x0,y0,x1,y1 =mapa.bounds
    if n_poligonos==0:
        if r=="X":
            puntos.append([x0,x1])
        elif r=="Y":
            puntos.append([y0,y1])
    elif n_poligonos==1:
        inf=lista_xy[0][0]
        sup=lista_xy[0][1]
        puntos.append([inf,sup])
    elif n_poligonos>1:
        for i in range(n_poligonos-1):
            if i==0:
                inf=lista_xy[i][0]
                sup=lista_xy[i][1]
                for j in range(1,n_poligonos):
                    if sup<lista_xy[j][0]:
                        sup=sup
                        c=j
                        break
                    elif lista_xy[j][0]<=sup and sup<=lista_xy[j][1]:
                        sup=lista_xy[j][1]
                        c=j
                    elif lista_xy[j][1]<sup:
                        sup=sup
                        c=j
                puntos.append([inf,sup])

            if i==c:
                inf=lista_xy[i][0]
                sup=lista_xy[i][1]
                for a in range(c,n_poligonos):
                    if sup<lista_xy[a][0]:
                        sup=sup
                        c=a
                        break
                    elif lista_xy[a][0]<=sup and sup<=lista_xy[a][1]:
                        sup=lista_xy[a][1]
                        c=a
                    elif lista_xy[a][1]<sup:
                        sup=sup
                        c=a
                puntos.append([inf,sup])
        
    return puntos


# In[22]:
def CalculoShapeBase(xy,puntosxy,mapa,r):
    #Calculo de los xmin,xmax,ymin,ymax del sector estadistico
    xmin, ymin, xmax, ymax =mapa.total_bounds
    coordsxy=[]
    longtotalxy=[]
    if xy=="X":
        ymin=ymin-0.01
        for i in range(len(puntosxy)):
            p=((puntosxy[i][0],ymin),(puntosxy[i][1],ymin))
            coordsxy.append(p)
    elif xy=="Y":
        xmax=xmax+0.01
        for i in range(len(puntosxy)):
            p=((xmax,puntosxy[i][0]),(xmax,puntosxy[i][1]))
            coordsxy.append(p)
    
    #Calculo de la Longitudes
    for i in coordsxy:
        (x1,y1),(x2,y2)=i
        angle1,angle2,longxy= geod.inv(x1,y1,x2,y2)
        longtotalxy.append(round(longxy,2))
    
    sum_longtotalxy=round(sum(longtotalxy),2)
    
    lines=MultiLineString(coordsxy)
    linea_xy=pd.DataFrame([lines],columns=["geometry"])
    #linea_x['geometry']=linea_x['geometry'].apply(wkt.loads)
    linea_xy= gpd.GeoDataFrame(linea_xy, crs='epsg:4326')
    if r=="linea":
        salida=linea_xy
    elif r=="longtotalxy":
        salida=longtotalxy
    elif r=="longitud_linea":
        salida=sum_longtotalxy
      
    return salida


# In[23]:


#Función para el cáculo de los puntos aleatorios en la linea Base x o y
def CalculoPuntosAleatorios(xy,sum_longtotalxy,puntos_xy,longtotalxy,n_aleatorio,df_aleatorio,mapa,r):
    linea_muestreo={}
    for i in range(1,6):
        text="N"+str(i)
        linea_muestreo["Linea"+str(i)]=round(df_aleatorio[text][n_aleatorio-1]*sum_longtotalxy,2)
    
    #Calculando los puntos aleatorios en la recta de mayor longitud
    puntos_aleatorios=[]
    for p in range(1,6):
        tex="Linea"+str(p)
        muestra=linea_muestreo[tex]
        for i in range(len(puntos_xy)):
            if muestra<=longtotalxy[i]:
                n_linea=i
                break
            if muestra>longtotalxy[i]:
                muestra-=longtotalxy[i]

        punto=puntos_xy[n_linea][0]+(puntos_xy[n_linea][1]-puntos_xy[n_linea][0])*(muestra/longtotalxy[n_linea])
        puntos_aleatorios.append(punto)
    
    #Calculo de los xmin,xmax,ymin,ymax del sector estadistico
    xmin, ymin, xmax, ymax =mapa.total_bounds
    #Caculo del shape puntos aleatorios
    coor_puntos_xy=[]
    if xy=="X":
        ymin=ymin-0.01
        for i in range(5):
            p=Point(puntos_aleatorios[i],ymin)
            coor_puntos_xy.append(p)
    elif xy=="Y":
        xmax=xmax+0.01
        for i in range(5):
            p=Point(xmax,puntos_aleatorios[i])
            coor_puntos_xy.append(p)
        
    #Creando los Point
    puntos_aleatorios_xy=pd.DataFrame(coor_puntos_xy,columns=["geometry"])
    #linea_x['geometry']=linea_x['geometry'].apply(wkt.loads)
    puntos_aleatorios_xy= gpd.GeoDataFrame(puntos_aleatorios_xy, crs='epsg:4326')
    puntos_aleatorios_xy
    
    if r=="linea_muestreo":
        salida=linea_muestreo
    elif r=="puntos_aleatorios":
        salida=puntos_aleatorios
    elif r=="puntos_aleatorios_xy":
        salida=puntos_aleatorios_xy
    
    return salida

# In[24]:

#Cáclulo de las proyecciones de las Bases 
def CalculoProyeccionesBases(xy,puntos_aleatorios,mapa):
    #Calculo de los xmin,xmax,ymin,ymax del sector estadistico
    xmin, ymin, xmax, ymax =mapa.total_bounds
    #Caculo del shape de la linea Horizontal
    proyeccionesxy=[]
    if xy=="X":
        ymin=ymin-0.01
        for i in range(5):
            p=((puntos_aleatorios[i],ymin),(puntos_aleatorios[i],ymax))
            proyeccionesxy.append(p)
    elif xy=="Y":
        xmax=xmax+0.01
        for i in range(5):
            p=((xmin,puntos_aleatorios[i]),(xmax,puntos_aleatorios[i]))
            proyeccionesxy.append(p)
        
    #Creando un Multipolyline
    lines=MultiLineString(proyeccionesxy)
    proyec_xy=pd.DataFrame([lines],columns=["geometry"])
    #linea_x['geometry']=linea_x['geometry'].apply(wkt.loads)
    proyec_xy= gpd.GeoDataFrame(proyec_xy, crs='epsg:4326')
     
    return proyec_xy

# In[25]:

#Cáculo de las coordenadas de los Bastones para obtener las lineas proyectadas en el área agrícola
def CalculoCoor_Bastones(xy,exploded1,r):
    line_bastones=[]
    for i in range(len(exploded1)):
        df = exploded1.filter(items =[i], axis=0)
        df1=df.loc[i,'geometry']
        x0,y0,x1,y1 =df1.bounds
        if xy=="X":
            dxy=[x0,[(x0,y0),(x1,y1)]]
        elif xy=="Y":
            dxy=[y0,[(x0,y0),(x1,y1)]]
        line_bastones.append(dxy)
    bt=[]
    for i in line_bastones:
        bt.append(i[0])
    btuni=list(set(bt))
    btuni.sort()
    if r=="line_bastones":
        salida=line_bastones
    elif r=="btuni":
        salida=btuni
    return salida


# In[26]:


#Calculo de la distancia basada en el elipsoide de WGS84
def CalculoLongProyecciones(line_bastones,btuni,r):
    #geod = pyproj.Geod(ellps="WGS84")
    #Longitud de los bastones en la RECTA X
    long_baston_proyecxy={}
    linea_bastonxy={}
    coord_bastonxy={}
    for i in range(1,6):
        suma=0
        clave="Baston"+str(i)
        bs=[]
        coo=[]
        for j in line_bastones:
            if btuni[i-1]==j[0]:
                (x1,y1),(x2,y2)=j[1]
                angle1,angle2,longxy= geod.inv(x1,y1,x2,y2)
                bs.append(round(longxy,2))
                suma+=longxy
                coo.append(j[1])
        long_baston_proyecxy[clave]=round(suma,2)
        linea_bastonxy[clave]=bs
        coord_bastonxy[clave]=coo
    if r=="long_baston_proyecxy":
        salida=long_baston_proyecxy
    elif r=="linea_bastonxy":
        salida=linea_bastonxy
    elif r=="coord_bastonxy":
        salida=coord_bastonxy
    return salida


# In[27]:


#Funcion de los once Puntos
def CalculoOncePuntos(xy,df_factores,linea_bastonxy,coord_bastonxy):
    #Calculando de los 11 puntos 
    puntos_baston={}
    data=df_factores[["Linea_muestreo","Punto_muestreo","Ubicacion_punto"]]
    for i in range(11):
        texto="Punto"+str(i+1)
        punto=data.loc[i]["Ubicacion_punto"]
        puntos_baston[texto]=round(punto,2)

    #Calculando los 11 puntos
    pt_bastones={}
    for p in range(1,12):
        text="Punto"+str(p)
        muestra=puntos_baston[text]
        if p<=2:
            lng=linea_bastonxy['Baston1']
            puntos_bastonxy=coord_bastonxy['Baston1']
            for i in range(len(puntos_bastonxy)):
                if muestra<=lng[i]:
                    n_linea=i
                    #print(n_linea)
                    break
                if muestra>lng[i]:
                    muestra-=lng[i]
            (x1,y1),(x2,y2)=puntos_bastonxy[n_linea]
            if xy=="X":
                punto=y1+(y2-y1)*(muestra/lng[n_linea])
                pt_bastones['P'+str(p)]=(x1,punto)
            elif xy=="Y":
                punto=x1+(x2-x1)*(muestra/lng[n_linea])
                pt_bastones['P'+str(p)]=(punto,y1)
                
        elif 2<p and p<=4:

            lng=linea_bastonxy['Baston2']
            puntos_bastonxy=coord_bastonxy['Baston2']
            for i in range(len(puntos_bastonxy)):
                if muestra<=lng[i]:
                    n_linea=i
                    break
                if muestra>lng[i]:
                    muestra-=lng[i]
            (x1,y1),(x2,y2)=puntos_bastonxy[n_linea]
            if xy=="X":
                punto=y1+(y2-y1)*(muestra/lng[n_linea])
                pt_bastones['P'+str(p)]=(x1,punto)
            elif xy=="Y":
                punto=x1+(x2-x1)*(muestra/lng[n_linea])
                pt_bastones['P'+str(p)]=(punto,y1)

        elif 4<p and p<=7:
            lng=linea_bastonxy['Baston3']
            puntos_bastonxy=coord_bastonxy['Baston3']
            for i in range(len(puntos_bastonxy)):
                if muestra<=lng[i]:
                    n_linea=i
                    break
                if muestra>lng[i]:
                    muestra-=lng[i]
            (x1,y1),(x2,y2)=puntos_bastonxy[n_linea]
            if xy=="X":
                punto=y1+(y2-y1)*(muestra/lng[n_linea])
                pt_bastones['P'+str(p)]=(x1,punto)
            elif xy=="Y":
                punto=x1+(x2-x1)*(muestra/lng[n_linea])
                pt_bastones['P'+str(p)]=(punto,y1)

        elif 7<p and p<=9:
            lng=linea_bastonxy['Baston4']
            puntos_bastonxy=coord_bastonxy['Baston4']
            for i in range(len(puntos_bastonxy)):
                if muestra<=lng[i]:
                    n_linea=i
                    break
                if muestra>lng[i]:
                    muestra-=lng[i]
            (x1,y1),(x2,y2)=puntos_bastonxy[n_linea]
            if xy=="X":
                punto=y1+(y2-y1)*(muestra/lng[n_linea])
                pt_bastones['P'+str(p)]=(x1,punto)
            elif xy=="Y":
                punto=x1+(x2-x1)*(muestra/lng[n_linea])
                pt_bastones['P'+str(p)]=(punto,y1)

        elif 9<p and p<=11:
            lng=linea_bastonxy['Baston5']
            puntos_bastonxy=coord_bastonxy['Baston5']
            for i in range(len(puntos_bastonxy)):
                if muestra<=lng[i]:
                    n_linea=i
                    #print(n_linea)
                    break
                if muestra>lng[i]:
                    muestra-=lng[i]
            (x1,y1),(x2,y2)=puntos_bastonxy[n_linea]
            if xy=="X":
                punto=y1+(y2-y1)*(muestra/lng[n_linea])
                pt_bastones['P'+str(p)]=(x1,punto)
            elif xy=="Y":
                punto=x1+(x2-x1)*(muestra/lng[n_linea])
                pt_bastones['P'+str(p)]=(punto,y1)
        
    return pt_bastones
               

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


# In[1]:
class ImagenFinal:
    def ImagenprincipalHtml(mapa, mapa1, linea_x, linea_y, proyec_xy, puntos_aleatorios_xy, pt_bastones, dep, prov, distr,sec_est,n_aleatorio, imagenprincipal, xy):
        
        def cargar_shape(ruta, dep, prov=None, distr=None):

            BASE_DIR = Path(__file__).resolve().parent.parent

            # Normaliza la ruta
            if not ruta:
                raise ValueError("La ruta del shapefile está vacía o no se proporcionó")

            path_maps = (BASE_DIR / ruta).resolve()
            

            if not path_maps.exists():
                raise ValueError(f"No se encontraron archivos en la ruta '{path_maps}'")

            try:
                shape = gpd.read_file(path_maps)
            except Exception as e:
                raise ValueError(f"Error leyendo shapefile: {e}")

            if prov and distr:
                return shape[(shape['DN99'] == dep) & (shape['PN99'] == prov) & (shape['DIN99'] == distr)]
            return shape[shape['DN99'] == dep]
        

        # Cargando archivos shape
        ruta = RutaShape(dep,prov,distr)
        mapa2 = cargar_shape(ruta[2], dep, prov, distr)
        mapa3 = cargar_shape(ruta[3], dep, prov, distr)
        mapa5 = cargar_shape(ruta[5], dep, prov, distr)
        mapa6 = cargar_shape(ruta[6], dep, prov, distr)

        # Convertir cualquier campo de tipo Timestamp a cadena
        for col in mapa.columns:
            if 'datetime64' in str(mapa[col].dtype):
                mapa[col] = mapa[col].astype(str)

        for col in mapa1.columns:
            if 'datetime64' in str(mapa1[col].dtype):
                mapa1[col] = mapa1[col].astype(str)

        for col in mapa2.columns:
            if 'datetime64' in str(mapa2[col].dtype):
                mapa2[col] = mapa2[col].astype(str)

        for col in mapa3.columns:
            if 'datetime64' in str(mapa3[col].dtype):
                mapa3[col] = mapa3[col].astype(str)

        for col in mapa5.columns:
            if 'datetime64' in str(mapa5[col].dtype):
                mapa5[col] = mapa5[col].astype(str)

        for col in mapa6.columns:
            if 'datetime64' in str(mapa6[col].dtype):
                mapa6[col] = mapa6[col].astype(str)

        # Puntos
        puntos = [Point(coords) for coords in pt_bastones.values()]
        gdf_puntos = gpd.GeoDataFrame(list(pt_bastones.keys()), geometry=puntos, crs="EPSG:4326")

        map_center = [gdf_puntos.geometry.y.mean(), gdf_puntos.geometry.x.mean()]
        m = folium.Map(location=map_center, zoom_start=14)
        #Token Mapbox
        mapbox_api_key = 'pk.eyJ1IjoiZW5yaXF1ZXNhbmRvdmFsIiwiYSI6ImNseWhyYm51ZzA3bTgyanB3bXp6OHF3azUifQ.vBNEIvxG3CUI_T-aSd372A'
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

        # Añadir capas según imagenprincipal
        
        if imagenprincipal == "M1":
            folium.GeoJson(
                mapa,name='Sector Estadistico',
                style_function=lambda feature: {
                    'fillColor': '#ADD8E6',  # Azul claro
                    'weight': 1,             # Grosor del borde
                    'fillOpacity': 0.4       # Opacidad del relleno
                }
            ).add_to(m)

            folium.GeoJson(
                mapa1,name='Sector Agrícola',
                style_function=lambda feature: {
                    'fillColor': '#90EE90',  # verde claro
                    'color': '#006400',      # verde oscuro para el borde
                    'weight': 1,             # Grosor del borde
                    'fillOpacity': 0.4       # Opacidad del relleno
                }
            ).add_to(m)

            if not mapa2.empty:
                # Crear un FeatureGroup para los centros poblados
                centros_poblados = folium.FeatureGroup(name='Centro Poblado')

                # Agregar los datos shapefile como puntos en el mapa con círculos púrpuras
                for _, feature in mapa2.iterrows():
                    folium.CircleMarker(
                        location=[feature.geometry.y, feature.geometry.x],
                        radius=4,  # Reducir el radio del círculo
                        color='purple',
                        fill=True,
                        fill_color='purple',
                        fill_opacity=0.6,
                        weight=1
                    ).add_to(centros_poblados)
                    # Agregar la etiqueta siempre visible
                    #folium.Marker(
                    #    location=[feature.geometry.y, feature.geometry.x],
                    #    icon=folium.DivIcon(
                    #        html=f'<div style="font-size: 10px; color: black; white-space: nowrap;">{feature["DESCRIPCIO"]}</div>'
                    #    )
                    #).add_to(centros_poblados)

                # Añadir el FeatureGroup al mapa
                centros_poblados.add_to(m)
            
            if not mapa3.empty:
                folium.GeoJson(
                    mapa3,name='Curvas de Nivel',
                    style_function=lambda feature: {
                        'fillColor': '#8B4513',  # Marron claro
                        'color': '#8B4513',      # Marron oscuro para el borde
                        'weight': 1,             # Grosor del borde
                        'fillOpacity': 0.6       # Opacidad del relleno
                    }
                ).add_to(m)

            if not mapa5.empty:
                folium.GeoJson(
                    mapa5,name='Ríos',
                    style_function=lambda feature: {
                        'fillColor': 'darkblue',  # blue claro
                        'color': 'darkblue',      # blue oscuro para el borde
                        'weight': 1,             # Grosor del borde
                        'fillOpacity': 0.6       # Opacidad del relleno
                    }
                ).add_to(m)
            
            if not mapa6.empty:
                folium.GeoJson(
                    mapa6,name='Trocha y Camino',
                    style_function=lambda feature: {
                        'fillColor': 'slategray', #gris
                        'color':'slategray',      #gris
                        'weight': 1,             # Grosor del borde
                        'fillOpacity': 0.6       # Opacidad del relleno
                    }
                ).add_to(m)

        elif imagenprincipal == "NO M1":
            folium.GeoJson(
                mapa,name='Sector Estadistico',
                style_function=lambda feature: {
                    'fillColor': '#ADD8E6',  # Azul claro
                    'weight': 1,             # Grosor del borde
                    'fillOpacity': 0.4       # Opacidad del relleno
                }
            ).add_to(m)

            if not mapa2.empty:
                # Crear un FeatureGroup para los centros poblados
                centros_poblados = folium.FeatureGroup(name='Centro Poblado')

                # Agregar los datos shapefile como puntos en el mapa con círculos púrpuras
                for _, feature in mapa2.iterrows():
                    folium.CircleMarker(
                        location=[feature.geometry.y, feature.geometry.x],
                        radius=4,  # Reducir el radio del círculo
                        color='purple',
                        fill=True,
                        fill_color='purple',
                        fill_opacity=0.6,
                        weight=1
                    ).add_to(centros_poblados)

                # Añadir el FeatureGroup al mapa
                centros_poblados.add_to(m)
            
            if not mapa3.empty:
                folium.GeoJson(
                    mapa3,name='Curvas de Nivel',
                    style_function=lambda feature: {
                        'fillColor': '#8B4513',  # Marron claro
                        'color': '#8B4513',      # Marron oscuro para el borde
                        'weight': 1,             # Grosor del borde
                        'fillOpacity': 0.6       # Opacidad del relleno
                    }
                ).add_to(m)

            if not mapa5.empty:
                folium.GeoJson(
                    mapa5,name='Ríos',
                    style_function=lambda feature: {
                        'fillColor': 'darkblue',  # blue claro
                        'color': 'darkblue',      # blue oscuro para el borde
                        'weight': 1,             # Grosor del borde
                        'fillOpacity': 0.6       # Opacidad del relleno
                    }
                ).add_to(m)
            
            if not mapa6.empty:
                folium.GeoJson(
                    mapa6,name='Trocha y Camino',
                    style_function=lambda feature: {
                        'fillColor': 'slategray', #gris
                        'color':'slategray',      #gris
                        'weight': 1,             # Grosor del borde
                        'fillOpacity': 0.6       # Opacidad del relleno
                    }
                ).add_to(m)
   
        # Añadir líneas
        if xy == "X":
            folium.GeoJson(
                linea_x,name='Línea Principal',
                style_function=lambda feature: {
                    'fillColor': 'Red',
                    'color':'Red',  
                    'weight': 2,             # Grosor del borde
                    'fillOpacity': 0.6       # Opacidad del relleno
                }
            ).add_to(m)
        elif xy == "Y":
            folium.GeoJson(
                linea_y,name='Línea Principal',
                style_function=lambda feature: {
                    'fillColor': 'Red',
                    'color':'Red',
                    'weight': 2,             # Grosor del borde
                    'fillOpacity': 0.6       # Opacidad del relleno
                }
            ).add_to(m)
        
        # Añadir proyecciones al mapa
        folium.GeoJson(
            proyec_xy,name='Líneas de Control',
            style_function=lambda feature: {
                'fillColor': '#90EE90',  # Verde claro (si tiene áreas de relleno)
                'color': '#FF0000',      # Rojo para las líneas
                'weight': 2,             # Grosor de las líneas
                'opacity': 0.3,          # Baja opacidad para las líneas
                'dashArray': '5, 5'      # Líneas punteadas (5 píxeles de línea, 5 píxeles de espacio)
            }
        ).add_to(m)

        # Añade los puntos aleatorios al mapa como puntos rojos sin radio significativo
        for _, row in puntos_aleatorios_xy.iterrows():
            folium.CircleMarker(
                location=[row.geometry.y, row.geometry.x],
                radius=1,  # radio pequeño para que se vea como un punto
                color='red',
                fill=True,
                fill_color='red'
            ).add_to(m)

        #for punto, coord in pt_bastones.items():
        #    folium.Marker(location=[coord[1], coord[0]], popup=punto, icon=folium.Icon(color='red')).add_to(m)
        
        # Agregar marcadores con texto personalizado
        
        for punto, coord in pt_bastones.items():
            folium.Marker(
                location=[coord[1], coord[0]],  # [latitud, longitud]
                popup=punto,
                icon=folium.DivIcon(
                    html=f'''
                        <div style="
                            position: relative;
                            text-align: center;
                            background-color: white;
                            color: red;
                            font-size: 8px;
                            font-weight: bold;
                            border-radius: 50%;
                            width: 11px;
                            height: 11px;
                            line-height: 11px;">
                            {punto}
                        </div>
                    '''
                )
            ).add_to(m)
        # Añadir control de capas
        folium.LayerControl().add_to(m)
        # Añadir leyenda
        # Añadir leyenda
        legend_html = '''
            <div style="position: fixed; 
            top: 420px; left: 7px; width: 300px; height: 236px; 
            background-color: white; z-index:9999; font-size:11px;
            border:2px solid grey; padding: 0px;">
            <div style="background-color: red; font-size:12px;color:white;padding: 2px;">
            <strong>LEYENDA</strong>
            </div>
            <div style="padding-left: 8px;"> <!-- Aplica margen interno a la izquierda -->
                <svg width="24" height="24"><circle cx="12" cy="12" r="8" style="fill:white;stroke-width:1;stroke:rgb(0,0,0)" /></svg> Puntos<br>
                <svg width="24" height="24"><rect width="24" height="18" style="fill:#ADD8E6;stroke-width:1;stroke:rgb(0,0,0)" /></svg> Sector Estadístico<br>
                <svg width="24" height="24"><rect width="24" height="18" style="fill:#90EE90;stroke-width:1;stroke:rgb(0,100,0)" /></svg> Sector Agrícola<br>
                <svg width="24" height="24"><circle cx="12" cy="12" r="6" style="fill:purple;stroke-width:1;stroke:rgb(0,0,0)" /></svg> Centro Poblado<br>
                <svg width="24" height="24"><rect width="24" height="18" style="fill:#8B4513;stroke-width:1;stroke:rgb(0,0,0)" /></svg> Curvas de Nivel<br>
                <svg width="24" height="24"><rect width="24" height="18" style="fill:darkblue;stroke-width:1;stroke:rgb(0,0,0)" /></svg> Ríos<br>
                <svg width="24" height="24"><rect width="24" height="18" style="fill:slategray;stroke-width:1;stroke:rgb(0,0,0)" /></svg> Trocha y Camino<br>
                <svg width="24" height="24"><line x1="0" y1="12" x2="24" y2="12" style="stroke:red;stroke-width:4" /></svg> Línea Principal<br>
                <svg width="24" height="24"><line x1="0" y1="12" x2="24" y2="12" style="stroke:red;stroke-width:4;stroke-dasharray:5, 5" /></svg> Líneas de Control<br>
            </div>
            </div>
        '''
        m.get_root().html.add_child(folium.Element(legend_html))
        # Añadir cuadro "Datos del sector Estadístico"
        datos_sector = f'''
        <div style="position: fixed; 
        top: 80px; left: 7px; width: 300px; height: 106px; 
        background-color: white; z-index:9999; font-size:11px;
        border:2px solid grey; padding: 0px;">
        <div style="background-color: red; font-size:12px;color:white;padding: 2px;">
        <strong>DATOS DEL SECTOR ESTADÍSTICO</strong>
        </div>
        <div style="padding-left: 8px;">
            Departamento: {dep}<br>
            Provincia: {prov}<br>
            Distrito: {distr}<br>
            Sector Estadístico: {sec_est}<br>
            N° Aleatorio: {n_aleatorio}<br>
        </div>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(datos_sector))

        # Añadir cuadro "Cuadro de Coordenadas"
        coordenadas = '''
        <div style="position: fixed; top: 183px; left: 7px; width: 300px; height: 241px; 
        background-color: white; z-index: 9999; font-size: 11px; border: 2px solid grey; padding: 0px;">
        <div style="background-color: red; font-size: 12px; color: white; padding: 2px;">
        <strong>CUADRO DE COORDENADAS</strong>
        </div>
        <table style="width: 100%; border-collapse: collapse; text-align: center;">
        <tr>
        <th style="text-align: center; padding-right: 10px;">Puntos</th>
        <th style="text-align: center; padding-right: 10px;">Longitud</th>
        <th style="text-align: center;">Latitud</th>
        </tr>
        '''
        # Iterar sobre los puntos y coordenadas
        for punto, coord in pt_bastones.items():
            # Conversión de longitud
            grados_lon, minutos_lon, segundos_lon = decimal_a_gms(coord[0])
            # Conversión de latitud
            grados_lat, minutos_lat, segundos_lat = decimal_a_gms(coord[1])
            # Direcciones W o S
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

        # Generar nombre de archivo HTML
        now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        url_mapa = f"{dep}_{prov}_{distr}_{now}.html"
        filepath = os.path.join("static", url_mapa)
        # Guardar el mapa como archivo HTML
        m.save(filepath)

        return  filepath
    
    def ImagenprincipalKml(mapa,mapa1,pt_bastones,dep,prov,distr):
        # Crear archivo KML
        kml = simplekml.Kml()

        # Añadir puntos de `pt_bastones` al KML con estilo de "globito" en color rojo
        for punto, coord in pt_bastones.items():
            pnt = kml.newpoint(name=punto, coords=[(coord[0], coord[1])])
            pnt.style.iconstyle.color = simplekml.Color.red  # Color rojo para el punto
            pnt.style.iconstyle.icon.href = "http://maps.google.com/mapfiles/kml/paddle/red-circle.png"  # Estilo de globito

        # Añadir geometrías de `mapa` al KML (Sector Estadístico) en azul claro
        for _, row in mapa.iterrows():
            if row.geometry.geom_type == 'Polygon':
                pol = kml.newpolygon(name=row.get('NOM_SE', 'Sector Estadístico'), 
                                    outerboundaryis=list(row.geometry.exterior.coords))
                # Estilo del sector estadístico
                pol.style.polystyle.color = simplekml.Color.changealphaint(100, simplekml.Color.hex("ADD8E6"))  # Color #ADD8E6
                pol.style.linestyle.color = simplekml.Color.hex("1d4ed8")  # Bordes en color azul oscuro
                pol.style.linestyle.width = 1  # Peso del borde
            elif row.geometry.geom_type == 'MultiPolygon':
                for poly in row.geometry.geoms:
                    pol = kml.newpolygon(name=row.get('NOM_SE', 'Sector Estadístico'), 
                                        outerboundaryis=list(poly.exterior.coords))
                    # Estilo del sector estadístico
                    pol.style.polystyle.color = simplekml.Color.changealphaint(100, simplekml.Color.hex("ADD8E6"))
                    pol.style.linestyle.color = simplekml.Color.hex("1d4ed8")
                    pol.style.linestyle.width = 1

        # Añadir geometrías de `mapa1` al KML (Sector Agrícola) en verde claro con borde verde oscuro
        for _, row in mapa1.iterrows():
            if row.geometry.geom_type == 'Polygon':
                pol = kml.newpolygon(name=row.get('NOM_SE', 'Sector Agrícola'), 
                                    outerboundaryis=list(row.geometry.exterior.coords))
                # Estilo del sector agrícola
                pol.style.polystyle.color = simplekml.Color.changealphaint(100, simplekml.Color.hex("90EE90"))  # Color #90EE90
                pol.style.linestyle.color = simplekml.Color.hex("006400")  # Bordes en color verde oscuro #006400
                pol.style.linestyle.width = 1
            elif row.geometry.geom_type == 'MultiPolygon':
                for poly in row.geometry.geoms:
                    pol = kml.newpolygon(name=row.get('NOM_SE', 'Sector Agrícola'), 
                                        outerboundaryis=list(poly.exterior.coords))
                    # Estilo del sector agrícola
                    pol.style.polystyle.color = simplekml.Color.changealphaint(100, simplekml.Color.hex("90EE90"))
                    pol.style.linestyle.color = simplekml.Color.hex("006400")
                    pol.style.linestyle.width = 1

        # Generar nombre de archivo KML con fecha y hora actuales
        now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        kml_filepath = os.path.join("static", f"{dep}_{prov}_{distr}_{now}.kml")
        
        # Guardar archivo KML
        kml.save(kml_filepath)
    
        return kml_filepath

