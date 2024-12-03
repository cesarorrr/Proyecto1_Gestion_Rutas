import sqlite3,random
from typing import Dict, Tuple
import networkx as nx
from networkx.algorithms import approximation as approx
import matplotlib.pyplot as plt
from math import radians, sin, cos, sqrt, atan2

# FUNCIO PER SABER LA DISTANCIA ENTRE COORDENADES
def haversine(lat1:float, lon1:float, lat2:float, lon2:float):
    # Radio de la Tierra en km
    R = 6371.0
    
    # Convertir grados a radianes
    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)
    
    # Diferencias
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    # Fórmula de Haversine
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    
    # Distancia en kilómetros
    distance = R * c
    return distance

def mostrar_ruta_con_costes_acumulados(ruta, grafo):
    coste_total = 0
    ruta_con_costes = []  # Lista para almacenar los nodos con sus costes acumulados

    # Recorrer la ruta para calcular los costes acumulados
    for i in range(len(ruta) - 1):
        nodo1 = ruta[i]
        nodo2 = ruta[i + 1]
        
        # Obtener el peso (distancia) entre los nodos
        peso = grafo[nodo1][nodo2]['weight']
        coste_total += peso
        
        # Formato: (nodo1) --> (nodo2) con su coste acumulado
        ruta_con_costes.append(f"{nodo2} ({coste_total:.2f} €)")

    distancia_total = coste_total * coste_medio_km
    temps_total = distancia_total / velocidad_media_camiones

    # Construir la cadena de la ruta con el nodo inicial y la distancia total
    ruta_str = "\nRUTA ÓPTIMA:\n" + f"{ruta[0]} (inicial) --> " + " --> ".join(ruta_con_costes)
    ruta_str += f"\n\nCoste total: {coste_total:.2f} €"
    ruta_str += f"\nDistancia total: {distancia_total:.2f} km"
    ruta_str += f"\nTemps total: {temps_total:.2f} hores"

    return ruta_str

def siguiente_id_camion(camiones:dict) -> int:
    
    # OBTENIR EL SEGÜENT ID DE CAMIÓ
    if not camiones:
        return 1
    else:
        return max(camiones.keys())+1

class Camion():
    def __init__(self,id_camion:int, id_pedidos:list, destinos:dict, id_productos:list, cantidad:int):
        self.id_camion = id_camion
        self.id_pedidos = id_pedidos
        self.destinos = destinos # {"nombre":coordenadas}
        self.id_productos = id_productos
        self.cantidad = cantidad

    def __str__(self):
            return (f"Camion ID: {self.id_camion}\n"
                    f"Pedidos: {', '.join(map(str, self.id_pedidos))}\n"
                    f"Destinos: {' | '.join(self.destinos)}\n"
                    f"Producto ID: {self.id_productos}\n"
                    f"Cantidad: {self.cantidad}")

class Pedido():
    def __init__(self, id_pedido:int, coordenadas:str, destino:str, id_producto:int, nombre_producto:str, cantidad:int):
        self.id_pedido = id_pedido
        self.coordenadas = coordenadas
        self.destino = destino
        self.id_producto = id_producto
        self.nombre_producto = nombre_producto
        self.cantidad = cantidad

    def __str__(self):
        return (
            f"Pedido #{self.id_pedido}:\n"
            f"  Producto: {self.nombre_producto} (ID: {self.id_producto})\n"
            f"  Cantidad: {self.cantidad}\n"
            f"  Coordenadas de recogida: {self.coordenadas}\n"
            f"  Destino: {self.destino}\n"
        )
        

# -----------------------------------------------------------------------------------------------------------------------------------------#

conn = sqlite3.connect(r"C:\Users\joant\OneDrive\Stucom\MasterIA\IA\Projecte 1 - Logistica\logistics.db")
cursor = conn.cursor()

###################################### ESTABLIR LES VARIABLES ########################################
velocidad_media_camiones = 100  # km/h
capacidad_camiones = 1000      # unidades
coste_medio_km = 0.6           # € por km
######################################################################################################

