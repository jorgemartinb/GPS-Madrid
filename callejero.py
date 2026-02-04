"""
callejero.py

Matemática Discreta - IMAT
ICAI, Universidad Pontificia Comillas

Grupo: GPxxx
Integrantes:
    - XX
    - XX

Descripción:
Librería con herramientas y clases auxiliares necesarias para la representación de un callejero en un grafo.

Complétese esta descripción según las funcionalidades agregadas por el grupo.
"""

import osmnx as ox
import networkx as nx
import pandas as pd
import re
import os
from typing import Tuple
from osmnx import convert

STREET_FILE_NAME="direcciones.csv"

PLACE_NAME = "Madrid, Spain"
MAP_FILE_NAME="madrid.graphml"

MAX_SPEEDS={'living_street': '20',
 'residential': '30',
 'primary_link': '40',
 'unclassified': '40',
 'secondary_link': '40',
 'trunk_link': '40',
 'secondary': '50',
 'tertiary': '50',
 'primary': '50',
 'trunk': '50',
 'tertiary_link':'50',
 'busway': '50',
 'motorway_link': '70',
 'motorway': '100'}


class ServiceNotAvailableError(Exception):
    "Excepción que indica que la navegación no está disponible en este momento"
    pass


class AdressNotFoundError(Exception):
    "Excepción que indica que una dirección buscada no existe en la base de datos"
    pass


############## Parte 2 ##############


def carga_callejero() -> pd.DataFrame:
    """ Función que carga el callejero de Madrid, lo procesa y devuelve
    un DataFrame con los datos procesados
    
    Args: None
    Returns:
        Dict[object,object]: Devuelve un diccionario que indica, para cada vértice del
            grafo, qué vértice es su padre en el árbol abarcador mínimo.
    Raises:
        FileNotFoundError si el fichero csv con las direcciones no existe
    """
    columnas_cargar =  ['VIA_CLASE', 'VIA_PAR', 'VIA_NOMBRE', 'NUMERO', 'LATITUD','LONGITUD']
    # Cargamos el df teniendo en cuenta solo las columnas que buscamos y empleando encoding = 'latin1' para que recoja bien los datos
    try:
        direcciones = pd.read_csv(STREET_FILE_NAME,usecols=columnas_cargar,encoding='latin-1',sep = ';')
    except FileNotFoundError as error:
        raise error
    # Creamos una función que empleando regex cambie las coordenadas y las transforme a formato float
    def transformacion(valor):
        patron = re.compile(r"(\d+)°(\d+)'([\d.]+)''\s*([NSEW])")
        matches = re.match(patron,valor)
        grados = int(matches.group(1))
        minutos = int(matches.group(2))
        segundos = float(matches.group(3))
        orientacion = matches.group(4)

        grado_corregido = grados + minutos/60+ segundos/3600
        if orientacion == 'W' or orientacion == 'S':
            grado_corregido = grado_corregido * -1
        return grado_corregido
    # Cambiamos las columnas del DataFrame
    direcciones['LONGITUD'] = direcciones['LONGITUD'].apply(transformacion)
    direcciones['LATITUD'] = direcciones['LATITUD'].apply(transformacion)
    
    # Para la función busca dirección los nan del VIA_PAR dan problema, asi que los hemos cambiado por "" en este apartado
    direcciones['VIA_PAR'] = direcciones['VIA_PAR'].fillna("")
    return direcciones




def busca_direccion(direccion:str, callejero:pd.DataFrame) -> Tuple[float,float]:
    """ Función que busca una dirección, dada en el formato
        calle, numero
    en el DataFrame callejero de Madrid y devuelve el par (latitud, longitud) en grados de la
    hubicación geográfica de dicha dirección
    
    Args:
        direccion (str): Nombre completo de la calle con número, en formato "Calle, num"
        callejero (DataFrame): DataFrame con la información de las calles
    Returns:
        Tuple[float,float]: Par de float (latitud,longitud) de la dirección buscada, expresados en grados
    Raises:
        AdressNotFoundError: Si la dirección no existe en la base de datos
    Example:
        busca_direccion("Calle de Alberto Aguilera, 23", data)=(40.42998055555555,3.7112583333333333)
        busca_direccion("Calle de Alberto Aguilera, 25", data)=(40.43013055555555,3.7126916666666667)
    """
    # Mediante un regex distingo entre los diferentes elemntos de la direccion
    patron = r"([a-zA-ZáéíóúÁÉÍÓÚñÑ]+)\s+((?:de\s+(?:la|las|el|los)|del|de)?)?\s*([a-zA-ZáéíóúÁÉÍÓÚñÑ\s\-[0-9]+?)\s*,+\s*(\d+)"
    matches = re.search(patron, direccion)
    # El primer grupo es un str de cualquier duración hasta llegar al primer espacio, por lo que la clase es el grupo en mayúscula
    via_clase = matches.group(1).upper()
    # El segundo grupo son las preposiciones de las calles y sus posibles combinaciones, quedando vacio si no hay
    if matches.group(2):
        via_par = matches.group(2).upper()
    else:
        via_par = ""
    # El tercer grupo es un str de cualquier duracion espacios incluídos hasta llegar a la coma
    via_nombre = matches.group(3).upper()
    # El cuarto grupo es el numero
    numero = int(matches.group(4))
    print(via_clase,via_par,via_nombre,numero)
    lista_df = callejero[(callejero['VIA_CLASE']== via_clase) & (callejero['VIA_PAR']== via_par) & \
                            (callejero['VIA_NOMBRE']== via_nombre) & (callejero['NUMERO']== numero)  
                            ]
    if not lista_df.empty:
        return (lista_df.iloc[0]['LATITUD'],lista_df.iloc[0]['LONGITUD'])
    else:
        raise AdressNotFoundError
    



############## Parte 4 ##############


def carga_grafo() -> nx.MultiDiGraph:
    """ Función que recupera el quiver de calles de Madrid de OpenStreetMap.
    Args: None
    Returns:
        nx.MultiDiGraph: Quiver de las calles de Madrid.
    Raises:
        ServiceNotAvailableError: Si no es posible recuperar el grafo de OpenStreetMap.
    """
    fichero = 'madrid_graphml'
    # Si el fichero existe cargamos el grafo desde el fichero
    if os.path.exists(fichero):
        grafo = ox.load_graphml(fichero)
    else:
        try:
            grafo = ox.graph_from_place("Madrid, Spain", network_type="drive")
            ox.save_graphml(grafo, fichero)
        except:
            raise ServiceNotAvailableError
            
    return grafo 

def procesa_grafo(multidigrafo:nx.MultiDiGraph) -> nx.DiGraph:
    """ Función que recupera el quiver de calles de Madrid de OpenStreetMap.
    Args:
        multidigrafo: multidigrafo de las calles de Madrid obtenido de OpenStreetMap.
    Returns:
        nx.DiGraph: Grafo dirigido y sin bucles asociado al multidigrafo dado.
    Raises: None
    """
    grafo_dirigido = convert.to_digraph(multidigrafo)
    bucles = list(nx.selfloop_edges(grafo_dirigido))
    grafo_dirigido.remove_edges_from(bucles) 
    return grafo_dirigido