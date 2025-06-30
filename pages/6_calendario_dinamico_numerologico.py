import streamlit as st
from pathlib import Path
import json
from datetime import datetime, date
import calendar
import pandas as pd
import io

# --- Configurazione pagina ---
st.set_page_config(page_title="Calendario Dinamico Numerologico", page_icon="📅")
st.title("Calendario Dinamico Numerologico")

# --- Percorso JSON ---
MAPPA_PATH = Path("mappa_per_chatbot.json")

# ----- Utility -----
def riduci_numero(n):
    while n > 9 and n not in [11, 22, 33]:
        n = sum(int(c) for c in str(n))
    return n

def anno_universale(anno):
    return riduci_numero(sum(int(c) for c in str(anno)))

def calcola_microcicli(dob, anno_ref):
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

def genera_tabella_quadrimestri(dob, anno_ref, m1, m2, sent):
    base_idx = dob.month - 1
    sent_red = riduci_numero(sent)
    raw_vals = [
        m1['uni_next'] + m1['personal'],
        sent_red + riduci_numero(m1['uni_next'] + m1['personal']),
        riduci_numero(m1['uni_next'] + m1['personal']) + riduci_numero(sent_red + riduci_numero(m1['uni_next'] + m1['personal'])),
        m2['uni_next'] + m2['personal'],
        sent_red + riduci_numero(m2['uni_next'] + m2['personal']),
        riduci_numero(m2['uni_next'] + m2['personal']) + riduci_numero(sent_red + riduci_numero(m2['uni_next'] + m2['personal'])),
    ]
    rows = []
    for i, raw in enumerate(raw_vals):
        red = riduci_numero(raw)
        offset = base_idx + i * 4
        sy = anno_ref + offset // 12
        sm = (offset % 12) + 1
        ey = anno_ref + (offset + 3) // 12
        em = ((offset + 3) % 12) + 1
        start = date(sy, sm, 1)
        end = date(ey, em, calendar.monthrange(ey, em)[1])
        rows.append({
            'Q': f"Q{i+1}",
            'Inizio': start.strftime("%d/%m/%Y"),
            'Fine': end.strftime("%d/%m/%Y"),
            'Micro cicli annuali': f"{raw} → {red}"
        })
    return pd.DataFrame(rows)

# --- Main ---
def main():
    if not MAPPA_PATH.exists():
        st.warning("Per favore genera prima la tua Mappa Numerologica dalla sezione dedicata.")
        return

    try:
        with open(MAPPA_PATH, "r", encoding="utf-8") as f:
            record = json.load(f)
    except Exception as e:
        st.error(f"Errore durante il caricamento della mappa: {e}")
        return

    nome = record.get("Nome Completo", "")
    dob_str = record.get("Data di Nascita", "")
    sentiero = record.get("Sentiero di Vita (Metodo 1 - riduzione 2)", 0)
    forza = record.get("Numero Forza (riduzione 2)", 0)

    if not nome or not dob_str:
        st.error("Dati essenziali mancanti. Ritorna alla Mappa Numerologica per rigenerarli.")
        return

    try:
        dob = datetime.strptime(dob_str, "%d/%m/%Y").date()
    except Exception:
        st.error("Formato data di nascita non valido nel file JSON.")
        return

    today = date.today()
    last_year = today.year if (today.month, today.day) >= (dob.month, dob.day) else today.year - 1
    m1 = calcola_microcicli(dob, last_year)
    m2 = calcola_microcicli(dob, last_year + 1)

    st.subheader(f"Dati di {nome}")
    st.write(f"- Data di Nascita: **{dob.strftime('%d/%m/%Y')}**")
    st.write(f"- Sentiero di Vita: **{sentiero}**")
    st.write(f"- Numero di Forza: **{forza}**")

    df_quad = genera_tabella_quadrimestri(dob, last_year, m1, m2, sentiero)
    st.subheader("Micro Cicli Annuali per Quadrimestri")
    st.dataframe(df_quad)

    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine='xlsxwriter') as writer:
        df_quad.to_excel(writer, index=False, sheet_name="Micro Cicli")
    st.download_button(
        label="📦 Scarica Micro Cicli in Excel",
        data=buf.getvalue(),
        file_name="micro_cicli_quadrimestri.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

if __name__ == "__main__":
    main()
