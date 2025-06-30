import streamlit as st
from datetime import datetime, date
import calendar
import pandas as pd
import io

st.set_page_config(
    page_title="Calendario Dinamico Numerologico",
    page_icon="📅"
)
st.title("Calendario Dinamico Numerologico")

# ---- Utility numerologiche ----
def riduci_numero(n: int) -> int:
    while n > 9 and n not in (11, 22, 33):
        n = sum(int(c) for c in str(n))
    return n

def anno_universale(anno: int) -> int:
    return riduci_numero(sum(int(c) for c in str(anno)))

def calcola_microcicli(dob: date, anno_ref: int) -> dict:
    uni_base = anno_universale(anno_ref)
    uni_next = anno_universale(anno_ref + 1)
    rid_g = riduci_numero(dob.day)
    rid_m = riduci_numero(dob.month)
    raw = rid_g + rid_m + uni_base
    personal = riduci_numero(raw)
    return {
        'anno_ref': anno_ref,
        'uni_base': uni_base,
        'uni_next': uni_next,
        'raw_personal': raw,
        'personal': personal
    }

# ---- Estrai dati da session_state (non da file!) ----
mappa = st.session_state.get("mappa_numerologica_corrente", None)

if not mappa:
    st.warning("Devi prima generare la tua mappa numerologica nella pagina 'Mappa Numerologica'.")
    st.stop()

nome = mappa.get("Nome Completo", "")
dob_str = mappa.get("Data di Nascita", "")
sentiero = mappa.get("Sentiero di Vita (Metodo 1 - riduzione 2)", 0)
forza = mappa.get("Numero Forza (riduzione 2)", 0)

try:
    dob = datetime.strptime(dob_str, "%d/%m/%Y").date()
except ValueError:
    st.error("Formato data di nascita non valido. Controlla la pagina Mappa Numerologica.")
    st.stop()

# ---- Calcoli base ----
today = date.today()
last_year = today.year if (today.month, today.day) >= (dob.month, dob.day) else today.year - 1
m1 = calcola_microcicli(dob, last_year)
m2 = calcola_microcicli(dob, last_year + 1)

st.subheader(f"Dati di **{nome}**")
st.write(f"- Data di Nascita: **{dob.strftime('%d/%m/%Y')}**")
st.write(f"- Sentiero di Vita: **{sentiero}**")
st.write(f"- Numero di Forza: **{forza}**")

# ---- Qui puoi continuare la tua logica come già la avevi ----
# (Per microcicli, pinnacoli ecc., basta usare `dob`, `sentiero`, `m1`, `m2`)
