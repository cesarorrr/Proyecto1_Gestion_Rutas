import sqlite3, json
import networkx as nx
from networkx.algorithms import approximation as approx
from math import radians, sin, cos, sqrt, atan2

############################## FUNCIONES DEL ALGORITMO ##############################

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

########################################################################################################################

############################## CLASES ##############################

class Camion():
    def __init__(self,id_camion:int, id_pedidos:list, destinos:dict, id_productos:list, cantidad:int):
        self.id_camion = id_camion
        self.id_pedidos = id_pedidos
        self.destinos = destinos # {"nombre":coordenadas}
        self.id_productos = id_productos
        self.cantidad = cantidad

    def to_dict(self):
        # Convert the object to a dictionary
        return {
            "id_camion": self.id_camion,
            "id_pedidos": self.id_pedidos,
            "destinos": self.destinos,
            "id_productos": self.id_productos,
            "cantidad": self.cantidad
    }

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
        

########################################################################################################################

############################################################ MAIN ############################################################

conn = sqlite3.connect(r"C:\Users\joant\OneDrive\Stucom\MasterIA\IA\Projecte 1 - Logistica\logistics.db")
cursor = conn.cursor()

# ESTABLIR LES VARIABLES 
velocidad_media_camiones = 100  # km/h
capacidad_camiones = 1000      # unidades
coste_medio_km = 0.6           # € por km

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

############################## DEFINIR QUINS PRODUCTES VAN A QUIN CAMIÓ ##############################


# ITERAR POR CADA ID_PRODUCTO
while len(pedidos_ordenados.keys()):

    for k,v in list(pedidos_ordenados.items()):
        if v == []:
            del pedidos_ordenados[k]

    # ITERAR POR CADA ID_PRODUCTO
    for id_producto, pedidos_producto in list(pedidos_ordenados.items()):
        
        pedidos_to_pop = []

        # ITERAR POR CADA PEDIDO DE UN ID_PRODUCTO
        for index1, pedido in enumerate(pedidos_producto):

            # COMPROVAR SI LA CANTITAT DEL PEDIDO ES MÉS GRAN QUE LA CAPACITAT DELS CAMIONS        
            while pedido.cantidad >= capacidad_camiones:
                
                # CREAR EL CAMIÓ
                camio = Camion(
                    id_camion = siguiente_id_camion(),
                    id_pedidos = [pedido.id_pedido],
                    destinos = {pedido.destino : pedido.coordenadas},
                    id_producto = [id_producto],
                    cantidad = capacidad_camiones
                )

                camiones[camio.id_camion] = camio

                # MODIFICAR LA QUANTIAT QUE QUEDA DEL PEDIDO EN pedidos_ordenados
                pedido.cantidad = pedido.cantidad - capacidad_camiones

            # SI LA QUANTITAT DEL PEDIDO ES INFERIOR A LA CAPACITAT DELS CAMIONS
            if pedido.cantidad < capacidad_camiones:

                # COMPROVAR SI HI HA CAMIONS CREATS
                if camiones:
                
                    # ITERAR PER CAMIONS CREATS PER VEURE SI HI CAP EN ALGÚN CAMIÓ
                    for id_camion, info_camion in list(camiones.items()):

                        # COMPROVAR SI EL CAMIÓ JA ESTA PLE
                        if info_camion.cantidad != capacidad_camiones:
                            
                            # SI LA SUMA DE LA QUANTIAT CARREGADA I LA QUANTITAT DEL PEDIDO ES MES GRAN QUE LA CAPACITAT D'UN CAMIÓ
                            if (info_camion.cantidad + pedido.cantidad) > capacidad_camiones:
                                
                                camiones[id_camion].id_pedidos.append(pedido.id_pedido)
                                camiones[id_camion].destinos[pedido.destino] = pedido.coordenadas
                                camiones[id_camion].id_productos.append(pedido.id_producto)

                                # LA NOVA QUANTITAT DEL PRODUCTE ES LA RESTA DE LA CAPACITAT QUE FALTA PER OMPLIR DEL CAMIÓ
                                pedido.cantidad = pedido.cantidad - (capacidad_camiones - info_camion.cantidad)

                                # ACTUALITZAR LA QUANTITAT DEL CAMIÓ
                                camiones[id_camion].cantidad += (capacidad_camiones - info_camion.cantidad)

                                # SI LA QUANTITAT DE LA COMANDA ACTUAL SEGUEIX SUPERANT LA CAPACITAT D'UN CAMIÓ
                                while pedido.cantidad > 0:
                                    camio = Camion(
                                        id_camion = siguiente_id_camion(camiones),
                                        id_pedidos = [pedido.id_pedido],
                                        destinos = {pedido.destino : pedido.coordenadas},
                                        id_productos = [id_producto],
                                        cantidad = pedido.cantidad
                                    )

                                    camiones[camio.id_camion] = camio

                                    pedido.cantidad = pedido.cantidad - camio.cantidad

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

                    # CREAR EL CAMIÓ SI NO HI HA CAP CAMIÓ QUE TINGUI MENYS PRODUCTES CARREGATS QUE LA CAPACITAT D'UN CAMIÓ
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

                # SI NO S'HA CREAT CAMIONS
                elif not camiones:

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
########################################################################################################################

