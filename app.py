# ==========================================
# 1. MODO IA (Tutor Conversacional)
# ==========================================
if modo == "🤖 Modo IA (Tutor)":
    # Carga automática e infalible de tu diseño gráfico de inicio
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
