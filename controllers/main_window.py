from PySide2.QtWidgets import QWidget, QTableWidgetItem,QMessageBox
from controllers.View_Model import ViewModel
from views.main_windows import *
from controllers.AlignDelegate import *
from PySide2 import QtCore
from controllers.Model import RutaShape
import geopandas as gpd
import os

class ListBookWindow(QWidget,ListBookForm):
    def __init__(self,parent=None):
        super().__init__()
        self.setupUi(self)
        self.parent = parent
        ListaDepa=["---","PUNO","MADRE DE DIOS","APURIMAC","AYACUCHO","HUANCAVELICA","MOQUEGUA",
                   "TACNA","TUMBES"]
        self.depacomboBox.addItems(ListaDepa)
        aleatorio=[" "]
        for i in range(1,32):
            aleatorio.append(str(i))
        self.aleatoriocombobox.addItems(aleatorio)
        ######################## TOTALES ##################################################
        
        self.searchButton.clicked.connect(self.searchAll)#PROCESAR BOTON
        self.clearButton.clicked.connect(self.limpiarCamposRefresh)#PROCESAR BOTON
       
        self.depacomboBox.currentTextChanged.connect(lambda:(self.populate_comboboxProvincia(self.depacomboBox.currentText())))
        self.provinciacombobox.currentTextChanged.connect(lambda:(self.populate_comboboxDistrito(self.depacomboBox.currentText(),self.provinciacombobox.currentText())))
        self.distritocombobox.currentTextChanged.connect(lambda:(self.populate_comboboxSector(self.depacomboBox.currentText(),self.provinciacombobox.currentText(),self.distritocombobox.currentText())))

    #################################FUNCIONES TOTALES#######################################


    def searchAll(self):
        TextoDepa = self.depacomboBox.currentText()
        TextoProv = self.provinciacombobox.currentText()
        TextoDist = self.distritocombobox.currentText()
        TextoSect = self.sectorcombobox.currentText()
        TextoAlea = self.aleatoriocombobox.currentText()
        NumAleatorio = int(TextoAlea)
        lista_shape=RutaShape(TextoDepa)
        shape_sector=gpd.read_file(lista_shape[0])
        shape_sector=shape_sector[(shape_sector['NOMBPROV']==TextoProv)&(shape_sector['NOMBDEP']==TextoDepa)&(shape_sector['NOMBDIST']==TextoDist)]
        lista_sector=shape_sector["NOM_SE"].to_numpy().tolist()
        
        if str(lista_sector[-1])=="nan":
            ViewModel.ProcesarModel(TextoDepa,TextoProv,TextoDist,TextoSect,NumAleatorio,"NULL")
        else:
            ViewModel.ProcesarModel(TextoDepa,TextoProv,TextoDist,TextoSect,NumAleatorio,"NO NULL")

        
    def limpiarCamposRefresh(self):
        self.depacomboBox.setCurrentIndex(0)
        self.provinciacombobox.clear()
        self.distritocombobox.clear()
        self.sectorcombobox.clear()
        self.aleatoriocombobox.setCurrentIndex(0)

        
    def to_upperAgencia(self, txt):
        self.nombreAgenciaLineEdit.setText(txt.upper())
    
  
    def populate_comboboxProvincia(self,txt):
        self.provinciacombobox.clear()
        self.provinciacombobox.addItems(" ")
        lista_shape=RutaShape(txt)
        shape_sector=gpd.read_file(lista_shape[0])
        lista_provincia=shape_sector['NOMBPROV'].to_numpy().tolist()
        lista_provincia=list(set(lista_provincia))
        self.provinciacombobox.addItems(lista_provincia)

    def populate_comboboxDistrito(self,depa,provincia):
        self.distritocombobox.clear()
        self.distritocombobox.addItems(" ")
        lista_shape=RutaShape(depa)
        shape_sector=gpd.read_file(lista_shape[0])
        shape_dist=shape_sector[(shape_sector['NOMBPROV']==provincia) &(shape_sector['NOMBDEP']==depa) ]
        lista_distrito=shape_dist["NOMBDIST"].to_numpy().tolist()
        lista_distrito=list(set(lista_distrito))
        self.distritocombobox.addItems(lista_distrito)

    def populate_comboboxSector(self,depa,provincia,distrito):
        self.sectorcombobox.clear()
        self.sectorcombobox.addItems(" ")
        lista_shape=RutaShape(depa)
        shape_sector=gpd.read_file(lista_shape[0])
        #shape_agricola=gpd.read_file(lista_shape[1])
        shape_sector_est=shape_sector[(shape_sector['NOMBPROV']==provincia)&(shape_sector['NOMBDEP']==depa)&(shape_sector['NOMBDIST']==distrito)]
        lista_sector=shape_sector_est["NOM_SE"].to_numpy().tolist()
        lista_sector=list(set(lista_sector))
        self.sectorcombobox.addItems(lista_sector)
            
            
    
