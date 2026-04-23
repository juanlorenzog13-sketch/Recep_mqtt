import streamlit as st
import paho.mqtt.client as mqtt
import json
import time

# Configuración de la página
st.set_page_config(
    page_title="Lector de Sensor MQTT",
    page_icon="💗",
    layout="centered"
)

# Estilos personalizados
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #ffe3ef 0%, #ffd6ea 45%, #fff0f7 100%);
}

h1, h2, h3 {
    color: #d63384;
}

section[data-testid="stSidebar"] {
    background: #fff0f7;
    border-right: 2px solid #f8b6d2;
}

section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] div {
    color: #b02a6b;
}

div[data-baseweb="input"] > div,
div[data-baseweb="select"] > div,
div[data-baseweb="base-input"] > div {
    border-radius: 14px !important;
    border: 2px solid #f3a6c8 !important;
    background-color: white !important;
}

.stNumberInput > div > div > input,
.stTextInput > div > div > input {
    border-radius: 14px !important;
}

.stButton > button {
    background: linear-gradient(135deg, #ff4fa3, #ff7bbf);
    color: white;
    border: none;
    border-radius: 14px;
    padding: 0.75rem 1.2rem;
    font-weight: 600;
    box-shadow: 0 8px 20px rgba(255, 79, 163, 0.25);
}

.stButton > button:hover {
    background: linear-gradient(135deg, #ff3d98, #ff69b4);
    color: white;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

.card {
    background: rgba(255,255,255,0.78);
    border: 2px solid #f6b2d0;
    border-radius: 20px;
    padding: 20px;
    box-shadow: 0 10px 24px rgba(214, 51, 132, 0.10);
    margin-bottom: 16px;
}

.result-card {
    background: rgba(255,255,255,0.88);
    border: 2px solid #f3b3d1;
    border-radius: 20px;
    padding: 20px;
    box-shadow: 0 10px 24px rgba(214, 51, 132, 0.10);
    margin-top: 16px;
}

[data-testid="stMetric"] {
    background: white;
    border: 2px solid #f5bfd8;
    border-radius: 18px;
    padding: 14px;
    box-shadow: 0 8px 18px rgba(214, 51, 132, 0.08);
}

[data-testid="stExpander"] {
    background: rgba(255,255,255,0.65);
    border: 2px solid #f6b2d0;
    border-radius: 16px;
    overflow: hidden;
}

hr {
    border-top: 1px solid #ef9fc7 !important;
}

.small-note {
    color: #9c4674;
    font-size: 0.95rem;
}
</style>
""", unsafe_allow_html=True)

# Variables de estado
if 'sensor_data' not in st.session_state:
    st.session_state.sensor_data = None

def get_mqtt_message(broker, port, topic, client_id):
    """Función para obtener un mensaje MQTT"""
    message_received = {"received": False, "payload": None}
    
    def on_message(client, userdata, message):
        try:
            payload = json.loads(message.payload.decode())
            message_received["payload"] = payload
            message_received["received"] = True
        except:
            # Si no es JSON, guardar como texto
            message_received["payload"] = message.payload.decode()
            message_received["received"] = True
    
    try:
        client = mqtt.Client(client_id=client_id)
        client.on_message = on_message
        client.connect(broker, port, 60)
        client.subscribe(topic)
        client.loop_start()
        
        # Esperar máximo 5 segundos
        timeout = time.time() + 5
        while not message_received["received"] and time.time() < timeout:
            time.sleep(0.1)
        
        client.loop_stop()
        client.disconnect()
        
        return message_received["payload"]
    
    except Exception as e:
        return {"error": str(e)}

# Sidebar - Configuración
with st.sidebar:
    st.subheader('⚙️ Configuración de Conexión')
    
    broker = st.text_input(
        'Broker MQTT',
        value='broker.mqttdashboard.com',
        help='Dirección del broker MQTT'
    )
    
    port = st.number_input(
        'Puerto',
        value=1883,
        min_value=1,
        max_value=65535,
        help='Puerto del broker (generalmente 1883)'
    )
    
    topic = st.text_input(
        'Tópico',
        value='Sensor/THP2',
        help='Tópico MQTT a suscribirse'
    )
    
    client_id = st.text_input(
        'ID del Cliente',
        value='streamlit_client',
        help='Identificador único para esta conexión'
    )

# Título
st.title('💗 Lector de Sensor MQTT')

st.markdown("""
<div class="card">
    <h3 style="margin-top:0;">Visualizador de datos en tiempo real</h3>
    <p class="small-note">
        Configura la conexión desde el panel lateral y presiona el botón para recibir el mensaje más reciente del tópico MQTT.
    </p>
</div>
""", unsafe_allow_html=True)

# Información al inicio
with st.expander('ℹ️ Información', expanded=False):
    st.markdown("""
    ### Cómo usar esta aplicación:
    
    1. **Broker MQTT**: Ingresa la dirección del servidor MQTT en el sidebar  
    2. **Puerto**: Generalmente es 1883 para conexiones no seguras  
    3. **Tópico**: El canal al que deseas suscribirte  
    4. **ID del Cliente**: Un identificador único para esta conexión  
    5. Haz clic en **Obtener Datos** para recibir el mensaje más reciente  
    
    ### Brokers públicos para pruebas:
    - broker.mqttdashboard.com
    - test.mosquitto.org
    - broker.hivemq.com
    """)

st.divider()

# Botón para obtener datos
if st.button('🔄 Obtener Datos del Sensor', use_container_width=True):
    with st.spinner('Conectando al broker y esperando datos...'):
        sensor_data = get_mqtt_message(broker, int(port), topic, client_id)
        st.session_state.sensor_data = sensor_data

# Mostrar resultados
if st.session_state.sensor_data:
    st.markdown('<div class="result-card">', unsafe_allow_html=True)
    st.subheader('📊 Datos Recibidos')
    
    data = st.session_state.sensor_data
    
    # Verificar si hay error
    if isinstance(data, dict) and 'error' in data:
        st.error(f"❌ Error de conexión: {data['error']}")
    else:
        st.success('✅ Datos recibidos correctamente')
        
        # Mostrar datos en formato JSON
        if isinstance(data, dict):
            cols = st.columns(len(data))
            for i, (key, value) in enumerate(data.items()):
                with cols[i]:
                    st.metric(label=key, value=value)
            
            with st.expander('Ver JSON completo'):
                st.json(data)
        else:
            st.code(data)
    
    st.markdown('</div>', unsafe_allow_html=True)
