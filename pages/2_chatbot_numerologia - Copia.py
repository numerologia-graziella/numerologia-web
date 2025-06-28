import json
import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os
from pypdf import PdfReader
import chromadb
from sentence_transformers import SentenceTransformer
import random
from datetime import datetime, date # Assicurati che datetime e date siano importati

# Domande riflessive per stimolare il dialogo
reflection_questions = [
    "Questo ti risuona?",
    "Hai esempi concreti di quando hai vissuto questo nella tua vita?",
    "Ti piacerebbe approfondire questo aspetto?",
    "Come potresti applicare questo consiglio nella pratica quotidiana? (es: scrivi 3 azioni pratiche)",
    "C’è qualcosa di cui vorresti sapere di più?",
    "Quali sono le tue riflessioni su quanto detto?"
]

# --- Configurazione Iniziale ---
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

# Prompt di sistema globale per Gemini
system_prompt_base = """La tua identità è Natascha, un'assistente numerologica personale. Il tuo nome è Natascha, non sei un modello linguistico. Sei stata creata per aiutare le persone a comprendere i numeri personali e i micro-cicli annuali e trimestrali.
Il tuo obiettivo principale è fornire una guida chiara, empatica e personalizzata basata sui dati numerologici forniti nel prompt.

Linee guida per la risposta:
- Sii sempre di supporto, positivo e incoraggiante.
- Utilizza un linguaggio semplice e accessibile.
- Evita il gergo numerologico eccessivo, spiegando i termini se necessario.
- Personalizza le tue risposte facendo riferimento diretto ai 'Dati Numerologici dell'Utente' e ai 'Dati del Calendario Dinamico' che ti verranno forniti.
- Se l'utente chiede il significato di un numero o di un ciclo, usa le informazioni fornite e, se appropriato, approfondisci con interpretazioni o consigli pratici.
- Se ti vengono chiesti i micro-cicli attuali, utilizza la "Data di Nascita" dell'utente e la "Data odierna" per identificare e descrivere il quadrimestre e il trimestre in corso tra quelli forniti.
- Se l'utente chiede interpretazioni specifiche dei Pinnacoli o delle Sfide, usa le informazioni fornite e offri consigli pertinenti al periodo di attivazione.
- Se l'utente chiede informazioni su Unione Coesiva, Unione Energetica o Interconnessione Energetica, rispondi riportando il valore esatto dal profilo e fornendo un'interpretazione energetica.
- Mantieni sempre una conversazione aperta e invogliante, ponendo una domanda riflessiva alla fine di ogni risposta per incoraggiare l'utente a continuare il dialogo. Non usare saluti o frasi di chiusura, vai dritto al punto con le tue risposte e termina sempre con una domanda.

Le informazioni che seguiranno sono i 'Dati Numerologici dell'Utente' e i 'Dati del Calendario Dinamico' che userai per personalizzare la tua risposta."""

# --- Percorso per i dati della mappa ---
project_root_dir = os.path.dirname(os.path.abspath(__file__))
MAPPA_PATH = os.path.join(os.path.dirname(project_root_dir), "mappa_per_chatbot.json")


# --- Utility Functions ---

# Funzione per caricare i dati della mappa
def carica_dati_mappa_per_chatbot(filepath=MAPPA_PATH):
    try:
        with open(filepath, "r", encoding="utf-8-sig") as f:
            return json.load(f)
    except FileNotFoundError:
        st.warning(f"File '{filepath}' non trovato. Assicurati di aver generato la mappa.")
        return None
    except json.JSONDecodeError:
        st.error(f"Errore nella lettura del file '{filepath}'. Il file potrebbe essere corrotto.")
        return None
    except Exception as e:
        st.error(f"Si è verificato un errore inatteso durante il caricamento della mappa: {e}")
        return None

# Funzione per ottenere il modello di embedding (per i PDF, se lo usi)
@st.cache_resource
def get_embedding_model():
    return SentenceTransformer('paraphrase-MiniLM-L6-v2')

# Funzione per ottenere chunk rilevanti (per i PDF, se lo usi)
def get_relevant_chunks(query, collection, embedding_model, n_results=3):
    query_embedding = embedding_model.encode(query).tolist()
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results
    )
    # Assicurati che 'documents' non sia vuoto prima di accedere
    if results and results['documents']:
        # Flatten the list of lists into a single list of strings
        flat_documents = [item for sublist in results['documents'] for item in sublist]
        return "\n".join(flat_documents)
    return "Nessun contesto aggiuntivo disponibile."

# Funzione per gestire i messaggi nella sessione di Streamlit
def st_session_message(role, content):
    st.session_state.messages.append({"role": role, "content": content})

