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
# DISEÑO GRÁFICO Y CSS PERSONALIZADO (ESTILO HUD CÓSMICO)
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    .stApp {
        background: radial-gradient(circle at center, #0B132B 0%, #050814 100%);
        color: #E2E8F0;
        font-family: 'Poppins', sans-serif !important;
    }
    
    /* Menú lateral estilo panel de nave espacial */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(11, 19, 43, 0.9) 0%, rgba(5, 8, 20, 0.95) 100%) !important;
        backdrop-filter: blur(15px);
        border-right: 1px solid rgba(0, 229, 255, 0.2);
        box-shadow: 5px 0 25px rgba(0, 0, 0, 0.5);
    }
    
    h1, h2, h3 {
        color: #00E5FF !important;
        font-weight: 600;
        text-shadow: 0 0 15px rgba(0, 229, 255, 0.4);
    }
    
    /* Botones futuristas con destello cian/dorado */
    .stButton>button {
        background: linear-gradient(90deg, #0077B6 0%, #00B4D8 50%, #90E0EF 100%);
        color: #050814 !important;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.3);
        padding: 0.6rem 1.5rem;
        font-weight: 600;
        box-shadow: 0 0 15px rgba(0, 180, 216, 0.4);
        transition: all 0.3s ease !important;
        width: 100%;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px) scale(1.02);
        background: linear-gradient(90deg, #00B4D8 0%, #90E0EF 100%);
        box-shadow: 0 0 25px rgba(0, 229, 255, 0.8);
        color: #000000 !important;
    }
    
    /* Cajas de texto y entradas tipo panel de control */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea, .stSelectbox>div>div>div {
        background-color: rgba(11, 19, 43, 0.6);
        color: #FFFFFF;
        border-radius: 10px;
        border: 1px solid rgba(0, 229, 255, 0.3);
        box-shadow: inset 0 0 10px rgba(0, 0, 0, 0.5);
    }
    
    /* Burbujas de chat */
    [data-testid="stChatMessage"] {
        background-color: rgba(15, 23, 42, 0.7);
        border-radius: 15px;
        padding: 15px;
        border: 1px solid rgba(0, 229, 255, 0.2);
        margin-bottom: 15px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# MENÚ LATERAL
# ==========================================
if isinstance(icono_ciel, Image.Image):
    st.sidebar.image(icono_ciel)

st.sidebar.title("🌟 Ciel AI")
st.sidebar.markdown("Interfaz de Estudio Cósmico.")
st.sidebar.markdown("---")

if st.sidebar.button("💬 Ir a Tutor IA"):
    st.session_state.modo = "🤖 Modo IA (Tutor)"
    st.rerun()

st.sidebar.markdown("---")
if st.sidebar.button("📅 Abrir Plan de Estudio"):
    st.session_state.modo = "📅 Modo Plan de Estudio"
    st.rerun()

st.sidebar.markdown("---")
if st.sidebar.button("📄 Abrir Lector de Documentos"):
    st.session_state.modo = "📄 Modo Lector de Documentos"
    st.rerun()

st.sidebar.markdown("---")
if st.sidebar.button("📝 Abrir Creador de Exámenes"):
    st.session_state.modo = "📝 Modo Creador de Exámenes"
    st.rerun()

st.sidebar.markdown("---")
activar_voz = st.sidebar.checkbox("🔊 Activar voz de Ciel", value=True)

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
    # Carga automática del diseño gráfico personalizado principal
    imagen_cargada = False
    for archivo_img in ["fondo_ciel.jpg", "fondo_ciel.jpeg", "Fondo_Ciel.jpg", "Fondo_Ciel.jpeg"]:
        try:
            st.image(archivo_img, use_container_width=True)
            imagen_cargada = True
            break
        except Exception:
            continue
            
    if not imagen_cargada:
        st.title("Hola, soy Ciel 👋")
    
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
        
    uploaded_file = st.file_uploader("Sube tu archivo (PDF o TXT)", type=["pdf", "txt"])

    if uploaded_file is not None:
        st.success(f"¡'{uploaded_file.name}' cargado correctamente!")
        pregunta_doc = st.text_input("¿Qué quieres que te explique, analice o reconozca del documento?")
        
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
