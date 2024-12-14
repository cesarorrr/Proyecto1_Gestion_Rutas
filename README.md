Optimización de Pedidos - Proyecto Logístico
============================================
Este proyecto tiene como objetivo optimizar el transporte de pedidos mediante la asignación de estos a camiones, la optimización de rutas y la estimación de costes y beneficios asociados. El sistema permite la lectura de datos de pedidos desde un archivo CSV proporcionado por el usuario o generarlos aleatoriamente desde una base de datos. A continuación, se optimiza la ruta de cada camión utilizando el algoritmo de Traveling Salesman Problem (TSP) y se calcula la rentabilidad de cada ruta.

Tabla de Contenidos
Descripción del Proyecto
Requisitos
Instalación
Uso
Estructura del Proyecto
Funciones Principales
Licencia
Descripción del Proyecto
El objetivo principal de este proyecto es optimizar la asignación de pedidos a camiones en función de su capacidad y la distancia a recorrer, minimizando costes y maximizando los beneficios.

Características principales:

Asignación de pedidos a camiones según la capacidad máxima.
Optimización de rutas utilizando el algoritmo TSP.
Cálculo de costes totales de transporte basados en distancia y tiempo.
Generación de un informe con la información de los camiones, incluyendo la ruta óptima, distancia, coste, ingresos y beneficios.
Requisitos
El proyecto requiere las siguientes dependencias:

pandas: Para la manipulación de datos tabulares.
numpy: Para cálculos numéricos.
sqlite3: Para interactuar con la base de datos SQLite.
networkx: Para la manipulación de grafos y optimización de rutas.
haversine: Para calcular distancias geográficas entre coordenadas.
json: Para exportar resultados en formato JSON.
Instalación
1. Clona el repositorio
bash
Copia el codi
git clone https://github.com/tu-usuario/optimizacion-pedidos.git
cd optimizacion-pedidos
2. Crea un entorno virtual
Si usas venv (recomendado):

bash
Copia el codi
python -m venv venv
source venv/bin/activate  # En Windows usa 'venv\Scripts\activate'
3. Instala las dependencias
bash
Copia el codi
pip install -r requirements.txt
Uso
1. Preparar el archivo CSV (opcional)
Si tienes un archivo CSV con datos de pedidos, debe tener la siguiente estructura:

csv
Copia el codi
id_pedido,id_producto,cantidad,destino
1,101,50,Barcelona
2,102,30,Madrid
...
2. Ejecutar el script
Para ejecutar el sistema de optimización de pedidos, solo necesitas llamar a la función optimizacion_pedidos desde tu archivo Python o interactuar con la base de datos directamente.

python
Copia el codi
import pandas as pd
from optimizacion import optimizacion_pedidos

# Leer un archivo CSV si lo tienes
csv_data = pd.read_csv('pedidos.csv')

# Llamar a la función de optimización
resultados = optimizacion_pedidos(
    velocidad_media_camiones=80.0,
    capacidad_camion=100,
    coste_medio_km=0.5,
    csv=csv_data
)

# Imprimir el resultado (en formato JSON)
print(resultados)
Si no proporcionas un archivo CSV, los pedidos se generarán aleatoriamente desde la base de datos.

3. Resultados
La salida de la función será un JSON con la información de cada camión, incluyendo:

ID del camión
Listado de pedidos asignados
Ruta óptima
Distancia total recorrida
Tiempo total estimado
Coste total
Ingresos y beneficios
Estructura del Proyecto
plaintext
Copia el codi
|   ejemplo_input.csv        # Archivo de entrada de ejemplo
|   README.md                # Este archivo
|   requirements.txt         # Dependencias del proyecto
|
+---src                     # Código fuente principal del proyecto
|   |   optimizacion.py     # Funciones principales para optimización
|   |   ui.py               # Interfaz de usuario (si aplica)
|
+---data                    # Archivos de datos relacionados con la entrada o procesamiento
|   |   clientes.csv        # Datos de clientes
|   |   destinos.csv        # Datos de destinos
|   |   pedidos.csv         # Datos de pedidos
|   |   productos.csv       # Datos de productos
|
+---db                      # Base de datos y notebooks relacionados
|   |   database.ipynb      # Notebook para manipulación de la base de datos
|   |   logistics.db        # Archivo de la base de datos SQLite
|
+---logs                    # Archivos de registro
|   |   log.txt             # Registro de errores o eventos
|
+---results                 # Resultados generados por el programa
|   |   camiones_info.json  # Archivo JSON con información generada
|
+---docs                    # Documentación adicional (opcional)
|   |   P1 Enunciado Alumnos.pdf
Funciones Principales
optimizacion_pedidos
La función principal que optimiza el transporte de pedidos. Asigna pedidos a camiones, calcula las rutas óptimas, y genera un informe con los resultados.

Funciones auxiliares:
inicializar_log(): Inicializa el sistema de logs.
csv_to_pedidos(): Convierte filas de un CSV en pedidos procesados.
random_pedidos(): Genera pedidos aleatorios si no se proporciona un CSV.
asignar_pedidos_a_camiones(): Asigna pedidos a camiones respetando la capacidad.
combinar_camiones(): Combina camiones para optimizar su capacidad.
haversine(): Calcula la distancia geográfica entre dos puntos.
costes_ruta(): Calcula los costes totales de una ruta.
ingresos_camion(): Calcula los ingresos generados por un camión.