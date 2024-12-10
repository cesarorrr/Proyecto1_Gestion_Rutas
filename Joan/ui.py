import streamlit as st
import pandas as pd
from mapa import generar_mapa_con_ruta
from Data.mina_for_ui import optimizacion_pedidos
import json

st.set_page_config(
    page_title="Gestión de Rutas",
    page_icon="🚚",
)

if "state" not in st.session_state:
    st.session_state.state = "initial"
if "truck_selected" not in st.session_state:
    st.session_state.truck_selected = None  # Start with None to indicate no truck is selected


def change_state(new_state):
    st.session_state.state = new_state
    st.rerun()

if st.session_state.state == "initial":
        # Mejorar la UI con estilos CSS
        st.markdown("""
            <style>
            /* Estilo general para el formulario */
            .form-container {
                max-width: 900px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f7f7f7;
                border-radius: 10px;
                box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
            }

            /* Estilo de los inputs */
            .stTextInput, .stNumberInput {
                margin-bottom: 20px;
                font-size: 16px;
            }

            .stTextInput input, .stNumberInput input {
                border-radius: 5px;
                padding: 10px;
                border: 1px solid #ddd;
                transition: border-color 0.3s;
            }

            .stTextInput input:focus, .stNumberInput input:focus {
                border-color: #007bff;
                outline: none;
            }

            /* Estilo para los botones */
            .stButton>button {
                font-size: 16px;
                background-color: #007bff;
                color: white;
                border: none;
                padding: 12px 25px;
                border-radius: 5px;
                cursor: pointer;
                transition: background-color 0.3s, transform 0.3s;
                width: 100%;
            }

            .stButton>button:hover {
                background-color: #0056b3;
                transform: scale(1.05);
            }

            .stButton>button:active {
                background-color: #003366;
            }

            /* Estilo para el archivo CSV */
            .stFileUploader {
                margin-bottom: 20px;
            }

            /* Estilo para los mensajes de error */
            .stError {
                background-color: #f8d7da;
                color: #721c24;
                border-left: 5px solid #f5c6cb;
                padding: 10px;
                margin-top: 20px;
            }

            /* Estilo para los mensajes de éxito */
            .stSuccess {
                background-color: #d4edda;
                color: #155724;
                border-left: 5px solid #c3e6cb;
                padding: 10px;
                margin-top: 20px;
            }
            </style>
        """, unsafe_allow_html=True)

        # Título del formulario
        st.title("Gestión de Rutas de Entrega")

        # Imagen al inicio
        #st.image("img/logo.webp", use_column_width=True)

        # Contenedor principal con el estilo mejorado
        with st.container():

            # Crear columnas para los inputs
            col1, col2, col3 = st.columns(3)

            with col1:
                Velocity = st.number_input("Velocidad Media Camión (km/h)", min_value=1, step=1, key="velocity")

            with col2:
                Capacity = st.number_input("Capacidad Camión (cantidad)", min_value=1, step=1, key="capacity")

            with col3:
                Price = st.number_input("Coste por Kilómetro (€)", min_value=0, step=1, key="price_km")

            # Subir archivo CSV
            csv = st.file_uploader("Subir archivo CSV", type=["csv"], key="csv")

            if csv is not None:
                try:
                    data = pd.read_csv(csv,sep=",")
                      # Eliminar espacios extra en los nombres de las columnas
                    data.columns = data.columns.str.strip()  # Elimina los espacios extra en los nombres de las columnas
                    # Definir las columnas requeridas
                    required_columns = ["id_pedido", "id_producto", "nombre_producto","destino","provincia","total_cantidad"]  # Reemplaza con los nombres de las columnas que necesitas
                    # Verificar si el CSV contiene las columnas requeridas
                    if all(col in data.columns for col in required_columns):
                        st.success("¡Archivo CSV cargado exitosamente!")
                        st.dataframe(data)  # Mostrar el contenido del CSV
                    else:
                        missing_columns = [col for col in required_columns if col not in data.columns]
                        st.error(f"El archivo CSV no contiene las siguientes columnas: {', '.join(missing_columns)}")
                except Exception as e:
                    st.error(f"Error al leer el archivo: {e}")

            # Botón de Procesar
            st.markdown('<div style="margin-top: 20px;">', unsafe_allow_html=True)
            if st.button("Procesar", use_container_width=True):
                # Validar que todos los campos estén completos
                if Velocity and Capacity and Price:
                    # Enviar datos de las variables al modelo

                    # En caso de subir csv trabajar en el modelo con el csv sino con los datos de la bbdd
                    if csv and all(col in data.columns for col in required_columns):
                        print(data)  # Procesar el archivo CSV
                        resultado = optimizacion_pedidos(Velocity, Capacity, Price, data)  # Aquí pasas los datos al modelo

                    else:
                        resultado = optimizacion_pedidos(Velocity, Capacity, Price, None)  # Usar datos predeterminados

                    camiones_array = json.loads(resultado)
                    st.session_state.camiones_array = camiones_array

                    # Cambio de escena para mostrar el resultado
                    change_state("deliveries")

                else:
                    st.warning("Por favor, completa todos los campos antes de continuar.")
            st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.state == "deliveries":

    # RECUPERAR CAMIONES ARRAY
    camiones_array = st.session_state.camiones_array

    if st.button("⬅️",key="back_to_initial"):
        change_state("initial")

    st.title("Camiones Totales: "+str(len(camiones_array)))
    
    for i,camion in enumerate(camiones_array):
        if st.button("Camion "+(str(camion["id_camion"])), use_container_width=True,key=f"button_{i}_{camion['id_camion']}"):
            st.session_state.truck_selected = camion
            generar_mapa_con_ruta(camion['ruta_optima'])
            change_state("truck")

    
