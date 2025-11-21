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
TOPIC_GESTURE = "IMIA" 
TOPIC_ALARM = "Vigilancia/Alarma" 
TOPIC_STATUS_LED = "Vigilancia/LED" 


# --- Funciones de MQTT ---
def on_publish(client, userdata, result):
    pass

def on_message(client, userdata, message):
    try:
        payload = str(message.payload.decode("utf-8"))
        if 'mqtt_log' in st.session_state:
              st.session_state.mqtt_log += f"\n📜 Recibido: {payload}" # Emojis de pergamino
    except Exception as e:
        if 'mqtt_log' in st.session_state:
            st.session_state.mqtt_log += f"\n💀 Error al decodificar: {e}" # Emoji de calavera

if 'mqtt_log' not in st.session_state:
    st.session_state.mqtt_log = "Registro de Eventos: Listado para la noche de caza... 🌑" # Luna
    st.session_state.mqtt_status = "Conexión MQTT: Pendiente 🕸️" # Telaraña
    st.session_state.client1 = None 

if st.session_state.client1 is None:
    try:
        client1 = paho.Client("APP_CERR")
        client1.on_message = on_message
        client1.on_publish = on_publish
        client1.connect(broker, port)
        client1.subscribe("Vigilancia/Log") 
        client1.loop_start()
        
        st.session_state.client1 = client1 
        st.session_state.mqtt_status = "Conexión MQTT: Establecida ✅" 
    except Exception as e:
        st.session_state.mqtt_status = f"Error al conectar MQTT: {e} ❌" 


# --- Estética y Tema Bloodborne (CSS Inyectado) ---
BLOODBORNE_CSS = """
<style>
/* Animación de latido para títulos */
@keyframes heartbeat {
    0% { transform: scale(1); }
    50% { transform: scale(1.01); }
    100% { transform: scale(1); }
}

/* Animación de resplandor sutil */
@keyframes subtle-glow {
    0% { box-shadow: 0 0 5px rgba(255, 196, 0, 0.2); }
    50% { box-shadow: 0 0 12px rgba(255, 196, 0, 0.4); }
    100% { box-shadow: 0 0 5px rgba(255, 196, 0, 0.2); }
}

/* Fondo Oscuro y Textura de Yharnam */
body {
    background-color: #0c0c0e; /* Fondo aún más oscuro */
    color: #c9c3b8; /* Dorado pálido/grisáceo para el texto principal */
    font-family: 'Times New Roman', serif; 
    overflow-x: hidden; /* Prevenir scroll horizontal */
}

/* Títulos y Encabezados */
h1, h2, h3, .st-emotion-cache-10trblm {
    color: #E6E1D6; 
    text-shadow: 2px 2px 6px rgba(0, 0, 0, 0.8);
    font-family: 'Georgia', serif;
    border-bottom: 2px solid #5a0000; /* Borde rojo oscuro */
    padding-bottom: 8px;
    margin-top: 25px;
    animation: heartbeat 2s infinite ease-in-out; /* Animación de latido */
}

/* Contenedores y Cajas de Entrada (Look and Feel de Piedra con tonos rojizos) */
.st-emotion-cache-121p9e6, .st-emotion-cache-1wb9m6h, .st-emotion-cache-12w0qpk, .stTextInput > div > div, .stTextArea { 
    background-color: #1a1a1c; /* Contenedor oscuro */
    border: 1px solid #700000; /* Borde rojo oscuro */
    border-radius: 6px;
    padding: 15px;
    box-shadow: 3px 3px 10px rgba(0, 0, 0, 0.8); 
    transition: all 0.3s ease-in-out;
}
.st-emotion-cache-121p9e6:hover, .st-emotion-cache-1wb9m6h:hover, .st-emotion-cache-12w0qpk:hover {
    border-color: #b30000; /* Rojo más intenso al pasar el ratón */
    box-shadow: 3px 3px 15px rgba(179, 0, 0, 0.4); /* Resplandor rojizo */
}

/* Texto de Citas/Información */
p, .st-b5 {
    color: #a39b8d; /* Sepia/Gris para texto secundario */
}
p { line-height: 1.6; } /* Espaciado para mejorar legibilidad */

/* Botones (Estilo Hierro Forjado con tintes de sangre) */
.stButton>button {
    background-color: #4d0000; /* Rojo oscuro como base */
    color: #E6E1D6;
    border: 3px outset #800000; 
    border-radius: 4px;
    padding: 10px 25px;
    font-weight: bold;
    letter-spacing: 1.5px;
    transition: all 0.3s ease-in-out;
    box-shadow: 0 5px 8px rgba(0, 0, 0, 0.6);
    cursor: pointer;
}
.stButton>button:hover {
    background-color: #7a0000; /* Rojo más intenso al hover */
    color: #ffde59; /* Dorado brillante */
    border-color: #ffde59;
    box-shadow: 0 0 15px rgba(255, 222, 89, 0.6), 0 0 25px rgba(179, 0, 0, 0.4); /* Doble resplandor */
    transform: translateY(-2px); /* Pequeño levantamiento */
}
.stButton>button:active {
    border: 3px inset #800000; 
    transform: translateY(0);
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.6);
}


/* Inputs (Cámara, Texto) */
.stCameraInput, .stTextInput > div > div > input {
    background-color: #121214; /* Fondo aún más oscuro para inputs */
    color: #bfa05d;
    border: 1px solid #700000; /* Borde rojo oscuro */
    border-radius: 4px;
    box-shadow: inset 1px 1px 3px rgba(0, 0, 0, 0.7);
    transition: border-color 0.3s ease-in-out;
}
.stCameraInput:hover, .stTextInput > div > div > input:hover {
    border-color: #b30000;
}


/* Barra Lateral */
.st-emotion-cache-vk33v6 {
    background-color: #0f0f10; /* Lateral más oscuro */
    color: #a39b8d;
    border-right: 1px solid #4d0000; /* Borde rojo oscuro */
    box-shadow: 5px 0 15px rgba(0, 0, 0, 0.7);
}
.st-emotion-cache-1629p8f { 
    color: #E6E1D6; 
    font-weight: bold;
}
.st-emotion-cache-1629p8f:hover {
    color: #ffde59;
}


/* Alerts (Advertencias/Éxito - más intensas) */
.stAlert {
    background-color: #1f1f21 !important;
    color: #d1c9bd !important;
    border: 1px solid #800000 !important; /* Borde rojo */
    border-left: 6px solid #b30000 !important; /* Barra lateral roja más gruesa */
    box-shadow: 0 0 10px rgba(179, 0, 0, 0.3) !important;
    animation: subtle-glow 3s infinite ease-in-out; /* Resplandor sutil */
}
.stAlert [role="img"] { 
    color: #ffde59 !important; /* Iconos dorados */
}
.stAlert.success {
    border-left-color: #4CAF50 !important; /* Verde para éxito, si se quiere menos terrorífico */
    box-shadow: 0 0 10px rgba(76, 175, 80, 0.3) !important;
}
.stAlert.warning {
    border-left-color: #FFC107 !important; /* Naranja para advertencia */
    box-shadow: 0 0 10px rgba(255, 193, 7, 0.3) !important;
}
.stAlert.error {
    border-left-color: #F44336 !important; /* Rojo fuerte para error */
    box-shadow: 0 0 15px rgba(244, 67, 54, 0.5) !important;
}


/* Ocultar botones de menú de Streamlit */
#MainMenu, footer, header {visibility: hidden;}

</style>
"""
st.markdown(BLOODBORNE_CSS, unsafe_allow_html=True)


