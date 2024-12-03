from heapq import heapify, heappop, heappush
import os
import networkx as nx
import matplotlib.pyplot as plt

graph = {
   "Lleida": {
       "Barcelona": 1.5,
       "Tarragona": 1,
       "Girona": 2.5,
       #"Valencia": 3.5,
       #"Castellon de la Plana": 2.75,
       "Zaragoza": 1.5,
       "Huesca": 1.25,
       #"Alicante": 4.5,
       "Teruel": 2.75
   },
   "Barcelona": {
       "Lleida": 1.5,
       #"Tarragona": 1,
       #"Girona": 1.25,
       #"Valencia": 3.5,
       #"Castellon de la Plana": 2.75,
       #"Zaragoza": 3,
       "Huesca": 3.5,
       #"Alicante": 5,
       "Teruel": 4
   },
   "Tarragona": {
       "Lleida": 1,
       #"Barcelona": 1,
       #"Girona": 2.25,
       "Valencia": 2.75,
       "Castellon de la Plana": 2,
       "Zaragoza": 2.5,
       "Huesca": 3,
       "Alicante": 4,
       #"Teruel": 3
   },
   "Girona": {
       "Lleida": 2.5,
       #"Barcelona": 1.25,
       #"Tarragona": 2.25,
       "Valencia": 4.5,
       #"Castellon de la Plana": 4,
       "Zaragoza": 4.5,
       #"Huesca": 5,
       "Alicante": 6,
       "Teruel": 5
   },
   "Valencia": {
       #"Lleida": 3.5,
       #"Barcelona": 3.5,
       "Tarragona": 2.75,
       "Girona": 4.5,
       #"Castellon de la Plana": 1,
       "Zaragoza": 3,
       "Huesca": 3.5,
       "Alicante": 1.75,
       "Teruel": 2
   },
   "Castellon de la Plana": {
       #"Lleida": 2.75,
       #"Barcelona": 2.75,
       "Tarragona": 2,
       #"Girona": 4,
       #"Valencia": 1,
       #"Zaragoza": 2.75,
       "Huesca": 3.25,
       #"Alicante": 2.75,
       "Teruel": 1.5
   },
   "Zaragoza": {
       "Lleida": 1.5,
       #"Barcelona": 3,
       "Tarragona": 2.5,
       "Girona": 4.5,
       "Valencia": 3,
       #"Castellon de la Plana": 2.75,
       #"Huesca": 0.75,
       "Alicante": 4.25,
       "Teruel": 2
   },
   "Huesca": {
       "Lleida": 1.25,
       "Barcelona": 3.5,
       "Tarragona": 3,
       #"Girona": 5,
       "Valencia": 3.5,
       "Castellon de la Plana": 3.25,
       #"Zaragoza": 0.75,
       "Alicante": 5,
       "Teruel": 3
   },
   "Alicante": {
       #"Lleida": 4.5,
       #"Barcelona": 5,
       "Tarragona": 4,
       "Girona": 6,
       "Valencia": 1.75,
       #"Castellon de la Plana": 2.75,
       "Zaragoza": 4.25,
       "Huesca": 5,
       "Teruel": 3
   },
   "Teruel": {
       "Lleida": 2.75,
       "Barcelona": 4,
       #"Tarragona": 3,
       "Girona": 5,
       "Valencia": 2,
       "Castellon de la Plana": 1.5,
       "Zaragoza": 2,
       "Huesca": 3,
       "Alicante": 3
   }
}

