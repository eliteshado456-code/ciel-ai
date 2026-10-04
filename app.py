import streamlit as st
import os
import google.generativeai as genai
from gtts import gTTS
from PIL import Image

# ==========================================
# CONFIGURACIÓN DE PÁGINA E ÍCONO
# ==========================================
try:
    icono_ciel = Image.open("icono_ciel.png")
except FileNotFoundError:
    try:
        icono_ciel = Image.open("icono_ciel.png.jfif")
    except FileNotFoundError:
        icono_ciel = "🌟"

st.set_page_config(page_title="Ciel - Tu Asistente de Estudio", page_icon=icono_ciel, layout="wide")

# ==========================================
# CONEXIÓN SEGURA A LA API DE GOOGLE
# ==========================================
api_key = os.environ.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
else:
    st.error("⚠️ Falla de seguridad: No se encontró la GEMINI_API_KEY en Render.")

# ==========================================
# CSS PERSONALIZADO
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
    # CORRECCIÓN AQUÍ: Quitamos el use_container_width que daba error en los logs
    st.sidebar.image(icono_ciel)

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
        pass

system_instruction_ciel = (
    "Eres Ciel, un tutor académico amigable, paciente y empático. "
    "Guía a los estudiantes mediante explicaciones claras. "
    "Firma tus respuestas con: '¡A seguir brillando y aprendiendo! 🌟 — Ciel'."
)

modelo_base = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    system_instruction=system_instruction_ciel
)

# ==========================================
# 1. MODO IA (Tutor Conversacional)
# ==========================================
if modo == "🤖 Modo IA (Tutor)":
    st.title("Hola, soy Ciel 👋")
    
    if "chat_session" not in st.session_state:
        st.session_state.chat_session = modelo_base.start_chat(history=[])

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
                    # CORRECCIÓN AQUÍ: Ahora Ciel nos dirá exactamente por qué falla
                    st.error(f"⚠️ Error detallado de Google: {e}")

# ==========================================
# 2. MODO PLAN DE ESTUDIO
# ==========================================
elif modo == "📅 Modo Plan de Estudio":
    st.title("📅 Planificador de Ciel")
    
    col1, col2 = st.columns(2)
    with col1:
        materia = st.text_input("Materia o Examen:")
        fecha_examen = st.text_input("¿Para cuándo es?:")
    with col2:
        horas_disponibles = st.slider("Horas de estudio diarias:", 1, 8, 2)

    if st.button("✨ Generar mi Ruta de Estudio"):
        if materia:
            with st.spinner("Ciel está estructurando tu calendario..."):
                try:
                    prompt = f"Crea un plan detallado para '{materia}'. El examen es {fecha_examen} y el estudiante cuenta con {horas_disponibles} horas diarias."
                    response = modelo_base.generate_content(prompt)
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"⚠️ Error detallado de Google: {e}")
        else:
            st.warning("Ingresa la materia.")

# ==========================================
# 3. LECTOR Y 4. EXÁMENES
# ==========================================
# (Se han minimizado para enfocarnos en arreglar el error principal de conexión)
elif modo == "📄 Modo Lector de Documentos" or modo == "📝 Modo Creador de Exámenes":
    st.info("⚠️ Estamos reparando la conexión del chat principal. Una vez funcione, activaremos los demás modos.")
