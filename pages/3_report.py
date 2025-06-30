import streamlit as st
import os
import sys

# Aggiunge la cartella 'report' al path per poter importare i moduli
report_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'report'))
if report_dir not in sys.path:
    sys.path.append(report_dir)

# Configurazione della pagina
st.set_page_config(page_title="Report Numerologici", layout="centered")

st.title("📊 Report Numerologici")
st.write("Scegli quale report desideri visualizzare:")

# Menu a tendina
opzione = st.selectbox("Seleziona un report:", [
    "—",
    "Mappa Numerologica",
    "Schema Energetico",
    "Report Chat"
])

# Logica di selezione dei report
if opzione == "Mappa Numerologica":
    try:
        import report_numerologico as modulo
        modulo.run()
    except Exception as e:
        st.error(f"Errore nel caricamento del modulo 'report_numerologico': {e}")

elif opzione == "Schema Energetico":
    try:
        import schema_energetico as modulo
        modulo.run()
    except Exception as e:
        st.error(f"Errore nel caricamento del modulo 'schema_energetico': {e}")

elif opzione == "Report Chat":
    try:
        import report_chat_pdf as modulo_chat
        modulo_chat.run()
    except Exception as e:
        st.error(f"Errore nel caricamento del modulo 'report_chat_pdf': {e}")
