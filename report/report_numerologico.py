import streamlit as st
from fpdf import FPDF
import pandas as pd
import os
import tempfile
from datetime import datetime

from pathlib import Path

from pathlib import Path

# --- Funzione aggiornata per trovare il font in entrambe le posizioni ---
def get_font_file(font_name: str) -> str:
    """
    Cerca il file del font sia in 'fonts/' sia in 'pages/fonts/'.
    Così funziona anche se qualcosa punta ancora al vecchio percorso.
    """
    base_dir = Path(__file__).resolve().parent.parent
    fallback_dir = base_dir / "pages"

    font_paths = [
        base_dir / "fonts" / font_name,
        fallback_dir / "fonts" / font_name
    ]

    for path in font_paths:
        if path.exists():
            return str(path)

    raise RuntimeError(
        f"Font '{font_name}' non trovato. "
        f"Controllati questi percorsi:\n" + "\n".join(str(p) for p in font_paths)
    )

# --- Funzione di utilità per formattare i valori numerici ---
def format_numeric_value(val):
    """
    Formatta i valori numerici per la visualizzazione.
    - Converte float che sono interi (es. 2025.0) in interi puri (2025).
    - Gestisce i valori NaN (Not a Number) restituendo pd.NA.
    - Lascia invariati altri tipi di dati.
    """
    if isinstance(val, (int, float)):
        if pd.isna(val):
            return pd.NA # Restituisce pd.NA, che Pandas gestisce bene come valore nullo numerico
        elif float(val).is_integer():
            return int(val) # Restituisce un intero Python puro senza decimali
        else:
            return val # Restituisce il float se ha decimali (es. 123.45)
    return val

# --- Aggiunge una tabella di DataFrame al PDF ---
def add_dataframe_to_pdf(pdf: FPDF, df: pd.DataFrame, title: str, include_page_break: bool = True):
    """
    Aggiunge un DataFrame Pandas come tabella al documento PDF.
    Formatta i numeri per una visualizzazione corretta nel PDF.
    """
    if include_page_break:
        pdf.add_page()

    pdf.set_font("DejaVu", "B", 14)
    pdf.multi_cell(0, 10, title, 0, "L")
    pdf.ln(5)

    if df.empty:
        pdf.set_font("DejaVu", "", 12)
        pdf.multi_cell(0, 10, "Nessun dato disponibile per questa sezione.", 0, "L")
        return

    num_cols = len(df.columns)
    # Adatta la dimensione del font e l'altezza della cella in base al numero di colonne
    font_header, font_content, cell_h = (10, 9, 8) if num_cols <= 5 else (8, 7, 5) if num_cols <= 8 else (6, 5, 4)
    page_w = pdf.w - pdf.l_margin - pdf.r_margin

    col_widths = []
    for col in df.columns:
        pdf.set_font("DejaVu", "B", font_header)
        header_w = pdf.get_string_width(str(col))
        pdf.set_font("DejaVu", "", font_content)
        
        data_w = 0
        for val in df[col]:
            formatted_val = format_numeric_value(val)
            # Fpdf.get_string_width si aspetta una stringa
            data_w = max(data_w, pdf.get_string_width(str(formatted_val) if formatted_val is not pd.NA else ""))
        col_widths.append(max(header_w, data_w) + 4)

    total_w = sum(col_widths)
    # Scala le larghezze delle colonne se superano la larghezza della pagina
    if total_w > page_w:
        scale = page_w / total_w
        col_widths = [w * scale for w in col_widths]
    else:
        # Distribuisci lo spazio extra se la tabella è più stretta della pagina
        extra = (page_w - total_w) / num_cols
        col_widths = [w + extra for w in col_widths]

    # Intestazione della tabella
    pdf.set_font("DejaVu", "B", font_header)
    pdf.set_fill_color(220, 220, 220)
    for i, col in enumerate(df.columns):
        pdf.cell(col_widths[i], cell_h, str(col), 1, 0, "C", True)
    pdf.ln(cell_h)

    # Contenuto della tabella
    pdf.set_font("DejaVu", "", font_content)
    fill_colors = [(255, 255, 255), (245, 245, 245)] # Colori alternati per le righe

    for idx, row in df.iterrows():
        # Aggiungi una nuova pagina se non c'è spazio sufficiente per la riga successiva
        if pdf.get_y() + cell_h > pdf.h - pdf.b_margin:
            pdf.add_page()
            # Ripeti l'intestazione nella nuova pagina
            pdf.set_font("DejaVu", "B", font_header)
            pdf.set_fill_color(220, 220, 220)
            for i, col in enumerate(df.columns):
                pdf.cell(col_widths[i], cell_h, str(col), 1, 0, "C", True)
            pdf.ln(cell_h)
            pdf.set_font("DejaVu", "", font_content)

        pdf.set_fill_color(*fill_colors[idx % 2]) # Alterna i colori di sfondo
        for i, val in enumerate(row):
            val_to_display = format_numeric_value(val)
            # Stampa il valore nella cella, gestendo pd.NA come stringa vuota
            pdf.cell(col_widths[i], cell_h, str(val_to_display) if val_to_display is not pd.NA else "", 1, 0, "L", True)
        pdf.ln(cell_h)

    pdf.ln(10) # Spazio dopo la tabella

