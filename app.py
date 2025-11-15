import paho.mqtt.client as paho
import time
import json
import streamlit as st
import numpy as np
from PIL import Image
from keras.models import load_model

# --- Configuración MQTT ---
broker="broker.hivemq.com"
port=1883
# Tópicos
TOPIC_GESTURE = "IMIA" # Control de Acceso (Página 1)
TOPIC_ALARM = "Vigilancia/Alarma" # Control de Alarma/Buzzer (Página 2)
TOPIC_STATUS_LED = "Vigilancia/LED" # Control de LED (Página 2)


# --- Funciones de MQTT ---
def on_publish(client, userdata, result):
    # print("El dato ha sido publicado")
    pass

def on_message(client, userdata, message):
    # Esta función se llama si recibimos mensajes (por ejemplo, logs o temperatura)
    try:
        payload = str(message.payload.decode("utf-8"))
        # Usamos un bloqueo para evitar que el log se actualice continuamente
        # y cause un re-run infinito. Streamlit no maneja muy bien los logs asíncronos.
        if 'mqtt_log' in st.session_state:
             st.session_state.mqtt_log += f"\n> Recibido: {payload}"
    except Exception as e:
        if 'mqtt_log' in st.session_state:
            st.session_state.mqtt_log += f"\n> Error al decodificar: {e}"

# Inicialización de Cliente y Conexión (Usando Session State para persistencia)
if 'mqtt_log' not in st.session_state:
    st.session_state.mqtt_log = "Registro de Eventos: Listado para la noche de caza..."
    st.session_state.mqtt_status = "Conexión MQTT: Pendiente"
    st.session_state.client1 = None # Inicializa el cliente a None

if st.session_state.client1 is None:
    try:
        client1 = paho.Client("APP_CERR")
        client1.on_message = on_message
        client1.on_publish = on_publish
        client1.connect(broker, port)
        client1.subscribe("Vigilancia/Log") # Tópico para logs/temperatura del ESP32
        client1.loop_start()
        
        # Guarda el cliente conectado en el Session State
        st.session_state.client1 = client1 
        st.session_state.mqtt_status = "Conexión MQTT: Establecida"
    except Exception as e:
        # Si la conexión falla, client1 permanece en None
        st.session_state.mqtt_status = f"Error al conectar MQTT: {e}"


# --- Estética y Tema Bloodborne (CSS Inyectado) ---
BLOODBORNE_CSS = """
<style>
/* 1. Fondo Oscuro y Textura */
body {
    background-color: #0b0b0d; /* Fondo muy oscuro */
    color: #bfa05d; /* Dorado/Amarillo pálido para el texto principal */
    font-family: 'Times New Roman', serif; /* Tipo de letra más antiguo/gótico */
}

/* 2. Títulos y Encabezados */
h1, h2, .st-emotion-cache-10trblm {
    color: #E6E1D6; /* Blanco sucio */
    text-shadow: 2px 2px 4px #000000;
    font-family: 'Georgia', serif;
    border-bottom: 1px solid #333333;
    padding-bottom: 5px;
}

/* 3. Contenedores y Cajas de Entrada (Look and Feel de Papel Viejo/Pergamino Oscuro) */
.st-emotion-cache-121p9e6, .st-emotion-cache-1wb9m6h, .st-emotion-cache-12w0qpk { 
    background-color: #2b2b2e; /* Contenedores oscuros */
    border: 1px solid #4a4a4a;
    border-radius: 8px;
    padding: 15px;
    box-shadow: 5px 5px 10px rgba(0, 0, 0, 0.5); /* Sombra oscura */
}

/* 4. Botones (Estilo Hierro/Metal Antiguo) */
.stButton>button {
    background-color: #3b3b40;
    color: #e0e0e0;
    border: 2px solid #6b6b6f;
    border-radius: 4px;
    padding: 10px 20px;
    font-weight: bold;
    transition: all 0.2s;
}
.stButton>button:hover {
    background-color: #4f4f54;
    color: #ffcc00; /* Efecto brillo al pasar el ratón */
    border-color: #ffcc00;
}

/* 5. Inputs (Cámara, Texto) */
.stCameraInput, .stTextInput > div > div > input {
    background-color: #1f1f21;
    color: #bfa05d;
    border: 1px solid #4a4a4a;
}

/* 6. Barra Lateral */
.st-emotion-cache-vk33v6 {
    background-color: #1a1a1c;
    color: #bfa05d;
}
.st-emotion-cache-1629p8f { /* Menú de navegación en la barra lateral */
    color: #E6E1D6; 
}

/* Ocultar botones de menú de Streamlit */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

</style>
"""
st.markdown(BLOODBORNE_CSS, unsafe_allow_html=True)


