import json
import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os
from pypdf import PdfReader

__import__("pysqlite3")
import sys
sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")

import chromadb
from sentence_transformers import SentenceTransformer
import random
from datetime import datetime, date

reflection_questions = [
    "Questo ti risuona?",
    "Hai esempi concreti di quando hai vissuto questo nella tua vita?",
    "Ti piacerebbe approfondire questo aspetto?",
    "Come potresti applicare questo consiglio nella pratica quotidiana? (es: scrivi 3 azioni pratiche)",
    "C’è qualcosa di cui vorresti sapere di più?",
    "Quali sono le tue riflessioni su quanto detto?"
]

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

system_prompt_base = """La tua identità è Natascha, un'assistente numerologica personale..."""

project_root_dir = os.path.dirname(os.path.abspath(__file__))
MAPPA_PATH = os.path.join(os.path.dirname(project_root_dir), "mappa_per_chatbot.json")

def carica_dati_mappa_per_chatbot(filepath=MAPPA_PATH):
    try:
        with open(filepath, "r", encoding="utf-8-sig") as f:
            return json.load(f)
    except FileNotFoundError:
        st.warning(f"File '{filepath}' non trovato.")
        return None
    except json.JSONDecodeError:
        st.error(f"Errore nella lettura del file '{filepath}'.")
        return None
    except Exception as e:
        st.error(f"Errore inatteso durante il caricamento della mappa: {e}")
        return None

@st.cache_resource
def get_embedding_model():
    return SentenceTransformer('paraphrase-MiniLM-L6-v2')

def get_relevant_chunks(query, collection, embedding_model, n_results=3):
    query_embedding = embedding_model.encode(query).tolist()
    results = collection.query(query_embeddings=[query_embedding], n_results=n_results)
    if results and results['documents']:
        flat_documents = [item for sublist in results['documents'] for item in sublist]
        return "\n".join(flat_documents)
    return "Nessun contesto aggiuntivo disponibile."

def st_session_message(role, content):
    st.session_state.messages.append({"role": role, "content": content})

def main():
    st.set_page_config(page_title="Chatbot Numerologica Personale", page_icon="🔮")
    st.title("Chatbot Numerologica ✨")
    st.markdown("Chiedimi qualsiasi cosa sulla tua Mappa Numerologica o sui tuoi cicli!")

    if "mappa_numerologica_utente" not in st.session_state:
        st.session_state.mappa_numerologica_utente = carica_dati_mappa_per_chatbot()

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar="😊" if message["role"] == "user" else "🥰"):
            st.markdown(message["content"])

    if prompt := st.chat_input("Cosa vuoi sapere sulla tua numerologia?"):
        with st.chat_message("user", avatar="😊"):
            st.markdown(prompt)
        st_session_message("user", prompt)

        full_gemini_prompt = system_prompt_base
        mappa = st.session_state.mappa_numerologica_utente

        if mappa:
            # Tutti i dati della mappa aggiunti al prompt (omessi qui per brevità)
            full_gemini_prompt += f"\n\nDomanda dell'Utente: {prompt}"

        try:
            with st.spinner("Natascha sta pensando..."):
                resp = model.generate_content(full_gemini_prompt)
                answer = resp.text
        except Exception as e:
            answer = f"Errore nella generazione della risposta: {e}"

        st_session_message('assistant', answer)
        with st.chat_message('assistant', avatar="🥰"):
            st.markdown(answer)
            n = random.choice([1, 2])
            for q in random.sample(reflection_questions, n):
                st.markdown(f"**{q}**")

    # --- Pulsante di Reset Chat (sempre visibile) ---
    st.divider()
    if st.button("🔄 Resetta la conversazione"):
        st.session_state.clear()
        st.rerun()

if __name__ == '__main__':
    main()
