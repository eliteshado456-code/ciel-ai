import streamlit as st
import os
from huggingface_hub import InferenceClient
from gtts import gTTS
from PIL import Image
import PyPDF2
import re

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
# ESTADO DE NAVEGACIÓN
# ==========================================
if 'modo' not in st.session_state:
    st.session_state.modo = "🤖 Modo IA (Tutor)"

# ==========================================
# CONEXIÓN A HUGGING FACE API (INFERENCE CLIENT)
# ==========================================
hf_token = os.environ.get("HUGGINGFACE_API_KEY") or os.environ.get("HF_TOKEN")

if hf_token:
    client = InferenceClient(api_key=hf_token)
    MODEL_NAME = "meta-llama/Llama-3.1-8B-Instruct"
else:
    client = None

# ==========================================
# CSS PERSONALIZADO: ESTILO TECNOLÓGICO Y ESTELAR
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;800&family=Poppins:wght@300;400;600&display=swap');
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Fondo general con efecto estelar y ciberespacial */
    .stApp {
        background: radial-gradient(circle at 50% 50%, #0d1b2a 0%, #0b0914 70%, #030208 100%);
        color: #e2e8f0;
        font-family: 'Poppins', sans-serif !important;
    }
    
    /* Menú lateral tecnológico */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(11, 15, 25, 0.95) 0%, rgba(15, 23, 42, 0.95) 100%) !important;
        backdrop-filter: blur(15px);
        border-right: 1px solid rgba(56, 189, 248, 0.2);
        box-shadow: 5px 0 25px rgba(0, 0, 0, 0.5);
    }
    
    /* Tipografías con estilo futurista */
    h1, h2, h3 {
        font-family: 'Orbitron', sans-serif !important;
        color: #38bdf8 !important;
        font-weight: 600;
        letter-spacing: 1px;
        text-shadow: 0 0 15px rgba(56, 189, 248, 0.4);
    }
    
    /* Botones estilo panel de control espacial */
    .stButton>button {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        color: #38bdf8 !important;
        border-radius: 12px;
        border: 1px solid rgba(56, 189, 248, 0.4);
        padding: 0.7rem 1.5rem;
        font-family: 'Orbitron', sans-serif;
        font-size: 13px;
        font-weight: 600;
        box-shadow: 0 0 10px rgba(56, 189, 248, 0.1);
        transition: all 0.3s ease !important;
        width: 100%;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #38bdf8 100%, #6366f1 0%);
        color: #ffffff !important;
        border-color: #38bdf8;
        transform: translateY(-2px);
        box-shadow: 0 0 20px rgba(56, 189, 248, 0.6);
    }
    
    /* Entradas de texto y selectores futuristas */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea, .stSelectbox>div>div>div {
        background-color: rgba(15, 23, 42, 0.8);
        color: #38bdf8;
        border-radius: 12px;
        border: 1px solid rgba(56, 189, 248, 0.3);
        font-family: 'Poppins', sans-serif;
    }
    .stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus {
        border-color: #38bdf8;
        box-shadow: 0 0 12px rgba(56, 189, 248, 0.4);
    }
    
    /* Cajas de chat estilo holográfico */
    [data-testid="stChatMessage"] {
        background: rgba(15, 23, 42, 0.6);
        border-radius: 16px;
        padding: 16px;
        border: 1px solid rgba(56, 189, 248, 0.2);
        margin-bottom: 15px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        backdrop-filter: blur(4px);
    }
    
    /* Barra inferior de entrada de chat estilo panel tecnológico */
    [data-testid="stChatInput"] {
        background-color: rgba(15, 23, 42, 0.9) !important;
        border-radius: 16px !important;
        border: 1px solid rgba(56, 189, 248, 0.4) !important;
        box-shadow: 0 0 20px rgba(56, 189, 248, 0.2) !important;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# MENÚ LATERAL TECNOLÓGICO
# ==========================================
if isinstance(icono_ciel, Image.Image):
    st.sidebar.image(icono_ciel)

st.sidebar.title("🌟 Ciel AI")
st.sidebar.markdown("<p style='color: #94a3b8; font-size: 12px;'>SISTEMA DE ASISTENCIA ESTELAR</p>", unsafe_allow_html=True)
st.sidebar.markdown("---")

if st.sidebar.button("💬 Interfaz Tutor IA"):
    st.session_state.modo = "🤖 Modo IA (Tutor)"

st.sidebar.markdown("---")
if st.sidebar.button("📅 Planificador Cuántico"):
    st.session_state.modo = "📅 Modo Plan de Estudio"

st.sidebar.markdown("---")
if st.sidebar.button("📄 Lector de Datos"):
    st.session_state.modo = "📄 Modo Lector de Documentos"

st.sidebar.markdown("---")
if st.sidebar.button("📝 Simulador de Pruebas"):
    st.session_state.modo = "📝 Modo Creador de Exámenes"

st.sidebar.markdown("---")
activar_voz = st.sidebar.checkbox("🔊 Canal de Voz Activo", value=True)

# Capturamos el modo actual de la sesión
modo = st.session_state.modo

# ==========================================
# FUNCIONES NÚCLEO
# ==========================================
def hablar_con_ciel(texto):
    try:
        texto_limpio = re.sub(r'[🌟✨🤖💬📄📅📝⚠️👤]', '', texto)
        tts = gTTS(text=texto_limpio, lang='es', slow=False)
        audio_file = "ciel_voz.mp3"
        tts.save(audio_file)
        st.audio(audio_file, format='audio/mp3', autoplay=True)
    except Exception as e:
        pass

def consultar_huggingface(mensajes_streamlit):
    if not client:
        return "⚠️ Falta configurar el token de Hugging Face en las variables de entorno de Render (`HUGGINGFACE_API_KEY`)."
    
    mensajes_completos = [
        {
            "role": "system", 
            "content": "Eres Ciel, un tutor académico amigable, paciente, empático y experto en astronomía, astrofísica, constelaciones, simbología científica y todo tipo de signos. Estructura tus respuestas usando pausas claras y puntuación adecuada para que al ser leídas en voz alta suenen suaves, armónicas y naturales. Firma tus respuestas con: '¡A seguir brillando y aprendiendo! 🌟 — Ciel'."
        }
    ]
    
    for msg in mensajes_streamlit:
        mensajes_completos.append({"role": msg["role"], "content": msg["content"]})
    
    try:
        response = client.chat_completion(
            model=MODEL_NAME,
            messages=mensajes_completos,
            temperature=0.7,
            max_tokens=1024
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ Error al conectar con Hugging Face: {e}"

def consultar_hf_prompt(prompt_texto):
    mensajes_temp = [{"role": "user", "content": prompt_texto}]
    return consultar_huggingface(mensajes_temp)

# ==========================================
# 1. MODO IA (Tutor Conversacional)
# ==========================================
if modo == "🤖 Modo IA (Tutor)":
    st.title("🌌 Ciel AI — Núcleo Estelar")
    st.markdown("<p style='color: #94a3b8; margin-bottom: 25px;'>Terminal de consulta académica e interpretación de signos y constelaciones.</p>", unsafe_allow_html=True)
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        avatar_a_usar = icono_ciel if msg["role"] == "assistant" else "👤"
        with st.chat_message(msg["role"], avatar=avatar_a_usar):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Transmita su consulta o símbolo al núcleo de Ciel..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar=icono_ciel):
            with st.spinner("Ciel está procesando en el núcleo estelar..."):
                try:
                    respuesta_texto = consultar_huggingface(st.session_state.messages)
                    st.markdown(respuesta_texto)
                    st.session_state.messages.append({"role": "assistant", "content": respuesta_texto})
                    
                    if activar_voz:
                        hablar_con_ciel(respuesta_texto)
                except Exception as e:
                    st.error(f"⚠️ Error: {e}")

# ==========================================
# 2. MODO PLAN DE ESTUDIO
# ==========================================
elif modo == "📅 Modo Plan de Estudio":
    st.title("📅 Planificador Cuántico")
    st.markdown("<p style='color: #94a3b8;'>Optimización temporal y distribución de cargas de estudio.</p>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        materia = st.text_input("Materia o Examen:")
        fecha_examen = st.text_input("¿Para cuándo es?:")
    with col2:
        horas_disponibles = st.slider("Horas de estudio diarias:", 1, 8, 2)

    if st.button("✨ Iniciar Secuencia de Planificación"):
        if materia:
            with st.spinner("Calculando ruta temporal óptima..."):
                prompt_plan = f"Crea un plan detallado para la materia '{materia}'. El examen es {fecha_examen} y el estudiante cuenta con {horas_disponibles} horas diarias."
                respuesta = consultar_hf_prompt(prompt_plan)
                st.markdown(respuesta)
        else:
            st.warning("Debe ingresar la materia o examen.")

# ==========================================
# 3. MODO LECTOR DE DOCUMENTOS
# ==========================================
elif modo == "📄 Modo Lector de Documentos":
    st.title("📄 Lector de Datos y Archivos")
    st.markdown("<p style='color: #94a3b8;'>Análisis estelar de contenido documental (PDF / TXT).</p>", unsafe_allow_html=True)
        
    uploaded_file = st.file_uploader("Cargue su archivo de texto o PDF", type=["pdf", "txt"])

    if uploaded_file is not None:
        st.success(f"¡Archivo '{uploaded_file.name}' sincronizado con éxito!")
        pregunta_doc = st.text_input("¿Qué parámetro o análisis requiere extraer del documento?")
        
        if st.button("🔍 Ejecutar Análisis Documental"):
            if pregunta_doc:
                with st.spinner("Extrayendo información del documento..."):
                    try:
                        texto_extraido = ""
                        if uploaded_file.name.endswith('.pdf'):
                            pdf_reader = PyPDF2.PdfReader(uploaded_file)
                            for page in pdf_reader.pages:
                                texto_extraido += page.extract_text() + "\n"
                        elif uploaded_file.name.endswith('.txt'):
                            texto_extraido = str(uploaded_file.read(), "utf-8")
                        
                        texto_corto = texto_extraido[:12000]
                        prompt_doc = f"Basado en este documento:\n{texto_corto}\n\nResponde: {pregunta_doc}"
                        respuesta = consultar_hf_prompt(prompt_doc)
                        st.markdown("### 💡 Diagnóstico de Ciel:")
                        st.markdown(respuesta)
                    except Exception as e:
                        st.error(f"Error al procesar el archivo: {e}")
            else:
                st.warning("Ingrese una consulta sobre el documento.")

# ==========================================
# 4. MODO CREADOR DE EXÁMENES
# ==========================================
elif modo == "📝 Modo Creador de Exámenes":
    st.title("📝 Simulador de Pruebas Estelares")
    st.markdown("<p style='color: #94a3b8;'>Generación avanzada de reactivos y evaluaciones de conocimiento.</p>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        tema_examen = st.text_input("¿Sobre qué área temática se evaluará?")
        dificultad = st.selectbox("Nivel de calibración:", ["Básico", "Intermedio", "Universitario / Avanzado"])
    with col2:
        num_preguntas = st.slider("Cantidad de reactivos:", 3, 10, 5)
        tipo_preguntas = st.selectbox("Formato de evaluación:", ["Opción múltiple", "Verdadero o Falso", "Preguntas de Desarrollo"])

    if st.button("🚀 Generar Evaluación"):
        if tema_examen:
            with st.spinner("Generando reactivos de evaluación..."):
                prompt_examen = f"Crea un examen de {num_preguntas} preguntas tipo '{tipo_preguntas}' sobre '{tema_examen}' (Dificultad: {dificultad}). Pon las preguntas primero y al final las respuestas."
                respuesta = consultar_hf_prompt(prompt_examen)
                st.markdown("### 📝 Evaluación Generada:")
                st.markdown(respuesta)
        else:
            st.warning("¡Debe especificar el tema de la evaluación!")
