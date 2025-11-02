
import pandas as pd
import os
import geopandas as gpd
from pathlib import Path

# In[2]:
url_aleatorio=os.path.join(f'Tabla_n_aleatorio.csv')
url_factores=os.path.join(f'Tabla_factores.csv')
if not os.path.exists(url_aleatorio):
        raise ValueError(f"No se encontraron archivos de shapefile para 'Tabla N° Aleatorio' en '{url_aleatorio}'")

if not os.path.exists(url_factores):
        raise ValueError(f"No se encontraron archivos de shapefile para 'Tabla Factores' en '{url_factores}'")

def BaseModel():
    df_aleatorio=pd.read_csv(url_aleatorio,encoding="utf-8")
    df_factores=pd.read_csv(url_factores,encoding="utf-8")
    return (df_aleatorio,df_factores)


# In[4]:



def RutaShape(dep, prov, dist):
    BASE_DIR = Path(__file__).resolve().parent
    dep = dep.upper()  # 🔧 forzar mayúsculas para compatibilidad Linux
    ruta_base = BASE_DIR.parent / "shapefiles" / dep

    if not ruta_base.exists():
        raise ValueError(f"No existe la carpeta de shapefiles: {ruta_base}")

    lista_encontrados = []

    # Helper: ruta relativa limpia
    def rel(path):
        if not path:
                return ""
        try:
                # intenta hacer la ruta relativa respecto al proyecto raíz
                return str(path.relative_to(BASE_DIR.parent)).replace("\\", "/")
        except ValueError:
                # si no se puede, devuelve la ruta absoluta como fallback
                return str(path).replace("\\", "/")


    # --- 1. SECTORES ESTADÍSTICOS ---
    archivo_estadistico = next(ruta_base.rglob(f"*{dep}*_SectoresEstadisticos.shp"), None)
    lista_encontrados.append(rel(archivo_estadistico))

    # --- 2. SUPERFICIE AGRÍCOLA ---
    archivos_agricolas = list(ruta_base.rglob(f"*{dep}*_SuperficieAgricola.shp"))
    path_agricola = ""
    for archivo in archivos_agricolas:
        try:
            gdf = gpd.read_file(archivo)
            if {"NOMBDEP", "NOMBPROV", "NOMBDIST"}.issubset(gdf.columns):
                filtro = gdf[
                    (gdf["NOMBDEP"].str.upper() == dep.upper()) &
                    (gdf["NOMBPROV"].str.upper() == prov.upper()) &
                    (gdf["NOMBDIST"].str.upper() == dist.upper())
                ]
                if not filtro.empty:
                    path_agricola = rel(archivo)
                    break
        except Exception as e:
            print(f"⚠️ Error leyendo {archivo.name}: {e}")
    lista_encontrados.append(path_agricola)

    # --- 3. CENTROS POBLADOS ---
    archivo_centros = next(ruta_base.rglob(f"*Centros Poblados*{dep}*.shp"), None)
    lista_encontrados.append(rel(archivo_centros))

    # --- 4. CURVAS DE NIVEL ---
    archivo_curvas = next(ruta_base.rglob(f"*Curvas de Nivel*{dep}*.shp"), None)
    lista_encontrados.append(rel(archivo_curvas))

    # --- 5. DEPARTAMENTO ---
    archivo_departamento = next(ruta_base.rglob(f"*Dep*{dep}*.shp"), None)
    lista_encontrados.append(rel(archivo_departamento))

    # --- 6. RÍOS ---
    archivo_rios = next(ruta_base.rglob(f"*Rios*{dep}*.shp"), None)
    lista_encontrados.append(rel(archivo_rios))

    # --- 7. TROCHAS Y CAMINOS ---
    archivo_trochascamino = next(ruta_base.rglob(f"*Trocha*Camino*{dep}*.shp"), None)
    lista_encontrados.append(rel(archivo_trochascamino))

    return lista_encontrados


