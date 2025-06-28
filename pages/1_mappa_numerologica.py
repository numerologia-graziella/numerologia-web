import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO, StringIO
import json
import os

# --- DEVE ESSERE IL PRIMISSIMO COMANDO STREAMLIT ---
st.set_page_config(layout="wide")

# --- 1. FUNZIONI DI CALCOLO NUMEROLOGICO ---

# Caricamento del logo
st.image("logo.png", width=100)

def valore_lettera(c):
    """Restituisce il valore numerico di una lettera secondo la tabella Pitagorica."""
    tabella = {
        "A": 1, "J": 1, "S": 1,
        "B": 2, "K": 2, "T": 2,
        "C": 3, "L": 3, "U": 3,
        "D": 4, "M": 4, "V": 4,
        "E": 5, "N": 5, "W": 5,
        "F": 6, "O": 6, "X": 6,
        "G": 7, "P": 7, "Y": 7,
        "H": 8, "Q": 8, "Z": 8,
        "I": 9, "R": 9
    }
    return tabella.get(c.upper(), 0)

def riduci(n):
    """Riduce un numero sommandone le cifre. Non riduce maestri/karmici (per R1)."""
    # Gestisce numeri non validi (es. None)
    if n is None:
        return 0
    return sum(int(d) for d in str(abs(n)))

def riduci_fino_1(n):
    """Riduce un numero fino a una cifra singola. I numeri maestri o karmici vengono segnalati ma non mantenuti."""
    if n is None:
        return 0
    while n > 9:
        n = sum(int(d) for d in str(n))
    return n


def riduci_fino_1_singolo(n):
    """Riduce un numero fino a una singola cifra (senza mantenere maestri)."""
    # Gestisce numeri non validi (es. None)
    if n is None:
        return 0
    while n > 9:
        n = sum(int(d) for d in str(n))
    return n

def segnala(n):
    """Restituisce il tipo di numero speciale (Maestro o Karmico)."""
    maestri = [11, 22, 33, 44] # Aggiungi 44 se li usi
    karmici = [13, 14, 16, 19]
    if n in maestri:
        return f" (Maestro {n})"
    elif n in karmici:
        return f" (Karmico {n})"
    else:
        return ""

def analizza_nome(nome_input):
    """Analizza il nome separando vocali e consonanti e calcolando i totali."""
    vocali = "AEIOU"
    nome_input = nome_input.upper()
    lettere = [(c, v) for c, v in [(char, valore_lettera(char)) for char in nome_input] if v != 0] # Filtra caratteri non validi
    vowels = [(c, v) for c, v in lettere if c in vocali]
    consonants = [(c, v) for c, v in lettere if c not in vocali]
    total = sum(v for c, v in lettere)
    return {
        "lettere": lettere,
        "vowels": vowels,
        "consonants": consonants,
        "total": total,
        "vowels_sum": sum(v for c, v in vowels),
        "consonants_sum": sum(v for c, v in consonants)
    }

def riduzioni(n):
    """Restituisce Riduzione 1 e Riduzione 2 di un numero."""
    r1 = riduci(n)
    r2 = riduci_fino_1(n)
    return r1, r2