# --- Genera il PDF completo con tutti i dati numerologici ---
def generate_full_numerology_pdf(mappa_dati_dict: dict, dataframes_dict: dict) -> bytes:
    """
    Genera l'intero report numerologico come file PDF.
    """
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15) # Abilita il salto pagina automatico con margini
    
    # Carica i font DejaVu Sans (necessari per Unicode e per i caratteri speciali)
    font_regular = get_font_file("DejaVuSans.ttf")
    font_bold = get_font_file("DejaVuSans-Bold.ttf")

    pdf.add_font("DejaVu", "", font_regular, uni=True)
    pdf.add_font("DejaVu", "B", font_bold, uni=True)

    # Pagina di copertina / Dettagli personali
    pdf.add_page()
    pdf.set_font("DejaVu", "B", 20)
    pdf.multi_cell(0, 15, "Report Numerologico Completo", 0, "C")
    pdf.ln(10)

    pdf.set_font("DejaVu", "B", 14)
    pdf.cell(0, 10, "Dettagli Personali:", 0, 1, "L")
    pdf.set_font("DejaVu", "", 12)
    
    # Nome Completo
    pdf.cell(50, 10, "Nome Completo:", 1, 0, "L")
    pdf.cell(0, 10, str(mappa_dati_dict.get("Nome Completo", "N.D.")), 1, 1, "L")
    
    # Data di Nascita
    pdf.cell(50, 10, "Data di Nascita:", 1, 0, "L")
    pdf.cell(0, 10, str(mappa_dati_dict.get("Data di Nascita", "N.D.")), 1, 1, "L")
    
    # Anno di Riferimento (formattato per sicurezza)
    pdf.cell(50, 10, "Anno di Riferimento:", 1, 0, "L")
    anno_riferimento = format_numeric_value(mappa_dati_dict.get("Anno Riferimento", "N.D."))
    # Converti in stringa, gestendo pd.NA
    pdf.cell(0, 10, str(anno_riferimento) if anno_riferimento is not pd.NA else "", 1, 1, "L")
    pdf.ln(10)

    # Aggiungi tutte le tabelle dei DataFrame al PDF
    for title, df in dataframes_dict.items():
        add_dataframe_to_pdf(pdf, df, title)

    # Salva il PDF in un file temporaneo e leggilo in byte
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        pdf.output(tmp_file.name)
        tmp_file_path = tmp_file.name

    with open(tmp_file_path, "rb") as f:
        pdf_bytes = f.read()
    os.remove(tmp_file_path) # Elimina il file temporaneo
    return pdf_bytes

