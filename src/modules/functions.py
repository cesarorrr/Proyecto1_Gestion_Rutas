from math import radians, sin, cos, sqrt, atan2
from clases import Camion, Pedido
import random, logging
from datetime import datetime, timedelta

############################## CONFIGURACIÓN DE LOGGING ##############################
# Configuración inicial para registrar eventos en un archivo de log
logging.basicConfig(
    filename=r'logs\log.txt',
    level=logging.INFO,  # Cambiar a DEBUG para mayor detalle si es necesario
    format='%(asctime)s - %(message)s',
    encoding="utf-8",
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Función para registrar mensajes en el archivo de log
def log_accion(message):
    logging.info(message)

# Función para inicializar el archivo de log (vaciarlo al inicio)
def inicializar_log():
    with open(r'logs\log.txt', "w") as log_file:
        pass

##########################################################################################

############################## FUNCIONES DEL ALGORITMO ##############################

# Genera pedidos aleatorios y los inserta en la base de datos
def random_pedidos(conn, cursor) -> tuple[bool, str]:
    """
    Elimina todos los pedidos existentes en la base de datos y genera 100 pedidos aleatorios.
    Los datos de los pedidos se basan en información preexistente en las tablas de la base de datos.

    Parámetros:
        - conn: conexión activa a la base de datos.
        - cursor: cursor para realizar consultas SQL.

    Retorna:
        - tuple(bool, str): Indicador de éxito y mensaje.
    """
    cursor.execute("DELETE FROM pedidos")  # Eliminar pedidos anteriores
    conn.commit()

    try:
        for i in range(100):  # Generar 100 pedidos
            # Generar un ID único para el pedido
            id_pedido = random.randint(1000000, 9999999)
            
            # Seleccionar un cliente aleatorio
            client_id = cursor.execute(
                "SELECT cif_empresa FROM clientes ORDER BY RANDOM() LIMIT 1"
            ).fetchone()
            if client_id:
                client_id = client_id[0]

            # Obtener coordenadas del destino según la dirección del cliente
            destino = cursor.execute(
                """
                SELECT latitud, longitud 
                FROM destinos 
                WHERE provincia = (SELECT direccion FROM clientes WHERE cif_empresa = ?)
                """, (client_id,)
            ).fetchone()
            
            if destino:
                latitud, longitud = destino

            # Seleccionar un producto aleatorio
            producto = cursor.execute(
                "SELECT * FROM productos ORDER BY RANDOM() LIMIT 1"
            ).fetchone()
            if producto:
                id_producto = producto[0]
                nombre_producto = producto[1]
                tiempo_fabricacion = producto[3]
                caducidad = producto[4]
            
            # Generar datos del pedido
            cantidad = random.randint(550, 990)  # Cantidad aleatoria
            fecha_pedido = datetime.today()
            fecha_caducidad = fecha_pedido + timedelta(days=caducidad)
            fecha_entrega_estimada = fecha_caducidad - timedelta(days=3)
            estado = "En fabricación"
            fecha_entregado = None

            # Insertar pedido en la base de datos
            cursor.execute("""
                INSERT INTO pedidos (
                    id_pedido, cif_empresa, id_producto, nombre_producto, destino, cantidad, 
                    fecha_pedido, fecha_caducidad, fecha_entrega_estimada, 
                    estado, fecha_entregado
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                id_pedido, client_id, id_producto,
                nombre_producto, f"{latitud}, {longitud}", cantidad, 
                fecha_pedido.strftime("%Y-%m-%d"), 
                fecha_caducidad.strftime("%Y-%m-%d"), 
                fecha_entrega_estimada.strftime("%Y-%m-%d"), 
                estado, fecha_entregado
            ))

        conn.commit()  # Confirmar cambios en la base de datos
        return (True, "Correcto")
    
    except Exception as e:
        return (False, str(e))

# Asigna pedidos a camiones según su capacidad y tipo de producto
def asignar_pedidos_a_camiones(pedidos, capacidad_camion):
    """
    Asigna pedidos a camiones agrupándolos por tipo de producto.

    Parámetros:
        - pedidos: Lista de pedidos obtenidos de la base de datos.
        - capacidad_camion: Capacidad máxima de los camiones.

    Retorna:
        - Lista de objetos Camion con los pedidos asignados.
    """
    camiones = []  # Lista de camiones
    camion_actual = None  # Camión que se está utilizando actualmente
    last_producto = None  # Producto del último pedido procesado

    for pedido in pedidos:
        # Convertir cada pedido a un objeto Pedido
        pedido = Pedido(
            id_pedido=pedido[0],
            coordenadas=pedido[3],
            destino=pedido[4],
            id_producto=pedido[1],
            nombre_producto=pedido[2],
            cantidad=pedido[5]
        )

        # Si el producto cambia, asignar el camión actual a la lista y crear uno nuevo
        if last_producto != pedido.nombre_producto:
            if camion_actual and len(camion_actual.pedidos) > 0:
                camiones.append(camion_actual)

            camion_actual = Camion(id_camion=len(camiones) + 1, capacidad=capacidad_camion)
            log_accion(f"Se ha creado el camión #{camion_actual.id_camion} para el pedido #{pedido.id_pedido}.")
            last_producto = pedido.nombre_producto

        # VERIFICAR SI SE HA PODIDO AÑADIR EL PEDIDO AL CAMION ACTUAL
        afegir, quantitat_restant_producte = camion_actual.agregar_pedido(pedido.id_pedido, pedido.nombre_producto, pedido.cantidad, pedido.destino, pedido.coordenadas,capacidad_camion)
            
        while afegir and quantitat_restant_producte > 0:
            camiones.append(camion_actual)  # Camión lleno, asignarlo a la lista
            log_accion(f"Añadido al camion #{camion_actual.id_camion} el pedido #{pedido.id_pedido} ({pedido.nombre_producto}): {pedido.cantidad-quantitat_restant_producte}")

            pedido.cantidad = quantitat_restant_producte # ACTUALIZAR LA CANTIDAD DEL PEDIDO CON LA CANTIDAD RESTANTE POR AÑADIR

            # CREAR UN NUEVO CAMION ACTUAL
            camion_actual = Camion(id_camion=len(camiones) + 1, capacidad=capacidad_camion)
            afegir, quantitat_restant_producte = camion_actual.agregar_pedido(pedido.id_pedido, pedido.nombre_producto, pedido.cantidad, pedido.destino, pedido.coordenadas, capacidad_camion)

            log_accion(f"Se ha creado el camión #{camion_actual.id_camion} para el pedido #{pedido.id_pedido}.")
        
        if not afegir and quantitat_restant_producte != pedido.cantidad:

            while pedido.cantidad > 0:

                camiones.append(camion_actual)  # El pedido actual no cabe en el camion actual

                # CREAR UN NUEVO CAMION ACTUAL
                camion_actual = Camion(id_camion=len(camiones) + 1, capacidad=capacidad_camion)
                afegir, quantitat_restant_producte = camion_actual.agregar_pedido(pedido.id_pedido, pedido.nombre_producto, pedido.cantidad, pedido.destino, pedido.coordenadas, capacidad_camion)

                log_accion(f"Se ha creado el camión #{camion_actual.id_camion} para el pedido #{pedido.id_pedido}.")

                # Log para agregar pedido
                log_accion(f"Añadido al camion #{camion_actual.id_camion} el pedido #{pedido.id_pedido} ({pedido.nombre_producto}): {pedido.cantidad-quantitat_restant_producte}")

                pedido.cantidad = quantitat_restant_producte # ACTUALIZAR LA CANTIDAD DEL PEDIDO CON LA CANTIDAD RESTANTE POR AÑADIR
            continue

            
        # Log para agregar pedido
        log_accion(f"Añadido al camion #{camion_actual.id_camion} el pedido #{pedido.id_pedido} ({pedido.nombre_producto}): {pedido.cantidad}")
    
    camiones.append(camion_actual) # AÑADIR EL ULTIMO CAMION ACTUAL A LA LISTA DE CAMIONES

    return camiones

# Combina camiones con capacidad sobrante para optimizar recursos
def combinar_camiones(camiones, capacidad_camiones):
    """
    Combina camiones con baja ocupación siempre que compartan destinos y no superen la capacidad máxima.

    Parámetros:
        - camiones: Lista de camiones a optimizar.
        - capacidad_camiones: Capacidad máxima de cada camión.

    Retorna:
        - Lista de camiones combinados.
    """
    camiones_combinados = []
    camiones_no_combinados = []

    for camion in camiones:
        if camion.capacidad_restante >= capacidad_camiones / 2:  # Verificar ocupación
            combinado = False
            for otro_camion in camiones_no_combinados:
                if set(camion.destinos).intersection(set(otro_camion.destinos)):
                    total_pedidos = sum(pedido[2] for pedido in camion.pedidos) + sum(pedido[2] for pedido in otro_camion.pedidos)
                    if total_pedidos <= capacidad_camiones:
                        camion.pedidos.extend(otro_camion.pedidos)
                        camion.destinos.update(otro_camion.destinos)
                        camion.capacidad_restante = capacidad_camiones - total_pedidos
                        camiones_combinados.append(camion)
                        camiones_no_combinados.remove(otro_camion)
                        log_accion(f"Se ha combinado el camión #{camion.id_camion} con el camión #{otro_camion.id_camion}.")
                        combinado = True
                        break
            if not combinado:
                camiones_combinados.append(camion)
        else:
            camiones_no_combinados.append(camion)

    camiones_combinados.extend(camiones_no_combinados)
    return camiones_combinados

# Calcula la distancia entre dos puntos geográficos usando la fórmula de Haversine
def haversine(lat1: float, lon1: float, lat2: float, lon2: float):
    """
    Calcula la distancia en kilómetros entre dos puntos geográficos.

    Parámetros:
        - lat1, lon1: Coordenadas del primer punto.
        - lat2, lon2: Coordenadas del segundo punto.

    Retorna:
        - Distancia en kilómetros.
    """
    R = 6371.0  # Radio de la Tierra en kilómetros
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])  # Convertir grados a radianes

    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c

# Calcula costes y tiempos de una ruta basados en un grafo
def costes_ruta(ruta, grafo, coste_medio_km: float, velocidad_media_camiones: float):
    """
    Calcula la distancia, el coste y el tiempo total de una ruta.

    Parámetros:
        - ruta: Lista de nodos en la ruta.
        - grafo: Representación del mapa con pesos entre nodos.
        - coste_medio_km: Coste promedio por kilómetro.
        - velocidad_media_camiones: Velocidad promedio de los camiones.

    Retorna:
        - Tuple con distancia total, coste total y tiempo total.
    """
    distancia_total = 0
    coste_total = 0

    for i in range(len(ruta) - 1):
        nodo1 = ruta[i]
        nodo2 = ruta[i + 1]
        coste = grafo[nodo1][nodo2]['weight']
        coste_total += coste
        distancia_total += coste / coste_medio_km

    tiempo_total = distancia_total / velocidad_media_camiones
    return distancia_total, coste_total, tiempo_total

# Calcula los ingresos totales generados por los pedidos de un camión
def ingresos_camion(cursor, camion: 'Camion'):
    """
    Calcula los ingresos totales de un camión basado en los pedidos que transporta.

    Parámetros:
        - cursor: Cursor para realizar consultas SQL.
        - camion: Objeto Camion con los pedidos asignados.

    Retorna:
        - Ingresos totales generados por el camión.
    """
    ingresos_totales = 0

    for pedido in camion.pedidos:
        precio_producto = cursor.execute(
            "SELECT precio FROM productos WHERE nombre_producto = ?",
            (pedido[1],)
        ).fetchone()[0]
        ingresos_totales += precio_producto * pedido[2]

    return ingresos_totales

def csv_to_pedidos(pedidos: list, fila):
    # Convertir fila en una tupla y añadirla a la lista pedidos
    pedidos.append((
        fila['id_pedido'],
        fila['id_producto'],
        str(fila['nombre_producto']),
        str(fila['destino']),
        str(fila['provincia']),
        fila['total_cantidad']
    ))