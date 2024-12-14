import folium
import requests
import polyline  # Librería para decodificar polylines de Google Maps

# Tu clave de API de Google Maps
api_key = "AIzaSyBCvUkuzXOcZOQk2sNjimAzaehZaLLabik"


def generar_mapa_con_ruta(destinos):
    # Coordenadas de las paradas: origen, puntos intermedios y destino
    paradas = [
    {
        "lat": float(loc["lat"]),
        "lng": float(loc["lon"]),
        "nombre": loc["nombre"]
    }
    for loc in destinos
    ]

    paradas.reverse()
    paradas.pop()

    # Construir la URL para la API de Directions
    waypoints = "|".join([f"{loc['lat']},{loc['lng']}" for loc in paradas[1:-1]])  # Puntos intermedios
    origin = f"{paradas[0]['lat']},{paradas[0]['lng']}"  # Origen
    destination = f"{paradas[-1]['lat']},{paradas[-1]['lng']}"  # Destino

    url = (
        f"https://maps.googleapis.com/maps/api/directions/json?"
        f"origin={origin}&destination={destination}&"
        f"waypoints={waypoints}&mode=driving&key={api_key}"
    )

    # Obtener la respuesta de la API
    response = requests.get(url)
    data = response.json()

    # Verificar que la solicitud fue exitosa
    if data["status"] == "OK":
        # Extraer la polyline de la ruta
        steps = data["routes"][0]["legs"]
        ruta_coordenadas = []
        for leg in steps:
            for step in leg["steps"]:
                points = step["polyline"]["points"]
                # Decodificar polyline usando la librería polyline
                ruta_coordenadas.extend(polyline.decode(points))
    else:
        print("Error en la solicitud a la API de Directions:", data["status"])
        exit()

    # Construir la URL para la API de Directions para la vuelta
    url_vuelta = (
        f"https://maps.googleapis.com/maps/api/directions/json?"
        f"origin={destination}&destination={origin}&mode=driving&key={api_key}"
    )

    # Obtener la respuesta de la API para la vuelta
    response_vuelta = requests.get(url_vuelta)
    data_vuelta = response_vuelta.json()

    if data_vuelta["status"] == "OK":
        # Extraer la polyline de la ruta de vuelta
        steps_vuelta = data_vuelta["routes"][0]["legs"]
        ruta_vuelta_coordenadas = []
        for leg in steps_vuelta:
            for step in leg["steps"]:
                points = step["polyline"]["points"]
                # Decodificar polyline usando la librería polyline
                ruta_vuelta_coordenadas.extend(polyline.decode(points))
    else:
        print("Error en la solicitud de la API de Directions para la vuelta:", data_vuelta["status"])
        exit()


    # Crear un mapa interactivo centrado en el origen (solo lat y lon, sin el nombre)
    mapa = folium.Map(location=[40.4168, -3.7038], zoom_start=6, control_scale=True)
    # Agregar capa de Google Maps
    folium.TileLayer(
        tiles=f"https://mt1.google.com/vt/lyrs=m&x={{x}}&y={{y}}&z={{z}}&key={api_key}",
        attr="Google Maps",
        name="Google Maps",
        overlay=True,
        control=True
    ).add_to(mapa)

    # Agregar marcadores para las paradas
    for i, parada in enumerate(paradas):
        lat = float(parada["lat"])  # Convertir lat y lng a float
        lng = float(parada["lng"])  # Convertir lat y lng a float
        nombre = parada["nombre"]
        color = "green" if i == 0 else "red" if i == len(paradas) - 1 else "blue"
        folium.Marker([lat, lng], tooltip=nombre, icon=folium.Icon(color=color)).add_to(mapa)


    # Dibujar la ruta en el mapa
    folium.PolyLine(ruta_coordenadas, color="blue", weight=7, opacity=0.7).add_to(mapa)

    # Dibujar la ruta de vuelta en el mapa con color rojo
    folium.PolyLine(ruta_vuelta_coordenadas, color="red", weight=2, opacity=0.7).add_to(mapa)

    # Agregar opciones de control de capas
    folium.LayerControl().add_to(mapa)

    # Guardar el mapa en un archivo HTML
    archivo_html = "mapa_con_ruta_google_directions.html"
    mapa.save(archivo_html)
    return archivo_html
