import osmnx as ox
import networkx as nx
import pandas as pd
import re
import os
import matplotlib.pyplot as plt
from typing import Tuple
from osmnx import convert
import callejero as c
from typing import List, Tuple, Dict, Callable, Union
from grafo_pesado import camino_minimo
import numpy as np


# Devuelve una tupla de str en caso de que sean vacios
def elegir_direcciones(df: pd.DataFrame, digrafo: nx.DiGraph) -> Union[Tuple[int, int], Tuple[str, str]]:
    """
    Solicita al usuario las direcciones de origen y destino

    Args:
        df (pd.DataFrame): DataFrame con los datos de las calles.
        digrafo (nx.DiGraph): Grafo que representa la red de calles.

    Returns:
        Union[Tuple[int, int], Tuple[str, str]]: Tupla con los nodos del grafo correspondientes al origen y destino, 
                                                 o ("", "") si el usuario decide salir
    """
    encontrado_origen = False
    encontrado_destino = False
    # Hasta que la dirección introducida no sea válida, seguimos pidiendo por que se introduzca un origen
    while not encontrado_origen:
        try:
            origen = input(
                "Introduce una direccion de origen: (Nombre Calle, numero) o (ENTER para salir del GPS): ")
            if origen != "":
                # Recurrimos a la función de buscar dirección de callejero.py para hacernos con la latitud y longitud del origen
                coords_origen = c.busca_direccion(origen, df)
            else:
                # si el origen es vacio no hace falta preguntar el destino
                encontrado_destino = True
            # Si no salta un error, el origen es válido y podemos abandonar el bucle
            encontrado_origen = True
        except:
            print("La direccion introducida no es válida, inténtalo otra vez")

    # Hacemos lo mismo con el destino
    while not encontrado_destino:
        try:
            destino = input(
                "Introduce una direccion de destino: (Nombre Calle, numero) o (ENTER para salir del GPS): ")
            if destino != "":
                coords_destino = c.busca_direccion(destino, df)
            encontrado_destino = True
        except:
            print("La direccion introducida no es válida, inténtalo otra vez")

    # Si alguno de los dos es vacío devolvemos una tupla con dos strings vacíos para que el main no se tenga que ejecutar todo
    if origen == "" or destino == "":
        return ("", "")
    # Si no, a través de la función de osmnx de nearest_nodes, encontramos el vértice del digrafo más cercano a nuestras coordenadas
    else:
        nodo_origen_id = ox.nearest_nodes(
            digrafo, X=coords_origen[1], Y=coords_origen[0])
        nodo_destino_id = ox.nearest_nodes(
            digrafo, X=coords_destino[1], Y=coords_destino[0])
        # Devolvemos una tupla con los identificadores de cada vertice dentro de digrafo.nodes
        return (nodo_origen_id, nodo_destino_id)

# Creamos aquí las distintas funciones de peso


def peso_ruta_mas_corta(digrafo: nx.DiGraph, origen=int, destino=int) -> float:
    """
    Calcula el peso de la ruta más corta, basado en la longitud de la arista

    Args:
        digrafo (nx.DiGraph): Grafo que contiene las aristas.
        origen (int): Nodo oriigen.
        destino (int): Nodo destino.

    Returns:
        float: longitud de la arista
    """
    # En este caso el peso será únicamente la longitud de la arista, que encontramos a partir de sus índices (origen y destino) en digrafo.edges
    longitud_arista = digrafo.edges[(origen, destino)]['length']
    return longitud_arista


