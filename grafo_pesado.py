"""
grafo.py

Matemática Discreta - IMAT
ICAI, Universidad Pontificia Comillas

Grupo: GPxxx
Integrantes:
    - XX
    - XX

Descripción:
Librería para el análisis de grafos pesados.
"""

from typing import List, Tuple, Dict, Callable, Union
import networkx as nx
import sys

import heapq  # Librería para la creación de colas de prioridad

INFTY = sys.float_info.max  # Distincia "infinita" entre nodos de un grafo

"""
En las siguientes funciones, las funciones de peso son funciones que reciben un grafo o digrafo y dos vértices y devuelven un real (su peso)
Por ejemplo, si las aristas del grafo contienen en sus datos un campo llamado 'valor', una posible función de peso sería:

def mi_peso(G:nx.Graph,u:object, v:object):
    return G[u][v]['valor']

y, en tal caso, para calcular Dijkstra con dicho parámetro haríamos

camino=dijkstra(G,mi_peso,origen, destino)


"""


def dijkstra(G: Union[nx.Graph, nx.DiGraph], peso: Union[Callable[[nx.Graph, object, object], float], Callable[[nx.DiGraph, object, object], float]], origen: object) -> Dict[object, object]:
    """ Calcula un Árbol de Caminos Mínimos para el grafo pesado partiendo
    del vértice "origen" usando el algoritmo de Dijkstra. Calcula únicamente
    el árbol de la componente conexa que contiene a "origen".

    Args:
        origen (object): vértice del grafo de origen
    Returns:
        Dict[object,object]: Devuelve un diccionario que indica, para cada vértice alcanzable
            desde "origen", qué vértice es su padre en el árbol de caminos mínimos.
    Raises:
        TypeError: Si origen no es "hashable".
    Example:
        Si G.dijksra(1)={2:1, 3:2, 4:1} entonces 1 es padre de 2 y de 4 y 2 es padre de 3.
        En particular, un camino mínimo desde 1 hasta 3 sería 1->2->3.
    """
    try:
        hash(origen)
    except TypeError:
        raise TypeError("el origen debe ser hashable.")
    padre = {}
    d = {}
    visitado = {}
    for v in G.nodes():
        padre[v] = None
        visitado[v] = False
        d[v] = INFTY
    d[origen] = 0

    contador = 0  # añadimos un parametro distinto en el heap entre el peso y el nombre para que nunca nos compare el nombre
    # es decir, si el peso es el mismo nos comparar el contador en lugar de comparar el nombre eligiendo entonces el primero a la hora de hacer el heappop
    # creamos una cola de prioridad con la librria heapq
    Q = []
    heapq.heappush(Q, (d[origen], contador, origen))

    while Q:
        contador += 1
        # extraer el nodo con menor distancia al origen
        dist_v, _, v = heapq.heappop(Q)
        if not visitado[v]:
            visitado[v] = True
            for x in G.neighbors(v):
                contador += 1
                peso_arista_v_x = peso(G, v, x)
                if d[x] > d[v] + peso_arista_v_x:
                    d[x] = d[v] + peso_arista_v_x
                    padre[x] = v
                    # añadimos x a la cola de prioridad
                    heapq.heappush(Q, (d[x], contador, x))
    return padre


def camino_minimo(G: Union[nx.Graph, nx.DiGraph], peso: Union[Callable[[nx.Graph, object, object], float], Callable[[nx.DiGraph, object, object], float]], origen: object, destino: object) -> List[object]:
    """ Calcula el camino mínimo desde el vértice origen hasta el vértice
    destino utilizando el algoritmo de Dijkstra.

    Args:
        G (nx.Graph o nx.Digraph): grafo a grado dirigido
        peso (función): función que recibe un grafo o grafo dirigido y dos vértices del mismo y devuelve el peso de la arista que los conecta
        origen (object): vértice del grafo de origen
        destino (object): vértice del grafo de destino
    Returns:
        List[object]: Devuelve una lista con los vértices del grafo por los que pasa
            el camino más corto entre el origen y el destino. El primer elemento de
            la lista es origen y el último destino.
    Example:
        Si dijksra(G,peso,1,4)=[1,5,2,4] entonces el camino más corto en G entre 1 y 4 es 1->5->2->4.
    Raises:
        TypeError: Si origen o destino no son "hashable".
        ValueError: Si no se puede llegar desde el origen hasta el destino
    """
    try:
        hash(origen)
        hash(destino)
    except TypeError:
        raise TypeError("el origen y el destino deben ser hashables.")
    if origen not in G or destino not in G:
        raise ValueError(
            f"No hay camino posible que vaya de {origen} hasta {destino}.")
    padres = dijkstra(G, peso, origen)
    nodo = destino
    camino = [destino]
    while nodo != origen:
        if nodo not in padres:
            raise ValueError(
                f"No hay camino posible que vaya de {origen} hasta {destino}.")
        nodo = padres[nodo]
        camino = [nodo]+camino
    return camino