elif st.session_state.state == "truck":
    if 'truck_selected' in st.session_state:
        camion = st.session_state.truck_selected
        if st.button("⬅️",key="back_to_deliveries"):
            change_state("deliveries")
            # Centrar todo el contenido
        st.markdown("<style> .main {display: flex; justify-content: center;} </style>", unsafe_allow_html=True)

        # Título del camión
        st.title(f"Camión {camion['id_camion']}")

        # Contenedor principal para organizar el diseño
        with st.container():
            # Información sobre los pedidos
            st.subheader("Pedidos")
            for pedido in camion["pedidos"]:
                with st.expander(f"Pedido ID {pedido['id_pedido']} - {pedido['nombre_producto']}"):
                    st.markdown(f"**Producto:** {pedido['nombre_producto']}")
                    st.markdown(f"**Cantidad:** {pedido['cantidad']}")
                    st.markdown(f"**Destino:** {pedido['destino']}")
                    st.markdown("---")
            
            # Información sobre la ruta óptima
            st.subheader("Ruta Óptima")
            for loc in reversed(camion["ruta_optima"]):
                with st.expander(f"Ciudad: {loc['nombre']}"):
                    st.markdown(f"**Latitud:** {loc['lat']}")
                    st.markdown(f"**Longitud:** {loc['lon'].strip()}")
                    st.markdown("---")

            # Información sobre el camión
            st.subheader("Información del Camión")
            # Distribute the truck info in columns for a better layout
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**Distancia Total:** {camion['distancia_total']} km")
                st.markdown(f"**Tiempo Total:** {camion['tiempo_total_horas']} horas")
                
            with col2:
                st.markdown(f"**Coste Total:** {camion['coste_total']} €")
                st.markdown(f"**Ingresos:** {camion['ingresos']} €")
                st.markdown(f"**Beneficio:** {camion['beneficio']} €")
            
            # Muestra el mapa en un contenedor centrado
            st.subheader("Mapa de la Ruta")
            with st.container():
                # Lee el contenido del archivo HTML
                with open("mapa_con_ruta_google_directions.html", 'r', encoding='utf-8') as file:
                    html_content = file.read()

                # Muestra el contenido HTML en un contenedor en Streamlit
                st.components.v1.html(html_content, height=600)
    else:
        st.error("No se ha seleccionado ningún camión.")
