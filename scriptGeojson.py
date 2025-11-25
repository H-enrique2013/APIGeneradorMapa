import geopandas as gpd
from pathlib import Path

# === Configuración ===
BASE_DIR = Path(__file__).resolve().parent
SHAPE_DIR = BASE_DIR / "shapefiles"        # carpeta que contiene las subcarpetas (APURIMAC, CUSCO, etc.)
OUTPUT_DIR = BASE_DIR                      # raíz del proyecto donde se guardarán los .geojson

print(f"📂 Buscando shapefiles dentro de: {SHAPE_DIR}")

# Verificar existencia
if not SHAPE_DIR.exists():
    raise FileNotFoundError(f"❌ No se encontró la carpeta shapefiles: {SHAPE_DIR}")

# === Conversión masiva ===
for shp_file in SHAPE_DIR.rglob("*.shp"):
    try:
        print(f"🧩 Leyendo: {shp_file.name}")
        gdf = gpd.read_file(shp_file)

        # Crear nombre de salida (ej: 03_APURIMAC1_SuperficieAgricola.geojson)
        output_name = shp_file.stem + ".geojson"
        output_path = OUTPUT_DIR / output_name

        # Guardar GeoJSON en la raíz
        gdf.to_file(output_path, driver="GeoJSON")

        print(f"✅ Convertido: {output_path}")
    except Exception as e:
        print(f"⚠️ Error al procesar {shp_file.name}: {e}")

print("🎯 Conversión completada.")
