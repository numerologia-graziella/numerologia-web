import streamlit as st
import os
import sys

# Aggiungi la cartella 'report' al percorso
report_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'report'))
if report_dir not in sys.path:
    sys.path.append(report_dir)

# Imposta la pagina
st.set_page_config(page_title="Report Numerologici", layout="centered")

st.title("📊 Report Numerologici")
st.write("Scegli quale report desideri visualizzare:")

opzione = st.selectbox("Seleziona un report:", [
    "—",
    "Mappa Numerologica",
    "Schema Energetico",
    "Report Chat" # <--- HO AGGIUNTO QUESTA RIGA QUI!
])

if opzione == "Mappa Numerologica":
    import report_numerologico as modulo
    modulo.run()

elif opzione == "Schema Energetico":
    import schema_energetico as modulo
    modulo.run()

elif opzione == "Report Chat": # <--- HO AGGIUNTO ANCHE QUESTO BLOCCO!
    import report_chat_pdf as modulo_chat
    modulo_chat.run()