# --- Carga del Modelo de Keras (Modelo pre-entrenado) ---
@st.cache_resource
def load_keras_model():
    # Asume que 'keras_model.h5' está disponible en el entorno de ejecución
    return load_model('keras_model.h5')

model = load_keras_model()
data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)

# --- NAVEGACIÓN ---
PAGES = {
    "El Portal de Yharnam (Acceso)": "page_access",
    "La Linterna del Cazador (Defensa)": "page_defense"
}

st.sidebar.title("Diario de la Cacería")
selection = st.sidebar.radio("Selecciona un Pabellón:", list(PAGES.keys()))
page = PAGES[selection]

st.sidebar.text("")
st.sidebar.text(st.session_state.mqtt_status)


# --- PÁGINA 1: CONTROL DE ACCESO (MODO IMAGEN) ---
if page == "page_access":
    st.title("El Portal de Yharnam")
    st.subheader("La Puerta de Hierro: Un Velo entre Mundos")
    
    st.markdown("""
    <p style="font-style: italic; color: #888; font-size: 1.1em;">
    "Aquí, en la entrada de nuestro refugio, solo la señalización correcta puede otorgar el paso. Muestra tu juramento, Cazador, o permanece exiliado en la pesadilla."
    </p>
    """, unsafe_allow_html=True)

    img_file_buffer = st.camera_input("Revelar el Juramento (Toma una Foto)", key="camera_input")

    if img_file_buffer is not None:
        if st.session_state.client1 is None:
            st.error("No se puede enviar el comando: La conexión MQTT no está establecida.")
        else:
            try:
                # 1. Preprocesamiento de la imagen
                img = Image.open(img_file_buffer).convert('RGB')
                newsize = (224, 224)
                img = img.resize(newsize)
                img_array = np.array(img)
                normalized_image_array = (img_array.astype(np.float32) / 127.0) - 1
                data[0] = normalized_image_array

                # 2. Inferencia (Reconocimiento del Juramento/Gesto)
                prediction = model.predict(data, verbose=0)
                
                st.markdown(f"**Verificación de Sello (Predicción):** `[{prediction[0][0]:.2f}, {prediction[0][1]:.2f}]`")

                gesto_detectado = None

                if prediction[0][0] > 0.7: # Umbral alto para "Abre"
                    gesto_detectado = 'Abre'
                    st.header('🔑 Sello Aceptado: **El Portal se Abre**')
                    st.info("La cerradura cede al juramento. Entra antes de que la noche te consuma.")
                elif prediction[0][1] > 0.7: # Umbral alto para "Cierra"
                    gesto_detectado = 'Cierra'
                    st.header('🔒 Sello Impuesto: **El Portal se Cierra**')
                    st.warning("El velo se vuelve a tejer. El portal permanece sellado de la pesadilla.")
                else:
                    st.header('❌ Juramento Confuso')
                    st.error("El gesto no es claro. El portal permanece inmóvil.")


                # 3. Publicación MQTT
                if gesto_detectado:
                    payload = json.dumps({'gesto': gesto_detectado})
                    st.session_state.client1.publish(TOPIC_GESTURE, payload, qos=0, retain=False)
                    st.session_state.mqtt_log += f"\n[Acceso] -> Publicado: {gesto_detectado}"
                    time.sleep(0.5) # Pausa breve para que el ESP32 reciba y actúe

            except Exception as e:
                st.error(f"Error durante el procesamiento de la imagen: {e}")

