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

st.set_page_config(page_title="Ciel AI - Tu Asistente Inteligente", page_icon=icono_ciel, layout="wide")

# ==========================================
# ESTADO DE NAVEGACIÓN
# ==========================================
if 'modo' not in st.session_state:
    st.session_state.modo = "🤖 Modo IA (Tutor)"

modo = st.session_state.modo

# ==========================================
# CONEXIÓN A HUGGING FACE API
# ==========================================
hf_token = os.environ.get("HUGGINGFACE_API_KEY") or os.environ.get("HF_TOKEN")

if hf_token:
    client = InferenceClient(api_key=hf_token)
    MODEL_NAME = "meta-llama/Llama-3.1-8B-Instruct"
else:
    client = None

# ==========================================
# NUEVO CSS Y DISEÑO VISUAL MEJORADO
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Fondo general moderno tipo glassmorphism oscuro */
    .stApp {
        background: radial-gradient(circle at 50% 10%, #171b36 0%, #0b0f19 100%);
        color: #f1f5f9;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }

    /* Menú lateral elegante */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(15, 23, 42, 0.85) 0%, rgba(11, 15, 25, 0.95) 100%) !important;
        backdrop-filter: blur(16px);
        border-right: 1px solid rgba(255, 255, 255, 0.08);
        padding-top: 1rem;
    }

    /* Tipografía de títulos */
    h1, h2, h3 {
        color: #f8fafc !important;
        font-weight: 700;
        letter-spacing: -0.5px;
    }

    /* Botones de navegación del sidebar estilizados */
    .stSidebar .stButton>button {
        background: rgba(255, 255, 255, 0.03);
        color: #cbd5e1 !important;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.06);
        padding: 0.6rem 1rem;
        font-weight: 500;
        text-align: left;
        width: 100%;
        transition: all 0.25s ease;
    }
    
    .stSidebar .stButton>button:hover {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
        color: #ffffff !important;
        border-color: transparent;
        transform: translateX(4px);
        box-shadow: 0 4px 20px rgba(99, 102, 241, 0.4);
    }

    /* Botones de acción general */
    .stButton>button {
        background: linear-gradient(135deg, #6366f1 0%, #9333ea 100%);
        color: white !important;
        border-radius: 14px;
        border: none;
        padding: 0.6rem 1.5rem;
        font-weight: 600;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(147, 51, 234, 0.5);
    }

    /* Inputs y áreas de texto con diseño flotante */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea, .stSelectbox>div>div>div {
        background-color: rgba(255, 255, 255, 0.04);
        color: #ffffff;
        border-radius: 14px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 0.6rem 1rem;
        transition: all 0.2s ease;
    }
    
    .stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus {
        border-color: #818cf8;
        box-shadow: 0 0 0 2px rgba(129, 140, 248, 0.2);
    }

    /* Burbujas de chat modernas y limpias */
    [data-testid="stChatMessage"] {
        background: rgba(255, 255, 255, 0.025);
        border-radius: 18px;
        padding: 1.2rem;
        border: 1px solid rgba(255, 255, 255, 0.06);
        margin-bottom: 1rem;
        backdrop-filter: blur(8px);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
    }

    /* Caja inferior de chat fija / estilizada */
    [data-testid="stChatInput"] {
        background-color: transparent !important;
        padding-bottom: 1rem;
    }
    [data-testid="stChatInput"] textarea {
        background-color: rgba(15, 23, 42, 0.8) !important;
        border: 1px solid rgba(129, 140, 248, 0.3) !important;
        border-radius: 16px !important;
        color: #f8fafc !important;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# MENÚ LATERAL REDISEÑADO
# ==========================================
with st.sidebar:
    col_logo, col_titulo = st.columns([1, 3])
    with col_logo:
        if isinstance(icono_ciel, Image.Image):
            st.image(icono_ciel, width=45)
        else:
            st.markdown("### 🌟")
    with col_titulo:
        st.markdown("### Ciel AI")
    
    st.markdown("<p style='font-size: 0.85rem; color: #94a3b8; margin-top: -10px;'>Asistente Académico Inteligente</p>", unsafe_allow_html=True)
    st.markdown("---")

    st.markdown("#### 🧭 Navegación")
    
    if st.button("💬 Tutor IA Interactivo"):
        st.session_state.modo = "🤖 Modo IA (Tutor)"
        st.rerun()

    if st.button("📅 Planificador de Estudio"):
        st.session_state.modo = "📅 Modo Plan de Estudio"
        st.rerun()

    if st.button("📄 Lector Inteligente"):
        st.session_state.modo = "📄 Modo Lector de Documentos"
        st.rerun()

    if st.button("📝 Simulador de Exámenes"):
        st.session_state.modo = "📝 Modo Creador de Exámenes"
        st.rerun()

    st.markdown("---")
    st.markdown("#### ⚙️ Configuración de Voz")
    activar_voz = st.toggle("Activar voz de Ciel", value=True)

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
    st.title("🌟 Hola, soy Ciel")
    st.markdown("<p style='color: #94a3b8; font-size: 1.05rem;'>Tu espacio personal de tutoría inteligente, listo para ayudarte a descifrar cualquier duda, concepto o constelación.</p>", unsafe_allow_html=True)
    st.markdown("---")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        avatar_a_usar = icono_ciel if msg["role"] == "assistant" else "👤"
        with st.chat_message(msg["role"], avatar=avatar_a_usar):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Escribe tu duda o pregúntale a Ciel sobre cualquier signo o símbolo..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar=icono_ciel):
            with st.spinner("Ciel está preparando su respuesta..."):
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
    st.title("📅 Planificador de Ciel")
    st.markdown("<p style='color: #94a3b8;'>Organiza tus metas académicas de forma eficiente.</p>", unsafe_allow_html=True)
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        materia = st.text_input("Materia o Examen:")
        fecha_examen = st.text_input("¿Para cuándo es?:")
    with col2:
        horas_disponibles = st.slider("Horas de estudio diarias:", 1, 8, 2)

    if st.button("✨ Generar mi Ruta de Estudio"):
        if materia:
            with st.spinner("Ciel está estructurando tu calendario..."):
                prompt_plan = f"Crea un plan detallado para la materia '{materia}'. El examen es {fecha_examen} y el estudiante cuenta con {horas_disponibles} horas diarias."
                respuesta = consultar_hf_prompt(prompt_plan)
                st.markdown(respuesta)
        else:
            st.warning("Ingresa la materia.")

# ==========================================
# 3. MODO LECTOR DE DOCUMENTOS
# ==========================================
elif modo == "📄 Modo Lector de Documentos":
    st.title("📄 Lector Inteligente de Ciel")
    st.markdown("<p style='color: #94a3b8;'>Sube tus archivos y obtén explicaciones detalladas al instante.</p>", unsafe_allow_html=True)
    st.markdown("---")
        
    uploaded_file = st.file_uploader("Sube tu archivo (PDF o TXT)", type=["pdf", "txt"])

    if uploaded_file is not None:
        st.success(f"¡'{uploaded_file.name}' cargado correctamente!")
        pregunta_doc = st.text_input("¿Qué quieres que te explique, analice or reconozca del documento?")
        
        if st.button("🔍 Consultar documento"):
            if pregunta_doc:
                with st.spinner("Ciel está leyendo el archivo..."):
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
                        st.markdown("### 💡 Respuesta de Ciel:")
                        st.markdown(respuesta)
                    except Exception as e:
                        st.error(f"Error al leer el archivo: {e}")
            else:
                st.warning("Escribe una pregunta.")

# ==========================================
# 4. MODO CREADOR DE EXÁMENES
# ==========================================
elif modo == "📝 Modo Creador de Exámenes":
    st.title("📝 Simulador de Exámenes")
    st.markdown("<p style='color: #94a3b8;'>Evalúa tus conocimientos con pruebas personalizadas.</p>", unsafe_allow_html=True)
    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        tema_examen = st.text_input("¿Sobre qué tema quieres evaluarte?")
        dificultad = st.selectbox("Nivel de dificultad:", ["Básico", "Intermedio", "Universitario / Avanzado"])
    with col2:
        num_preguntas = st.slider("Cantidad de preguntas:", 3, 10, 5)
        tipo_preguntas = st.selectbox("Formato:", ["Opción múltiple", "Verdadero o Falso", "Preguntas de Desarrollo"])

    if st.button("🚀 Generar mi Examen"):
        if tema_examen:
            with st.spinner("Ciel está redactando las preguntas..."):
                prompt_examen = f"Crea un examen de {num_preguntas} preguntas tipo '{tipo_preguntas}' sobre '{tema_examen}' (Dificultad: {dificultad}). Pon las preguntas primero y al final las respuestas."
                respuesta = consultar_hf_prompt(prompt_examen)
                st.markdown("### 📝 Tu Examen:")
                st.markdown(respuesta)
        else:
            st.warning("¡Necesito saber el tema!")
