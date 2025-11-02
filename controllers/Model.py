
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
    dep = dep.upper()
    BASE_DIR = Path(__file__).resolve().parent

    # ✅ Ruta base configurable por variable de entorno
    ruta_base_env = os.getenv("RUTA_BASE", str(BASE_DIR.parent / "shapefiles"))
    ruta_base = Path(ruta_base_env) / dep

    print(f"📁 Buscando shapefiles en: {ruta_base}")

    if not ruta_base.exists():
        raise ValueError(f"No existe la carpeta de shapefiles: {ruta_base}")

    lista_encontrados = []

    # --- Helper: búsqueda insensible a mayúsculas ---
    def buscar_archivo(patron):
        for root, _, files in os.walk(ruta_base):
            for file in files:
                if patron.lower() in file.lower() and file.lower().endswith(".shp"):
                    full_path = os.path.join(root, file)
                    print(f"✅ Encontrado: {full_path}")
                    return full_path
        print(f"⚠️ No se encontró ningún archivo para patrón: {patron}")
        return ""

    # --- Helper: ruta relativa limpia ---
    def rel(path):
        if not path:
            return ""
        try:
            return str(Path(path).relative_to(BASE_DIR.parent)).replace("\\", "/")
        except ValueError:
            return str(path).replace("\\", "/")

    # --- 1. SECTORES ESTADÍSTICOS ---
    archivo_estadistico = buscar_archivo(f"{dep}_SectoresEstadisticos")
    lista_encontrados.append(rel(archivo_estadistico))

    # --- 2. SUPERFICIE AGRÍCOLA ---
    path_agricola = ""
    for root, _, files in os.walk(ruta_base):
        for file in files:
            if "SuperficieAgricola".lower() in file.lower() and file.lower().endswith(".shp"):
                full_path = os.path.join(root, file)
                try:
                    gdf = gpd.read_file(full_path)
                    if {"NOMBDEP", "NOMBPROV", "NOMBDIST"}.issubset(gdf.columns):
                        filtro = gdf[
                            (gdf["NOMBDEP"].str.upper() == dep.upper()) &
                            (gdf["NOMBPROV"].str.upper() == prov.upper()) &
                            (gdf["NOMBDIST"].str.upper() == dist.upper())
                        ]
                        if not filtro.empty:
                            path_agricola = full_path
                            print(f"✅ Archivo agrícola filtrado: {path_agricola}")
                            break
                except Exception as e:
                    print(f"⚠️ Error leyendo {file}: {e}")
        if path_agricola:
            break
    lista_encontrados.append(rel(path_agricola))

    # --- 3. CENTROS POBLADOS ---
    archivo_centros = buscar_archivo("Centros Poblados")
    lista_encontrados.append(rel(archivo_centros))

    # --- 4. CURVAS DE NIVEL ---
    archivo_curvas = buscar_archivo("Curvas de Nivel")
    lista_encontrados.append(rel(archivo_curvas))

    # --- 5. DEPARTAMENTO ---
    archivo_departamento = buscar_archivo("Dep")
    lista_encontrados.append(rel(archivo_departamento))

    # --- 6. RÍOS ---
    archivo_rios = buscar_archivo("Rios")
    lista_encontrados.append(rel(archivo_rios))

    # --- 7. TROCHAS Y CAMINOS ---
    archivo_trochascamino = buscar_archivo("Trocha y Camino")
    lista_encontrados.append(rel(archivo_trochascamino))

    print("📦 Archivos encontrados:", lista_encontrados)
    return lista_encontrados



# === Prueba local ===
if __name__ == "__main__":
    resultados = RutaShape(dep="APURIMAC", prov="CHINCHEROS", dist="URANMARCA")
    print(resultados)