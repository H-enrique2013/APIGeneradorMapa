from controllers.View_Model import ViewModel
from flask import Flask, request, jsonify, send_from_directory, render_template
import os
import time
import threading
import logging
from controllers.script_mapa import GeneradorHmtl_mapa
from controllers.Model import RutaShape
import geopandas as gpd

app = Flask(__name__, template_folder='templates')

def delete_file(filepath):
    time.sleep(60)
    if os.path.exists(filepath):
        try:
            os.remove(filepath)
        except Exception as e:
            print(f"Error al eliminar el archivo: {str(e)}")

@app.route('/')
def index():
    return render_template('index.html')
#Método POST
@app.route('/generateoncepuntosmap-html', methods=['POST'])
def generateoncepuntosmap_html():
    data = request.get_json()
    dep = data.get('Departamento')
    prov = data.get('Provincia')
    distr = data.get('Distrito')
    sect = data.get('Sector')
    N_aleatorio = int(data.get('N_aleatorio'))
    #Comprobando si el shape de Sector estadistico tiene geometry
    file_shape=RutaShape(dep)
    shape_sector=gpd.read_file(file_shape[0])
    shape_sector=shape_sector[(shape_sector['NOMBDEP']==dep)&(shape_sector['NOMBPROV']==prov)&(shape_sector['NOMBDIST']==distr)]
    lista_sector=shape_sector["NOM_SE"].to_numpy().tolist()

    logging.info(f"Datos recibidos: dep={dep}, prov={prov}, distr={distr}, sect={sect}, N_aleatorio={N_aleatorio}")
    
    try:
        if str(lista_sector[-1]) == 'nan':
            html_filepath = ViewModel.ProcesarModel(dep, prov, distr, sect, N_aleatorio,"NULL")
        else:
            html_filepath = ViewModel.ProcesarModel(dep, prov, distr, sect, N_aleatorio,"NO NULL")

        logging.info(f"html_filepath generado: {html_filepath}")

        if html_filepath is None:
            raise ValueError("El procesamiento del modelo devolvió None")

        filename = os.path.basename(html_filepath)
        directory = os.path.dirname(html_filepath)
        response = send_from_directory(directory=directory, path=filename)
        threading.Thread(target=delete_file, args=(html_filepath,)).start()
        return response, 200
    except Exception as e:
        logging.error(f"Tipo de error: {type(e).__name__}")
        logging.error(f"Mensaje de error: {str(e)}")
        return jsonify({"error": f"Error al generar el mapa: {str(e)}"}), 500
    
#Método POST
@app.route('/generatemap-html', methods=['POST'])
def generatemap_html():
    data = request.get_json()
    dep = data.get('Departamento')
    prov = data.get('Provincia')
    distr = data.get('Distrito')
    sect = data.get('Sector')
    dicPuntos = data.get('DiccionarioPuntos')

    html_filepath = None
    #kml_filepath=None
    try:
        (html_filepath,kml_filepath)=GeneradorHmtl_mapa(dep, prov, distr,sect, dicPuntos)
        filename = os.path.basename(html_filepath)
        directory = os.path.dirname(html_filepath)
        response = send_from_directory(directory=directory, path=filename)
        threading.Thread(target=delete_file, args=(html_filepath,)).start()
        threading.Thread(target=delete_file, args=(kml_filepath,)).start()
        return response, 200
    except Exception as e:
        # Imprimir el tipo de excepción y el mensaje para depuración
        print(f"Tipo de error: {type(e).__name__}")
        print(f"Mensaje de error: {str(e)}")
        # Convertir la excepción en una cadena para asegurar que sea serializable a JSON
        return jsonify({"error": f"Error al generar el mapa: {str(e)}"}), 500
    

#Método POST
@app.route('/generatemap-kml', methods=['POST'])
def generatemap_kml():
    
    data = request.get_json()
    dep = data.get('Departamento')
    prov = data.get('Provincia')
    distr = data.get('Distrito')
    sect = data.get('Sector')
    dicPuntos = data.get('DiccionarioPuntos')

    kml_filepath=None
    try:
        (html_filepath,kml_filepath) =GeneradorHmtl_mapa(dep, prov, distr,sect, dicPuntos)
        filename = os.path.basename(kml_filepath)
        directory = os.path.dirname(kml_filepath)
        response = send_from_directory(directory=directory, path=filename)
        threading.Thread(target=delete_file, args=(kml_filepath,)).start()
        threading.Thread(target=delete_file, args=(html_filepath,)).start()
        return response, 200
    except Exception as e:
        # Imprimir el tipo de excepción y el mensaje para depuración
        print(f"Tipo de error: {type(e).__name__}")
        print(f"Mensaje de error: {str(e)}")
        # Convertir la excepción en una cadena para asegurar que sea serializable a JSON
        return jsonify({"error": f"Error al generar el mapa: {str(e)}"}), 500
    
@app.route('/geopandasIcon.ico')
def favicon():
    return send_from_directory('static', 'geopandasIcon.ico')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