# --- Funzione Principale del Chatbot ---
def main():
    st.set_page_config(
        page_title="Chatbot Numerologica Personale",
        page_icon="🔮"
    )
    st.title("Chatbot Numerologica ✨")
    st.markdown("Chiedimi qualsiasi cosa sulla tua Mappa Numerologica o sui tuoi cicli!")

    # Carica la mappa numerologica all'inizio, solo una volta per sessione
    if "mappa_numerologica_utente" not in st.session_state:
        st.session_state.mappa_numerologica_utente = carica_dati_mappa_per_chatbot()
    
    # Inizializza la cronologia della chat se non esiste
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Visualizza i messaggi della cronologia della chat
    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar="😊" if message["role"] == "user" else "🥰"):
            st.markdown(message["content"])

    # Gestione input utente
    if prompt := st.chat_input("Cosa vuoi sapere sulla tua numerologia?"):
        with st.chat_message("user", avatar="😊"):
            st.markdown(prompt)
        st_session_message("user", prompt)


        # Costruzione del prompt per Gemini
        full_gemini_prompt = system_prompt_base
        mappa = st.session_state.mappa_numerologica_utente

        if mappa:
            nome = mappa.get('Nome Completo', 'utente')
            
            # --- Inclusione Dati Personali Base ---
            numeri_personali = {
                "Nome Completo": mappa.get("Nome Completo"),
                "Data di Nascita": mappa.get("Data di Nascita"), # <-- Include la Data di Nascita qui
                "Sentiero di Vita": mappa.get("Sentiero di Vita (Metodo 1 - riduzione 2)"),
                "Numero Espressione": mappa.get("Numero Espressione (riduzione 2)"),
                "Numero Anima": mappa.get("Numero Anima (riduzione 2)"),
                "Numero Personalita": mappa.get("Numero Personalita (riduzione 2)"),
                "Numero Forza": mappa.get("Numero Forza (riduzione 2)"),
                "Numero Dono": mappa.get("Numero Dono (riduzione 2)"),
                "Quintessenza": mappa.get("Quintessenza (riduzione 2)"),
                "Iniziazione Spirituale": mappa.get("Iniziazione Spirituale (riduzione 2)"),
                "Ciclo Esperienza": mappa.get("Ciclo Esperienza (valore)"),
                "Ciclo Potere": mappa.get("Ciclo Potere (valore)"),
                "Ciclo Saggezza": mappa.get("Ciclo Saggezza (valore)")
            }
            # Aggiungi i dati numerologici al prompt solo se presenti
            personal_data_lines = []
            for label, value in numeri_personali.items():
                if value is not None: # Controlla che il valore esista
                    personal_data_lines.append(f"- {label}: {value}")
            if personal_data_lines:
                full_gemini_prompt += "\n\nDati Numerologici dell'Utente:\n" + "\n".join(personal_data_lines)

            # Dettagli sui Pinnacoli e Sfide
            pinnacoli = {k: v for k, v in mappa.items() if k.startswith("Pinnacolo")}
            sfide = {k: v for k, v in mappa.items() if k.startswith("Sfida")}
            if pinnacoli or sfide:
                full_gemini_prompt += "\n\nPinnacoli e Sfide:\n"
                full_gemini_prompt += json.dumps(pinnacoli, indent=2, ensure_ascii=False) + "\n"
                full_gemini_prompt += json.dumps(sfide, indent=2, ensure_ascii=False) + "\n"

            # Valori energetici (Unioni)
            energy = [("Unione Coesiva","Unione Coesiva"), ("Unione Energetica","Unione Energetica"), ("Interconnessione Energetica","Interconnessione Energetica")]
            energy_lines = []
            for label, key in energy:
                val = mappa.get(key,'N/A')
                if val != 'N/A':
                    energy_lines.append(f"- {label}: {val}")
            if energy_lines:
                full_gemini_prompt += "\n--- Valori Energetici (Schema Energetico) ---\n"
                full_gemini_prompt += "\n".join(energy_lines)
                full_gemini_prompt += (
                    "\nSe l'utente chiede informazioni su Unione Coesiva, Unione Energetica "
                    "o Interconnessione Energetica, rispondi riportando il valore esatto dal profilo "
                    "e fornendo un'interpretazione energetica."
                )

            # --- SEZIONE CALENDARIO DINAMICO (CRUCIALE!) ---
            dob_str = mappa.get("Data di Nascita")
            if dob_str:
                try:
                    dob = datetime.strptime(dob_str, "%d/%m/%Y").date()
                    today = date.today() # Data odierna per determinare il ciclo attuale

                    # INIZIO MODIFICA QUI PER RENDERE I DATI DEL CALENDARIO PIÙ ESPLICITI
                    full_gemini_prompt += "\n\nDati del Calendario Dinamico:\n"
                    # Aggiungi anni base e data odierna prima
                    full_gemini_prompt += f"- Anno di Riferimento Calendario: {mappa.get('anno_di_riferimento_calendario', '')}\n"
                    full_gemini_prompt += f"- Anno Universale Base: {mappa.get('anno_universale_base', '')}\n"
                    full_gemini_prompt += f"- Anno Personale Base: {mappa.get('anno_personale_base', '')}\n"
                    full_gemini_prompt += f"- Data Odierna: {today.strftime('%d/%m/%Y')}\n"

                    # Poi aggiungi i dettagli dei quadrimestri e trimestri
                    quadrimestri = mappa.get("micro_cicli_quadrimestri_calendario", [])
                    trimestri = mappa.get("micro_pinnacoli_sfide_trimestri_calendario", [])

                    if quadrimestri:
                        full_gemini_prompt += "\n--- Micro Cicli (Quadrimestri Completi) ---\n"
                        for q in quadrimestri:
                            full_gemini_prompt += f"  - Q: {q.get('Q')}, Inizio: {q.get('Inizio')}, Fine: {q.get('Fine')}, Micro cicli annuali: {q.get('Micro cicli annuali')}\n"

                    if trimestri:
                        full_gemini_prompt += "\n--- Micro Pinnacoli e Sfide (Trimestri Completi) ---\n"
                        for t in trimestri:
                            full_gemini_prompt += f"  - Trimestre: {t.get('Trimestre')}, Inizio: {t.get('Inizio')}, Fine: {t.get('Fine')}, Micro-Pinnacoli: {t.get('Micro-Pinnacoli')}, MicroSfide: {t.get('MicroSfide')}\n"

                    # Logica per determinare il micro ciclo attuale e aggiungerlo al prompt (rimane invariata)
                    current_q = None
                    for q in quadrimestri:
                        try:
                            q_start = datetime.strptime(q['Inizio'], "%d/%m/%Y").date()
                            q_end = datetime.strptime(q['Fine'], "%d/%m/%Y").date()
                            if q_start <= today <= q_end:
                                current_q = q
                                break
                        except ValueError:
                            pass # Ignora se la data non è nel formato atteso

                    if current_q:
                        full_gemini_prompt += f"\n\nMicro ciclo annuale ATTUALE (Quadrimestre): Q{current_q['Q'].replace('Q','')}, Inizio: {current_q['Inizio']}, Fine: {current_q['Fine']}, Valore: {current_q['Micro cicli annuali']}"

                    current_t = None
                    for t in trimestri:
                        try:
                            t_start = datetime.strptime(t['Inizio'], "%d/%m/%Y").date()
                            t_end = datetime.strptime(t['Fine'], "%d/%m/%Y").date()
                            if t_start <= today <= t_end:
                                current_t = t
                                break
                        except ValueError:
                            pass # Ignora se la data non è nel formato atteso

                    if current_t:
                        full_gemini_prompt += f"\nMicro Pinnacolo e Sfida ATTUALI (Trimestre): Trimestre {current_t['Trimestre'].replace('T','')}, Inizio: {current_t['Inizio']}, Fine: {current_t['Fine']}, Pinnacolo: {current_t['Micro-Pinnacoli']}, Sfida: {current_t['MicroSfide']}"

                    # FINE MODIFICA QUI

                except ValueError:
                    full_gemini_prompt += "\nAttenzione: Impossibile elaborare la data di nascita dal file della mappa per i calcoli del calendario. Formato non valido."
                except Exception as e:
                    full_gemini_prompt += f"\nAttenzione: Errore durante l'elaborazione o l'aggiunta dei dati del calendario al prompt: {e}"
            else:
                full_gemini_prompt += "\nAttenzione: La data di nascita non è disponibile nel file della mappa per i calcoli del calendario dinamico."
            
            # Contesto dai PDF (se presente)
            # Assicurati che le tue collezioni ChromaDB e il modello di embedding siano inizializzati correttamente altrove
            # Se non usi i PDF, puoi commentare o rimuovere questa sezione
            if st.session_state.get('vector_collection') and st.session_state.get('embedding_model_instance'):
                try:
                    ctx = get_relevant_chunks(prompt, st.session_state.vector_collection, st.session_state.embedding_model_instance)
                    full_gemini_prompt += f"\n\nContesto Generale (dai PDF):\n{ctx}"
                except Exception as e:
                    full_gemini_prompt += f"\nAttenzione: Errore nel recupero del contesto dai PDF: {e}"

        full_gemini_prompt += f"\n\nDomanda dell'Utente: {prompt}"

        # Genera risposta
        try:
            with st.spinner("Natascha sta pensando..."):
                resp = model.generate_content(full_gemini_prompt)
                answer = resp.text
        except Exception as e:
            answer = f"Errore nella generazione della risposta: {e}"

        st_session_message('assistant', answer)
        with st.chat_message('assistant', avatar="🥰") as msg:
            st.markdown(answer)
            # Domande riflessive random
            n = random.choice([1, 2])
            for q in random.sample(reflection_questions, n):
                st.markdown(f"**{q}**")
            
# Assicurati che 'main()' venga chiamato solo quando lo script è eseguito direttamente
if __name__ == '__main__':
    main()