# --- FUNZIONE PRINCIPALE PER I CALCOLI NUMEROLOGICI ---
def calcola_mappa_numerologica(nome, cognome, giorno, mese, anno, anno_rif):
    """
    Esegue tutti i calcoli numerologici e restituisce un dizionario
    contenente i risultati e i DataFrame per la visualizzazione.
    """
    mappa_dati = {}
    dataframes = {}
    riepilogo_speciali_final = [] # Inizializza per garantire che sia sempre definito

    # === Nome/Cognome ===
    analisi_nome = analizza_nome(nome)
    analisi_cognome = analizza_nome(cognome)
    
    # Preparazione DataFrame Nome/Cognome
    tab_nome = pd.DataFrame(analisi_nome["lettere"], columns=["Lettera", "Valore"])
    tab_nome["Tipo"] = ["Vocale" if l in "AEIOU" else "Consonante" for l, _ in analisi_nome["lettere"]]
    tab_cognome = pd.DataFrame(analisi_cognome["lettere"], columns=["Lettera", "Valore"])
    tab_cognome["Tipo"] = ["Vocale" if l in "AEIOU" else "Consonante" for l, _ in analisi_cognome["lettere"]]
    dataframes["tab_nome"] = tab_nome
    dataframes["tab_cognome"] = tab_cognome

    # Calcolo anno universale
    anno_universale_r1 = riduci(anno_rif)
    anno_universale_r2 = riduci_fino_1(anno_universale_r1)
    
    # Calcoli anno personale
    anno_personale_intero = giorno + mese + anno_universale_r2
    anno_personale_r1 = riduci(anno_personale_intero)
    anno_personale_r2 = riduci_fino_1(anno_personale_intero)
    
    # Preparazione DataFrame Anno Universale & Anno Personale
    df_anno_universale_personale = pd.DataFrame([
        ["Anno Universale", "Anno di riferimento", anno_rif, ""],
        ["Anno Universale", "Somma cifre anno (Riduzione 1)", anno_universale_r1, segnala(anno_universale_r1)],
        ["Anno Universale", "Anno Universale (Riduzione finale)", anno_universale_r2, segnala(anno_universale_r2)],
        ["Anno Personale", f"Calcolo: {giorno} (giorno) + {mese} (mese) + {anno_universale_r2} (anno universale)", anno_personale_intero, ""],
        ["Anno Personale", "Anno Personale Intero", anno_personale_intero, ""],
        ["Anno Personale", "Riduzione 1 (somma cifre)", anno_personale_r1, segnala(anno_personale_r1)],
        ["Anno Personale", "Riduzione 2 (cifra finale)", anno_personale_r2, segnala(anno_personale_r2)]
    ], columns=["Tipo", "Descrizione", "Valore", "Note Speciali"])

    # ✅ Evita il separatore di migliaia (es. 2,025) forzando i valori come stringhe
    df_anno_universale_personale["Valore"] = df_anno_universale_personale["Valore"].astype(str)
    # Salva il DataFrame nel dizionario
    dataframes["df_anno_universale_personale"] = df_anno_universale_personale
    
    # === Fondamentali ===
    full_total = analisi_nome["total"] + analisi_cognome["total"]
    anima = analisi_nome["vowels_sum"] + analisi_cognome["vowels_sum"]
    persona = analisi_nome["consonants_sum"] + analisi_cognome["consonants_sum"]
    forza_intero = giorno + mese
    forza_r1, forza_r2 = riduzioni(forza_intero)
    
    # Numero del Dono
    ultime_due = anno % 100
    cifra1 = ultime_due // 10
    cifra2 = ultime_due % 10
    numero_dono_anno_intero = cifra1 + cifra2
    numero_dono_anno_r1 = riduci(numero_dono_anno_intero)
    numero_dono_anno_r2 = riduci_fino_1_singolo(numero_dono_anno_intero)
    
    esp_r1, esp_r2 = riduzioni(full_total)
    ani_r1, ani_r2 = riduzioni(anima)
    per_r1, per_r2 = riduzioni(persona)

    # Preparazione DataFrame Fondamentali
    df_fondamentali = pd.DataFrame([
        ["Espressione (nome+cognome)", full_total, esp_r1, esp_r2, segnala(full_total)],
        ["Anima (tutte le vocali)", anima, ani_r1, ani_r2, segnala(anima)],
        ["Persona (tutte le consonanti)", persona, per_r1, per_r2, segnala(persona)],
        ["Numero di Forza (giorno+mese)", forza_intero, forza_r1, forza_r2, segnala(forza_intero)],
        ["Numero del Dono (ultime 2 cifre anno)", numero_dono_anno_intero, numero_dono_anno_r1, numero_dono_anno_r2, segnala(numero_dono_anno_intero)]
    ], columns=["Valore", "Intero", "Riduzione 1 (r1)", "Riduzione 2 (r2)", "Note Speciali"])
    dataframes["df_fondamentali"] = df_fondamentali

    # === Sentiero di vita (DUE METODI) ===
    # Pre-calcola riduzioni di giorno e mese, usate da entrambi i metodi del Sentiero di Vita
    giorno_rid2 = riduci_fino_1_singolo(giorno)
    mese_rid2 = riduci_fino_1_singolo(mese)
    anno_somma_cifre = riduci(anno) # Sum of digits of the full year (e.g., 1990 -> 19)
    anno_rid2_sv = riduci_fino_1_singolo(anno_somma_cifre) # Year reduced to a single digit (e.g., 19 -> 1)


    # Metodo 1: giorno ridotto + mese ridotto + somma cifre anno (non ridotta)
    sv1_intero = giorno_rid2 + mese_rid2 + anno_somma_cifre
    sv1_rid1, sv1_rid2 = riduzioni(sv1_intero)

    # Metodo 2: giorno ridotto + mese ridotto + anno ridotto (a una cifra)
    sv2_intero = giorno_rid2 + mese_rid2 + anno_rid2_sv
    sv2_rid1, sv2_rid2 = riduzioni(sv2_intero)

    # Preparazione DataFrame Sentiero di Vita
    df_sentiero = pd.DataFrame([
        ["Metodo 1: giorno ridotto+mese ridotto+somma cifre anno", f"{giorno_rid2} + {mese_rid2} + {anno_somma_cifre}", sv1_intero, sv1_rid1, sv1_rid2, segnala(sv1_intero)],
        ["Metodo 2: giorno ridotto+mese ridotto+anno ridotto (a una cifra)", f"{giorno_rid2} + {mese_rid2} + {anno_rid2_sv}", sv2_intero, sv2_rid1, sv2_rid2, segnala(sv2_intero)],
    ], columns=["Metodo", "Calcolo", "Somma", "Riduzione 1 (r1)", "Riduzione 2 (r2)", "Note Speciali"])
    dataframes["df_sentiero"] = df_sentiero

    # === Quintessenza & Iniziazione ===
    quintessenza_intera = full_total + sv1_intero
    iniziazione_intera = full_total + anima + giorno + sv1_intero # 'giorno' qui è il valore intero del giorno di nascita

    quint_r1, quint_r2 = riduzioni(quintessenza_intera)
    iniz_r1, iniz_r2 = riduzioni(iniziazione_intera)

    # Preparazione DataFrame Quintessenza
    df_quint = pd.DataFrame([
        ["Quintessenza", quintessenza_intera, quint_r1, quint_r2, segnala(quintessenza_intera)],
        ["Iniziazione Spirituale", iniziazione_intera, iniz_r1, iniz_r2, segnala(iniziazione_intera)]
    ], columns=["Valore", "Intero", "Riduzione 1 (r1)", "Riduzione 2 (r2)", "Note Speciali"])
    dataframes["df_quint"] = df_quint

    # === CICLI DI VITA ===
    fine_exp = 36 - sv1_rid2
    fine_pot = fine_exp + 27
    esperienza_val = mese_rid2
    potere_val = giorno_rid2
    saggezza_val = anno_rid2_sv
    
    # Preparazione DataFrame Cicli di Vita
    df_cicli = pd.DataFrame([
        ["Esperienza", f"0–{fine_exp} anni", esperienza_val, segnala(esperienza_val)],
        ["Potere", f"{fine_exp+1}–{fine_pot} anni", potere_val, segnala(potere_val)],
        ["Saggezza", f"Da {fine_pot+1} anni in poi", saggezza_val, segnala(saggezza_val)],
    ], columns=["Ciclo", "Periodo", "Valore", "Note Speciali"])
    dataframes["df_cicli"] = df_cicli

    # === PINNACOLI (con periodi) ===
    p1_val_calc_intero = giorno_rid2 + mese_rid2
    p1_val_r1 = riduci(p1_val_calc_intero)
    p1_val_r2 = riduci_fino_1_singolo(p1_val_calc_intero)

    p2_val_calc_intero = giorno_rid2 + anno_rid2_sv
    p2_val_r1 = riduci(p2_val_calc_intero)
    p2_val_r2 = riduci_fino_1_singolo(p2_val_calc_intero)

    p3_val_calc_intero = p1_val_r2 + p2_val_r2
    p3_val_r1 = riduci(p3_val_calc_intero)
    p3_val_r2 = riduci_fino_1_singolo(p3_val_calc_intero)

    p4_val_calc_intero = mese_rid2 + anno_rid2_sv
    p4_val_r1 = riduci(p4_val_calc_intero)
    p4_val_r2 = riduci_fino_1_singolo(p4_val_calc_intero)

    periodi_pinnacoli = [
        f"Dalla Nascita a {fine_exp} anni",
        f"Da {fine_exp + 1} a {fine_exp + 9} anni",
        f"Da {fine_exp + 10} a {fine_exp + 18} anni",
        f"Da {fine_exp + 19} anni in poi"
    ]

    pinnacoli_data = [
        ["Pinnacolo 1", f"({giorno_rid2}+{mese_rid2})", p1_val_calc_intero, p1_val_r1, p1_val_r2, periodi_pinnacoli[0], segnala(p1_val_calc_intero)],
        ["Pinnacolo 2", f"({giorno_rid2}+{anno_rid2_sv})", p2_val_calc_intero, p2_val_r1, p2_val_r2, periodi_pinnacoli[1], segnala(p2_val_calc_intero)],
        ["Pinnacolo 3", f"({p1_val_r2}+{p2_val_r2})", p3_val_calc_intero, p3_val_r1, p3_val_r2, periodi_pinnacoli[2], segnala(p3_val_calc_intero)],
        ["Pinnacolo 4", f"({mese_rid2}+{anno_rid2_sv})", p4_val_calc_intero, p4_val_r1, p4_val_r2, periodi_pinnacoli[3], segnala(p4_val_calc_intero)],
    ]
    df_pinnacoli = pd.DataFrame(
        pinnacoli_data,
        columns=["Nome", "Calcolo Base", "Valore Intero", "Riduzione 1 (r1)", "Riduzione 2 (r2)", "Periodo di Attivazione", "Note Speciali"]
    )
    dataframes["df_pinnacoli"] = df_pinnacoli

    # === SFIDE (con periodi) ===
    s1_val_calc_intero = abs(giorno_rid2 - mese_rid2)
    s1_val_r1 = riduci(s1_val_calc_intero)
    s1_val_r2 = riduci_fino_1_singolo(s1_val_calc_intero)

    s2_val_calc_intero = abs(anno_rid2_sv - giorno_rid2)
    s2_val_r1 = riduci(s2_val_calc_intero)
    s2_val_r2 = riduci_fino_1_singolo(s2_val_calc_intero)

    s3_val_calc_intero = abs(s1_val_r2 - s2_val_r2)
    s3_val_r1 = riduci(s3_val_calc_intero)
    s3_val_r2 = riduci_fino_1_singolo(s3_val_calc_intero)

    s4_val_calc_intero = abs(anno_rid2_sv - mese_rid2)
    s4_val_r1 = riduci(s4_val_calc_intero)
    s4_val_r2 = riduci_fino_1_singolo(s4_val_calc_intero)

    # I periodi delle sfide sono gli stessi dei pinnacoli
    sfide_data = [
        ["Sfida 1", f"|{giorno_rid2}-{mese_rid2}|", s1_val_calc_intero, s1_val_r1, s1_val_r2, periodi_pinnacoli[0], segnala(s1_val_calc_intero)],
        ["Sfida 2", f"|{anno_rid2_sv}-{giorno_rid2}|", s2_val_calc_intero, s2_val_r1, s2_val_r2, periodi_pinnacoli[1], segnala(s2_val_calc_intero)],
        ["Sfida 3", f"|{s1_val_r2}-{s2_val_r2}|", s3_val_calc_intero, s3_val_r1, s3_val_r2, periodi_pinnacoli[2], segnala(s3_val_calc_intero)],
        ["Sfida 4", f"|{anno_rid2_sv}-{mese_rid2}|", s4_val_calc_intero, s4_val_r1, s4_val_r2, periodi_pinnacoli[3], segnala(s4_val_calc_intero)],
    ]
    df_sfide = pd.DataFrame(
        sfide_data,
        columns=["Nome", "Calcolo Base", "Valore Intero", "Riduzione 1 (r1)", "Riduzione 2 (r2)", "Periodo di Attivazione", "Note Speciali"]
    )
    dataframes["df_sfide"] = df_sfide

    # === Tabella 0-80 Anni ===
    tabella_anni = []
    for eta in range(81):
        anno_eta = anno + eta
        au_eta = riduci_fino_1(anno_eta)
        ap_eta_base = giorno + mese + au_eta
        ap_eta_r = riduci_fino_1(ap_eta_base)

        ciclo_nome, ciclo_val = "", ""
        pinrid, sfrid = 0, 0 # Valori ridotti (cifra finale)
        pin_intero, sf_intero = 0, 0 # Nuovi valori interi (non ridotti)
        per = ""
        stag = ""

        if eta <= fine_exp:
            ciclo_nome, ciclo_val = "Esperienza", esperienza_val
            per = periodi_pinnacoli[0]
            stag = "Primavera"
            pinrid, sfrid = p1_val_r2, s1_val_r2
            pin_intero, sf_intero = p1_val_calc_intero, s1_val_calc_intero # Assegna i valori interi
        elif eta <= fine_pot:
            ciclo_nome, ciclo_val = "Potere", potere_val
            if eta <= fine_exp + 9:
                per = periodi_pinnacoli[1]
                stag = "Estate"
                pinrid, sfrid = p2_val_r2, s2_val_r2
                pin_intero, sf_intero = p2_val_calc_intero, s2_val_calc_intero # Assegna i valori interi
            else:
                per = periodi_pinnacoli[2]
                stag = "Autunno"
                pinrid, sfrid = p3_val_r2, s3_val_r2
                pin_intero, sf_intero = p3_val_calc_intero, s3_val_calc_intero # Assegna i valori interi
        else:
            ciclo_nome, ciclo_val = "Saggezza", saggezza_val
            per = periodi_pinnacoli[3]
            stag = "Inverno"
            pinrid, sfrid = p4_val_r2, s4_val_r2
            pin_intero, sf_intero = p4_val_calc_intero, s4_val_calc_intero # Assegna i valori interi
            
        tabella_anni.append({
            "Età": eta,
            "Anno": anno_eta,
            "Anno Universale": au_eta,
            "Anno Personale": ap_eta_r,
            "Ciclo Vita": ciclo_nome,
            "Valore Ciclo": ciclo_val,
            "Stagione Ciclo": stag,
            "Periodo Pinnacolo/Sfida": per,
            "Pinnacolo": pinrid,
            "Pinnacolo Intero": pin_intero, # NUOVA COLONNA
            "Sfida": sfrid,
            "Sfida Intera": sf_intero # NUOVA COLONNA
        })
    df_tabella_anni = pd.DataFrame(tabella_anni)
    df_tabella_anni["Anno"] = df_tabella_anni["Anno"].astype(str)  # forza stringa per evitare 1,955
    dataframes["df_tabella_anni"] = df_tabella_anni

    # === RIEPILOGO NUMERI MAESTRI E KARMICI ===
    valori_check = [
        ("Espressione", full_total), ("Espressione (rid. 1)", esp_r1), ("Espressione (rid. 2)", esp_r2),
        ("Anima", anima), ("Anima (rid. 1)", ani_r1), ("Anima (rid. 2)", ani_r2),
        ("Personalità", persona), ("Personalità (rid. 1)", per_r1), ("Personalità (rid. 2)", per_r2),
        ("Forza (Destino)", forza_intero), ("Forza (rid. 1)", forza_r1), ("Forza (rid. 2)", forza_r2),
        ("Dono", numero_dono_anno_intero), ("Dono (rid. 1)", numero_dono_anno_r1), ("Dono (rid. 2)", numero_dono_anno_r2),
        ("Sentiero di Vita 1 (intero)", sv1_intero), ("Sentiero di Vita 1 (rid. 1)", sv1_rid1), ("Sentiero di Vita 1 (rid. 2)", sv1_rid2),
        ("Sentiero di Vita 2 (intero)", sv2_intero), ("Sentiero di Vita 2 (rid. 1)", sv2_rid1), ("Sentiero di Vita 2 (rid. 2)", sv2_rid2),
        ("Quintessenza (intero)", quintessenza_intera), ("Quintessenza (rid. 1)", quint_r1), ("Quintessenza (rid. 2)", quint_r2),
        ("Iniziazione (intero)", iniziazione_intera), ("Iniziazione (rid. 1)", iniz_r1), ("Iniziazione (rid. 2)", iniz_r2),
        ("Ciclo Esperienza", esperienza_val), ("Ciclo Potere", potere_val), ("Ciclo Saggezza", saggezza_val),
        ("Pinnacolo 1", p1_val_r2), ("Pinnacolo 2", p2_val_r2), ("Pinnacolo 3", p3_val_r2), ("Pinnacolo 4", p4_val_r2),
        ("Sfida 1", s1_val_r2), ("Sfida 2", s2_val_r2), ("Sfida 3", s3_val_r2), ("Sfida 4", s4_val_r2),
        ("Anno Universale (r1)", anno_universale_r1), ("Anno Universale (r2)", anno_universale_r2),
        ("Anno Personale (r1)", anno_personale_r1), ("Anno Personale (r2)", anno_personale_r2),
    ]
    riepilogo_speciali_final = []
    for nome_pos, val in valori_check:
        tipo = segnala(val)
        if tipo:
            riepilogo_speciali_final.append([nome_pos, val, tipo.strip()])
    
    if riepilogo_speciali_final:
        df_riepilogo_speciali = pd.DataFrame(riepilogo_speciali_final, columns=["Posizione", "Valore", "Tipo"])
        dataframes["df_riepilogo_speciali"] = df_riepilogo_speciali
    else:
        dataframes["df_riepilogo_speciali"] = pd.DataFrame(columns=["Posizione", "Valore", "Tipo"]) # DataFrame vuoto se non ci sono speciali

    # --- SALVATAGGIO DATI PER LA CHATBOT (JSON in session_state e file) ---
    # Formatta la data_nascita_obj solo se è valida
    try:
        temp_date_obj = datetime(anno, mese, giorno).date()
        data_nascita_formattata = temp_date_obj.strftime("%d/%m/%Y")
    except ValueError:
        data_nascita_formattata = "Data non valida"


    mappa_dati = {
        "Nome Completo": f"{nome} {cognome}",
        "Data di Nascita": data_nascita_formattata,
        "Anno Riferimento": anno_rif,
        "Anno Universale (riduzione 2)": anno_universale_r2,
        "Anno Personale (riduzione 2)": anno_personale_r2,
        "Numero Espressione (riduzione 2)": esp_r2,
        "Numero Anima (riduzione 2)": ani_r2,
        "Numero Personalita (riduzione 2)": per_r2,
        "Numero Forza (riduzione 2)": forza_r2,
        "Numero Dono (riduzione 2)": numero_dono_anno_r2,
        "Sentiero di Vita (Metodo 1 - riduzione 2)": sv1_rid2,
        "Sentiero di Vita (Metodo 2 - riduzione 2)": sv2_rid2,
        "Quintessenza (riduzione 2)": quint_r2,
        "Iniziazione Spirituale (riduzione 2)": iniz_r2,
        "Ciclo Esperienza (valore)": esperienza_val,
        "Ciclo Potere (valore)": potere_val,
        "Ciclo Saggezza (valore)": saggezza_val,
       # Pinnacoli - Aggiungi valori interi, riduzione 1 e periodo
        "Pinnacolo 1 (intero)": p1_val_calc_intero,
        "Pinnacolo 1 (riduzione 1)": p1_val_r1,
        "Pinnacolo 1 (ridotto)": p1_val_r2,
        "Pinnacolo 1 (Periodo di Attivazione)": periodi_pinnacoli[0],

        "Pinnacolo 2 (intero)": p2_val_calc_intero,
        "Pinnacolo 2 (riduzione 1)": p2_val_r1,
        "Pinnacolo 2 (ridotto)": p2_val_r2,
        "Pinnacolo 2 (Periodo di Attivazione)": periodi_pinnacoli[1],

        "Pinnacolo 3 (intero)": p3_val_calc_intero,
        "Pinnacolo 3 (riduzione 1)": p3_val_r1,
        "Pinnacolo 3 (ridotto)": p3_val_r2,
        "Pinnacolo 3 (Periodo di Attivazione)": periodi_pinnacoli[2],

        "Pinnacolo 4 (intero)": p4_val_calc_intero,
        "Pinnacolo 4 (riduzione 1)": p4_val_r1,
        "Pinnacolo 4 (ridotto)": p4_val_r2,
        "Pinnacolo 4 (Periodo di Attivazione)": periodi_pinnacoli[3],

        # Sfide - Aggiungi valori interi, riduzione 1 e periodo
        "Sfida 1 (intero)": s1_val_calc_intero,
        "Sfida 1 (riduzione 1)": s1_val_r1,
        "Sfida 1 (ridotta)": s1_val_r2,
        "Sfida 1 (Periodo di Attivazione)": periodi_pinnacoli[0], # I periodi delle sfide sono gli stessi dei pinnacoli

        "Sfida 2 (intero)": s2_val_calc_intero,
        "Sfida 2 (riduzione 1)": s2_val_r1,
        "Sfida 2 (ridotta)": s2_val_r2,
        "Sfida 2 (Periodo di Attivazione)": periodi_pinnacoli[1],

        "Sfida 3 (intero)": s3_val_calc_intero,
        "Sfida 3 (riduzione 1)": s3_val_r1,
        "Sfida 3 (ridotta)": s3_val_r2,
        "Sfida 3 (Periodo di Attivazione)": periodi_pinnacoli[2],

        "Sfida 4 (intero)": s4_val_calc_intero,
        "Sfida 4 (riduzione 1)": s4_val_r1,
        "Sfida 4 (ridotta)": s4_val_r2,
        "Sfida 4 (Periodo di Attivazione)": periodi_pinnacoli[3],
        "Numeri Maestri/Karmici Rilevati": [f"{item[0]} ({item[1]}{item[2]})" for item in riepilogo_speciali_final] if riepilogo_speciali_final else "Nessuno",
    }
    
    return mappa_dati, dataframes