class Graph:
    def __init__(self, graph: dict = {}):
        self.graph = graph  # A dictionary for the adjacency list

    def add_edge(self, node1, node2, weight):
        if node1 not in self.graph:  # Check if the node is already added
            self.graph[node1] = {}  # If not, create the node
        self.graph[node1][node2] = weight  # Add a connection to its neighbor

    def shortest_distances(self, source: str):
        # ESTABLIR TOTES LES DISTANCIES A INFINIT
        distances = {node: float("inf") for node in self.graph}
        
        # ESTABLIR LA DISTANCIA DE L'ORIGEN A 0
        distances[source] = 0  

        # INICIALITZAR UNA CUA DE PRIORITAT AMB L'ORIGEN COM A PRIMER ELEMENT (CUA ORDENADA PER WEIGHT)
        pq = [(0, source)]
        heapify(pq)

        # CREAR UN SET PER GUARDAR ELS NODES VISITATS
        visited = set()

        # CREAR DICCIONARI DE NODES PREDECESSORS PER RECONSTRUIR EL CAMI
        predecessors = {node: None for node in self.graph}

        # MENTRE LA CUA DE PRIORITAT NO ESTIGUI BUIDA
        while pq:

            # DEFINIR EL NODE ACTUAL I LA DISTANCIA DES DE L'ORIGEN O NODE PREVI
            current_distance, current_node = heappop(pq)

            # SI EL NODE ESTA DINTRE DEL SET DE VISITATS, SALTAR AL INICI DEL BUCLE
            if current_node in visited:
                continue 

            # AFEGIR EL NODE AL SET DE VISITATS
            visited.add(current_node)

            # BUCLE PER ITERAR SOBRE CADA NODE VEÏ AMB EL SEU WEIGHT
            for neighbor, weight in self.graph[current_node].items():
                
                # CALCULAR LA DISTANCIA DEL NODE ACTUAL AL VEI SUMANT LA DISTANCIA JA RECORREGUDA
                tentative_distance = current_distance + weight

                # SI LA DISTANCIA CALCULADA ES MÉS PETTIA QUE LA DISTANCIA DEFINIDA
                if tentative_distance < distances[neighbor]:

                    # MODIFICAR LA DISTANCIA DEL VEI AMB LA NOVA 'tentative_distance'                    
                    distances[neighbor] = tentative_distance

                    # DEFINIR QUE EL PREDECESOR DEL VEI ES EL NODE ACTUAL
                    predecessors[neighbor] = current_node

                    # AFEGIR A LA CUA DE PRIORITAT LA DISTANCIA I EL VEI DEL NODE ACTUAL
                    heappush(pq, (tentative_distance, neighbor))

        return distances, predecessors
       
    def shortest_path(self, source: str, target: str):
        # GENERAR EL DICCIONARI DE PREDECESSORS
        _, predecessors = self.shortest_distances(source)

        path = []

        #ESTABLIR COM A CURRENT NODE EL NODE AL QUE VOLEM ARRIBAR
        current_node = target

        # FER LA RUTA INVERSA A PARTIR DEL DICCIONARI DE PREDECESSORS
        while current_node:
            # AFEGIR EL NODE ACTUAL AL PATH
            path.append(current_node)

            # ACTUALITZAR EL NODE ACTUAL AMB EL PREDECESSOR D'AQUEST
            current_node = predecessors[current_node]

        # REVERTIR L'ORDRE DEL PATH PERQUE QUEDI ORDENAR DE ORIGEN A DESTI
        path.reverse()

        # RETORNA EL PATH SI EL PRIMER ELEMENT COINCIDEIX AMB L'ORGIEN ESTABLERT
        return path if path[0] == source else []

os.system("cls")

# CREAR UN OBJECTE Graph
G = Graph(graph)
camions = {
    "camion1":("Barcelona","Tarragona"),
    "camion2" : ("Valencia","Castellon de la Plana"),
    "camion3": ("Huesca","Zaragoza")
}


# ESTABLIR ORIGEN I DESTÍ
# origen = "Girona"
# desti = "Castellon de la Plana"

# for camion in camions.keys():
#     origen = camions[camion][0]
#     desti = camions[camion][1]

#     # OBTENIR LES DISTANCIES MES CURTES DES DE L'ORIGEN
#     distances, predecessors = G.shortest_distances(origen)

#     print("-"*80)
#     # IMPRIMIR LA DISTANCIA MES CURTA FINS AL DESTÍ
#     total_time = distances[desti]
#     print(f"\nTrigaras {total_time}h en anar de {origen} a {desti}\n")

#     # OBTENIR EL CAMI MES CURT ENTRE ORIGEN I DESTI
#     path = G.shortest_path(origen, desti)
#     print(f"El camí més curt és {', '.join(path)}\n")
#     print("-"*80)