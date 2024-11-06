#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import os


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
                      ]
                      
        }
    
    return dicdep[dep]


