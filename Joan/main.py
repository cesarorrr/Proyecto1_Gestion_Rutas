import sqlite3, json
import networkx as nx
from networkx.algorithms import approximation as approx

from functions import del_pedidos_vacios, add_to_camiones, crear_camion, mostrar_ruta_con_costes_acumulados, haversine, check_id_producto, check_destinos
from clases import Pedido

############################## MAIN ##############################

conn = sqlite3.connect(r"C:\Users\joant\OneDrive\Stucom\MasterIA\IA\Proyecto1_Gestion_Rutas\Joan\logistics.db")
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

    pedidos_ordenados = del_pedidos_vacios(pedidos_ordenados)

    # ITERAR POR CADA ID_PRODUCTO
    for id_producto, pedidos_producto in list(pedidos_ordenados.items()):
        
        pedidos_to_pop = []

        # ITERAR POR CADA PEDIDO DE UN ID_PRODUCTO
        for index1, pedido in enumerate(pedidos_producto):

            # COMPROVAR SI LA CANTITAT DEL PEDIDO ES MÉS GRAN QUE LA CAPACITAT DELS CAMIONS        
            while pedido.cantidad >= capacidad_camiones:
                
                camiones = crear_camion(
                    ped_id = [pedido.id_pedido],
                    dest = {pedido.destino : pedido.coordenadas},
                    prod_id = [id_producto],
                    cant = capacidad_camiones,
                    dict_camiones = camiones
                )

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
                                
                                # SI EL CAMIÓ CONTÉ LA id_producto DEL PEDIDO ACTUAL AFEGIR AL CAMIÓ
                                if check_id_producto(info_camion.id_productos, pedido.id_producto) | check_destinos(info_camion.destinos, pedido.coordenadas):

                                    # AFEGIR AL CAMIÓ EXISTENT LA QUANTITAT DEL PEDIDO
                                    camiones, pedido = add_to_camiones(
                                        dict_camiones = camiones,
                                        camion_id = id_camion,
                                        camion_atributes = info_camion,
                                        ped = pedido,
                                        capacidad_camiones = capacidad_camiones,
                                        mes_cantidad_que_capacidad = True
                                    )
                                
                                    # SI LA QUANTITAT DE LA COMANDA ACTUAL SEGUEIX SUPERANT LA CAPACITAT D'UN CAMIÓ
                                    while pedido.cantidad > 0:
                                        

                                        # CREAR NOU CAMIÓ AMB LA QUANTIAT SOBRANT
                                        camiones = crear_camion(
                                            ped_id = [pedido.id_pedido],
                                            dest = {pedido.destino : pedido.coordenadas},
                                            prod_id = [id_producto],
                                            cant = pedido.cantidad,
                                            dict_camiones = camiones
                                        )

                                        # RESTAR LA QUANTITAT DE PRODUCTE QUE HI HA AL CAMIÓ CREAT A LA QUANTIAT DEL PEDIDO ACTUAL
                                        pedido.cantidad = pedido.cantidad - camiones[list(camiones.keys())[-1]].cantidad

                                    pedidos_to_pop.append(index1)

                                    break

                            # SI LA QUANTITAT CARREGADA AL CAMIÓ I LA QUANTITAT DEL PEDIDO ES INFERIOR A LA CAPACITAT DEL CAMIÓ
                            elif (info_camion.cantidad + pedido.cantidad) < capacidad_camiones:

                                # SI EL CAMIÓ CONTÉ LA id_producto DEL PEDIDO ACTUAL AFEGIR AL CAMIÓ
                                if check_id_producto(info_camion.id_productos, pedido.id_producto) | check_destinos(info_camion.destinos, pedido.coordenadas):

                                    # ACTUALITZAR EL CAMIÓ AMB LA INFO DEL PEDIDO ACTUAL
                                    camiones, pedido = add_to_camiones(
                                        dict_camiones = camiones,
                                        camion_id = id_camion,
                                        camion_atributes = info_camion,
                                        ped = pedido,
                                        capacidad_camiones = pedido.cantidad,
                                        mes_cantidad_que_capacidad = False
                                    )

                                    pedidos_to_pop.append(index1)

                                    break


                            else:
                                # SI NO COMPLEIX CAP DE LES DUES CONDICIONS, CREAR UN NOU CAMIÓ AMB LA COMANDA
                                camiones = crear_camion(
                                    ped_id = [pedido.id_pedido],
                                    dest = {pedido.destino : pedido.coordenadas},
                                    prod_id = [id_producto],
                                    cant = pedido.cantidad,
                                    dict_camiones = camiones
                                )
                                

                    # CREAR EL CAMIÓ SI NO HI HA CAP CAMIÓ QUE TINGUI MENYS PRODUCTES CARREGATS QUE LA CAPACITAT D'UN CAMIÓ
                    else:
                        camiones = crear_camion(
                            ped_id = [pedido.id_pedido],
                            dest = {pedido.destino : pedido.coordenadas},
                            prod_id = [id_producto],
                            cant = capacidad_camiones,
                            dict_camiones = camiones
                        )

                        pedidos_to_pop.append(index1)

                # SI NO S'HA CREAT CAMIONS
                elif not camiones:

                    camiones = crear_camion(
                        ped_id = [pedido.id_pedido],
                        dest = {pedido.destino : pedido.coordenadas},
                        prod_id = [id_producto],
                        cant = pedido.cantidad,
                        dict_camiones = camiones
                    )

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
    ruta_con_costes = mostrar_ruta_con_costes_acumulados(ruta_optima_cerrada, G, coste_medio_km, velocidad_media_camiones)

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