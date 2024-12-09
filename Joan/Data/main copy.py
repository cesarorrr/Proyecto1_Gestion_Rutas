import sqlite3, json
import networkx as nx
from networkx.algorithms import approximation as approx
from functions import asignar_pedidos_a_camiones, haversine, costes_ruta, ingresos_camion, random_pedidos, inicializar_log, combinar_camiones

############################## MAIN ##############################
# Inicializar el log (borra contenido previo del archivo de log)
inicializar_log()

# Conexión a la base de datos SQLite
conn = sqlite3.connect(r"Joan\Database\logistics.db")
cursor = conn.cursor()

# Configuración inicial
velocidad_media_camiones = 100  # Velocidad promedio de los camiones en km/h
capacidad_camion = 2000  # Capacidad máxima de un camión en unidades de carga
coste_medio_km = 0.6  # Coste promedio por kilómetro recorrido (€)

# Generar pedidos aleatorios para simular datos iniciales
result, msg = random_pedidos(conn, cursor)
if not result:
    print(f"Error: {msg}")  # Mostrar mensaje de error si falla la generación de pedidos
    quit()

# Obtener pedidos agrupados por producto y destino
pedidos = cursor.execute("""
    SELECT
        ped.id_pedido,
        ped.id_producto, 
        prod.nombre_producto, 
        ped.destino,
        dest.provincia,
        COUNT(ped.id_pedido) AS total_pedidos, 
        SUM(ped.cantidad) AS total_cantidad
    FROM pedidos ped
    JOIN productos prod ON ped.id_producto = prod.id_producto
    JOIN destinos dest ON ped.destino = dest.latitud || ', ' || dest.longitud
    GROUP BY ped.id_producto, ped.destino
    ORDER BY ped.id_producto, ped.destino
""").fetchall()

# Asignar los pedidos a camiones respetando la capacidad
camiones_asignados = asignar_pedidos_a_camiones(pedidos, capacidad_camion)

# Combinar camiones para optimizar el uso de la capacidad
camiones_optimizados = combinar_camiones(camiones_asignados, capacidad_camion)
# Ordenar los camiones por su identificador para facilitar la lectura
camiones_optimizados = sorted(camiones_optimizados, key=lambda camion: camion.id_camion)

# Lista para almacenar la información final de cada camión
camiones_info = []

# Optimizar las rutas para cada camión
for camion in camiones_optimizados:
    # Agregar siempre el punto inicial y final como "Mataró"
    destinos_finales = {"Mataró": "41.532521,2.423604"}  # Coordenadas de Mataró
    destinos_finales.update(camion.destinos)  # Añadir destinos de los pedidos al camión
    camion.destinos = destinos_finales

    G = nx.Graph()  # Crear un grafo para representar la red de destinos

    # Añadir nodos al grafo, uno por cada destino
    for destino, coordenadas in camion.destinos.items():
        lat, lon = coordenadas.strip().split(',')  # Separar las coordenadas en latitud y longitud
        G.add_node(destino, pos=(lat, lon))

    # Añadir aristas con peso entre cada par de nodos basado en la distancia (Haversine)
    for destino1, coordenadas1 in camion.destinos.items():
        for destino2, coordenadas2 in camion.destinos.items():
            if destino1 != destino2:
                lat1, lon1 = coordenadas1.strip().split(',')
                lat2, lon2 = coordenadas2.strip().split(',')

                distancia = haversine(float(lat1), float(lon1), float(lat2), float(lon2))
                coste_total = distancia * coste_medio_km  # Calcular coste en base a la distancia
                G.add_edge(destino1, destino2, weight=coste_total)

    # Usar el algoritmo TSP para encontrar la ruta óptima cerrada (vuelta completa)
    ruta_optima_cerrada = approx.traveling_salesman_problem(G, cycle=True, weight='weight')

    # Convertir la ruta óptima a un formato amigable para JSON
    ruta_optima_final = []
    for destino in ruta_optima_cerrada:
        ruta_optima_final.append({
            "nombre": destino,
            "lat": camion.destinos[destino].strip().split(',')[0],
            "lon": camion.destinos[destino].strip().split(',')[1]
        })

    # Calcular costes acumulados (distancia, coste y tiempo) para la ruta
    distancia_total, coste_total, temps_total = costes_ruta(ruta_optima_cerrada, G, coste_medio_km, velocidad_media_camiones)

    # Calcular ingresos del camión basados en los pedidos que transporta
    ingreso_total = ingresos_camion(cursor, camion)
    # Calcular beneficios del camión
    beneficios = ingreso_total - coste_total

    # Preparar la información del camión para el archivo JSON
    camion_info = {
        "id_camion": camion.id_camion,
        "pedidos": [
            {
                "id_pedido": id_pedido,
                "nombre_producto": nombre_producto,
                "cantidad": cantidad,
                "destino": destino
            }
            for id_pedido, nombre_producto, cantidad, destino in camion.pedidos
        ],
        "ruta_optima": ruta_optima_final,
        "distancia_total": round(distancia_total, 2),
        "tiempo_total_horas": round(temps_total, 2),
        "coste_total": round(coste_total, 2),
        "ingresos": round(ingreso_total, 2),
        "beneficio": round(beneficios, 2)
    }

    # Añadir información del camión a la lista general
    camiones_info.append(camion_info)

# Guardar la información generada en un archivo JSON
with open("Joan\Results\camiones_info.json", "w", encoding="utf-8") as f:
    json.dump(camiones_info, f, indent=4, ensure_ascii=False)