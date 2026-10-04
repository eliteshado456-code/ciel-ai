import streamlit as st
import os
import google.generativeai as genai
from gtts import gTTS
from PIL import Image

# ==========================================
# CONFIGURACIÓN DE PÁGINA E ÍCONO
# ==========================================
# Intentamos cargar la imagen (asegúrate de que esté en tu GitHub)
try:
    # Si la subiste como .png normal
    icono_ciel = Image.open("icono_ciel.png")
except FileNotFoundError:
    try:
        # Por si la subiste con la extensión que me enviaste (.jfif)
        icono_ciel = Image.open("icono_ciel.png.jfif")
    except FileNotFoundError:
        icono_ciel = "🌟" # Fallback si no encuentra la imagen

st.set_page_config(page_title="Ciel - Tu Asistente de Estudio", page_icon=icono_ciel, layout="wide")

# ==========================================
# CONEXIÓN SEGURA A LA API DE GOOGLE
# ==========================================
# Lee la clave secreta directamente de Render, evitando que quede expuesta en el código.
api_key = os.environ.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
else:
    st.error("⚠️ Falla de seguridad: No se encontró la GEMINI_API_KEY en las variables de entorno.")

# ==========================================
# CSS PERSONALIZADO (Glassmorphism & Animaciones)
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
        color: #f8fafc;
        font-family: 'Poppins', sans-serif !important;
    }
    [data-testid="stSidebar"] {
        background-color: rgba(15, 23, 42, 0.4) !important;
        backdrop-filter: blur(12px);
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    h1, h2, h3 {
        color: #e0e7ff !important;
        font-weight: 600;
        text-shadow: 0 2px 10px rgba(168, 85, 247, 0.2);
    }
    .stButton>button {
        background: linear-gradient(90deg, #6366f1 0%, #a855f7 100%);
        color: white !important;
        border-radius: 30px;
        border: none;
        padding: 0.6rem 1.5rem;
        font-weight: 600;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3);
        transition: all 0.3s ease !important;
    }
    .stButton>button:hover {
        transform: translateY(-3px) scale(1.02);
        box-shadow: 0 8px 25px rgba(168, 85, 247, 0.6);
    }
    .stTextInput>div>div>input, .stTextArea>div>div>textarea, .stSelectbox>div>div>div {
        background-color: rgba(255, 255, 255, 0.05);
        color: #ffffff;
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    [data-testid="stChatMessage"] {
        background-color: rgba(255, 255, 255, 0.03);
        border-radius: 20px;
        padding: 15px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# BARRA LATERAL (Menú e Imagen de Ciel)
# ==========================================
if isinstance(icono_ciel, Image.Image):
    st.sidebar.image(icono_ciel, use_container_width=True)

st.sidebar.title("🌟 Ciel AI")
st.sidebar.markdown("Tu espacio de estudio inteligente.")

modo = st.sidebar.radio("Elige un modo:", [
    "🤖 Modo IA (Tutor)", 
    "📅 Modo Plan de Estudio", 
    "📄 Modo Lector de Documentos",
    "📝 Modo Creador de Exámenes"
])

st.sidebar.markdown("---")
activar_voz = st.sidebar.checkbox("🔊 Activar voz de Ciel", value=True)

st.sidebar.markdown("<p style='color: #a1a1aa; font-size: 0.85rem;'>La hermana menor del mundo de las IA, lista para ayudarte a triunfar. 🌟</p>", unsafe_allow_html=True)

# ==========================================
# FUNCIONES NÚCLEO
# ==========================================
def hablar_con_ciel(texto):
    try:
        tts = gTTS(text=texto, lang='es', slow=False)
        audio_file = "ciel_voz.mp3"
        tts.save(audio_file)
        st.audio(audio_file, format='audio/mp3', autoplay=True)
    except Exception as e:
        print(f"Error generando voz: {e}")

system_instruction_ciel = (
    "Eres Ciel, un tutor académico amigable, paciente y empático (la hermana menor del mundo de las IA). "
    "Guía a los estudiantes mediante explicaciones claras, analogías sencillas y preguntas que les ayuden a pensar, "
    "sin darles las respuestas directamente. "
    "IMPORTANTE: Siempre debes cerrar tus respuestas y explicaciones con la firma característica: "
    "'¡A seguir brillando y aprendiendo! 🌟 — Ciel'."
)

# Inicializamos el modelo correcto
modelo_base = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    system_instruction=system_instruction_ciel
)

# ==========================================
# 1. MODO IA (Tutor Conversacional)
# ==========================================
if modo == "🤖 Modo IA (Tutor)":
    st.title("Hola, soy Ciel 👋")
    st.markdown("¿Qué concepto o materia quieres dominar hoy?")

    if "chat_session" not in st.session_state:
        st.session_state.chat_session = modelo_base.start_chat(history=[])

    # Mostrar historial de mensajes usando la imagen de Ciel como avatar
    for message in st.session_state.chat_session.history:
        role = "assistant" if message.role == "model" else "user"
        avatar_a_usar = icono_ciel if role == "assistant" else "👤"
        
        with st.chat_message(role, avatar=avatar_a_usar):
            st.markdown(message.parts[0].text)

    if prompt := st.chat_input("Escribe tu duda aquí..."):
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar=icono_ciel):
            with st.spinner("Ciel está pensando..."):
                try:
                    response = st.session_state.chat_session.send_message(prompt)
                    st.markdown(response.text)
                    
                    if activar_voz:
                        hablar_con_ciel(response.text)
                        
                except Exception as e:
                    st.error("Ocurrió un error de conexión con Google. Intenta nuevamente en unos segundos.")

# ==========================================
# 2. MODO PLAN DE ESTUDIO
# ==========================================
elif modo == "📅 Modo Plan de Estudio":
    st.title("📅 Planificador de Ciel")
    st.markdown("Diseña una estrategia a tu medida para vencer cualquier examen.")

    col1, col2 = st.columns(2)
    with col1:
        materia = st.text_input("Materia o Examen:", placeholder="Ej. Cálculo II")
        fecha_examen = st.text_input("¿Para cuándo es?:", placeholder="Ej. En 4 días")
    with col2:
        horas_disponibles = st.slider("Horas de estudio diarias:", 1, 8, 2)

    if st.button("✨ Generar mi Ruta de Estudio"):
        if materia:
            with st.spinner("Ciel está estructurando tu calendario..."):
                try:
                    prompt = f"Crea un plan detallado para '{materia}'. El examen es {fecha_examen} y el estudiante cuenta con {horas_disponibles} horas diarias."
                    response = modelo_base.generate_content(prompt)
                    
                    st.markdown("### 📋 Tu Plan de Ciel:")
                    st.markdown(response.text)
                    
                    if activar_voz:
                        hablar_con_ciel("Aquí tienes tu plan de estudio. ¡Vamos con todo!")
                except Exception as e:
                    st.warning("⚠️ Los servidores están ocupados. ¡Dame unos segundos e intenta de nuevo!")
        else:
            st.warning("Por favor ingresa al menos el nombre de la materia.")

# ==========================================
# 3. MODO LECTOR DE DOCUMENTOS
# ==========================================
elif modo == "📄 Modo Lector de Documentos":
    st.title("📄 Lector Inteligente de Ciel")
    st.markdown("Sube tu guía o PDF y hazle preguntas directas al contenido.")

    uploaded_file = st.file_uploader("Arrastra o selecciona tu archivo", type=["pdf", "txt", "docx"])

    if uploaded_file is not None:
        temp_path = os.path.join("temp_" + uploaded_file.name)
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        st.success(f"¡'{uploaded_file.name}' cargado correctamente!")
        pregunta_doc = st.text_input("¿Qué quieres que te explique o resuma del documento?")
        
        if st.button("🔍 Consultar documento"):
            if pregunta_doc:
                with st.spinner("Ciel está leyendo el documento..."):
                    try:
                        archivo_subido = genai.upload_file(path=temp_path)
                        response = modelo_base.generate_content([archivo_subido, pregunta_doc])
                        
                        st.markdown("### 💡 Respuesta de Ciel:")
                        st.markdown(response.text)
                        
                        if activar_voz:
                            hablar_con_ciel(response.text)
                            
                        # Limpieza del archivo en Google
                        genai.delete_file(archivo_subido.name)
                    except Exception as e:
                        st.warning("⚠️ Hubo un problema de conexión al procesar el archivo. Intenta de nuevo.")
            else:
                st.warning("Escribe una pregunta sobre el documento.")
                
        # Limpieza local
        if os.path.exists(temp_path):
            os.remove(temp_path)

# ==========================================
# 4. MODO CREADOR DE EXÁMENES
# ==========================================
elif modo == "📝 Modo Creador de Exámenes":
    st.title("📝 Simulador de Exámenes")
    st.markdown("Ponte a prueba antes del gran día. Yo te evaluaré.")

    col1, col2 = st.columns(2)
    with col1:
        tema_examen = st.text_input("¿Sobre qué tema quieres evaluarte?", placeholder="Ej. Historia de Venezuela")
        dificultad = st.selectbox("Nivel de dificultad:", ["Básico", "Intermedio", "Universitario / Avanzado"])
    with col2:
        num_preguntas = st.slider("Cantidad de preguntas:", 3, 10, 5)
        tipo_preguntas = st.selectbox("Formato:", ["Opción múltiple", "Verdadero o Falso", "Preguntas de Desarrollo"])

    if st.button("🚀 Generar mi Examen"):
        if tema_examen:
            with st.spinner("Ciel está redactando las preguntas..."):
                try:
                    prompt = f"Actúa como un profesor evaluador. Crea un examen de {num_preguntas} preguntas de tipo '{tipo_preguntas}' sobre el tema '{tema_examen}' con un nivel de dificultad '{dificultad}'. \n\nInstrucciones: \n1. Primero escribe solo las preguntas.\n2. Deja una línea de separación visual que diga '--- RESPUESTAS ---'. \n3. Luego escribe las respuestas correctas con una breve explicación para que el estudiante pueda autocorregirse."
                    
                    response = modelo_base.generate_content(prompt)
                    
                    st.markdown("### 📝 Tu Examen:")
                    st.markdown(response.text)
                    
                    if activar_voz:
                        hablar_con_ciel("He generado tu examen. Tómate tu tiempo para responder, ¡tú puedes!")
                except Exception as e:
                    st.warning("⚠️ Servidores ocupados. No logré redactar el examen ahora mismo, ¡intenta de nuevo en unos segundos!")
        else:
            st.warning("¡Necesito saber el tema para poder crear el examen!")