# OBTENIR LES COMANDES PER PRODUCTE
pedidos = cursor.execute("""
    SELECT
        ped.id_pedido,
        ped.id_producto, 
        prod.nombre_producto, 
        ped.destino, 
        COUNT(ped.id_pedido) AS total_pedidos, 
        SUM(ped.cantidad) AS total_cantidad
    FROM pedidos ped
    JOIN productos prod ON ped.id_producto = prod.id_producto
    GROUP BY ped.id_producto, ped.destino
    ORDER BY ped.id_producto, ped.destino
""").fetchall()


# ITERAR PER ELS RESULTATS DE LA QUERY PER AGRUPAR TOTES LES COORDENADES D'UN MATEIX PRODUCTE I OBTENIR EL TOTAL DE PRODUCTES

pedidos_ordenados = {} # ID_PRODUCTO : [NOMBRE_PRODUCTO, {DESTINO:COORDENADAS}, [CANTIDAD_TOTAL_PRODUCTO]]


for ped in pedidos:

    pedido = Pedido(
        id_pedido = int(ped[0]),
        coordenadas = str(ped[3].replace(" ","")),
        destino = "",
        id_producto = int(ped[1]),
        nombre_producto = str(ped[2]),
        cantidad = int(ped[5])
    )


    # OBTENIR EL NOM DEL DESTI PER FER ELS NODES
    provincia_desti = cursor.execute("""SELECT provincia FROM destinos WHERE latitud = ? AND longitud = ?""",(pedido.coordenadas.split(",")[0],pedido.coordenadas.split(",")[1])).fetchone()

    pedido.destino = provincia_desti[0]

    if pedido.id_producto in pedidos_ordenados.keys():
        pedidos_ordenados[pedido.id_producto].append(pedido)
    
    elif pedido.id_producto not in pedidos_ordenados.keys():
        pedidos_ordenados[pedido.id_producto] = []
        pedidos_ordenados[pedido.id_producto].append(pedido)


pedidos_pendientes = {} # ID_PEDIDO : [CANTIDAD,[COORDENADAS]]
camiones = {} # ID_PEDIDO : {CAMION}

################################################################# DEFINIR QUINS PRODUCTES VAN A QUIN CAMIÓ ##############################################################################

pedidos_to_pop = []

