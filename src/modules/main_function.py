import sqlite3, json
import networkx as nx
import pandas as pd
from networkx.algorithms import approximation as approx
from functions import asignar_pedidos_a_camiones, haversine, costes_ruta, ingresos_camion, random_pedidos, inicializar_log, combinar_camiones, csv_to_pedidos

def optimizacion_pedidos(velocidad_media_camiones: float, capacidad_camion: int, coste_medio_km: float, csv: 'pd.Dataframe') -> json:

    """
    Optimiza el transporte de pedidos asignándolos a camiones, calculando rutas y beneficios.

    Esta función recibe datos de pedidos ya sea desde un archivo CSV proporcionado o generados aleatoriamente,
    los agrupa respetando la capacidad de los camiones, optimiza las rutas de entrega utilizando el algoritmo
    de TSP (Problema del Viajante) y calcula los costes, tiempos e ingresos asociados.

    ### Parámetros:
    - **velocidad_media_camiones** (`float`): 
      Velocidad promedio a la que viajan los camiones (en km/h).

    - **capacidad_camion** (`int`): 
      Capacidad máxima de carga que puede llevar cada camión (en unidades).

    - **coste_medio_km** (`float`): 
      Coste promedio en euros por kilómetro recorrido.

    - **csv** (`pd.DataFrame`): 
      Datos de pedidos proporcionados por el usuario en formato DataFrame. 
      Si es `None` o está vacío, se generan datos de pedidos aleatorios desde la base de datos.

    ### Retorno:
    - `str`: Un JSON con los resultados de la optimización, incluyendo:
      - Información de los pedidos asignados a cada camión.
      - Ruta óptima para cada camión.
      - Distancia total recorrida, tiempo estimado, costes, ingresos y beneficios.

    ### Salida JSON:
    Ejemplo de estructura de salida:
    ```json
    [
        {
            "id_camion": 1,
            "pedidos": [
                {
                    "id_pedido": 1,
                    "nombre_producto": "Producto A",
                    "cantidad": 50,
                    "destino": "Barcelona"
                },
                ...
            ],
            "ruta_optima": [
                {"nombre": "Mataró", "lat": "41.532521", "lon": "2.423604"},
                {"nombre": "Destino A", "lat": "41.12345", "lon": "2.56789"},
                ...
            ],
            "distancia_total": 350.45,
            "tiempo_total_horas": 5.84,
            "coste_total": 123.50,
            "ingresos": 200.00,
            "beneficio": 76.50
        },
        ...
    ]
    ```

    ### Flujo del Programa:
    1. **Inicialización de Logs**: Se inicializa el sistema de logs borrando cualquier contenido previo.
    2. **Entrada de Datos**: 
        - Si se proporciona un archivo CSV con datos de pedidos, este se procesa.
        - Si no, se generan pedidos aleatorios desde la base de datos.
    3. **Asignación de Pedidos**: Los pedidos se agrupan por destino y producto, respetando la capacidad máxima de los camiones.
    4. **Optimización de Rutas**: 
        - Cada camión recibe una ruta optimizada calculada con el algoritmo TSP (Traveling Salesman Problem).
        - Se usa la distancia entre destinos calculada mediante la fórmula Haversine.
    5. **Cálculo de Costes e Ingresos**: Se determinan los costes de transporte, el tiempo necesario, los ingresos por pedidos y el beneficio neto.
    6. **Salida JSON**: Los resultados se devuelven en formato JSON.

    ### Detalles Técnicos:
    - **Uso de Redes**:
        - Se utiliza `networkx.Graph` para modelar los destinos y distancias.
        - Se calcula la ruta óptima con el algoritmo `traveling_salesman_problem`.
    - **Base de Datos**: 
        - Los datos de productos, destinos y pedidos provienen de una base de datos SQLite.
        - Los pedidos se agrupan y suman para optimizar la asignación.
    - **Optimización de Camiones**:
        - Los pedidos se asignan inicialmente a camiones según su capacidad.
        - Se optimiza el uso de camiones combinando aquellos con capacidad sobrante.

    ### Librerías Utilizadas:
    - `pandas`: Para manipular datos tabulares.
    - `sqlite3`: Para interactuar con la base de datos SQLite.
    - `networkx`: Para modelar y resolver problemas de rutas.
    - `json`: Para la exportación de los resultados en formato JSON.
    - Funciones auxiliares definidas en el proyecto:
        - `inicializar_log()`: Inicializa el archivo de log.
        - `csv_to_pedidos()`: Convierte las filas del DataFrame en objetos pedidos.
        - `random_pedidos()`: Genera datos de pedidos aleatorios.
        - `asignar_pedidos_a_camiones()`: Asigna pedidos a camiones.
        - `combinar_camiones()`: Combina camiones para optimizar su capacidad.
        - `haversine()`: Calcula la distancia entre dos puntos geográficos.
        - `costes_ruta()`: Calcula costes totales (distancia, tiempo, coste monetario).
        - `ingresos_camion()`: Calcula ingresos generados por los pedidos transportados por un camión.
    """
        
    # Inicializar el log (borra contenido previo del archivo de log)
    inicializar_log()

    # Conexión a la base de datos SQLite
    conn = sqlite3.connect(r"Joan\Database\logistics.db")
    cursor = conn.cursor()

    # SI EL USUARIO HA SUBIDO UN CSV LEER LA INFORMACIÓN
    if csv is not None and not csv.empty:
        pedidos_list = []

        # Aplicar csv_to_pedidos a cada fila del DataFrame
        csv.apply(lambda fila: csv_to_pedidos(pedidos_list, fila), axis=1)
       
        # Convertir a tuple al final si es necesario
        pedidos = tuple(pedidos_list)

    # SI NO HA SUBIDO NADA, SE GENERAN PEDIDOS RANDOM
    else:
        
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

        # cursor.close()
        # conn.close()

    return json.dumps(camiones_info, indent=4, ensure_ascii=False)