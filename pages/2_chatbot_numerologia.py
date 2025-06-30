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

# --- Domande riflessive ---
reflection_questions = [
    "Questo ti risuona?",
    "Hai esempi concreti di quando hai vissuto questo nella tua vita?",
    "Ti piacerebbe approfondire questo aspetto?",
    "Come potresti applicare questo consiglio nella pratica quotidiana? (es: scrivi 3 azioni pratiche)",
    "C’è qualcosa di cui vorresti sapere di più?",
    "Quali sono le tue riflessioni su quanto detto?"
]

# --- API Key ---
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    st.error("❌ GOOGLE_API_KEY mancante nel file .env o nei secrets di Streamlit Cloud.")
    st.stop()

# --- Configura modello ---
genai.configure(api_key=api_key)
try:
    model = genai.GenerativeModel('models/gemini-1.5-flash')
except Exception as e:
    st.error(f"Errore nella configurazione del modello Gemini: {e}")
    st.stop()

# --- Prompt base ---
system_prompt_base = """La tua identità è Natascha, un'assistente numerologica personale. Parla sempre in tono gentile, rassicurante e coinvolgente. Offri interpretazioni numerologiche basate sui dati dell'utente, incluse informazioni sulla sua mappa, cicli personali, pinnacoli e sfide. Quando non trovi dati, chiedi gentilmente di generarli nella sezione Mappa Numerologica."""

# --- Percorso mappa ---
project_root_dir = os.path.dirname(os.path.abspath(__file__))
MAPPA_PATH = os.path.join(os.path.dirname(project_root_dir), "mappa_per_chatbot.json")

# --- Carica dati JSON ---
def carica_dati_mappa_per_chatbot(filepath=MAPPA_PATH):
    try:
        with open(filepath, "r", encoding="utf-8-sig") as f:
            return json.load(f)
    except FileNotFoundError:
        return None
    except json.JSONDecodeError:
        st.error(f"❌ Errore nella lettura del file '{filepath}'.")
        return None
    except Exception as e:
        st.error(f"❌ Errore inatteso durante il caricamento della mappa: {e}")
        return None

# --- Embedding (non usato al momento ma utile) ---
@st.cache_resource
def get_embedding_model():
    return SentenceTransformer('paraphrase-MiniLM-L6-v2')

# --- Sessione messaggi ---
def st_session_message(role, content):
    st.session_state.messages.append({"role": role, "content": content})

# --- MAIN ---
def main():
    st.set_page_config(page_title="Chatbot Numerologica Personale", page_icon="🔮")
    st.title("Chatbot Numerologica ✨")
    st.markdown("Chiedimi qualsiasi cosa sulla tua Mappa Numerologica o sui tuoi cicli!")

    # --- Carica dati in sessione ---
    if "mappa_numerologica_utente" not in st.session_state:
        st.session_state.mappa_numerologica_utente = carica_dati_mappa_per_chatbot()

    # --- Feedback visivo nella sidebar ---
    with st.sidebar:
        if st.session_state.mappa_numerologica_utente:
            st.success("✅ Dati mappa caricati.")
        else:
            st.warning("⚠️ Nessun dato disponibile. Vai alla sezione Mappa Numerologica e genera la tua mappa.")

    # --- Messaggi utente precedenti ---
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar="😊" if message["role"] == "user" else "🥰"):
            st.markdown(message["content"])

    # --- Input chat ---
    if prompt := st.chat_input("Cosa vuoi sapere sulla tua numerologia?"):
        with st.chat_message("user", avatar="😊"):
            st.markdown(prompt)
        st_session_message("user", prompt)

        # --- Prompt completo ---
        full_gemini_prompt = system_prompt_base
        mappa = st.session_state.mappa_numerologica_utente

        if mappa:
            calendario_info = ""

            if "micro_cicli_quadrimestri_calendario" in mappa:
                calendario_info += "\n\n📅 Micro Cicli Quadrimestrali:\n"
                for item in mappa["micro_cicli_quadrimestri_calendario"]:
                    calendario_info += f"{item['Q']}: {item['Inizio']} - {item['Fine']} → {item['Micro cicli annuali']}\n"

            if "micro_pinnacoli_sfide_trimestri_calendario" in mappa:
                calendario_info += "\n\n🌄️ Micro Pinnacoli e Sfide Trimestrali:\n"
                for item in mappa["micro_pinnacoli_sfide_trimestri_calendario"]:
                    calendario_info += f"{item['Trimestre']}: {item['Inizio']} - {item['Fine']}, Pinnacolo: {item['Micro-Pinnacoli']}, Sfida: {item['MicroSfide']}\n"

            full_gemini_prompt += "\n\n📂 Dati Utente:\n"
            for k, v in mappa.items():
                if isinstance(v, str | int | float):
                    full_gemini_prompt += f"- {k}: {v}\n"
            full_gemini_prompt += calendario_info
            full_gemini_prompt += f"\n\nDomanda dell'Utente: {prompt}"

        else:
            full_gemini_prompt += f"\n\n⚠️ Nessun dato utente disponibile. La risposta sarà generica.\n\nDomanda dell'Utente: {prompt}"

        # --- Chiamata a Gemini ---
        try:
            with st.spinner("Natascha sta pensando..."):
                resp = model.generate_content(full_gemini_prompt)
                answer = resp.text
        except Exception as e:
            answer = f"❌ Errore nella generazione della risposta: {e}"

        # --- Risposta nella UI ---
        st_session_message('assistant', answer)
        with st.chat_message('assistant', avatar="🥰"):
            st.markdown(answer)
            for q in random.sample(reflection_questions, k=random.choice([1, 2])):
                st.markdown(f"**{q}**")

    # --- Pulsante reset chat ---
    st.divider()
    if st.button("🔄 Resetta la conversazione"):
        st.session_state.clear()
        st.rerun()

if __name__ == '__main__':
    main()