def peso_ruta_mas_rapida(digrafo: nx.DiGraph, origen=object, destino=object) -> float:
    """
    Calcula el peso de la ruta más rápida, considerando la velocidad máxima de la arista.

    Args:
        digrafo (nx.DiGraph): grafo
        origen (object): Nodo origen.
        destino (object): Nodo destino.

    Returns:
        float: Tiempo que tarda en desplazarse desde origen a destion
    """
    MAX_SPEEDS = {'living_street': '20',
                  'residential': '30',
                  'primary_link': '40',
                  'unclassified': '40',
                  'secondary_link': '40',
                  'trunk_link': '40',
                  'secondary': '50',
                  'tertiary': '50',
                  'primary': '50',
                  'trunk': '50',
                  'tertiary_link': '50',
                  'busway': '50',
                  'motorway_link': '70',
                  'motorway': '100'}

    # Nos quedamos con el diccionario de datos asociado a la arista formada por los dos vértices dados
    dict_datos_arista = digrafo.edges[(origen, destino)]

    # Distinguimos tres casos, si la arista tiene su propia velocidad máxima, si solo conocemos el tipo de vía, o si no sabemos nada
    if 'maxspeed' in dict_datos_arista:
        # según hemos observado, existen tres formas en las que puede aparecer la velocidad, entonces las diferenciamos
        # Caso 1, que sea una lista, en este caso elegimos siempre la primera velocidad que aperece
        if type(dict_datos_arista['maxspeed']) == list:
            velocidad = float(dict_datos_arista['maxspeed'][0])
        # Caso 2, que aparezca como vmin|vmax, en este caso elegimos la vmax
        elif '|' in dict_datos_arista['maxspeed']:
            # Creamos una lista con ambas velocidades con el .split, y luego elegimos la maxima
            lista_velocidades = dict_datos_arista['maxspeed'].split('|')
            velocidad = float(lista_velocidades[1])
        # Caso 3, caso normal en el que solo aparece una velocidad
        else:
            velocidad = float(dict_datos_arista['maxspeed'])
    elif 'highway' in dict_datos_arista:
        # En este caso, tambien puede aparecer más de un tipo de vía, dentro de una lista
        if type(dict_datos_arista['highway']) == list:
            # En este caso nos quedamos con la primera
            tipo_via = dict_datos_arista['highway'][0]
        else:
            # si no nos quedamos con el único tipo de via que aparece
            tipo_via = dict_datos_arista['highway']
        # si el tipo de via esta en el diccionario, nos quedamos con esa velocidad, sino la establecemos por defecto
        if tipo_via in MAX_SPEEDS:
            velocidad = float(MAX_SPEEDS[tipo_via])
        else:
            velocidad = 50
    else:
        # Si no hay información establecemos l velocidad por defecto en 50
        velocidad = 50
    # Pasamos la velocidad a m/s
    velocidad_m_s = velocidad / 3.6
    # En este caso el peso de la arista vendrá dado por el tiempo que se tarda en recorrer
    # Como velocidad = distancia/tiempo -> tiempo = distancia/velocidad
    distancia = dict_datos_arista['length']
    tiempo = distancia / velocidad_m_s
    return tiempo


def peso_ruta_mas_rapida_semaforos(digrafo: nx.DiGraph, origen=object, destino=object) -> float:
    """
    Calcula el peso de la ruta más rápida considerando también la probabilidad de encontrar semáforos en el camino
    La probabilidad de encontrar semaforos depende de si hay un curce o no (hay un curce si un vertice tiene mas de dos aristas)

    Args:
        digrafo (nx.DiGraph): Grafo que contiene las aristas y los atributos de los nodos.
        origen (object): Nodo origen.
        destino (object): Nodo destino.

    Returns:
        float: Tiempo estimado
    """
    # En esta función el tiempor se calculará igual que en la anterior, pero añadiendo una función de probabilidad según los semáforos
    # Calculamos el tiempo si no hubiera semáforos con la función de peso anterior
    tiempo = peso_ruta_mas_rapida(digrafo, origen, destino)
    # Comprobamos si hay cruce con el street_count de el vértice de destino
    cruce = False
    if digrafo.nodes[destino]['street_count'] > 2:
        cruce = True
    # Si hay cruce añadimos al tiempo la función de probabilidad (sumando el tiempo de espera por su probabilidad)
    if cruce:
        tiempo += 0.8*30
    return tiempo