# --- Streamlit App ---
def run():
    st.title("📄 Report Numerologico Completo in PDF")
    st.write("Genera e scarica il report PDF con tutti i dati calcolati della tua mappa numerologica.")

    # Recupera i dati della mappa numerologica e i DataFrame dallo session_state
    mappa_dati = st.session_state.get("mappa_numerologica_corrente", {})
    dataframes_mappa = st.session_state.get("dataframes_mappa", {})

    if mappa_dati and dataframes_mappa:
        st.subheader("Anteprima dei dati disponibili")
        for name, df in dataframes_mappa.items():
            st.write(f"**{name}**")
            df_display = df.copy() # Lavora su una copia per non alterare i dati in session_state
            
            # --- MODIFICA CRUCIALE PER LA VISUALIZZAZIONE STREAMLIT: FORZIAMO STRINGA ---
            # Applica la formattazione a tutte le colonne per una visualizzazione pulita
            for col in df_display.columns:
                # 1. Applica la funzione format_numeric_value per gestire interi da float e NaN
                df_display[col] = df_display[col].apply(format_numeric_value)
                
                # 2. CONVERTIAMO ESPLICITAMENTE A STRINGA.
                # Questo aggira qualsiasi formattazione locale automatica di Pandas/Streamlit
                # che potrebbe reintrodurre la virgola per i numeri.
                df_display[col] = df_display[col].astype(str)
            
            # Puoi decommentare le seguenti righe per debugging dei tipi di dato a video
            # st.write(f"DEBUG: Tipi di dato per {name} (dopo conversione a stringa):")
            # st.dataframe(pd.DataFrame(df_display.dtypes, columns=['Dtype']))

            st.dataframe(df_display.head()) # Mostra le prime righe del DataFrame formattato

        # Inizializza lo stato per il download del PDF
        if "pdf_ready" not in st.session_state:
            st.session_state["pdf_ready"] = False
        
        # Pulsante per avviare la generazione del PDF
        if st.button("Genera PDF", type="primary", key="generate_pdf_button"):
            try:
                # Genera i byte del PDF
                pdf_bytes = generate_full_numerology_pdf(mappa_dati, dataframes_mappa)
                
                # Crea un nome file significativo per il download
                filename = mappa_dati.get("Nome Completo", "report").replace(" ", "_").lower()
                filename += f"_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                
                # Salva i byte del PDF e il nome file nello session_state
                st.session_state["pdf_bytes"] = pdf_bytes
                st.session_state["pdf_filename"] = filename
                st.session_state["pdf_ready"] = True # Imposta il flag per mostrare il pulsante di download
                
                st.success("✅ PDF generato con successo! Clicca su 'Scarica Report PDF' qui sotto.")
                st.rerun() # Forza un re-run per aggiornare la UI e mostrare il pulsante di download

            except Exception as e:
                st.error("❌ Errore durante la generazione del PDF.")
                st.exception(e) # Mostra l'eccezione completa per debugging
        
        # Mostra il pulsante di download solo se il PDF è stato generato e il flag è True
        if st.session_state["pdf_ready"]:
            st.download_button(
                label="📥 Scarica Report PDF",
                data=st.session_state["pdf_bytes"],
                file_name=st.session_state["pdf_filename"],
                mime="application/pdf",
                key="download_button_final"
            )
            # Puoi decommentare la riga sotto se vuoi che il pulsante di download sparisca dopo il primo download
            # st.session_state["pdf_ready"] = False 

    else:
        st.warning("⚠ Nessun dato disponibile.")
        st.info("Torna alla sezione **Mappa Numerologica** e genera la mappa prima di accedere a questa pagina.")

# Avvia l'applicazione Streamlit se lo script viene eseguito direttamente
if __name__ == '__main__':
    run()