def prim(G: nx.Graph, peso: Callable[[nx.Graph, object, object], float]) -> Dict[object, object]:
    """ Calcula un Árbol Abarcador Mínimo para el grafo pesado
    usando el algoritmo de Prim.

    Args:
        G (nx.Graph): grafo
        peso (función): función que recibe un grafo y dos vértices del grafo y devuelve el peso de la arista que los conecta
    Returns:
        Dict[object,object]: Devuelve un diccionario que indica, para cada vértice del
            grafo, qué vértice es su padre en el árbol abarcador mínimo.
    Raises: None
    Example:
        Si prim(G,peso)={1: None, 2:1, 3:2, 4:1} entonces en un árbol abarcador mínimo tenemos que:
            1 es una raíz (no tiene padre)
            1 es padre de 2 y de 4
            2 es padre de 3
    """
    padre = {}
    coste_minimo = {}
    Q = []
    nodos_sin_visitar = set(G.nodes())
    for v in G.nodes():
        padre[v] = None
        coste_minimo[v] = INFTY
    # cogemos un nodo cualquiera como nodo origen (hemos cogido el primero de G.nodes() por coger uno)
    nodo_inicial = list(G.nodes())[0]
    coste_minimo[nodo_inicial] = 0
    contador = 0
    heapq.heappush(Q, (coste_minimo[nodo_inicial], contador, nodo_inicial))

    while Q != []:
        contador += 1
        coste_minimo_v, _,  v = heapq.heappop(Q)
        if v in nodos_sin_visitar:
            nodos_sin_visitar.remove(v)
        for x in G.neighbors(v):
            contador += 1
            if x in nodos_sin_visitar:
                peso_arista_v_x = peso(G, v, x)
                if peso_arista_v_x < coste_minimo[x]:
                    coste_minimo[x] = peso_arista_v_x
                    padre[x] = v
                    heapq.heappush(Q, (coste_minimo[x], contador, x))
    return padre


def kruskal(G: nx.Graph, peso: Callable[[nx.Graph, object, object], float]) -> List[Tuple[object, object]]:
    """ Calcula un Árbol Abarcador Mínimo para el grafo
    usando el algoritmo de Kruskal.

    Args:
        G (nx.Graph): grafo
        peso (función): función que recibe un grafo y dos vértices del grafo y devuelve el peso de la arista que los conecta
    Returns:
        List[Tuple[object,object]]: Devuelve una lista [(s1,t1),(s2,t2),...,(sn,tn)]
            de los pares de vértices del grafo que forman las aristas
            del arbol abarcador mínimo.
    Raises: None
    Example:
        En el ejemplo anterior en que prim(G,peso)={1:None, 2:1, 3:2, 4:1} podríamos tener, por ejemplo,
        kruskal(G,peso)=[(1,2),(1,4),(3,2)]
    """
    aristas_arbol = []
    L = []
    for u, v in G.edges():
        L.append((peso(G, u, v), u, v))
    L.sort(key=lambda x: x[0])

    componentes = {v: (v,) for v in G.nodes()}
    for peso_arista, u, v in L:
        if componentes[u] != componentes[v]:
            aristas_arbol.append((u, v))
            componente_u = componentes[u]
            componente_v = componentes[v]
            componente_unida = componente_u + componente_v
            for nodo in componente_unida:
                componentes[nodo] = componente_unida

    return aristas_arbol