# --- 2. IMPOSTAZIONI PAGINA E TITOLO ---
st.title("Numerologia Pitagorica – Metodo Natascha")
st.markdown("Calcola la tua mappa numerologica completa.")
st.markdown("---")

# --- 3. INPUT UTENTE (Nella sidebar) ---
st.sidebar.header("Inserisci i tuoi Dati")
nome = st.sidebar.text_input("Nome", key="nome_input_sidebar").strip()
cognome = st.sidebar.text_input("Cognome", key="cognome_input_sidebar").strip()

# Input data con validazione
data_nascita_str = st.sidebar.text_input("Data di nascita (GG/MM/AAAA)", key="data_string_input").strip()

# Inizializza data_nascita_obj, giorno, mese, anno a None o 0
data_nascita_obj = None
giorno, mese, anno = 0, 0, 0 # Inizializza con 0 per evitare NameError nei calcoli se la data non è valida

if data_nascita_str:
    try:
        data_nascita_obj = datetime.strptime(data_nascita_str, "%d/%m/%Y").date()
        giorno = data_nascita_obj.day
        mese = data_nascita_obj.month
        anno = data_nascita_obj.year
        
        if data_nascita_obj > datetime.now().date():
            st.sidebar.error("La data di nascita non può essere nel futuro.")
            giorno, mese, anno = 0, 0, 0 # Resetta i valori se la data è invalida
            data_nascita_obj = None # Resetta anche l'oggetto data
        elif data_nascita_obj < datetime(1, 1, 1).date(): # Puoi adattare questo limite
            st.sidebar.error("La data di nascita è troppo vecchia. Inserisci una data valida.")
            giorno, mese, anno = 0, 0, 0
            data_nascita_obj = None # Resetta anche l'oggetto data
    except ValueError:
        st.sidebar.error("Formato data non valido. Usa GG/MM/AAAA (es. 01/01/1990).")
        giorno, mese, anno = 0, 0, 0 # Resetta i valori se la data è invalida
        data_nascita_obj = None # Resetta anche l'oggetto data