def elegir_modo_calculo_ruta() -> Callable[[nx.DiGraph, object, object], float]:
    """
    Presenta un menú al usuario para elegir el modo de cálculo de la ruta.

    Returns:
        Callable: Función correspondiente al cálculo seleccionado (ruta más corta, más rápida o con semáforos)
    """
    dic_funciones = {1: peso_ruta_mas_corta,
                     2: peso_ruta_mas_rapida, 3: peso_ruta_mas_rapida_semaforos}
    menu = """
    1. Ruta más corta entre esas dos direcciones
    2. Ruta más rápida entre esas dos direcciones
    3. Ruta más rápida, optimizando semáforos:
    """
    print(menu)
    opcion = ""
    # Desplegamos el menú de opciones, y mientras no se escoja una válida seguimos preguntando
    while opcion != 1 and opcion != 2 and opcion != 3:
        try:
            opcion = int(
                input("Elige el modo de cálculo de ruta que prefieras: "))
            if opcion != 1 and opcion != 2 and opcion != 3:
                # Si la opción no esta en el menú mostramos un mensaje de error
                print("Esa opción no está en el menú, inténatlo otra vez")
        except ValueError as error:
            # si el tipo de dato no es el adecuado (int), mostramo sotro error
            print("El dato introducido es incorrecto, inténtalo otra vez")
    funcion = dic_funciones[opcion]
    return funcion


def determinar_giro(digrafo: nx.DiGraph, inicio: int, intermedio: int, final: int) -> str:
    """
    Determina si se debe girar a la izquierda, derecha o seguir recto
    al pasar del nodo 'inicio' al 'final' a través del 'intermedio'.

    Args:
        digrafo (nx.DiGraph): grafo
        inicio (int): nodo de inicio.
        intermedio (int): nodo intermedio (donde se evalúa el giro)
        final (int): ndo final

    Returns:
        str: Instrucción de giro ("izquierda", "derecha" o "recto")
    """
    # Obtenemos la scoordenadas
    lat0, lon0 = digrafo.nodes[inicio]['y'], digrafo.nodes[inicio]['x']
    lat1, lon1 = digrafo.nodes[intermedio]['y'], digrafo.nodes[intermedio]['x']
    lat2, lon2 = digrafo.nodes[final]['y'], digrafo.nodes[final]['x']

    # conversion a radianes
    lat0_rad, lon0_rad = np.radians(lat0), np.radians(lon0)
    lat1_rad, lon1_rad = np.radians(lat1), np.radians(lon1)
    lat2_rad, lon2_rad = np.radians(lat2), np.radians(lon2)

    # Calcular coordenadas cartesianas de todos los nodos
    # Coordenadas del nodo de inicio
    x0 = np.cos(lat0_rad) * np.cos(lon0_rad)
    y0 = np.cos(lat0_rad) * np.sin(lon0_rad)
    z0 = np.sin(lat0_rad)
    coord0 = np.array([x0, y0, z0])

    # Coordenadas del nodo intermedio
    x1 = np.cos(lat1_rad) * np.cos(lon1_rad)
    y1 = np.cos(lat1_rad) * np.sin(lon1_rad)
    z1 = np.sin(lat1_rad)
    coord1 = np.array([x1, y1, z1])

    # Coordenadas del nodo final
    x2 = np.cos(lat2_rad) * np.cos(lon2_rad)
    y2 = np.cos(lat2_rad) * np.sin(lon2_rad)
    z2 = np.sin(lat2_rad)
    coord2 = np.array([x2, y2, z2])

    # Calcular los vectores entre los puntos
    v1 = coord1 - coord0
    v2 = coord2 - coord1

    v1_norm = v1 / np.linalg.norm(v1)
    v2_norm = v2 / np.linalg.norm(v2)

    angulo = np.arccos(np.dot(v1_norm, v2_norm))
    signo = np.sign(np.cross(v1_norm, v2_norm)[2])

    angle_degrees = np.degrees(angulo) * signo
    # Determinar la dirección del giro
    if angle_degrees > 5:
        return "izquierda"
    elif angle_degrees < -5:
        return "derecha"
    else:
        return "recto"


