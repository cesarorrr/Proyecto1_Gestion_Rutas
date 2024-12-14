Optimización de Pedidos - Proyecto Logístico
============================================
Este proyecto tiene como objetivo optimizar el transporte de pedidos mediante la asignación de estos a camiones, la optimización de rutas y la estimación de costes y beneficios asociados. El sistema permite la lectura de datos de pedidos desde un archivo CSV proporcionado por el usuario o generarlos aleatoriamente desde una base de datos. A continuación, se optimiza la ruta de cada camión utilizando el algoritmo de Traveling Salesman Problem (TSP) y se calcula la rentabilidad de cada ruta.

# Tabla de Contenidos
1. Descripción del Proyecto
2. Requisitos
3. Instalación
4. Uso
5. Resultados
6. Estructura del Proyecto
7. Funciones Principales

# Descripción del Proyecto
El objetivo principal de este proyecto es optimizar la asignación de pedidos a camiones en función de su capacidad y la distancia a recorrer, minimizando costes y maximizando los beneficios.

## Características principales:

- Asignación de pedidos a camiones según la capacidad máxima.
- Optimización de rutas utilizando el algoritmo TSP.
- Cálculo de costes totales de transporte basados en distancia y tiempo.
- Generación de un informe con la información de los camiones, incluyendo la ruta óptima, distancia, coste, ingresos y beneficios.

# Requisitos
El proyecto requiere las siguientes dependencias:

- pandas: Para la manipulación de datos tabulares.
- numpy: Para cálculos numéricos.
- sqlite3: Para interactuar con la base de datos SQLite.
- networkx: Para la manipulación de grafos y optimización de rutas.
- haversine: Para calcular distancias geográficas entre coordenadas.
- json: Para exportar resultados en formato JSON.

# Instalación
**1. Clona el repositorio**
```bash
git clone https://github.com/tu-usuario/optimizacion-pedidos.git
cd optimizacion-pedidos
```
**2. Instala las dependencias**
```bash
pip install -r requirements.txt
```

# Uso
1. Preparar el archivo CSV (opcional)
Si tienes un archivo CSV con datos de pedidos, debe tener la siguiente estructura:

```csv
id_pedido,id_producto,nombre_producto,destino,provincia,total_cantidad
6009659,1,Leche entera 500ml,"40.365727, -1.157177",Teruel,668
1598453,1,Leche entera 500ml,"41.788533, -6.779713",Braganza,554
...
```
*id_producto*, *nombre_producto*, *destino* y *provincia* deben encontrarse dentro de los cvs correspondientes en la carpeta /data.

2. Ejecutar el script
Para ejecutar el sistema de optimización de pedidos, solo necesitas ejecutar el archivo main.py situado en la raiz principal.
```python
import subprocess

def run_app():
    # Usar subprocess para ejecutar streamlit
    subprocess.run(["streamlit", "run", "src/modules/ui.py"])

if __name__ == "__main__":
    run_app()
```

# Resultados
La salida de la función será un JSON con la información de cada camión, incluyendo:

ID del camión
- Listado de pedidos asignados
- Ruta óptima
- Distancia total recorrida
- Tiempo total estimado
- Coste total
- Ingresos y beneficios

# Estructura del Proyecto
```plaintext
|   ejemplo_input.csv
|   README.md
|   requirements.txt
|
+---.vscode
|       launch.json
|
+---data
|       clientes.csv
|       destinos.csv
|       pedidos.csv
|       productos.csv
|
+---db
|       database.ipynb
|       logistics.db
|
+---docs
|       P1 Enunciado Alumnos.pdf
|
+---img
|       icono.jpg
|
+---logs
|       log.txt
|
+---results
|       camiones_info.json
|
\---src
    |   main.py
    |
    \---modules
            clases.py
            functions.py
            main_function.py
            mapa.py
            ui.py
```

# Funciones Principales
### optimizacion_pedidos
La función principal que optimiza el transporte de pedidos. Asigna pedidos a camiones, calcula las rutas óptimas, y genera un informe con los resultados.

## Funciones auxiliares:
- inicializar_log(): Inicializa el sistema de logs.
- csv_to_pedidos(): Convierte filas de un CSV en pedidos procesados.
- random_pedidos(): Genera pedidos aleatorios si no se proporciona un CSV.
- asignar_pedidos_a_camiones(): Asigna pedidos a camiones respetando la capacidad.
- combinar_camiones(): Combina camiones para optimizar su capacidad.
- haversine(): Calcula la distancia geográfica entre dos puntos.
- costes_ruta(): Calcula los costes totales de una ruta.
- ingresos_camion(): Calcula los ingresos generados por un camión.