# --- Carga del Modelo de Keras ---
@st.cache_resource
def load_keras_model():
    return load_model('keras_model.h5')

model = load_keras_model()
data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)

# --- NAVEGACIÓN ---
PAGES = {
    "👁️ El Portal de Yharnam (Acceso)": "page_access", # Ojo místico
    "🕯️ La Linterna del Cazador (Defensa)": "page_defense" # Vela/linterna
}

st.sidebar.title("Diario de la Cacería 📖") # Libro
selection = st.sidebar.radio("Selecciona un Pabellón: 🌌", list(PAGES.keys())) # Vía láctea/misterio
page = PAGES[selection]

st.sidebar.text("")
st.sidebar.text(st.session_state.mqtt_status)


# --- PÁGINA 1: CONTROL DE ACCESO ---
if page == "page_access":
    st.title("El Portal de Yharnam 🩸") # Gota de sangre
    st.subheader("La Puerta de Hierro: Un Velo entre Mundos 🗝️") # Llave
    
    st.markdown("""
    <p style="font-style: italic; color: #a39b8d; font-size: 1.1em;">
    "Aquí, en la entrada de nuestro refugio, solo la señalización correcta puede otorgar el paso. Muestra tu juramento, Cazador, o permanece exiliado en la pesadilla... 💀"
    </p>
    """, unsafe_allow_html=True)

    img_file_buffer = st.camera_input("Revelar el Juramento (Toma una Foto) 📸", key="camera_input")

    if img_file_buffer is not None:
        if st.session_state.client1 is None:
            st.error("No se puede enviar el comando: La conexión MQTT no está establecida. 🕸️")
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

                if prediction[0][0] > 0.7: 
                    gesto_detectado = 'Abre'
                    st.header('🔑 Sello Aceptado: **El Portal se Abre** 🚪') # Puerta abierta
                    st.info("La cerradura cede al juramento. Entra antes de que la noche te consuma... 🌕") # Luna llena
                elif prediction[0][1] > 0.7: 
                    gesto_detectado = 'Cierra'
                    st.header('🔒 Sello Impuesto: **El Portal se Cierra** 🌑') # Luna nueva
                    st.warning("El velo se vuelve a tejer. El portal permanece sellado de la pesadilla... ⛓️") # Cadenas
                else:
                    st.header('❌ Juramento Confuso ❓') # Interrogante
                    st.error("El gesto no es claro. El portal permanece inmóvil. Algo acecha... 👁️‍🗨️") # Ojo en burbuja


                # 3. Publicación MQTT
                if gesto_detectado:
                    payload = json.dumps({'gesto': gesto_detectado})
                    st.session_state.client1.publish(TOPIC_GESTURE, payload, qos=0, retain=False)
                    st.session_state.mqtt_log += f"\n[Acceso] -> Publicado: {gesto_detectado} 📜" 
                    time.sleep(0.5) 

            except Exception as e:
                st.error(f"Error durante el procesamiento de la imagen: {e} 💔")

