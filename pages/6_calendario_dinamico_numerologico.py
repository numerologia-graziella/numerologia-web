import streamlit as st
from pathlib import Path
import json
from datetime import datetime, date
import calendar
import pandas as pd
import io

# --- Configurazione pagina ---
st.set_page_config(
    page_title="Calendario Dinamico Numerologico",
    page_icon="📅"
)
st.title("Calendario Dinamico Numerologico")

# --- Percorso JSON ---
BASE_DIR = Path(__file__).parent.parent.resolve()
MAPPA_PATH = BASE_DIR / "mappa_per_chatbot.json"

# ----- Utility -----
def riduci_numero(n: int) -> int:
    """Riduce un numero a una singola cifra, eccetto 11, 22, 33 (Numeri Maestri)."""
    while n > 9:
        n = sum(int(c) for c in str(n))
    return n

def anno_universale(anno: int) -> int:
    """Calcola l'Anno Universale per un dato anno."""
    return riduci_numero(sum(int(c) for c in str(anno)))

def calcola_microcicli(dob: date, anno_ref: int) -> dict:
    """Calcola i micro-cicli annuali per un anno di riferimento."""
    uni_base = anno_universale(anno_ref)
    uni_next = anno_universale(anno_ref + 1)
    rid_g = riduci_numero(dob.day)
    rid_m = riduci_numero(dob.month)
    raw = rid_g + rid_m + uni_base
    personal = riduci_numero(raw)
    return {
        'anno_ref':      anno_ref,
        'uni_base':      uni_base,
        'uni_next':      uni_next,
        'raw_personal': raw,
        'personal':      personal
    }

def genera_tabella_quadrimestri(dob: date, anno_ref: int, m1: dict, m2: dict, sent: int) -> pd.DataFrame:
    """Genera la tabella dei micro cicli annuali per quadrimestri."""
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
        offset = base_idx + i*4
        sy = anno_ref + offset // 12
        sm = (offset % 12) + 1
        ey = anno_ref + (offset + 3) // 12
        em = ((offset + 3) % 12) + 1
        start = date(sy, sm, 1)
        end = date(ey, em, calendar.monthrange(ey, em)[1])
        rows.append({
            'Q': f"Q{i+1}",
            'Inizio': start.strftime("%d/%m/%Y"), # <-- Modifica questa riga
            'Fine':   end.strftime("%d/%m/%Y"),   # <-- Modifica questa riga    
            'Micro cicli annuali': f"{raw} → {red}"
        })
    return pd.DataFrame(rows)