# --- PÁGINA 2: ALERTA DE HOGAR (MODO TEXTO/CONTROLES) ---
elif page == "page_defense":
    st.title("La Linterna del Cazador")
    st.subheader("Vigilancia de la Mansión: El Ojo de la Noche")

    st.markdown("""
    <p style="font-style: italic; color: #888; font-size: 1.1em;">
    "Las alarmas silenciosas y las defensas del refugio pueden ser activadas desde aquí. La tranquilidad es un lujo, úsalo con prudencia."
    </p>
    """, unsafe_allow_html=True)
    
    # Comprobación de conexión antes de renderizar botones interactivos
    if st.session_state.client1 is None:
        st.error("La aplicación de vigilancia está inactiva. No se pueden enviar comandos hasta que se establezca la conexión MQTT.")
    else:
        # --- Interacción 1: Control de Luz (LED) ---
        st.markdown("### El Candelabro (Control de Estado - LED RGB)")
        
        col_led_rep, col_led_alert = st.columns(2)
        
        if col_led_rep.button("🕯️ Reposo (Verde)", key="btn_reposo"):
            st.session_state.client1.publish(TOPIC_STATUS_LED, "REPOSO", qos=0, retain=False)
            st.session_state.mqtt_log += "\n[LED] -> Publicado: REPOSO"
            st.success("Candelabro en modo Reposo. La vigilancia es sutil.")
        
        if col_led_alert.button("🚨 Alerta (Rojo)", key="btn_alerta"):
            st.session_state.client1.publish(TOPIC_STATUS_LED, "ALERTA", qos=0, retain=False)
            st.session_state.mqtt_log += "\n[LED] -> Publicado: ALERTA"
            st.warning("Candelabro en modo Alerta. ¡Algo se acerca!")

        # --- Interacción 2: Control de Defensa (Buzzer) ---
        st.markdown("### La Campana de Defensa (Alarma - Buzzer)")
        
        col_alarm_on, col_alarm_off = st.columns(2)
        
        if col_alarm_on.button("🔊 Activar Alarma", key="btn_buzzer_on"):
            st.session_state.client1.publish(TOPIC_ALARM, "HIGH", qos=0, retain=False)
            st.session_state.mqtt_log += "\n[Alarma] -> Publicado: HIGH"
            st.error("Alarma activada: El eco de la Campana resonará en la noche.")

        if col_alarm_off.button("🔇 Silenciar Campana", key="btn_buzzer_off"):
            st.session_state.client1.publish(TOPIC_ALARM, "LOW", qos=0, retain=False)
            st.session_state.mqtt_log += "\n[Alarma] -> Publicado: LOW"
            st.info("Campana silenciada. El silencio es nuestro aliado.")

        # --- Interacción 3: Comando de Voz/Texto (Modo de Entrada de Texto) ---
        st.markdown("### Comando Rápido (Entrada de Texto)")
        
        comando_texto = st.text_input("Ingresa un comando ('abrir' o 'cerrar'):", key="text_command")
        
        if st.button("Ejecutar Comando", key="btn_execute_text"):
            comando_limpio = comando_texto.strip().lower()
            if comando_limpio == 'abrir':
                payload = json.dumps({'gesto': 'Abre'})
                st.session_state.client1.publish(TOPIC_GESTURE, payload, qos=0, retain=False)
                st.session_state.mqtt_log += "\n[Texto] -> Publicado: Abre"
                st.success("Comando 'Abrir' enviado al Portal.")
            elif comando_limpio == 'cerrar':
                payload = json.dumps({'gesto': 'Cierra'})
                st.session_state.client1.publish(TOPIC_GESTURE, payload, qos=0, retain=False)
                st.session_state.mqtt_log += "\n[Texto] -> Publicado: Cierra"
                st.success("Comando 'Cerrar' enviado al Portal.")
            else:
                st.warning("Comando no reconocido. Usa 'abrir' o 'cerrar'.")


# --- Registro de Eventos (Se muestra en ambas páginas) ---
st.sidebar.markdown("---")
st.sidebar.markdown("### Pergamino de Eventos")
st.sidebar.text_area("Logs MQTT", st.session_state.mqtt_log, height=300)

# -----------------------------------------------------------
# --- CORRECCIÓN DEL ERROR ---
# -----------------------------------------------------------
# La llamada a loop_end() debe estar protegida para evitar el AttributeError
# si el cliente nunca se inicializó correctamente (por ejemplo, si falló el connect).
if st.session_state.client1 is not None:
    try:
        st.session_state.client1.loop_end()
    except Exception as e:
        # Esto puede ocurrir si el cliente ya estaba inactivo o desconectado de forma inesperada.
        # En Streamlit, a veces es mejor dejar que la aplicación se reinicie o manejar el error en los logs.
        pass
# -----------------------------------------------------------