def instrucciones(digrafo: nx.DiGraph, camino: list):
    """
    Genera instrucciones paso a paso para recorrer un camino en el grafo

    Args:
        digrafo (nx.DiGraph): Grafo que contiene las aristas y nodos
        camino (list): Lista de nodos  del recorrido

    Returns:
        None
    """
    nombre_anterior = ""
    distancia_anterior = 0
    for j in range(len(camino)-1):
        # Obtenemos los vértices de cada arista a partir de nuestro camino
        inicio_paso = camino[j]
        fin_paso = camino[j+1]
        # Accedemos al diccionario asociado a cada arista
        dic_arista = digrafo.edges[(inicio_paso, fin_paso)]
        # Aquí también distinguimos entre tres casos, cuando la arista en vez de un nombre es una lista de nombres, cuando aperece normal o cuando no tiene
        if 'name' in dic_arista:
            nombre = dic_arista['name']
        # Caso en el que no aparece nombre en la arista, en este caso definimos el nombre igual que el nombre anterior
        else:
            nombre = nombre_anterior
        # Obtenemos la longitud de la arista del diccionario y la sumamos a la distncia anterior que es 0 si se ha cambiado de calle y se acumula si no
        distancia = dic_arista['length']
        distancia_anterior += distancia
        # Tenemos en cuenta la primera iteración del bucle
        if nombre_anterior == "":
            nombre_anterior = nombre
        # Si hemos cambiado
        elif nombre_anterior != nombre:
            print(
                f"Continúa recto por {nombre_anterior} durante {distancia_anterior} metros")
            nombre_anterior = nombre
            distancia_anterior = 0
            # Determinamos el giro con la función que hemos creado antes
            # Para ello no tenemos en cuenta la última arista, ya que no habrá que girar
            if j + 2 < len(camino):
                direccion_giro = determinar_giro(
                    digrafo, camino[j-1], camino[j], camino[j+1])
                if direccion_giro != 'recto':
                    print(f"Gira a la {direccion_giro} en direccion {nombre}")
                else:
                    print(f"Continúa recto hacia {nombre}")
    print(f"Continúa recto por {nombre} durante {distancia} metros")
    print("Ha llegado a su destino")


def dibujar(digrafo: nx.DiGraph, camino: List[int]) -> None:
    """
    Dibuja el grafo resaltando el camino proporcionado.

    Args:
        digrafo (nx.DiGraph): El grafo a dibujar.
        camino (List[int]): Lista de nodos que representan el camino a resaltar.

    Returns:
        None
    """

    pos = {node: (data['x'], data['y'])
           for node, data in digrafo.nodes(data=True)}

    plt.figure(figsize=(8, 8))

    # dibujamos las aristas generales
    nx.draw_networkx_edges(
        digrafo,
        pos=pos,
        edge_color='lightgray',
        width=0.5,
        alpha=0.7,
        arrows=False
    )

    # dibujamos las aristas del camino
    path_edges = list(zip(camino[:-1], camino[1:]))
    nx.draw_networkx_edges(
        digrafo,
        pos=pos,
        edgelist=path_edges,
        edge_color='black',
        width=2.5,
        arrows=False
    )

    # dibjamos el nodo de incio y final
    nx.draw_networkx_nodes(
        digrafo,
        pos=pos,
        nodelist=[camino[0], camino[-1]],
        node_color='darkblue',
        node_size=40,
        label='Origen y Destino'
    )

    plt.legend()

    plt.axis('off')
    plt.show()


if __name__ == "__main__":
    # 1
    df = c.carga_callejero()
    multidigrafo = c.carga_grafo()
    digrafo = c.procesa_grafo(multidigrafo)

    # 7
    origen_o_destino_vacios = False
    while not origen_o_destino_vacios:
        # 2
        tupla_direcciones = elegir_direcciones(df, digrafo)
        origen = tupla_direcciones[0]
        destino = tupla_direcciones[1]

        if origen == "" or destino == "":
            origen_o_destino_vacios = True
        else:
            # 3
            funcion_peso = elegir_modo_calculo_ruta()

            # 4
            print("Calculando la ruta...")
            lista_camino = camino_minimo(
                digrafo, funcion_peso, origen, destino)

            # 5
            instrucciones(digrafo, lista_camino)

            # 6
            print("Dibujando la gráfica...")
            dibujar(digrafo, lista_camino)

    print("Gracias por usar el GPS y ¡¡¡buen viaje!!!")