############################## ESTABLIR MATARÓ COM EL ORIGEN ##############################
for camio in camiones.values():

    destinos_finales = {'Mataró':'41.532521,2.423604'}
    destinos_finales.update(camio.destinos)

    camio.id_productos = list(dict.fromkeys(camio.id_productos))
    camio.destinos = destinos_finales


########################################################################################################################

############################## OPTIMIZAR LAS RUTAS ##############################

rutes_optimes = {} # ID PEDIDO : RUTA

# ITERAR POR LOS CAMIONES
for camion_id, detalles in camiones.items():

    G = nx.Graph()
    
    # AÑADIR LOS NODOS EN BASE A LOS DESTINOS DEL CAMIÓN
    for provincia, coords_gps in detalles.destinos.items():

        lat, lon = map(float, coords_gps.split(","))
        G.add_node(provincia, pos=(lat, lon))

    # AÑADIR LAS ARISTAS ENTRE LOS NODOS CREADOS
    for provincia1, coords_gps1 in detalles.destinos.items():
        for provincia2, coords_gps2 in detalles.destinos.items():

            if provincia1 != provincia2:

                lat1, lon1 = coords_gps1.split(",")
                lat2, lon2 = coords_gps2.split(",")

                distancia = haversine(float(lat1), float(lon1), float(lat2), float(lon2))

                coste_total = distancia * coste_medio_km

                G.add_edge(provincia1, provincia2, weight=coste_total)

    # OBTENER LA RUTA OPTIMA
    ruta_optima_cerrada = approx.traveling_salesman_problem(G, cycle=True, weight='weight')
    
    # MOSTRAR LA RUTA CON LOS COSTES ACUMULADOS
    ruta_con_costes = mostrar_ruta_con_costes_acumulados(ruta_optima_cerrada, G)

    # AÑADIR LA RUTA OPTIMA DE CADA CAMIÓN AL DICCIONARIO rutes_optimes
    rutes_optimes[camion_id] = ruta_con_costes

########################################################################################################################

############################## RESULTATS ##############################

# CAMBIAR LOS ID_PRODUCTOS POR LOS NOMBRES DE PRODUCTO
for id,truck in camiones.items():
    for ind, producto in enumerate(list(truck.id_productos)):
        nombre_producto = cursor.execute(f"SELECT nombre_producto FROM productos WHERE id_producto = {producto}").fetchone()

        truck.id_productos[ind] = str(truck.id_productos[ind]).replace(str(producto), nombre_producto[0])


# PASARLO A JSON
camiones_data = {key: value.to_dict() for key, value in camiones.items()}

with open('camiones_data.json', 'w', encoding='utf-8') as f:
    json.dump(camiones_data, f, indent=4,ensure_ascii=False)