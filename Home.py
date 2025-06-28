import streamlit as st
import os
from pathlib import Path

# --- PATH PER IL FILE JSON DELLA MAPPA ---
MAPPA_PATH = Path("mappa_per_chatbot.json")

# --- FUNZIONE PER CANCELLARE IL FILE JSON ESISTENTE ---
def clear_existing_map_file_and_get_feedback():
    print(f"\n--- DEBUG CANCELLAZIONE (da Home.py) ---")
    print(f"Tentativo di cancellare il file: {MAPPA_PATH.absolute()}")
    
    if MAPPA_PATH.exists():
        print(f"DEBUG: Il file '{MAPPA_PATH.name}' ESISTE.")
        try:
            os.remove(MAPPA_PATH)
            print(f"DEBUG: Il file '{MAPPA_PATH.name}' è stato rimosso con successo.")
            return "Il file JSON della mappa precedente è stato rimosso."
        except OSError as e:
            print(f"ERRORE DEBUG: Impossibile rimuovere il file '{MAPPA_PATH.name}': {e}")
            return f"Errore durante la rimozione del file JSON: {e}. Controlla i permessi o se il file è in uso."
    else:
        print(f"DEBUG: Il file '{MAPPA_PATH.name}' NON ESISTE.")
        return "Nessun file JSON della mappa precedente trovato da rimuovere."

# --- Configurazione della pagina di Streamlit ---
st.set_page_config(
    page_title="La Mia App di Numerologia",
    page_icon="✨",
    layout="centered"
)

# --- Chiama la funzione di cancellazione e memorizza il feedback ---
feedback_msg = clear_existing_map_file_and_get_feedback()

# --- Mostra il feedback nella sidebar DOPO che st.set_page_config è stato eseguito ---
if "Errore" in feedback_msg:
    st.sidebar.error(feedback_msg)
else:
    st.sidebar.info(feedback_msg)

# --- Contenuto della pagina Home ---
st.title("Benvenuta nell'App Completa di Numerologia ✨")

# --- NUOVO TESTO ESPLICATIVO SULLA NUMEROLOGIA ALLINEATO A DESTRA ---
# Usiamo HTML con uno stile per l'allineamento a destra.
# Il testo è racchiuso in un div con style="text-align: right;".
st.markdown(
    """
    <div style="text-align: justify;">
        **La Numerologia** è una disciplina affascinante che funge contemporaneamente da strumento pratico
        e di grande utilità. Il suo obiettivo principale è consentire alle persone di conoscere sé stesse, 
        decifrare i propri meccanismi psicologici profondi e i cicli personali.
        Nella Numerologia, i numeri sono considerati contenitori che rappresentano un progetto, indicando
        ciò che l'individuo è destinato a diventare. La polarità di ogni numero offre la possibilità di 
        scegliere quale aspetto sviluppare, influenzando il modo in cui si vive questa dualità. 
        Secondo Carl Gustav Jung, i numeri sono simboli, archetipi dell'ordine che diventa cosciente. 
        Jung, psichiatra, psicoanalista, antropologo e filosofo svizzero, considerava i numeri come rappre-
        sentazioni simboliche dell'ordine cosmico che diventano consapevoli nella psiche umana. Quindi, 
        nella prospettiva di Jung, i numeri non sono solo simboli matematici, ma anche simboli profondi 
        che riflettono l'ordine e la struttura dell'inconscio collettivo.
    </div>
    """,
    unsafe_allow_html=True # Questo è FONDAMENTALE per permettere a Streamlit di renderizzare l'HTML.
)

st.markdown("---") # Linea separatrice per chiarezza

# --- FRASE SUL MENU SPOSTATA QUI SOTTO ---
st.write("Usa il menu a sinistra per navigare tra le diverse sezioni:")

 #st.markdown("""
#- **Mappa Numerologica:** Calcola la mappa personale inserendo nome, cognome e data di nascita.
#- **Chatbot di Numerologia:** Chiedi informazioni generali sulla numerologia, basate sui miei documenti.
#""")

# Streamlit rileverà automaticamente i file Python presenti nella sottocartella './pages/'
# e creerà la sidebar di navigazione con i link a queste pagine.
