import streamlit as st
import matplotlib.pyplot as plt
import os
import json

def run():
    st.header("🧭 Schema Energetico")

    mappa = st.session_state.get("mappa_numerologica_corrente", {})

    if not mappa:
        st.error("⚠️ Alcuni valori numerologici non sono disponibili. Torna alla sezione 'Mappa Numerologica' e calcola la mappa prima di accedere a questo schema.")
        return

    # Estrai valori numerologici
    valori_schema = {
        "Anima": mappa.get("Numero Anima (riduzione 2)", 0),
        "Espressione": mappa.get("Numero Espressione (riduzione 2)", 0),
        "Sentiero di Vita": mappa.get("Sentiero di Vita (Metodo 1 - riduzione 2)", 0),
        "Quintessenza": mappa.get("Quintessenza (riduzione 2)", 0),
        "Persona": mappa.get("Numero Personalita (riduzione 2)", 0)
    }

    def riduci_fino_1(n):
        while n > 9:
            n = sum(int(c) for c in str(n))
        return n

    # Calcoli energetici
    unione_coesiva = riduci_fino_1(valori_schema["Sentiero di Vita"] + valori_schema["Persona"] + valori_schema["Quintessenza"])
    unione_energetica = riduci_fino_1(valori_schema["Anima"] + valori_schema["Persona"] + valori_schema["Espressione"])
    interconnessione = riduci_fino_1(valori_schema["Anima"] + valori_schema["Sentiero di Vita"] + valori_schema["Espressione"] + valori_schema["Quintessenza"])

    # --- Grafico ---
    fig, ax = plt.subplots(figsize=(6, 6))
    posizioni = {
        "Anima": (0, 1),
        "Quintessenza": (1, 1),
        "Espressione": (1, 0),
        "Sentiero di Vita": (0, 0),
        "Persona": (0.5, 0.5)
    }

    ax.plot([0, 0.5, 1], [1, 0.5, 0], color="green", linestyle="solid", label="Unione Coesiva")
    ax.plot([0, 0.5, 1], [0, 0.5, 1], color="blue", linestyle="solid", label="Unione Energetica")
    ax.plot([0, 1, 1, 0, 0], [1, 1, 0, 0, 1], color="red", linestyle="dashed", label="Interconnessione")

    for chiave, (x, y) in posizioni.items():
        ax.text(x, y, f"{chiave}\n({valori_schema[chiave]})", ha="center", va="center", fontsize=10,
                bbox=dict(facecolor='lightyellow', edgecolor='black'))

    ax.set_xlim(-0.2, 1.2)
    ax.set_ylim(-0.2, 1.2)
    ax.axis('off')
    ax.legend(loc="center left", bbox_to_anchor=(1.05, 0.5), borderaxespad=0.)
    st.pyplot(fig)

    # --- Descrizioni ---
    energia_descrizioni = {
        1: "Volontà individuale, energia primaria, iniziativa.",
        2: "Sensibilità relazionale, armonia e intuizione.",
        3: "Espressività, gioia, espansione creativa.",
        4: "Stabilità, ordine, costruzione.",
        5: "Cambiamento, libertà, movimento.",
        6: "Amore, responsabilità, armonia domestica.",
        7: "Ricerca interiore, saggezza, introspezione.",
        8: "Potere, gestione, equilibrio materiale.",
        9: "Altruismo, spiritualità, servizio agli altri."
    }

    st.markdown("### 🔍 Significati delle Energie")
    st.markdown(f"**Unione Coesiva ({unione_coesiva}):** {energia_descrizioni.get(unione_coesiva, 'Descrizione non disponibile')}")
    st.markdown(f"**Unione Energetica ({unione_energetica}):** {energia_descrizioni.get(unione_energetica, 'Descrizione non disponibile')}")
    st.markdown(f"**Interconnessione Energetica ({interconnessione}):** {energia_descrizioni.get(interconnessione, 'Descrizione non disponibile')}")

    approfondimenti = {
        1: "🟡 Energia 1: L'unione con questa vibrazione indica un impulso forte a guidare e decidere in autonomia. Agisci come pioniere, spinto da un desiderio di indipendenza e leadership.",
        2: "🔵 Energia 2: L'energia è dolce, cooperativa e intuitiva. Hai un grande bisogno di armonia nei legami e sei sensibile alle energie altrui.",
        3: "🟠 Energia 3: Hai unione attraverso la comunicazione, l’allegria e l’espressione creativa. Il dialogo e la leggerezza sono il tuo linguaggio.",
        4: "🟤 Energia 4: Struttura, disciplina e affidabilità guidano le tue relazioni. Ami la stabilità e tendi a costruire legami solidi e duraturi.",
        5: "🔺 Energia 5: Il cambiamento è l’elemento dominante. Ti unisci con flessibilità e apertura, ma cerchi stimoli e novità.",
        6: "❤️ Energia 6: Amore, cura e responsabilità sono i pilastri. La tua unione avviene attraverso la dedizione e il senso del dovere.",
        7: "💜 Energia 7: La profondità, la riflessione e la connessione spirituale guidano i tuoi legami. Cerchi senso e verità.",
        8: "⚫ Energia 8: Il potere personale, la concretezza e la visione materiale influenzano il modo in cui ti relazioni.",
        9: "🌈 Energia 9: Agisci con compassione e altruismo. La tua unione è ispirata da ideali elevati e senso del servizio."
    }

    with st.expander("🔍 Approfondisci la tua Unione Coesiva"):
        st.markdown(approfondimenti.get(unione_coesiva, "Nessuna descrizione disponibile."))

    with st.expander("🔍 Approfondisci la tua Unione Energetica"):
        st.markdown(approfondimenti.get(unione_energetica, "Nessuna descrizione disponibile."))

    with st.expander("🔍 Approfondisci la tua Interconnessione Energetica"):
        st.markdown(approfondimenti.get(interconnessione, "Nessuna descrizione disponibile."))

    st.markdown("### ℹ️ Che cosa sono queste energie?")
    st.markdown("""
- **Unione Coesiva**: rappresenta il legame profondo tra la tua essenza, la tua personalità e la missione della tua vita.
- **Unione Energetica**: riflette l'allineamento tra il tuo mondo interiore (Anima), l'identità percepita (Persona) e l'espressione sociale.
- **Interconnessione Energetica**: mostra come le tue energie fondamentali cooperano per sostenere la tua evoluzione personale.
    """)

    if st.button("🔗 Salva e apri la Chatbot dalla sidebar"):
        st.session_state["valori_energetici_schema"] = {
            "Unione Coesiva": unione_coesiva,
            "Unione Energetica": unione_energetica,
            "Interconnessione Energetica": interconnessione
        }

        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        json_path = os.path.join(root_dir, "mappa_per_chatbot.json")

        dati_esistenti = {}
        if os.path.exists(json_path):
            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    dati_esistenti = json.load(f)
            except json.JSONDecodeError:
                pass

        dati_esistenti.update({
            "Unione Coesiva": unione_coesiva,
            "Unione Energetica": unione_energetica,
            "Interconnessione Energetica": interconnessione
        })

        try:
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(dati_esistenti, f, ensure_ascii=False, indent=2)
        except Exception as e:
            st.error(f"Errore nel salvataggio del file: {e}")
            return

        st.markdown("---")
        st.success("✅ I valori sono stati salvati.")
        st.info("👈 Ora apri la **Chatbot Numerologica** dal menu a sinistra.")
