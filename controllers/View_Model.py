#!/usr/bin/env python
# coding: utf-8

# In[1]:
import geopandas as gpd
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from controllers.Controller_Model import *
from controllers.Model import *


# %%

# In[4]:

class ViewModel():
    def ProcesarModel(dep,prov,distr,sec_est,n_aleatorio,campo_sector):
        if campo_sector=="NULL":
            (mapa,mapa1)=ImportDataSectorNULL(dep,prov,distr)
        elif campo_sector=="NO NULL":
            (mapa,mapa1)=ImportData(dep,prov,distr,sec_est)
            
        #lista_no_dep=["TUMBES","LAMBAYEQUE","PIURA","CAJAMARCA","AREQUIPA","AMAZONAS"]
        
        nom_sector=mapa["NOM_SE"].tolist()
        nom_agricola=mapa1["NOM_SE"].tolist()
        mapageometry_agricola=mapa1["geometry"].tolist()
        mapageometry_sector=mapa["geometry"].tolist()
        if nom_agricola==[] and nom_sector!=[] and mapageometry_agricola==[]:
            print("No hay sector agricola ,solo sector estadistico")
            (df_orden_x,df_orden_y)=CalculoListaCoordenadas(mapa)
            imagenprincipal="NO M1"
        elif nom_agricola==[] and nom_sector!=[] and mapageometry_agricola!=[]:
            print("Nombre del sector agricola Nan pero si hay su geometría")
            (df_orden_x,df_orden_y)=CalculoListaCoordenadas(mapa1)
            imagenprincipal="M1"
        elif (nom_sector==nom_agricola) and (len(nom_agricola)==1) and (nom_sector!=[]):
            print("Si hay un unico sector agricola")
            (df_orden_x,df_orden_y)=CalculoListaCoordenadas(mapa1)
            imagenprincipal="M1"
        elif nom_agricola==[] and nom_sector==[] and mapageometry_agricola!=[] and mapageometry_sector!=[]:
            print("Si hay geometria agricola pero su nombre esta como vacio!")
            (df_orden_x,df_orden_y)=CalculoListaCoordenadas(mapa1)
            imagenprincipal="M1"
        elif nom_agricola==[] and nom_sector==[] and mapageometry_agricola==[] and mapageometry_sector!=[]:
            print("No hay geometrya  agricola y los nombres sector estadistico y agricola esta vacio pero hay geometria en el sector")
            (df_orden_x,df_orden_y)=CalculoListaCoordenadas(mapa)
            imagenprincipal="NO M1"
            
        puntos_x=CalculoLineaBase(df_orden_x,mapa,"X")
        puntos_y=CalculoLineaBase(df_orden_y,mapa,"Y")
        
        #Shape de Puntos de las lineas Bases 
        linea_x=CalculoShapeBase("X",puntos_x,mapa,"linea")
        linea_y=CalculoShapeBase("Y",puntos_y,mapa,"linea")
        #longitud de las bases
        #Shape de Puntos de las lineas Bases 
        longtotalx=CalculoShapeBase("X",puntos_x,mapa,"longtotalxy")
        longtotaly=CalculoShapeBase("Y",puntos_y,mapa,"longtotalxy")
        #Longitud de las Lineas Bases 
        sum_longtotalx=CalculoShapeBase("X",puntos_x,mapa,"longitud_linea")
        sum_longtotaly=CalculoShapeBase("Y",puntos_y,mapa,"longitud_linea")
        #print("Long X:{}      Long Y :{}".format(sum_longtotalx,sum_longtotaly))
        (df_aleatorio,df_factores)=BaseModel()
        #Eligiendo la linea base de mayor longitud
        if sum_longtotalx>=sum_longtotaly:
            xy="X"
            sum_longtotalxy=sum_longtotalx
            puntos_xy=puntos_x
            longtotalxy=longtotalx
        else:
            xy="Y"
            sum_longtotalxy=sum_longtotaly
            puntos_xy=puntos_y
            longtotalxy=longtotaly

        linea_muestreo=CalculoPuntosAleatorios(xy,sum_longtotalxy,puntos_xy,longtotalxy,n_aleatorio,df_aleatorio,mapa,"linea_muestreo")
        puntos_aleatorios=CalculoPuntosAleatorios(xy,sum_longtotalxy,puntos_xy,longtotalxy,n_aleatorio,df_aleatorio,mapa,"puntos_aleatorios")
        puntos_aleatorios_xy=CalculoPuntosAleatorios(xy,sum_longtotalxy,puntos_xy,longtotalxy,n_aleatorio,df_aleatorio,mapa,"puntos_aleatorios_xy")
        #Proyecciones de los puntos en la línea Base
        proyec_xy=CalculoProyeccionesBases(xy,puntos_aleatorios,mapa)
        #Interseccion de los shape
        if nom_agricola==[]:
            intersec=proyec_xy.intersection(mapa, align=False)
        else:
            intersec=proyec_xy.intersection(mapa1, align=False)
            
        exploded1=intersec.explode(ignore_index=True)
        exploded1=gpd.GeoDataFrame(geometry=gpd.GeoSeries(exploded1))

        line_bastones=CalculoCoor_Bastones(xy,exploded1,"line_bastones")
        btuni=CalculoCoor_Bastones(xy,exploded1,"btuni")

        long_baston_proyecxy=CalculoLongProyecciones(line_bastones,btuni,"long_baston_proyecxy")
        linea_bastonxy=CalculoLongProyecciones(line_bastones,btuni,"linea_bastonxy")
        coord_bastonxy=CalculoLongProyecciones(line_bastones,btuni,"coord_bastonxy")

        #Creando la Tabla de Factores
        bast=list(long_baston_proyecxy.values())
        longitud_b=[bast[0],bast[0],bast[1],bast[1],bast[2],bast[2],bast[2],bast[3],bast[3],bast[4],bast[4]]
        df_factores["Longitud_linea"]=pd.DataFrame(longitud_b)
        df_factores["Longitud_linea1"]=df_factores['Longitud_linea']*df_factores['Factor1']
        df_factores["Longitud_linea2"]=df_factores['Longitud_linea']*df_factores['Factor2']
        df_factores["Ubicacion_punto"]=(df_factores["Longitud_linea1"]+df_factores["Longitud_linea2"])/2
        #Diccionario con los 11 puntos
        pt_bastones=CalculoOncePuntos(xy,df_factores,linea_bastonxy,coord_bastonxy)
        #Shape Once Puntos
        #once_puntos=ShapeOncePuntos(pt_bastones)
        #===============================================================================================================================
        
        Url=ImagenFinal.Imagenprincipal(mapa,mapa1,linea_x,linea_y, proyec_xy,puntos_aleatorios_xy,pt_bastones,
                                    dep,prov,distr,sec_est,n_aleatorio,imagenprincipal,xy)
        
        return Url
       
        




