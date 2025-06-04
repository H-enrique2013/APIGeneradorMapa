from controllers.View_Model import ViewModel
from flask import Flask, request, jsonify, send_from_directory, render_template
import os
import time
import threading
import logging
from controllers.script_mapa import generar_errorespuntos
from controllers.Model import RutaShape
import geopandas as gpd

app = Flask(__name__, template_folder='templates')

def delete_file(filepath):
    time.sleep(5)
    if os.path.exists(filepath):
        try:
            os.remove(filepath)
        except Exception as e:
            print(f"Error al eliminar el archivo: {str(e)}")

def delete_file_temporales(filepath):
    time.sleep(300)
    if os.path.exists(filepath):
        try:
            os.remove(filepath)
        except Exception as e:
            print(f"Error al eliminar el archivo: {str(e)}")

@app.route('/')
def index():
    return render_template('index.html')
#Método POST
@app.route('/generateoncepuntosmap', methods=['POST'])
def generateoncepuntosmap_html():
    data = request.get_json()
    dep = data.get('Departamento')
    prov = data.get('Provincia')
    distr = data.get('Distrito')
    sect = data.get('Sector')
    N_aleatorio = int(data.get('N_aleatorio'))
    tipo_archivo = data.get('Tipo_Archivo')
    #Comprobando si el shape de Sector estadistico tiene geometry
    file_shape=RutaShape(dep)
    shape_sector=gpd.read_file(file_shape[0])
    shape_sector=shape_sector[(shape_sector['NOMBDEP']==dep)&(shape_sector['NOMBPROV']==prov)&(shape_sector['NOMBDIST']==distr)]
    lista_sector=shape_sector["NOM_SE"].to_numpy().tolist()

    logging.info(f"Datos recibidos: dep={dep}, prov={prov}, distr={distr}, sect={sect}, N_aleatorio={N_aleatorio},tipo_archivo={tipo_archivo}")
    
    try:
        if str(lista_sector[-1]) == 'nan':
            url_filepath = ViewModel.ProcesarModel(dep, prov, distr, sect, N_aleatorio,"NULL",tipo_archivo)
        else:
            url_filepath = ViewModel.ProcesarModel(dep, prov, distr, sect, N_aleatorio,"NO NULL",tipo_archivo)

        logging.info(f"html_filepath generado: {url_filepath}")

        if url_filepath is None:
            raise ValueError("El procesamiento del modelo devolvió None")

        filename = os.path.basename(url_filepath)
        directory = os.path.dirname(url_filepath)
        response = send_from_directory(directory=directory, path=filename)
        threading.Thread(target=delete_file, args=(url_filepath,)).start()
        return response, 200
    except Exception as e:
        logging.error(f"Tipo de error: {type(e).__name__}")
        logging.error(f"Mensaje de error: {str(e)}")
        return jsonify({"error": f"Error al generar el mapa: {str(e)}"}), 500
    
#Método POST
@app.route('/generatemap', methods=['POST'])
def generatemap_html():
    data = request.get_json()
    dep = data.get('Departamento')
    prov = data.get('Provincia')
    distr = data.get('Distrito')
    sect = data.get('Sector')
    dicPuntos = data.get('DiccionarioPuntos')
    
    #kml_filepath=None
    
    
    try:
        VerificarPuntosFuera=generar_errorespuntos(dep,prov,distr,sect,dicPuntos)
        # Obtener el nombre del archivo
        url_filepath=VerificarPuntosFuera["file_mapa_path"]
        filename = os.path.basename(url_filepath)

        # Construir la URL pública
        url_mapa = f"{request.host_url}mapas_temporales/{filename}"

        # Agregar la URL al JSON de respuesta
        VerificarPuntosFuera["url_mapa"] = url_mapa
        threading.Thread(target=delete_file_temporales, args=(url_filepath,)).start()
        return jsonify(VerificarPuntosFuera),200

    except Exception as e:
        # Imprimir el tipo de excepción y el mensaje para depuración
        print(f"Tipo de error: {type(e).__name__}")
        print(f"Mensaje de error: {str(e)}")
        # Convertir la excepción en una cadena para asegurar que sea serializable a JSON
        return jsonify({"error": f"Error al generar el mapa: {str(e)}"}), 500
    
@app.route("/mapas_temporales/<filename>")
def servir_mapa(filename):
    """Sirve el archivo HTML generado desde mapas_temporales"""
    return send_from_directory("mapas_temporales", filename)

    
@app.route('/geopandasIcon.ico')
def favicon():
    return send_from_directory('static', 'geopandasIcon.ico')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