# --- PÁGINA 2: ALERTA DE HOGAR ---
elif page == "page_defense":
    st.title("La Linterna del Cazador 🕯️") # Linterna/Vela
    st.subheader("Vigilancia de la Mansión: El Ojo de la Noche 🦉") # Búho/Ojo
    
    st.markdown("""
    <p style="font-style: italic; color: #a39b8d; font-size: 1.1em;">
    "Las alarmas silenciosas y las defensas del refugio pueden ser activadas desde aquí. La tranquilidad es un lujo, úsalo con prudencia, pues el eco de la Bestia se acerca... 🐾"
    </p>
    """, unsafe_allow_html=True)
    
    if st.session_state.client1 is None:
        st.error("La aplicación de vigilancia está inactiva. No se pueden enviar comandos hasta que se establezca la conexión MQTT. 🕷️") # Araña
    else:
        # --- Interacción 1: Control de Luz (LED) ---
        st.markdown("### El Candelabro (Control de Estado - LED RGB) 💡") # Bombilla
        
        col_led_rep, col_led_alert = st.columns(2)
        
        if col_led_rep.button("🕯️ Reposo (Verde)", key="btn_reposo"):
            st.session_state.client1.publish(TOPIC_STATUS_LED, "REPOSO", qos=0, retain=False)
            st.session_state.mqtt_log += "\n[LED] -> Publicado: REPOSO 🟢" 
            st.success("Candelabro en modo Reposo. La vigilancia es sutil... 🌫️") # Niebla
        
        if col_led_alert.button("🚨 Alerta (Rojo)", key="btn_alerta"):
            st.session_state.client1.publish(TOPIC_STATUS_LED, "ALERTA", qos=0, retain=False)
            st.session_state.mqtt_log += "\n[LED] -> Publicado: ALERTA 🔴" 
            st.warning("Candelabro en modo Alerta. ¡Algo se acerca! 👹") # Demonio

        # --- Interacción 2: Control de Defensa (Buzzer) ---
        st.markdown("### La Campana de Defensa (Alarma - Buzzer) 🔔") # Campana
        
        col_alarm_on, col_alarm_off = st.columns(2)
        
        if col_alarm_on.button("🔊 Activar Alarma", key="btn_buzzer_on"):
            st.session_state.client1.publish(TOPIC_ALARM, "HIGH", qos=0, retain=False)
            st.session_state.mqtt_log += "\n[Alarma] -> Publicado: HIGH 📢" 
            st.error("Alarma activada: El eco de la Campana resonará en la noche... ¡Cuidado! 🦇") # Murciélago

        if col_alarm_off.button("🔇 Silenciar Campana", key="btn_buzzer_off"):
            st.session_state.client1.publish(TOPIC_ALARM, "LOW", qos=0, retain=False)
            st.session_state.mqtt_log += "\n[Alarma] -> Publicado: LOW 🤫" 
            st.info("Campana silenciada. El silencio es nuestro aliado... por ahora. 🤫") 

        # --- Interacción 3: Comando de Voz/Texto ---
        st.markdown("### Comando Rápido (Entrada de Texto) ✍️") # Pluma
        
        comando_texto = st.text_input("Ingresa un comando ('abrir' o 'cerrar'): 📜", key="text_command")
        
        if st.button("Ejecutar Comando", key="btn_execute_text"):
            comando_limpio = comando_texto.strip().lower()
            if comando_limpio == 'abrir':
                payload = json.dumps({'gesto': 'Abre'})
                st.session_state.client1.publish(TOPIC_GESTURE, payload, qos=0, retain=False)
                st.session_state.mqtt_log += "\n[Texto] -> Publicado: Abre 🔓" 
                st.success("Comando 'Abrir' enviado al Portal. La oscuridad aguarda. 🌌") 
            elif comando_limpio == 'cerrar':
                payload = json.dumps({'gesto': 'Cierra'})
                st.session_state.client1.publish(TOPIC_GESTURE, payload, qos=0, retain=False)
                st.session_state.mqtt_log += "\n[Texto] -> Publicado: Cierra 🔒" 
                st.success("Comando 'Cerrar' enviado al Portal. El velo se espesa. ⛓️") 
            else:
                st.warning("Comando no reconocido. Usa 'abrir' o 'cerrar'. 👁️") # Ojo
                
# --- Registro de Eventos ---
st.sidebar.markdown("---")
st.sidebar.markdown("### Pergamino de Eventos 📜") # Pergamino
st.sidebar.text_area("Logs MQTT", st.session_state.mqtt_log, height=300)

# -----------------------------------------------------------
# --- CORRECCIÓN FINAL ---
# -----------------------------------------------------------
if st.session_state.client1 is not None:
    try:
        st.session_state.client1.loop_end()
    except Exception as e:
        pass
