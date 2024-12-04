from math import radians, sin, cos, sqrt, atan2

from clases import Camion, Pedido

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

def mostrar_ruta_con_costes_acumulados(ruta, grafo, coste_medio_km: float, velocidad_media_camiones: float):
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

############################## FUNCIONES CAMIONES ##############################

def siguiente_id_camion(camiones:dict) -> int:
    
    # OBTENIR EL SEGÜENT ID DE CAMIÓ
    if not camiones:
        return 1
    else:
        return max(camiones.keys()) + 1

def crear_camion(ped_id: list, dest: dict, prod_id: list, cant: int, dict_camiones: dict):
    camio = Camion(
        id_camion = siguiente_id_camion(dict_camiones),
        id_pedidos = ped_id,
        destinos = {list(dest.keys())[0]: list(dest.values())[0]},
        id_productos = prod_id,
        cantidad = cant
    )

    dict_camiones[camio.id_camion] = camio

    return dict_camiones

def add_to_camiones(dict_camiones: dict, camion_id: int, camion_atributes: 'Camion', ped: 'Pedido', capacidad_camiones:int, mes_cantidad_que_capacidad: bool):

    dict_camiones[camion_id].id_pedidos.append(ped.id_pedido)
    dict_camiones[camion_id].destinos[ped.destino] = ped.coordenadas
    dict_camiones[camion_id].id_productos.append(ped.id_producto)

    if not mes_cantidad_que_capacidad:
        dict_camiones[camion_id].cantidad += ped.cantidad

    elif mes_cantidad_que_capacidad:

        # LA NOVA QUANTITAT DEL PRODUCTE ES LA RESTA DE LA CAPACITAT QUE FALTA PER OMPLIR DEL CAMIÓ
        ped.cantidad = ped.cantidad - (capacidad_camiones - camion_atributes.cantidad)

        # ACTUALITZAR LA QUANTITAT DEL CAMIÓ
        dict_camiones[camion_id].cantidad += (capacidad_camiones - camion_atributes.cantidad)
    

    return dict_camiones, ped

def check_destinos(destinos_camion: dict, coordenadas_pedido: list):

    coincidencias = set(destinos_camion.values()) & set(coordenadas_pedido)

    if len(coincidencias) > 0:
        return True
    else:
        return False
    
def check_id_producto(pedidos_id_camion: list, product_id_pedido: int):
    if product_id_pedido in pedidos_id_camion:
        return True
    else:
        return False

##########################################################################################

############################## FUNCIONES PEDIDOS ##############################

def del_pedidos_vacios(pedidos_ordenados:dict):
    for k,v in list(pedidos_ordenados.items()):
        if v == []:
            del pedidos_ordenados[k]
    return pedidos_ordenados

##########################################################################################