while len(pedidos_ordenados.keys()):

    # ITERAR POR CADA ID_PRODUCTO
    for id_producto, pedidos_producto in list(pedidos_ordenados.items()):
        
        # ITERAR POR CADA PEDIDO DE UN ID_PRODUCTO
        for index1, pedido in enumerate(pedidos_producto):

            # COMPROVAR SI LA CANTITAT DEL PEDIDO ES MÉS GRAN QUE LA CAPACITAT DELS CAMIONS        
            if pedido.cantidad >= capacidad_camiones:

                # LA QUANTITAT QUE ANIRA AL CAMIÓ ES EL TOTAL DE LA SEVA CAPACITAT
                cantidad_camion = capacidad_camiones
                
                # CREAR EL CAMIÓ
                camio = Camion(
                    id_camion = siguiente_id_camion(),
                    id_pedidos = [pedido.id_pedido],
                    destinos = {pedido.destino : pedido.coordenadas},
                    id_producto = [id_producto],
                    cantidad = pedido.cantidad
                )

                camiones[camio.id_camion] = camio

                # MODIFICAR LA QUANTIAT QUE QUEDA DEL PEDIDO EN pedidos_ordenados
                pedidos_ordenados[id_producto][index1].cantidad = capacidad_camiones

            # SI LA QUANTITAT DEL PEDIDO ES INFERIOR A LA CAPACITAT DELS CAMIONS
            elif pedido.cantidad < capacidad_camiones:

                if camiones:
                
                    # ITERAR PER CAMIONS CREATS PER VEURE SI HI CAP EN ALGÚN CAMIÓ
                    for id_camion, info_camion in list(camiones.items()):
                        
                        # SI LA SUMA DE LA QUANTIAT CARREGADA I LA QUANTITAT DEL PEDIDO ES MES GRAN QUE LA CAPACITAT D'UN CAMIÓ
                        if (info_camion.cantidad + pedido.cantidad) > capacidad_camiones:
                            
                            camiones[id_camion].id_pedidos.append(pedido.id_pedido)
                            camiones[id_camion].destinos[pedido.destino] = pedido.coordenadas
                            camiones[id_camion].id_productos.append(pedido.id_producto)

                            pedidos_ordenados[id_producto][index1].cantidad = pedido.cantidad - (capacidad_camiones - info_camion.cantidad)

                            camiones[id_camion].cantidad += (capacidad_camiones - info_camion.cantidad)

                            
                            break

                        # SI LA QUANTITAT CARREGADA AL CAMIÓ I LA QUANTITAT DEL PEDIDO ES INFERIOR A LA CAPACITAT DEL CAMIÓ
                        elif (info_camion.cantidad + pedido.cantidad) < capacidad_camiones:

                            # ACTUALITZAR EL CAMIÓ AMB LA INFO DEL PEDIDO ACTUAL
                            camiones[id_camion].id_pedidos.append(pedido.id_pedido)
                            camiones[id_camion].destinos[pedido.destino] = pedido.coordenadas
                            camiones[id_camion].id_productos.append(pedido.id_producto)
                            camiones[id_camion].cantidad += pedido.cantidad

                            pedidos_to_pop.append(index1)

                            break

                # CREAR EL CAMIÓ
                else:
                    camio = Camion(
                        id_camion = siguiente_id_camion(camiones),
                        id_pedidos = [pedido.id_pedido],
                        destinos = {pedido.destino : pedido.coordenadas},
                        id_productos = [id_producto],
                        cantidad = pedido.cantidad
                    )

                    camiones[camio.id_camion] = camio

                    pedidos_to_pop.append(index1)

        # ELIMINAR LES COMANDES QUE JA S'HAN AFEGIT EN UN CAMIÓ
        pedidos_to_pop.reverse()
        for index in pedidos_to_pop:
            pedidos_ordenados[id_producto].pop(index)


# IMPRIMIR ELS CAMIONS CREATS DE NOU
for camio in camiones.values():
    print(camio, "\n")

print(f"TOTAL CAMIONES: {len(camiones.keys())}\n")

##########################################################################################################################################################

rutes_optimes = {} # ID PEDIDO : RUTA

G = nx.Graph()

for id_ped, atributos in pedidos_x_producto.items():

    for provincia, coords_gps in atributos[1].items():

        lat, lon = map(float, coords_gps.split(","))
        G.add_node(provincia, pos=(lat, lon))

    for provincia1, coords_gps1 in atributos[1].items():
        for provincia2, coords_gps2 in atributos[1].items():

            if provincia1 != provincia2:

                lat1, lon1 = coords_gps1.split(",")
                lat2, lon2 = coords_gps2.split(",")

                distancia = haversine(float(lat1), float(lon1), float(lat2), float(lon2))

                coste_total = distancia * coste_medio_km

                G.add_edge(provincia1, provincia2, weight=coste_total)

    ruta_optima_cerrada = approx.traveling_salesman_problem(G, cycle=True, weight='weight')
    
    # Mostrar la ruta con los costes acumulados
    ruta_con_costes = mostrar_ruta_con_costes_acumulados(ruta_optima_cerrada, G)

    rutes_optimes[id_ped] = ruta_con_costes


for id_producto, atributos in pedidos_x_producto.items():
    print(f"\n\nID Producto: {id_producto}")
    print(f"Nombre Producto: {atributos[0]}")
    print(f"Destinos: {atributos[1]}")
    #print(f"Cantidad Total: {atributos[2]}")
    
    for id, ruta in rutes_optimes.items():
        if id == id_producto:
            print(ruta)
    
    print("-" * 50)

# DEFINIR EL NOMBRE DE CAMIONS EN BASE A LA CANTITAT DE PRODUCTES Y RECALULAR TOT