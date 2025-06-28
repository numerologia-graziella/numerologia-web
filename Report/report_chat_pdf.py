import streamlit as st
import io
from fpdf import FPDF
import os # Importa il modulo os per la gestione dei percorsi

# --- Percorso per i font ---
# Assicurati che questi file si trovino nella cartella 'fonts' sotto 'pages'.
FONT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "pages", "fonts")
DEJAVU_FONT_PATH = os.path.join(FONT_DIR, "DejaVuSans.ttf")
DEJAVU_BOLD_FONT_PATH = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf") # Path per il bold
DEJAVU_BOLD_OBLIQUE_FONT_PATH = os.path.join(FONT_DIR, "DejaVuSans-BoldOblique.ttf") # Path per il bold-oblique/italic

# --- Classe PDF personalizzata ---
class PDF(FPDF):
    def __init__(self, orientation='P', unit='mm', format='A4'):
        super().__init__(orientation, unit, format)
        try:
            # Aggiungi il font normale
            if not os.path.exists(DEJAVU_FONT_PATH):
                st.error(f"ERRORE CRITICO: Font normale DejaVuSans.ttf non trovato al percorso: {DEJAVU_FONT_PATH}")
                raise FileNotFoundError(f"Font normale non trovato: {DEJAVU_FONT_PATH}")
            self.add_font("DejaVuSans", "", DEJAVU_FONT_PATH)
            
            # Aggiungi esplicitamente il font bold
            if os.path.exists(DEJAVU_BOLD_FONT_PATH):
                self.add_font("DejaVuSans", "B", DEJAVU_BOLD_FONT_PATH)
            else:
                print(f"Attenzione: Font bold non trovato: {DEJAVU_BOLD_FONT_PATH}. Il bold potrebbe essere sintetizzato.")

            # --- NUOVA AGGIUNTA QUI: Aggiungi il font per lo stile italic ('I') ---
            if os.path.exists(DEJAVU_BOLD_OBLIQUE_FONT_PATH):
                # Usiamo DejaVuSans-BoldOblique.ttf per lo stile italic ('I')
                self.add_font("DejaVuSans", "I", DEJAVU_BOLD_OBLIQUE_FONT_PATH)
            else:
                print(f"Attenzione: Font BoldOblique (per italic) non trovato: {DEJAVU_BOLD_OBLIQUE_FONT_PATH}. L'italic potrebbe essere sintetizzato.")
            # --- FINE NUOVA AGGIUNTA ---

            self.set_font('DejaVuSans', size=12) # Imposta il font predefinito per il documento
        except Exception as e:
            st.error(f"Errore caricamento font per PDF: {e}. Il PDF potrebbe non visualizzare correttamente i caratteri speciali.")
            self.set_font('Helvetica', size=12) 

    def header(self):
        self.set_font('DejaVuSans', 'B', 15)
        self.cell(0, 10, 'Report Chat con Natascha', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        # Ora che 'DejaVuSans', 'I' dovrebbe essere caricato
        self.set_font('DejaVuSans', 'I', 8) 
        self.cell(0, 10, f'Pagina {self.page_no()}/{{nb}}', 0, 0, 'C')

    def chapter_title(self, title):
        self.set_font('DejaVuSans', 'B', 12)
        self.cell(0, 8, title, 0, 1, 'L')
        self.ln(3)

# --- Funzione per generare il PDF dalla cronologia della chat ---
def generate_pdf_fpdf2(chat_messages):
    pdf = PDF() 
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=10)

    USER_TEXT_COLOR = (60, 90, 180)      
    ASSISTANT_TEXT_COLOR = (70, 70, 70) 

    INDENT_ASSISTANT = 20 
    MESSAGE_SPACING = 5 

    page_content_width = pdf.w - pdf.l_margin - pdf.r_margin

    pdf.chapter_title("Contenuto della Conversazione")
    pdf.ln(MESSAGE_SPACING)

    for msg in chat_messages:
        content = msg["content"].replace("> **", "").replace("**", "") 
        role_prefix = "Utente: " if msg["role"] == "user" else "Natascha: "
        
        if msg["role"] == "user":
            text_color = USER_TEXT_COLOR
            current_indent = 0 
            text_width_for_message = page_content_width 
        else: # assistant
            text_color = ASSISTANT_TEXT_COLOR
            current_indent = INDENT_ASSISTANT 
            text_width_for_message = page_content_width - INDENT_ASSISTANT 

        pdf.set_font('DejaVuSans', 'B' if msg["role"] == "user" else '', 10) 
        pdf.set_text_color(*text_color)

        message_content_with_prefix = f"{role_prefix}{content}"

        pdf.set_x(pdf.l_margin + current_indent)
        
        pdf.multi_cell(w=text_width_for_message, h=6, txt=message_content_with_prefix)
        
        pdf.ln(MESSAGE_SPACING)

    pdf_output = io.BytesIO(pdf.output())
    pdf_output.seek(0)
    return pdf_output

# --- Funzione 'run' (rimane invariata) ---
def run():
    st.title("📄 Genera il Tuo Report della Chat")
    st.write(
        "Qui puoi generare un report PDF contenente l'intera conversazione avuta con Natascha. "
        "Utile per rivedere le tue intuizioni numerologiche!"
    )
    st.subheader("Anteprima Chat")
    if st.session_state.get('messages'):
        for msg in st.session_state.messages:
            with st.chat_message(msg['role'], avatar="🥰" if msg['role']=='assistant' else None):
                st.markdown(msg['content'])
    else:
        st.info("Nessun messaggio nella chat. Avvia una conversazione sulla pagina principale (Chatbot Numerologia).")
    st.markdown("---")
    if st.button("📄 Scarica Report PDF"):
        if st.session_state.get('messages'):
            with st.spinner("Preparando il tuo PDF..."):
                pdf_output = generate_pdf_fpdf2(st.session_state.messages) 
                st.download_button(
                    label="Clicca per Scaricare il PDF",
                    data=pdf_output,
                    file_name="report_chat_natascha.pdf",
                    mime="application/pdf"
                )
            st.success("Il tuo report PDF è pronto per il download!")
        else:
            st.warning("La chat è vuota! Avvia una conversazione sulla pagina principale prima di generare un report.")
