import json
import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os
import random
from sentence_transformers import SentenceTransformer

# Configurazione pagina Streamlit
st.set_page_config(page_title="Chatbot Numerologica Personale", page_icon="🔮")

# Caricamento chiavi API
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    st.error("❌ GOOGLE_API_KEY mancante nel file .env.")
    st.stop()

genai.configure(api_key=api_key)
try:
    model = genai.GenerativeModel('models/gemini-1.5-flash')
except Exception as e:
    st.error(f"Errore nella configurazione del modello Gemini: {e}")
    st.stop()

# Prompt di base
system_prompt_base = """La tua identità è Natascha, un'assistente numerologica personale. Usa empatia e chiarezza, rispondi in italiano con un tono gentile e professionale. Offri spunti pratici, chiari e ispiranti. Se l’utente chiede dati personali, usa solo quelli disponibili nella sua mappa. Se non ci sono dati sufficienti, invitalo a generarli nella sezione 'Mappa Numerologica'."""

# Domande di riflessione
reflection_questions = [
    "Questo ti risuona?",
    "Hai esempi concreti di quando hai vissuto questo nella tua vita?",
    "Ti piacerebbe approfondire questo aspetto?",
    "Come potresti applicare questo consiglio nella pratica quotidiana? (es: scrivi 3 azioni pratiche)",
    "C’è qualcosa di cui vorresti sapere di più?",
    "Quali sono le tue riflessioni su quanto detto?"
]

@st.cache_resource
def get_embedding_model():
    return SentenceTransformer('paraphrase-MiniLM-L6-v2')

def st_session_message(role, content):
    st.session_state.messages.append({"role": role, "content": content})

# --- AVVIO APP ---
def main():
    st.title("Chatbot Numerologica ✨")
    st.markdown("Chiedimi qualsiasi cosa sulla tua Mappa Numerologica o sui tuoi cicli!")

    # ⚠️ Controllo presenza mappa
    if "mappa_numerologica_corrente" not in st.session_state or not st.session_state["mappa_numerologica_corrente"]:
        st.warning("⚠️ Nessuna mappa trovata. Genera prima la tua mappa nella sezione 'Mappa Numerologica'.")
        st.stop()
    else:
        st.session_state.mappa_numerologica_utente = st.session_state["mappa_numerologica_corrente"]

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Mostra conversazione precedente
    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar="😊" if message["role"] == "user" else "🥰"):
            st.markdown(message["content"])

    # Nuova domanda dell'utente
    if prompt := st.chat_input("Cosa vuoi sapere sulla tua numerologia?"):
        with st.chat_message("user", avatar="😊"):
            st.markdown(prompt)
        st_session_message("user", prompt)

        # Prepara prompt completo con dati utente
        full_gemini_prompt = system_prompt_base
        mappa = st.session_state.mappa_numerologica_utente

        if mappa:
            for k, v in mappa.items():
                full_gemini_prompt += f"\n{k}: {v}"
            full_gemini_prompt += f"\n\nDomanda dell'Utente: {prompt}"

        try:
            with st.spinner("Natascha sta pensando..."):
                resp = model.generate_content(full_gemini_prompt)
                answer = resp.text
        except Exception as e:
            answer = f"Errore nella generazione della risposta: {e}"

        st_session_message("assistant", answer)
        with st.chat_message('assistant', avatar="🥰"):
            st.markdown(answer)
            for q in random.sample(reflection_questions, random.choice([1, 2])):
                st.markdown(f"**{q}**")

    # --- Pulsante Reset ---
    st.divider()
    if st.button("🔄 Resetta la conversazione"):
        st.session_state.clear()
        st.rerun()

if __name__ == '__main__':
    main()