# --- Funzione principale della pagina Streamlit ---
def main():
    # --- Gestione Caricamento JSON ---
    record = {} # Inizializza record come dizionario vuoto
    try:
        # Aggiungo un controllo esplicito dell'esistenza del file
        if not MAPPA_PATH.exists():
            raise FileNotFoundError(f"Il file '{MAPPA_PATH.name}' non è stato trovato al percorso specificato.")

        record = json.load(open(MAPPA_PATH, encoding='utf-8'))
        # st.success("File mappa_per_chatbot.json caricato con successo!") # Puoi anche rimuovere questo se non vuoi il messaggio di successo
    except FileNotFoundError as e:
        st.warning("Per visualizzare il calendario dinamico, devi prima generare la tua **Mappa Numerologica**.")
        st.info("Vai alla pagina **Mappa Numerologica** (nella sidebar) e inserisci i tuoi dati per creare o aggiornare il file della mappa.")
        st.error(f"Errore: {e}") # Mostra l'errore esatto del percorso
        return # Esci dalla funzione main se il file non viene trovato
    except json.JSONDecodeError:
        st.error("Errore nella lettura del file della mappa. Il file potrebbe essere corrotto. Per favor, rigenera la tua Mappa Numerologica.")
        return # Esci dalla funzione main in caso di errore JSON
    except Exception as e:
        st.error(f"Si è verificato un errore inatteso durante il caricamento della mappa: {e}")
        return # Esci dalla funzione main in caso di altri errori

    # --- Estrazione Dati dal JSON ---
    nome     = record.get("Nome Completo", "")
    dob_str  = record.get("Data di Nascita", "")
    sentiero = record.get("Sentiero di Vita (Metodo 1 - riduzione 2)", 0)
    forza    = record.get("Numero Forza (riduzione 2)", 0)

    # Controllo che i dati essenziali siano presenti nel JSON
    if not nome or not dob_str:
        st.error("Dati essenziali (Nome o Data di Nascita) mancanti nel file della mappa.")
        st.info("Per favore, assicurati di compilare tutti i campi nella pagina **Mappa Numerologica** e rigenera la mappa.")
        return # Esci se i dati sono incompleti

    # Tentativo di convertire la data di nascita
    try:
        dob = datetime.strptime(dob_str, "%d/%m/%Y").date()
    except ValueError:
        st.error("Formato Data di Nascita non valido (GG/MM/AAAA) nel file della mappa.")
        st.info("Per favor, controlla i dati e rigenera la tua Mappa Numerologica nella pagina apposita.")
        return # Esci se il formato data è errato

    # --- Calcoli e Display del Calendario ---
    today = date.today()
    last_year = today.year if (today.month, today.day) >= (dob.month, dob.day) else today.year - 1
    m1 = calcola_microcicli(dob, last_year)
    m2 = calcola_microcicli(dob, last_year + 1)

    st.subheader(f"Dati di **{nome}**")
    st.write(f"- Data di Nascita: **{dob.strftime('%d/%m/%Y')}**")
    st.write(f"- Sentiero di Vita: **{sentiero}**")
    st.write(f"- Numero di Forza: **{forza}**")

    with st.expander("Mostra Dettagli Micro Cicli Iniziali"):
        st.write(f"Anno rif. ultimo compleanno: **{m1['anno_ref']}**")
        st.write(f"Anno Universale in corso (del tuo ultimo compleanno): {m1['uni_base']}")
        st.write(f"Anno Universale che verrà (del tuo prossimo compleanno): {m1['uni_next']}")
        st.write(f"Anno Personale intero: {m1['raw_personal']}")
        st.write(f"Anno Personale ridotto: {m1['personal']}")
        st.markdown("---")
        st.write(f"Anno rif. prossimo compleanno: **{m2['anno_ref']}**")
        st.write(f"Anno Universale in corso (del tuo prossimo compleanno): {m2['uni_base']}")
        st.write(f"Anno Universale che verrà (dell'anno successivo): {m2['uni_next']}")
        st.write(f"Anno Personale intero: {m2['raw_personal']}")
        st.write(f"Anno Personale ridotto: {m2['personal']}")

    st.markdown("---")

    # Tabella Micro Cicli (Quadrimestri)
    df_quad = genera_tabella_quadrimestri(dob, last_year, m1, m2, sentiero)
    st.subheader("Tabella Micro Cicli (Quadrimestri)")
    st.table(df_quad)

    # Tabella MicroPinnacoli e MicroSfide (Trimestri)
    rows, mp_vals, sf_vals = [], [], []
    for i in range(8):
        start_month = 1 + i*3
        y = last_year + (start_month - 1) // 12
        sm = ((start_month - 1) % 12) + 1
        start = date(y, sm, 1)
        em = ((sm + 2 - 1) % 12) + 1
        ey = y + (sm + 2 - 1) // 12
        end = date(ey, em, calendar.monthrange(ey, em)[1])

        if i == 0:
            raw_mp, raw_sf = m1['uni_base'] + forza, m1['uni_base'] - forza
        elif i == 1:
            raw_mp, raw_sf = forza + m1['personal'], forza - m1['personal']
        elif i == 2:
            raw_mp, raw_sf = mp_vals[0] + mp_vals[1], sf_vals[0] - sf_vals[1]
        elif i == 3:
            raw_mp, raw_sf = m1['uni_base'] + m1['personal'], m1['uni_base'] - m1['personal']
        elif i == 4:
            raw_mp, raw_sf = m2['uni_base'] + forza, m2['uni_base'] - forza
        elif i == 5:
            raw_mp, raw_sf = forza + m2['personal'], forza - m2['personal']
        elif i == 6:
            raw_mp, raw_sf = mp_vals[4] + mp_vals[5], sf_vals[4] - sf_vals[5]
        else:
            raw_mp, raw_sf = m2['uni_base'] + m2['personal'], m2['uni_base'] - m2['personal']

        raw_sf = abs(raw_sf)
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
    st.subheader("MicroPinnacoli e MicroSfide (Trimestri)")
    st.table(df_ms)

    # --- Sezione Download Excel ---
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine='xlsxwriter') as writer:
        pd.DataFrame({
            'Campo': ['Nome', 'Data di Nascita', 'Sentiero di Vita', 'Numero di Forza'],
            'Valore': [nome, dob.strftime('%d/%m/%Y'), sentiero, forza]
        }).to_excel(writer, sheet_name='Dati Utente', index=False)
        pd.DataFrame({
            'Parametro': ['Anno rif ultimo', 'Uni in corso', 'Uni che verrà', 'Anno pers intero', 'Anno pers ridotto'],
            'Valore': [m1['anno_ref'], m1['uni_base'], m1['uni_next'], m1['raw_personal'], m1['personal']]
        }).to_excel(writer, sheet_name='MicroCicli1', index=False)
        pd.DataFrame({
            'Parametro': ['Anno rif prox', 'Uni in corso', 'Uni che verrà', 'Anno pers intero', 'Anno pers ridotto'],
            'Valore': [m2['anno_ref'], m2['uni_base'], m2['uni_next'], m2['raw_personal'], m2['personal']]
        }).to_excel(writer, sheet_name='MicroCicli2', index=False)
        df_quad.to_excel(writer, sheet_name='Micro Cicli', index=False)
        df_ms.to_excel(writer, sheet_name='MicroPinnacoli e Sfide', index=False)
    data_full = buf.getvalue()
    st.download_button(
        label="Download Excel Completo",
        data=data_full,
        file_name="oroscopo_completo.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    start_ts_c = date(last_year, dob.month, 1)
    months_c = pd.date_range(start=start_ts_c, periods=24, freq='MS')
    labels_c = [m.strftime('%b-%y') for m in months_c]

    dfq2 = df_quad.copy()
    parts_q = dfq2['Micro cicli annuali'].str.split('→')
    dfq2['raw_q'] = parts_q.str[0].str.strip().astype(int)
    dfq2['red_q'] = parts_q.str[1].str.strip().astype(int)
    dfq2['Start'] = pd.to_datetime(dfq2['Inizio'], format='%d/%m/%Y')
    dfq2['End']   = pd.to_datetime(dfq2['Fine'], format='%d/%m/%Y') + pd.offsets.MonthEnd(0)

    vals_q = []
    for m in months_c:
        sel = dfq2[(dfq2['Start'] <= m) & (dfq2['End'] >= m)]
        if not sel.empty:
            r, d = sel.iloc[0]['raw_q'], sel.iloc[0]['red_q']
            vals_q.append(f"{r} → {d}")
        else:
            vals_q.append("")
    df_ts_c = pd.DataFrame([vals_q], index=['Micro cicli'], columns=labels_c)

    start_ts_p = date(last_year, 1, 1)
    months_p = pd.date_range(start=start_ts_p, periods=24, freq='MS')
    labels_p = [m.strftime('%b-%y') for m in months_p]

    parts_mp = df_ms['Micro-Pinnacoli'].str.split('→')
    raw_mp = parts_mp.str[0].str.strip().astype(int)
    red_mp = parts_mp.str[1].str.strip().astype(int)
    parts_sf = df_ms['MicroSfide'].str.split('→')
    raw_sf = parts_sf.str[0].str.strip().astype(int)
    red_sf = parts_sf.str[1].str.strip().astype(int)

    def tri_idx_p(m: pd.Timestamp) -> int:
        delta = (m.year - start_ts_p.year) * 12 + (m.month - start_ts_p.month)
        return delta // 3

    vals_mp, vals_sf = [], []
    for m in months_p:
        idx = tri_idx_p(m)
        vals_mp.append(f"{raw_mp[idx]} → {red_mp[idx]}")
        vals_sf.append(f"{raw_sf[idx]} → {red_sf[idx]}")
    df_ts_p = pd.DataFrame([vals_mp, vals_sf], index=['Micro-Pinnacoli', 'MicroSfide'], columns=labels_p)

    buf2 = io.BytesIO()
    with pd.ExcelWriter(buf2, engine='xlsxwriter') as w2:
        df_ts_c.to_excel(w2, sheet_name='TS_MicroCicli', index=True)
        df_ts_p.to_excel(w2, sheet_name='TS_MicroPinnacoli e Sfide', index=True)
    data_ts = buf2.getvalue()
    st.download_button(
        label="Download Timescale Excel",
        data=data_ts,
        file_name="timescale_completo.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # --- SEZIONE MODIFICATA: Salva Dati per Chatbot in mappa_per_chatbot.json ---
    st.markdown("---")
    st.subheader("Esporta Dati Calendario per Chatbot")

    if st.button("Aggiorna Mappa per Chatbot (Include Dati Calendario)"):
        # Prepara i dati delle tabelle come liste di dizionari
        quadrimestri_data = df_quad.to_dict(orient='records')
        trimestri_data = df_ms.to_dict(orient='records')

        # Aggiungi i nuovi dati al dizionario 'record' già caricato
        record["micro_cicli_quadrimestri_calendario"] = quadrimestri_data
        record["micro_pinnacoli_sfide_trimestri_calendario"] = trimestri_data
        
        # Puoi anche aggiungere altri dati calcolati se servono al chatbot, ad esempio:
        record["anno_di_riferimento_calendario"] = last_year
        record["anno_universale_base"] = m1['uni_base']
        record["anno_personale_base"] = m1['personal']

        try:
            # Sovrascrivi il file mappa_per_chatbot.json con il dizionario aggiornato
            with open(MAPPA_PATH, 'w', encoding='utf-8') as f: # Modalità 'w' sovrascrive
                json.dump(record, f, indent=4, ensure_ascii=False)
            st.success(f"Dati del calendario aggiunti con successo a `{MAPPA_PATH.name}`!")
            st.info("Il tuo chatbot può ora leggere i dati aggiornati nel file della mappa.")
        except Exception as e:
            st.error(f"Errore durante l'aggiornamento di `{MAPPA_PATH.name}`: {e}")

# Assicurati che 'main()' venga chiamato solo quando lo script è eseguito direttamente
if __name__ == '__main__':
    main()