# Anno di riferimento rimane st.number_input
anno_rif_input = st.sidebar.number_input(
    "Anno di riferimento (invio=anno attuale)",
    min_value=1900,
    max_value=2100,
    value=datetime.now().year,
    step=1,
    key="anno_rif_input_sidebar"
)
anno_rif = int(anno_rif_input)

# Gestione degli errori prima di generare la mappa
errore = None
if not nome:
    errore = "Inserisci il nome."
elif not cognome:
    errore = "Inserisci il cognome."
# Controlla che giorno, mese, anno siano validi (non 0 o None se la data non è stata parsata correttamente)
elif giorno == 0 or mese == 0 or anno == 0 or data_nascita_obj is None:
    errore = "Inserisci una data di nascita valida nel formato GG/MM/AAAA."

# --- Inizializzazione di st.session_state ---
if "mappa_numerologica_corrente" not in st.session_state:
    st.session_state["mappa_numerologica_corrente"] = {}
if "dataframes_mappa" not in st.session_state:
    st.session_state["dataframes_mappa"] = {}

# --- 4. LOGICA DEL BOTTONE "GENERA MAPPA" ---
if st.sidebar.button("Genera Mappa Numerologica", type="primary"):
    if errore:
        st.error(errore)
        # Svuota i dati in session_state se c'è un errore, per evitare di mostrare dati obsoleti
        st.session_state["mappa_numerologica_corrente"] = {}
        st.session_state["dataframes_mappa"] = {}
    else:
        try:
            # Chiama la funzione che esegue tutti i calcoli
            mappa_json_chatbot, dataframes_calcolati = calcola_mappa_numerologica(
                nome, cognome, giorno, mese, anno, anno_rif
            )
            st.session_state["mappa_numerologica_corrente"] = mappa_json_chatbot
            st.session_state["dataframes_mappa"] = dataframes_calcolati
            st.success("Mappa numerologica calcolata con successo! Scorri in basso per i dettagli.")
            st.markdown("---")
        except Exception as e:
            st.error(f"Si è verificato un errore nel calcolo della mappa: {e}. Controlla i dati inseriti.")
            st.exception(e) # Mostra i dettagli dell'errore per il debug
            # Svuota i dati in session_state in caso di errore di calcolo
            st.session_state["mappa_numerologica_corrente"] = {}
            st.session_state["dataframes_mappa"] = {}

