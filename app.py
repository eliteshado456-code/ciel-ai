import streamlit as st
import os
from google import genai
from google.genai import errors
from gtts import gTTS
from PIL import Image

# ==========================================
# CONFIGURACIÓN DE PÁGINA E ÍCONO
# ==========================================
try:
    icono_ciel = Image.open("icono_ciel.png")
    icono_pestana = icono_ciel
except FileNotFoundError:
    icono_ciel = None
    icono_pestana = "🤖"

st.set_page_config(page_title="Ciel - Tu Asistente de Estudio", page_icon=icono_pestana, layout="wide")

client = genai.Client(api_key="AQ.Ab8RN6K8OVjfYfWV0lVdKnBh1xBCGycLCY2PHLppq5IhSeBgMw")

# ==========================================
# CSS PERSONALIZADO (Glassmorphism & Animaciones)
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    /* El header {visibility: hidden;} fue eliminado para asegurar que el botón del menú siempre aparezca en móviles */

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
    
    .stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus {
        border: 1px solid #a855f7;
        box-shadow: 0 0 10px rgba(168, 85, 247, 0.3);
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
if icono_ciel:
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
# FUNCIÓN DE VOZ
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

# ==========================================
# 1. MODO IA (Tutor Conversacional)
# ==========================================
if modo == "🤖 Modo IA (Tutor)":
    st.title("Hola, soy Ciel 👋")
    st.markdown("¿Qué concepto o materia quieres dominar hoy?")

    if "messages_ia" not in st.session_state:
        st.session_state.messages_ia = []

    for message in st.session_state.messages_ia:
        with st.chat_message(message["role"], avatar="🌟" if message["role"] == "assistant" else "👤"):
            st.markdown(message["content"])

    if prompt := st.chat_input("Escribe tu duda aquí..."):
        st.session_state.messages_ia.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar="🌟"):
            with st.spinner("Ciel está analizando..."):
                contents = [
                    {"role": "user" if m["role"] == "user" else "model", "parts": [{"text": m["content"]}]}
                    for m in st.session_state.messages_ia
                ]

                try:
                    response = client.models.generate_content(
                        model="gemini-3.8-flash",
                        contents=contents,
                        config={"system_instruction": system_instruction_ciel}
                    )
                    st.markdown(response.text)
                    st.session_state.messages_ia.append({"role": "assistant", "content": response.text})
                    
                    if activar_voz:
                        hablar_con_ciel(response.text)
                        
                except errors.ServerError as e:
                    st.warning("⚠️ ¡Uff! Muchas personas me están haciendo preguntas ahora mismo y mis servidores están un poco cansados. Por favor, espera unos segundos e intenta enviarme tu pregunta de nuevo. 🌟")
                    if activar_voz:
                        hablar_con_ciel("Estoy un poco ocupada ahora mismo, por favor intenta de nuevo en unos segundos.")
                except Exception as e:
                    st.error(f"Ocurrió un error inesperado de conexión. Intenta nuevamente.")

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
                    response = client.models.generate_content(
                        model="gemini-3.8-flash",
                        contents=prompt,
                        config={"system_instruction": system_instruction_ciel}
                    )
                    st.markdown("### 📋 Tu Plan de Ciel:")
                    st.markdown(response.text)
                    
                    if activar_voz:
                        hablar_con_ciel("Aquí tienes tu plan de estudio. ¡Vamos con todo!")
                except Exception as e:
                    st.warning("⚠️ Los servidores de Google están saturados. ¡Dame unos segundos e intenta de nuevo!")
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

        try:
            with st.spinner("Procesando archivo..."):
                archivo_subido = client.files.upload(file=temp_path)

            pregunta_doc = st.text_input("¿Qué quieres que te explique o resuma del documento?")
            
            if st.button("🔍 Consultar documento"):
                if pregunta_doc:
                    with st.spinner("Ciel está leyendo las páginas..."):
                        response = client.models.generate_content(
                            model="gemini-3.8-flash",
                            contents=[archivo_subido, pregunta_doc],
                            config={"system_instruction": system_instruction_ciel}
                        )
                        st.markdown("### 💡 Respuesta de Ciel:")
                        st.markdown(response.text)
                        
                        if activar_voz:
                            hablar_con_ciel(response.text)
                else:
                    st.warning("Escribe una pregunta sobre el documento.")
        except Exception as e:
            st.warning("⚠️ Hubo un problema al procesar el archivo por saturación de servidores. Intenta de nuevo en un momento.")
        finally:
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
                    
                    response = client.models.generate_content(
                        model="gemini-3.8-flash",
                        contents=prompt,
                        config={"system_instruction": system_instruction_ciel}
                    )
                    st.markdown("### 📝 Tu Examen:")
                    st.markdown(response.text)
                    
                    if activar_voz:
                        hablar_con_ciel("He generado tu examen. Tómate tu tiempo para responder, ¡tú puedes!")
                except Exception as e:
                    st.warning("⚠️ Servidores ocupados. No logré redactar el examen ahora mismo, ¡intenta de nuevo en unos segundos!")
        else:
            st.warning("¡Necesito saber el tema para poder crear el examen!")