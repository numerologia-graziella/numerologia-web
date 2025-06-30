import streamlit as st
from pathlib import Path
import json
from datetime import datetime, date
import calendar
import pandas as pd
import io

# --- Config pagina ---
st.set_page_config(page_title="Calendario Dinamico Numerologico", page_icon="📅")
st.title("Calendario Dinamico Numerologico")

# --- Path JSON ---
MAPPA_PATH = "mappa_per_chatbot.json"


def riduci_numero(n):
    while n > 9 and n not in (11, 22, 33):
        n = sum(int(c) for c in str(n))
    return n

def anno_universale(anno):
    return riduci_numero(sum(int(c) for c in str(anno)))

def calcola_microcicli(dob, anno_ref):
    base = anno_universale(anno_ref)
    next_ = anno_universale(anno_ref + 1)
    raw = riduci_numero(dob.day) + riduci_numero(dob.month) + base
    personale = riduci_numero(raw)
    return {'anno_ref': anno_ref, 'uni_base': base, 'uni_next': next_, 'raw': raw, 'personale': personale}

def genera_tabella_quadrimestri(dob, anno_ref, m1, m2, sentiero):
    base_idx = dob.month - 1
    sent = riduci_numero(sentiero)
    raw_vals = [
        m1['uni_next'] + m1['personale'],
        sent + riduci_numero(m1['uni_next'] + m1['personale']),
        riduci_numero(m1['uni_next'] + m1['personale']) + riduci_numero(sent + riduci_numero(m1['uni_next'] + m1['personale'])),
        m2['uni_next'] + m2['personale'],
        sent + riduci_numero(m2['uni_next'] + m2['personale']),
        riduci_numero(m2['uni_next'] + m2['personale']) + riduci_numero(sent + riduci_numero(m2['uni_next'] + m2['personale'])),
    ]
    rows = []
    for i, raw in enumerate(raw_vals):
        red = riduci_numero(raw)
        offset = base_idx + i*4
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

def main():
    try:
        if not MAPPA_PATH.exists():
            st.warning("⚠️ Genera prima la mappa numerologica.")
            return
        with open(MAPPA_PATH, encoding='utf-8') as f:
            record = json.load(f)
    except Exception as e:
        st.error(f"Errore caricamento file: {e}")
        return

    nome = record.get("Nome Completo", "")
    dob_str = record.get("Data di Nascita", "")
    sentiero = record.get("Sentiero di Vita (Metodo 1 - riduzione 2)", 0)
    forza = record.get("Numero Forza (riduzione 2)", 0)

    if not nome or not dob_str:
        st.warning("Nome o data mancanti. Rigenera la mappa numerologica.")
        return
    try:
        dob = datetime.strptime(dob_str, "%d/%m/%Y").date()
    except:
        st.error("Formato data errato.")
        return

    today = date.today()
    last_year = today.year if (today.month, today.day) >= (dob.month, dob.day) else today.year - 1
    m1 = calcola_microcicli(dob, last_year)
    m2 = calcola_microcicli(dob, last_year + 1)

    st.subheader(f"Dati di {nome}")
    st.write(f"- Data di Nascita: **{dob.strftime('%d/%m/%Y')}**")
    st.write(f"- Sentiero di Vita: **{sentiero}**")
    st.write(f"- Numero di Forza: **{forza}**")

    st.markdown("---")
    df_quad = genera_tabella_quadrimestri(dob, last_year, m1, m2, sentiero)
    st.subheader("Micro Cicli (Quadrimestri)")
    st.table(df_quad)

    # Tabella Micro Pinnacoli e Micro Sfide (Trimestri)
    st.markdown("---")
    st.subheader("Micro Pinnacoli e Micro Sfide (Trimestri)")
    rows, mp_vals, sf_vals = [], [], []
    for i in range(8):
        sm = 1 + i*3
        sy = last_year + (sm - 1) // 12
        sm = ((sm - 1) % 12) + 1
        em = ((sm + 2 - 1) % 12) + 1
        ey = sy + (sm + 2 - 1) // 12
        start = date(sy, sm, 1)
        end = date(ey, em, calendar.monthrange(ey, em)[1])

        if i == 0:
            raw_mp, raw_sf = m1['uni_base'] + forza, abs(m1['uni_base'] - forza)
        elif i == 1:
            raw_mp, raw_sf = forza + m1['personale'], abs(forza - m1['personale'])
        elif i == 2:
            raw_mp, raw_sf = mp_vals[0] + mp_vals[1], abs(sf_vals[0] - sf_vals[1])
        elif i == 3:
            raw_mp, raw_sf = m1['uni_base'] + m1['personale'], abs(m1['uni_base'] - m1['personale'])
        elif i == 4:
            raw_mp, raw_sf = m2['uni_base'] + forza, abs(m2['uni_base'] - forza)
        elif i == 5:
            raw_mp, raw_sf = forza + m2['personale'], abs(forza - m2['personale'])
        elif i == 6:
            raw_mp, raw_sf = mp_vals[4] + mp_vals[5], abs(sf_vals[4] - sf_vals[5])
        else:
            raw_mp, raw_sf = m2['uni_base'] + m2['personale'], abs(m2['uni_base'] - m2['personale'])

        mp = riduci_numero(raw_mp)
        sf = riduci_numero(raw_sf)
        mp_vals.append(mp)
        sf_vals.append(sf)
        rows.append({
            'Trimestre': f"T{i+1}",
            'Inizio': start.strftime('%d/%m/%Y'),
            'Fine': end.strftime('%d/%m/%Y'),
            'Micro-Pinnacoli': f"{raw_mp} → {mp}",
            'MicroSfide': f"{raw_sf} → {sf}"
        })
    df_ms = pd.DataFrame(rows)
    st.table(df_ms)

    st.markdown("---")
    if st.button("📤 Esporta su mappa_per_chatbot.json"):
        try:
            record["micro_cicli_quadrimestri_calendario"] = df_quad.to_dict(orient="records")
            record["micro_pinnacoli_sfide_trimestri_calendario"] = df_ms.to_dict(orient="records")
            with open(MAPPA_PATH, "w", encoding="utf-8") as f:
                json.dump(record, f, indent=4, ensure_ascii=False)
            st.success("Dati calendario aggiornati nel file JSON.")
        except Exception as e:
            st.error(f"Errore salvataggio: {e}")

if __name__ == "__main__":
    main()