# --- 5. VISUALIZZAZIONE DEI RISULTATI (LEGGI DA session_state) ---
# Mostra i risultati solo se sono stati calcolati e salvati in session_state
if st.session_state["mappa_numerologica_corrente"]:
    mappa_dati_display = st.session_state["mappa_numerologica_corrente"]
    dataframes_display = st.session_state["dataframes_mappa"]

    # --- Mostra tutte le sezioni della mappa ---
    st.header("Mappa Numerologica Completa")
    st.markdown("---")

    st.header("1. Analisi Nome e Cognome")
    st.subheader("Nome:")
    st.dataframe(dataframes_display["tab_nome"])
    st.write(f"**Somma vocali:** {sum(row['Valore'] for _, row in dataframes_display['tab_nome'].iterrows() if row['Tipo'] == 'Vocale')}, "
             f"**Somma consonanti:** {sum(row['Valore'] for _, row in dataframes_display['tab_nome'].iterrows() if row['Tipo'] == 'Consonante')}, "
             f"**Totale:** {dataframes_display['tab_nome']['Valore'].sum()}")
    st.subheader("Cognome:")
    st.dataframe(dataframes_display["tab_cognome"])
    st.write(f"**Somma vocali:** {sum(row['Valore'] for _, row in dataframes_display['tab_cognome'].iterrows() if row['Tipo'] == 'Vocale')}, "
             f"**Somma consonanti:** {sum(row['Valore'] for _, row in dataframes_display['tab_cognome'].iterrows() if row['Tipo'] == 'Consonante')}, "
             f"**Totale:** {dataframes_display['tab_cognome']['Valore'].sum()}")

    st.header("2. Anno Universale & Anno Personale")
    st.dataframe(dataframes_display["df_anno_universale_personale"])
    
    st.header("3. Numeri Fondamentali")
    st.dataframe(dataframes_display["df_fondamentali"])

    st.header("4. Sentiero di Vita – Due Metodi di Calcolo")
    st.dataframe(dataframes_display["df_sentiero"])

    st.header("5. Quintessenza & Iniziazione Spirituale")
    st.dataframe(dataframes_display["df_quint"])

    st.header("6. Cicli di Vita")
    st.dataframe(dataframes_display["df_cicli"])

    st.header("7. Pinnacoli")
    st.dataframe(dataframes_display["df_pinnacoli"])

    st.header("8. Sfide")
    st.dataframe(dataframes_display["df_sfide"])

    st.header("9. Tabella Dettagliata 0-80 Anni")
    st.dataframe(dataframes_display["df_tabella_anni"])

    st.header("10. Riepilogo Numeri Maestri e Karmici Rilevati")
    if not dataframes_display["df_riepilogo_speciali"].empty:
        st.dataframe(dataframes_display["df_riepilogo_speciali"])
    else:
        st.info("Nessun numero maestro o karmico riscontrato nelle principali posizioni.")

    st.markdown("---")
    st.header("Dettagli per la Chatbot (dati JSON)") # Titolo

    # Mostra i dettagli della mappa subito dopo il calcolo
    st.subheader("Contenuto del file JSON:")
    st.json(mappa_dati_display) # Usa i dati dalla session_state

    json_filename = "mappa_per_chatbot.json"
    
    # --- MODIFICA QUI PER SALVARE NELLA DIRECTORY RADICE ---
    # Ottiene la directory dello script corrente (es. C:\Users\Graziella\Desktop\numerologia\pages)
    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Sale alla directory padre (es. C:\Users\Graziella\Desktop\numerologia)
    parent_dir = os.path.dirname(current_script_dir)
    
    # Costruisce il percorso completo al file JSON nella directory padre
    json_filepath = os.path.join(parent_dir, json_filename)
    # --- FINE MODIFICA ---

    # --- Stampe di Debugging Migliorate (Terminale) ---
    print(f"Current Working Directory: {os.getcwd()}")
    #print(f"Script Directory: {script_dir}")
    print(f"Tentativo di salvare il file JSON al PERCORSO ASSOLUTO: {json_filepath}")
    print(f"Contenuto JSON da salvare (prima della serializzazione): {mappa_dati_display}")

    # Blocco di salvataggio del file
    try:
        # Salviamo solo se la mappa non è vuota
        if mappa_dati_display: # Controlla se il dizionario è non vuoto
            with open(json_filepath, "w", encoding="utf-8") as f:
                json.dump(mappa_dati_display, f, indent=4, ensure_ascii=False)
                f.flush() # Forza la scrittura immediata
                os.fsync(f.fileno()) # Assicura che sia scritto su disco
            st.success(f"Dati della mappa salvati in: `{json_filepath}` per la chatbot.")
            print(f"File '{json_filepath}' salvato con successo.") # Debug

            # --- VERIFICA IMMEDIATA: Prova a rileggere il file ---
            try:
                with open(json_filepath, "r", encoding="utf-8") as f_read:
                    read_content = json.load(f_read)
                print(f"Contenuto letto dal file (per verifica): {read_content}")
                if read_content == mappa_dati_display:
                    print("Verifica riuscita: Il contenuto letto corrisponde al contenuto salvato.")
                else:
                    print("Verifica FALLITA: Il contenuto letto NON corrisponde al contenuto salvato.")
            except json.JSONDecodeError as jde:
                print(f"Errore JSONDecodeError durante la lettura di verifica: Il file potrebbe essere vuoto o malformato. {jde}")
            except Exception as e_read:
                print(f"Errore generico durante la lettura di verifica: {e_read}")
        else:
            st.warning("La mappa numerologica è vuota, il file JSON non è stato salvato.")
            print("DEBUG: La mappa numerologica è vuota, il file JSON non è stato salvato.")

    except Exception as e:
        st.error(f"Errore nel salvataggio del file JSON per la chatbot: {e}")
        print(f"ERRORE nel salvataggio del file JSON: {e}") # Debug

    st.markdown("---")

    # --- SEZIONE DOWNLOAD ---
    st.header("Opzioni di Download")
    
    # Prendi i DataFrame da session_state per i download
    tab_nome = dataframes_display["tab_nome"]
    tab_cognome = dataframes_display["tab_cognome"]
    df_anno_universale_personale = dataframes_display["df_anno_universale_personale"]
    df_fondamentali = dataframes_display["df_fondamentali"]
    df_sentiero = dataframes_display["df_sentiero"]
    df_quint = dataframes_display["df_quint"]
    df_cicli = dataframes_display["df_cicli"]
    df_pinnacoli = dataframes_display["df_pinnacoli"]
    df_sfide = dataframes_display["df_sfide"]
    df_tabella_anni = dataframes_display["df_tabella_anni"]
    df_riepilogo_speciali = dataframes_display["df_riepilogo_speciali"] # Potrebbe essere vuoto

    # Download multi-foglio Excel
    buffer_excel = BytesIO()
    with pd.ExcelWriter(buffer_excel, engine='xlsxwriter') as writer:
        tab_nome.to_excel(writer, sheet_name="Nome", index=False)
        tab_cognome.to_excel(writer, sheet_name="Cognome", index=False)
        df_anno_universale_personale.to_excel(writer, sheet_name="Anno Universale_Personale", index=False)
        df_fondamentali.to_excel(writer, sheet_name="Fondamentali", index=False)
        df_sentiero.to_excel(writer, sheet_name="Sentiero di Vita", index=False)
        df_quint.to_excel(writer, sheet_name="Quintessenza", index=False)
        df_cicli.to_excel(writer, sheet_name="Cicli di Vita", index=False)
        df_pinnacoli.to_excel(writer, sheet_name="Pinnacoli", index=False)
        df_sfide.to_excel(writer, sheet_name="Sfide", index=False)
        df_tabella_anni.to_excel(writer, sheet_name="Tabella 0-80 Anni", index=False)
        if not df_riepilogo_speciali.empty:
            df_riepilogo_speciali.to_excel(writer, sheet_name="Riepilogo Maestri_Karmici", index=False)
    buffer_excel.seek(0)
    
    st.download_button(
        label="📥 Scarica Mappa Completa (Excel Multi-foglio)",
        data=buffer_excel,
        file_name=f"mappa_numerologica_{mappa_dati_display.get('Nome Completo', 'utente').replace(' ', '_')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key="download_excel_button"
    )

    # Download CSV unificato
    tabelle_unificate_csv = [
        ("Nome", tab_nome),
        ("Cognome", tab_cognome),
        ("Anno Universale_Personale", df_anno_universale_personale),
        ("Fondamentali", df_fondamentali),
        ("Sentiero di Vita", df_sentiero),
        ("Quintessenza", df_quint),
        ("Cicli di Vita", df_cicli),
        ("Pinnacoli", df_pinnacoli),
        ("Sfide", df_sfide),
        ("Tabella 0-80 Anni", df_tabella_anni)
    ]
    if not df_riepilogo_speciali.empty:
        tabelle_unificate_csv.append(("Riepilogo Maestri_Karmici", df_riepilogo_speciali))

    df_unificato_csv = pd.concat(
        [df.assign(Sezione=nome_sezione) for nome_sezione, df in tabelle_unificate_csv],
        ignore_index=True
    )
    csv_buffer = StringIO()
    df_unificato_csv.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)

    st.download_button(
        label="📥 Scarica Riepilogo Completo (CSV Unificato)",
        data=csv_buffer.getvalue(),
        file_name=f"riepilogo_mappa_numerologica_{mappa_dati_display.get('Nome Completo', 'utente').replace(' ', '_')}.csv",
        mime="text/csv",
        key="download_csv_button"
    )
else:
    st.info("Inserisci i tuoi dati nella sidebar e clicca 'Genera Mappa Numerologica' per visualizzare la mappa.")

