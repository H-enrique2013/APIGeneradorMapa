
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
    dep = dep.upper()

    # ✅ Ruta base configurable por variable de entorno
    ruta_base_env = os.getenv("RUTA_BASE", str(BASE_DIR.parent / "shapefiles"))
    ruta_base = Path(ruta_base_env) / dep

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



# === Prueba local ===
if __name__ == "__main__":
    resultados = RutaShape(dep="APURIMAC", prov="CHINCHEROS", dist="URANMARCA")
    print(resultados)