'''

def RutaShape(dep):
    
    dicdep={
          
            "APURIMAC":['shapefiles/03_APURIMAC_SectoresEstadisticos.shp',
                        'shapefiles/03_APURIMAC_SuperficieAgricola.shp',
                        'shapefiles/Centros Poblados Apurimac.shp',
                        'shapefiles/Curvas de Nivel Apurimac.shp',
                        'shapefiles/Dep Apurimac.shp',
                        'shapefiles/Rios Apurimac.shp',
                        'shapefiles/Trocha y Camino Apurimac.shp'],
            
            "AYACUCHO":['shapefiles/05_AYACUCHO_SectoresEstadisticos.shp',
                        'shapefiles/05_AYACUCHO_SuperficieAgricola.shp',
                        'shapefiles/Centros Poblados Ayacucho.shp',
                        'shapefiles/Curvas de Nivel Ayacucho.shp',
                        'shapefiles/Dep Ayacucho.shp',
                        'shapefiles/Rios Ayacucho.shp',
                        'shapefiles/Trocha y Camino Ayacucho.shp'
                        ],
            
            "HUANCAVELICA":['shapefiles/09_HUANCAVELICA_SectoresEstadisticos.shp',
                            'shapefiles/09_HUANCAVELICA_SuperficieAgricola.shp',
                            'shapefiles/Centros Poblados Huancavelica.shp',
                            'shapefiles/Curvas de Nivel Huancavelica.shp',
                            'shapefiles/Dep Huancavelica.shp',
                            'shapefiles/Rios Huancavelica.shp',
                            'shapefiles/Trocha y Camino Huancavelica.shp'
                            ],
            
            "MADRE DE DIOS":['shapefiles/17_MADRE_DE_DIOS_SectoresEstadisticos.shp',
                             'shapefiles/17_MADRE_DE_DIOS_SuperficieAgricola.shp',
                             'shapefiles/Centros Poblados Madre de Dios.shp',
                             'shapefiles/Curvas de Nivel Madre de Dios.shp',
                             'shapefiles/Dep Madre de Dios.shp',
                             'shapefiles/Rios Madre de Dios.shp',
                             'shapefiles/Trocha y Camino Madre de Dios.shp'
                             ],
            
            "MOQUEGUA":['shapefiles/18_MOQUEGUA_SectoresEstadisticos.shp',
                        'shapefiles/18_MOQUEGUA_SuperficieAgricola.shp',
                        'shapefiles/Centros Poblados Moquegua.shp',
                        'shapefiles/Curvas de Nivel Moquegua.shp',
                        'shapefiles/Dep Moquegua.shp',
                        'shapefiles/Rios Moquegua.shp',
                        'shapefiles/Trocha y Camino Moquegua.shp'
                        ],

            "PUNO":['shapefiles/21_PUNO_SectoresEstadisticos.shp',
                    'shapefiles/21_PUNO_SuperficieAgricola.shp',
                    'shapefiles/Centros Poblados Puno.shp',
                    'shapefiles/Curvas de Nivel Puno.shp',
                    'shapefiles/Dep Puno.shp',
                    'shapefiles/Rios Puno.shp',
                    'shapefiles/Trocha y Camino Puno.shp'
                    ],

            "TACNA":['shapefiles/23_TACNA_SectoresEstadisticos.shp',
                     'shapefiles/23_TACNA_SuperficieAgricola.shp',
                     'shapefiles/Centros Poblados Tacna.shp',
                     'shapefiles/Curvas de Nivel Tacna.shp',
                     'shapefiles/Dep Tacna.shp',
                     'shapefiles/Rios Tacna.shp',
                     'shapefiles/Trocha y Camino Tacna.shp'
                     ],

            "TUMBES":['shapefiles/24_TUMBES_SectoresEstadisticos.shp',
                      'shapefiles/24_TUMBES_SuperficieAgricola.shp',
                      'shapefiles/Centros Poblados Tumbes.shp',
                      'shapefiles/Curvas de Nivel Tumbes.shp',
                      'shapefiles/Dep Tumbes.shp',
                      'shapefiles/Rios Tumbes.shp',
                      'shapefiles/Trocha y Camino Tumbes.shp'
                      ],

            "CUSCO":['shapefiles/08_CUSCO_SectoresEstadisticos.shp',
                      'shapefiles/08_CUSCO_SuperficieAgricola.shp',
                      'shapefiles/Centros Poblados Cusco.shp',
                      'shapefiles/Curvas de Nivel Cusco.shp',
                      'shapefiles/Dep Cusco.shp',
                      'shapefiles/Rios Cusco.shp',
                      'shapefiles/Trocha y Camino Cusco.shp'
                     ],

             "LORETO":['shapefiles/16_LORETO_SectoresEstadisticos.shp',
                      'shapefiles/16_LORETO_SuperficieAgricola.shp',
                      'shapefiles/Centros Poblados Loreto.shp',
                      'shapefiles/Curvas de Nivel Loreto.shp',
                      'shapefiles/Dep Loreto.shp',
                      'shapefiles/Rios Loreto.shp',
                      'shapefiles/Trocha y Camino Loreto.shp'
                      ],

             "ICA":['shapefiles/11_ICA_SectoresEstadisticos.shp',
                        'shapefiles/11_ICA_SuperficieAgricola.shp',
                        'shapefiles/Centros Poblados Ica.shp',
                        'shapefiles/Curvas de Nivel Ica.shp',
                        'shapefiles/Dep Ica.shp',
                        'shapefiles/Rios Ica.shp',
                        'shapefiles/Trocha y Camino Ica.shp'
                        ],

             "CAJAMARCA":['shapefiles/06_CAJAMARCA_SectoresEstadisticos.shp',
                      'shapefiles/06_CAJAMARCA_SuperficieAgricola.shp',
                      'shapefiles/Centros Poblados Cajamarca.shp',
                      'shapefiles/Curvas de Nivel Cajamarca.shp',
                      'shapefiles/Dep Cajamarca.shp',
                      'shapefiles/Rios Cajamarca.shp',
                      'shapefiles/Trocha y Camino Cajamarca.shp'
                      ],

             "PASCO":['shapefiles/19_PASCO_SectoresEstadisticos.shp',
                      'shapefiles/19_PASCO_SuperficieAgricola.shp',
                      'shapefiles/Centros Poblados Pasco.shp',
                      'shapefiles/Curvas de Nivel Pasco.shp',
                      'shapefiles/Dep Pasco.shp',
                      'shapefiles/Rios Pasco.shp',
                      'shapefiles/Trocha y Camino Pasco.shp'
                      ]
                      
        }
    
    return dicdep[dep]

'''
# === Prueba local ===
if __name__ == "__main__":
    resultados = RutaShape(dep="APURIMAC", prov="CHINCHEROS", dist="URANMARCA")
    print(resultados)

