import streamlit as st
import re # Per le espressioni regolari per l'analisi dell'indirizzo

st.set_page_config(layout="centered") # Assicurati che il layout sia centrato per questa pagina

st.title("Curiosità Numerologiche 🌟")
st.write("Esplora aspetti unici e affascinanti della numerologia attraverso queste sezioni speciali.")

# Inizializza lo stato della sessione per gestire la sottosezione corrente
if 'curiosita_sottopagina' not in st.session_state:
    st.session_state.curiosita_sottopagina = 'principale' # Le opzioni saranno: 'principale', 'pet_energy', 'nome_arte', 'numerologia_indirizzo'

# --- FUNZIONI DI CALCOLO NUMEROLOGICO GENERALI ---

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

def riduci_fino_1_singolo(n):
    """Riduce un numero fino a una singola cifra (sempre)."""
    if n is None:
        return 0
    while n > 9:
        n = sum(int(digit) for digit in str(n))
    return n

# --- FUNZIONE GENERALE PER IL CALCOLO NUMEROLOGICO (DA NOME/TESTO) ---
# Questa funzione è stata spostata qui per essere definita PRIMA di essere chiamata
def calculate_numerology_number(name):
    """
    Calcola il numero numerologico di un nome (o testo).
    Ogni lettera è mappata a un numero e la somma viene ridotta a una singola cifra.
    Rileva anche se la somma iniziale era un numero karmico (13, 14, 16, 19).
    """
    name = name.upper().replace(" ", "") # Converti in maiuscolo e rimuovi spazi
    total_sum = 0
    for char in name:
        total_sum += valore_lettera(char) # Usa la funzione valore_lettera

    # Controlla se la somma totale iniziale è un numero karmico
    karmic_debt_numbers = [13, 14, 16, 19]
    is_karmic_debt_base = None
    if total_sum in karmic_debt_numbers:
        is_karmic_debt_base = total_sum

    final_number = riduci_fino_1_singolo(total_sum) # Usa la funzione riduci_fino_1_singolo

    return final_number, is_karmic_debt_base # Restituisce il numero finale e l'eventuale base karmica


# --- FUNZIONI SPECIFICHE PER L'ANALISI DELL'INDIRIZZO ---
# Queste funzioni sono state mantenute qui, dato che usano le funzioni generali sopra.

def calcola_numero_civico(civico_str):
    """
    Calcola il numero numerologico di un civico, gestendo vari formati:
    - Numerico (es. "2")
    - Frazionale numerico (es. "2/12")
    - Alfanumerico (es. "2/A")
    """
    if not civico_str:
        return None # Nessun civico da calcolare

    civico_str = civico_str.strip().upper() # Normalizza

    # Caso 2: Civico frazionale numerico (es. 2/12)
    # Caso 3: Civico alfanumerico (es. 2/A)
    match_slash = re.match(r'(\d+)\s*/\s*(\w+)', civico_str)
    if match_slash:
        num_parte1 = int(match_slash.group(1))
        parte2 = match_slash.group(2)
        
        if parte2.isdigit(): # Esempio: 2/12
            num_parte2 = int(parte2)
            somma_base = num_parte1 + num_parte2
        else: # Esempio: 2/A
            val_lettera_val = valore_lettera(parte2) # Usa valore_lettera
            somma_base = num_parte1 + val_lettera_val
        
        return riduci_fino_1_singolo(somma_base) # Usa riduci_fino_1_singolo

    # Caso 1: Civico numerico semplice (es. "2", "N. 2", "NR. 2", "CIVICO 2")
    # Cerca numeri all'interno o alla fine della stringa, ignorando prefissi comuni
    match_simple_num = re.search(r'\b(?:N(?:R)?\.?\s*|CIVICO\s+)?(\d+)\b', civico_str)
    if match_simple_num:
        num_semplice = int(match_simple_num.group(1))
        return riduci_fino_1_singolo(num_semplice) # Usa riduci_fino_1_singolo
    
    return None # Nessun formato civico riconosciuto

def estrai_nome_via_per_numerologia(indirizzo_completo):
    """
    Estrae il nome proprio della via/luogo rimuovendo tipi di indirizzo e numeri civici.
    Utilizzato quando non c'è un numero civico esplicito o per il caso 4.
    """
    # Normalizza l'indirizzo
    indirizzo_pulito = indirizzo_completo.strip().lower()

    # Rimuovi i numeri civici espliciti (se presenti ma non identificati da calcola_numero_civico)
    # pattern per "n. X", "nr. X", "civico X", "X/Y", "X/A", o solo "X" alla fine
    indirizzo_pulito = re.sub(r'\b(?:n(?:r)?\.?\s*|civico\s+)?\d+\s*(?:[/.-]?\s*\w+)?\b', '', indirizzo_pulito)
    
    # Rimuovi i termini che indicano il tipo di luogo o prefissi descrittivi noti
    termini_da_escludere = [
        r'\bvia\b', r'\bpiazza\b', r'\bcorso\b', r'\bviale\b', r'\bstrada\b',
        r'\blargo\b', r'\bvicolo\b', r'\bfrazione\b', r'\blocalita\b', r'\bpodere\b',
        r'\bcascina\b', r'\bcontrada\b', r'\bresidence\b', r'\bcomplesso\b',
        r'\bvillaggio\b', r'\bcs\s*casa\b', r'\bcasa\b' # 'casa' da solo va con attenzione
    ]
    
    for termine in termini_da_escludere:
        indirizzo_pulito = re.sub(termine, '', indirizzo_pulito)

    # Rimuovi segni di punteggiatura e spazi extra
    indirizzo_pulito = re.sub(r'[^\w\s]', '', indirizzo_pulito).strip()
    indirizzo_pulito = re.sub(r'\s+', ' ', indirizzo_pulito).strip()
    
    return indirizzo_pulito


def calcola_numero_da_stringa(testo):
    """Calcola il numero numerologico da una stringa di testo."""
    somma_lettere = 0
    for char in testo:
        somma_lettere += valore_lettera(char) # Usa valore_lettera
    return riduci_fino_1_singolo(somma_lettere) # Usa riduci_fino_1_singolo


# --- DIZIONARI DELLE INTERPRETAZIONI ---

# Interpretazioni dei numeri numerologici per Pet Energy
pet_interpretations = {
    1: "Questo pet incarna lo spirito del Capo: è l'Alpha indiscusso del branco, una creatura fiera che non si piega mai. E' coraggioso, energico, solitario e ama andare a caccia.",
    2: "Sensibile, affetuoso, dolce, cerca compagnia, fedele, pacifico.",
    3: "Questo pet è l’incarnazione della dolcezza e della sensibilità. Con occhi che sembrano leggere l’animo e una presenza rassicurante. E' Giocherellone, espressivo, vivace, ama essere al centro dell'attenzione e giocare con i bambini.",
    4: "Solido come una roccia, questo pet è una presenza costante e rassicurante. Ha una natura stabile e tranquilla, ama la routine, è protettivo ed affidabile.",
    5: "Questo pet è nato per muoversi, scoprire, vivere intensamente. Ogni suo passo è guidato dalla curiosità. E'avventuroso, curioso, energico, ama l'esplorazione e la libertà.",
    6: "Questo pet è il cuore caldo della casa, una presenza amorevole che nutre chi gli sta intorno con affetto, calma e dedizione. Ha un animo dolce e profondo, sempre pronto a offrire conforto nei momenti difficili e gioia in quelli sereni.",
    7: "Questo pet è avvolto da un’aura silenziosa e affascinante. Intuitivo al punto da percepire emozioni non dette, si muove con grazia e attenzione, come se sapesse sempre qualcosa in più. E'misterioso ed intuitivo",
    8: "Questo pet è una forza della natura. Dotato di una presenza imponente e un’energia incrollabile, domina l’ambiente con naturale autorità. E' forte ma protettivo.",
    9: "Questo pet possiede un’anima antica, fatta di calma, empatia e profonda saggezza. È compassionevole altruista, saggio, protettivo verso i più deboli per natura."
}

# Interpretazioni dei numeri numerologici per Nome d'Arte
art_name_interpretations = {
    1: "Il nome d’arte con vibrazione numerologica 1 è perfetto per chi desidera iniziare un nuovo cammino, distinguersi, e guidare. È il numero dei leader nati, degli innovatori, di chi non segue le orme degli altri ma traccia la propria strada con coraggio e determinazione..",
    2: "Il nome d’arte con vibrazione numerologica 2 è l’emblema della cooperazione, della sensibilità e dell’armonia interiore. Questo nome è perfetto per chi vuole portare bellezza, equilibrio e mediare per la pace.",
    3: "Il numero 3 è la vibrazione della creatività pura, dell’espressione gioiosa e della comunicazione magnetica. Un nome d’arte che risuona con il numero 3 è fatto per chi vuole incantare, divertire, ispirare. È ideale per artisti che mettono il cuore nella loro arte e usano la parola, il corpo, la voce o l’immaginazione per creare bellezza.",
    4: "Il numero 4 è la vibrazione della stabilità, della disciplina e della dedizione al lavoro. Un nome d’arte con questa energia parla di qualcuno affidabile, coerente e determinato, che punta non solo al successo, ma alla credibilità e alla sostanza e ad un percorso solido",
    5: "Il numero 5 è la vibrazione della libertà, del cambiamento e dell’energia travolgente. Un nome d’arte che risuona con il 5 è perfetto per chi vuole vivere e comunicare senza limiti, con spirito avventuroso e una personalità che ama rompere gli schemi.",
    6: "Il numero 6 vibra con le energie dell’amore, della bellezza, della cura e dell’equilibrio. Un nome d’arte con questa vibrazione appartiene a chi si esprime con profondità emotiva e genera connessione attraverso l’arte. È perfetto per artisti che portano sensibilità, grazia e messaggi positivi nel mondo.",
    7: "Il numero 7 è la vibrazione della ricerca interiore, della mente acuta e del mistero. Un nome d’arte che risuona con il 7 è perfetto per chi vuole esprimere un’identità profonda, riflessiva, enigmatica e spirituale. È il numero di chi non si accontenta delle apparenze.",
    8: "Il numero 8 è la vibrazione del potere, della leadership e del successo tangibile. Un nome d’arte che risuona con l’8 porta con sé un’energia magnetica, forte, determinata, capace di attrarre visibilità, ricchezza e influenza.",
    9: "Il numero 9 è la vibrazione dell’idealismo, dell’arte ispirata e del servizio al mondo. Un nome d’arte con questa energia appartiene a chi è guidato da una missione più grande di sé, che usa il proprio talento per toccare le coscienze, guarire, unire o risvegliare."
}

karmic_interpretations = {
    13: " (Debito Karmico del 13/4): Implica la necessità di affrontare pigrizia o mancanza di disciplina. Il successo arriverà con dedizione e lavoro duro.",
    14: " (Debito Karmico del 14/5): Suggerisce una lezione sulla gestione della libertà e sul controllo degli eccessi. Richiede adattabilità e disciplina.",
    16: " (Debito Karmico del 16/7): Spesso legato a lezioni sull'ego e sulla distruzione per la rinascita. Richiede umiltà e una profonda crescita spirituale.",
    19: " (Debito Karmico del 19/1): Indica una lezione sull'indipendenza e la disponibilità ad accettare aiuto. Richiede di imparare a collaborare senza perdere la propria forza."
}

# Interpretazioni dei numeri numerologici per Indirizzo (corrette nella chiusura della stringa)
interpretazioni_indirizzo = {
    1: """
    Una casa di tipo **Uno** è ottima per una persona che vuole intraprendere un’iniziativa individuale. Chi vive in una casa di tipo Uno impara dall’esperienza piuttosto che attraverso l’istruzione e i consigli degli altri. Una casa di tipo Uno è di aiuto a chi vuole seguire il proprio istinto ed esprimere la propria personalità in modo creativo e originale. In una casa di tipo Uno spesso si possono avvertire forti emozioni, specie se vi abitano individui dalla spiccata personalità. Una casa di tipo Uno non sempre è pulita; spesso alcuni dettagli saranno secondari rispetto alla creatività. Se in passato ti sei preso cura degli altri e ora desideri essere tu al centro della tua vita, allora trasferisciti in una casa di questo tipo. Ti sentirai più assertivo, indipendente e disponibile ad affrontare dei rischi.
    """,
    2: """
    Una casa di tipo **Due** è un luogo di armonia, cooperazione e partnership. È ideale per coppie o famiglie che cercano di costruire una vita insieme con supporto reciproco. Forza: favorisce la pace, la diplomazia e la connessione emotiva. Sfida: può portare a indecisione, codipendenza o tendenza a evitare i conflitti. Le persone potrebbero sentirsi troppo concentrate sulle dinamiche relazionali. Ottima per chi cerca un nido accogliente e vuole imparare a coesistere.
    """,
    3: """
    Una casa di tipo **Tre** vibra con energia di gioia, creatività e socialità. È un ambiente vivace, ispirante, spesso pieno di arte e conversazioni. Forza: stimola l'espressione personale, l'ottimismo e la socializzazione. Ideale per artisti, scrittori o chi ama ospitare. Sfida: può portare a dispersione di energie, superficialità o difficoltà a gestire le responsabilità quotidiane. Potrebbe essere un po' caotica ma divertente.
    """,
    4: """
    Una casa di tipo **Quattro** offre stabilità, struttura e un forte senso di sicurezza. È un luogo dove si possono costruire solide fondamenta, ideale per chi cerca radicamento e disciplina. Forza: favorisce il lavoro duro, l'organizzazione e la praticità. È un ambiente affidabile e concreto. Sfida: può diventare troppo rigida, prevedibile o noiosa. Rischio di sentirsi limitati o eccessivamente concentrati su doveri e routine.
    """,
    5: """
    Una casa di tipo **Cinque** è un centro di cambiamento, libertà e avventura. È un luogo in cui le cose non rimangono mai uguali a lungo, perfetto per chi ama l'esplorazione e la varietà. Forza: stimola l'adattabilità, l'eccitazione e nuove esperienze. Ideale per viaggiatori o spiriti liberi. Sfida: può portare a irrequietezza, impulsività e mancanza di stabilità. Rischio di sentirsi sempre in transizione o di non riuscire a mettere radici.
    """,
    6: """
    Una casa di tipo **Sei** emana energia di amore, cura e responsabilità. È il prototipo di "casa" in senso familiare, un rifugio accogliente e dedito al benessere dei suoi abitanti. Forza: favorisce l'armonia familiare, il senso di comunità e la bellezza. Ideale per famiglie numerose o chi ama prendersi cura degli altri. Sfida: può portare a eccessiva preoccupazione, perfezionismo o tendenza a immischiarsi troppo nella vita altrui. Rischio di sentirsi gravati da troppe responsabilità.
    """,
    7: """
    Una casa di tipo **Sette** è un santuario per l'introspezione, lo studio e la ricerca spirituale. È un luogo tranquillo, spesso isolato, che favorisce la riflessione e la crescita interiore. Forza: stimola l'analisi, l'intuizione e la ricerca della verità. Ideale per pensatori, ricercatori o chi cerca pace e solitudine. Sfida: può portare a isolamento, eccessiva riservatezza o un'atmosfera un po' fredda. Rischio di sentirsi disconnessi dal mondo esterno o di perdere la spontaneità.
    """,
    8: """
    Una casa di tipo **Otto** vibra con energia di potere, ambizione e abbondanza materiale. È un ambiente dinamico che supporta il successo, il riconoscimento e la realizzazione di grandi obiettivi. Forza: attrae prosperità, organizzazione e leadership. Ideale per imprenditori o chiunque miri a grandi risultati. Sfida: può portare a materialismo, lotta per il controllo o stress legato alle finanze e alla carriera. Rischio di un'atmosfera troppo focalizzata sul "fare" piuttosto che sull'"essere".
    """,
    9: """
    Una casa di tipo **Nove** emana energia di umanitarismo, compassione e completamento. È un luogo di accettazione universale, spesso aperto a tutti e con un'atmosfera di saggezza. Forza: favorisce l'altruismo, l'ispirazione e il senso di servizio. Ideale per chi vuole contribuire al bene comune o ha una visione ampia. Sfida: può portare a idealismo eccessivo, sacrificio di sé o dispersione di energie. Rischio di trascurare i bisogni personali o della casa stessa a favore di cause esterne.
    """
}


# --- Layout per i pulsanti delle sottosezioni ---
col1, col2, col3 = st.columns(3) # Aggiungi una terza colonna per il nuovo pulsante

with col1:
    # Pulsante per la sezione "Pet Energy"
    if st.button("Pet Energy 🐾", use_container_width=True):
        st.session_state.curiosita_sottopagina = 'pet_energy'

with col2:
    # Pulsante per la sezione "Nome d'Arte"
    if st.button("Nome d'Arte 🎨", use_container_width=True):
        st.session_state.curiosita_sottopagina = 'nome_arte'

with col3: # Nuova colonna per il pulsante Indirizzo
    # Pulsante per la sezione "Numerologia dell'Indirizzo"
    if st.button("Numerologia Indirizzo 🏠", use_container_width=True):
        st.session_state.curiosita_sottopagina = 'numerologia_indirizzo'

st.markdown("---") # Una linea orizzontale per separare i pulsanti dal contenuto

# --- Logica per mostrare il contenuto in base alla selezione della sottosezione ---
if st.session_state.curiosita_sottopagina == 'pet_energy':
    st.header("Numerologia per i tuoi Amici a Quattro Zampe: Pet Energy 🐾")
    st.image("https://placehold.co/600x200/C1FFDDC1/800000?text=Pet+Energy", caption="[Image of Pet Energy]")
    st.write("""
    Anche i nostri compagni animali, siano essi cani, gatti, uccelli o altri, portano con sé una propria "energia" unica.
    Pur non essendo una pratica numerologica tradizionale, molti amanti degli animali
    si divertono a esplorare come la numerologia possa offrire intuizioni sul temperamento e le abitudini del proprio pet.
    """)

    # Input per il nome del pet
    pet_name = st.text_input("Inserisci il nome del tuo pet:", key="pet_name_input")

    if pet_name:
        # Calcola il numero del pet e controlla il debito karmico
        pet_number, pet_karmic_base = calculate_numerology_number(pet_name)

        st.subheader(f"Il Numero del Sentiero di Vita del tuo pet **{pet_name}** è: **{pet_number}**")

        # Interpretazione del numero principale usando il dizionario specifico per i pet
        st.write(f"Interpretazione: {pet_interpretations.get(pet_number, 'Numero non riconosciuto.')}")

        # Aggiungi nota per il debito karmico, se presente
        if pet_karmic_base:
            st.warning(f"**Nota:** La somma iniziale del nome era {pet_karmic_base}. Questo indica un **Debito Karmico**{karmic_interpretations.get(pet_karmic_base, '')}")

    else:
        st.info("Inserisci il nome del tuo pet per scoprire la sua energia numerologica!")

    st.subheader("Come Applicarla?")
    st.write("""
    Puoi considerare la **data di nascita** (se conosciuta) o la **data di adozione** del tuo animale.
    Calcolando il **Numero del Sentiero di Vita** (la somma di tutte le cifre della data ridotta a un'unica cifra), puoi ottenere una "vibrazione" principale.
    È un modo divertente per riflettere sulla personalità del tuo animale e rafforzare il vostro legame!
    """)
    st.info("Pensa al tuo animale: quale numero pensi che descriva meglio la sua essenza?")


elif st.session_state.curiosita_sottopagina == 'nome_arte':
    st.header("Il Tuo Pseudonimo: Numerologia del Nome d'Arte 🎨")
    st.image("https://placehold.co/600x200/DDC1FF/800000?text=Nome+d'Arte", caption="[Image of Art Name]")
    st.write("""
    Per artisti, scrittori o chiunque desideri un'identità pubblica distinta, la scelta di un **nome d'arte**
    non è casuale. La numerologia può essere uno strumento affascinante per selezionare uno pseudonimo
    che vibri in armonia con i tuoi obiettivi creativi e il messaggio che vuoi trasmettere.
    """)

    # Input per il nome d'arte
    art_name = st.text_input("Inserisci il tuo nome d'arte o pseudonimo:", key="art_name_input")

    if art_name:
        # Calcola il numero del nome d'arte e controlla il debito karmico
        art_name_number, art_karmic_base = calculate_numerology_number(art_name)

        st.subheader(f"Il Numero del Sentiero di Vita per **{art_name}** è: **{art_name_number}**")

        # Interpretazione del numero principale usando il dizionario specifico per i nomi d'arte
        st.write(f"Interpretazione: {art_name_interpretations.get(art_name_number, 'Numero non riconosciuto.')}")

        # Aggiungi nota per il debito karmico, se presente
        if art_karmic_base:
            st.warning(f"**Nota:** La somma iniziale del nome era {art_karmic_base}. Questo indica un **Debito Karmico**{karmic_interpretations.get(art_karmic_base, '')}")

    else:
        st.info("Inserisci un nome d'arte per scoprire la sua energia numerologica!")

    st.subheader("Come Scegliere un Nome d'Arte?")
    st.write("""
    Ogni lettera dell'alfabeto corrisponde a un numero (A=1, B=2, C=3, ecc.).
    Sommando i valori numerici delle lettere del nome d'arte, si ottiene un **Numero del Sentiero di Vita**
    per quel nome, che ne rivela l'energia principale.
    Scegliere un nome d'arte con una risonanza numerologica positiva può amplificare la tua energia
    e attrarre il tipo di attenzione desiderato per la tua opera.
    """)
    st.info("Stai pensando a un nome d'arte? Calcola la sua numerologia per scoprire la sua vibrazione!")

# --- NUOVA SOTTOSEZIONE: NUMEROLOGIA DELL'INDIRIZZO ---
elif st.session_state.curiosita_sottopagina == 'numerologia_indirizzo':
    st.header("Numerologia della Tua Casa e Indirizzo 🏠")
    st.image("https://placehold.co/600x200/FFC1DD/800000?text=Numerologia+Indirizzo", caption="[Image of Numerologia Indirizzo]")
    st.write("Scopri l'energia numerologica del tuo indirizzo, che può influenzare l'atmosfera e le esperienze di chi ci vive.")
    
    indirizzo_input = st.text_input("Inserisci l'indirizzo completo (es. Via Roma 10, Piazza Manzoni, cs casa simonelli n. 2)", key="indirizzo_input_curiosita").strip()

    if st.button("Calcola Numero dell'Indirizzo 🔢", type="primary"):
        if not indirizzo_input:
            st.error("Per favore, inserisci un indirizzo per calcolare il suo numero.")
        else:
            numero_calcolato = None
            
            # Tenta di estrarre un numero civico con vari formati
            civico_pattern = re.compile(r'\b(?:n(?:r)?\.?\s*|civico\s+)?(\d+(?:\s*[/.-]?\s*\w+)?)\b', re.IGNORECASE)
            match_civico = civico_pattern.search(indirizzo_input)
            
            if match_civico:
                civico_found = match_civico.group(1)
                numero_calcolato = calcola_numero_civico(civico_found)
                
                if numero_calcolato is not None:
                    st.subheader(f"Numero civico rilevato: `{civico_found}`")
                    st.success(f"Il numero numerologico del tuo civico è: **{numero_calcolato}**")
            
            # Se non è stato trovato un numero civico o il calcolo ha fallito (es. None)
            if numero_calcolato is None:
                st.info("Nessun numero civico specifico rilevato o valido. Calcolo basato sul nome della via/località.")
                via_pulita_per_calcolo = estrai_nome_via_per_numerologia(indirizzo_input)
                
                if via_pulita_per_calcolo:
                    numero_calcolato = calcola_numero_da_stringa(via_pulita_per_calcolo)
                    st.subheader(f"Nome della via/località utilizzato per il calcolo: `{via_pulita_per_calcolo}`")
                    st.success(f"Il numero numerologico della tua via/località è: **{numero_calcolato}**")
                else:
                    st.error("Impossibile estrarre un nome valido della via/località dall'indirizzo fornito.")

            st.markdown("---")
            if numero_calcolato is not None and numero_calcolato > 0:
                st.subheader(f"Significato del Numero {numero_calcolato} per il tuo Indirizzo:")
                st.write(interpretazioni_indirizzo.get(numero_calcolato, "Significato non disponibile per questo numero."))
            else:
                st.warning("Impossibile determinare un numero numerologico significativo per l'indirizzo fornito. Prova con un formato diverso.")
    
    st.subheader("Come Funziona?")
    st.write("""
    La numerologia applicata agli indirizzi analizza l'energia vibratoria di un luogo.
    Il calcolo si concentra sul numero civico. Se presente e interpretabile (anche con frazioni o lettere),
    si riduce quel numero a una singola cifra.
    Se non è presente un numero civico chiaro, si prende in considerazione il nome della via o della località,
    e si calcola la somma numerologica delle sue lettere, riducendola a una singola cifra.
    """)
    st.info("L'energia del tuo indirizzo può influenzare l'atmosfera e le esperienze di chi lo abita. Scopri la tua!")


# --- SEZIONE PRINCIPALE DELLE CURIOSITÀ (DEFAULT) ---
else: # st.session_state.curiosita_sottopagina == 'principale'
    st.write("""
    Seleziona una delle opzioni qui sopra per scoprire di più su come la numerologia
    può svelare aspetti interessanti nella vita dei tuoi amici animali, guidarti nella
    scelta di un nome d'arte significativo o rivelare l'energia del tuo indirizzo.
    """)
    st.image("https://placehold.co/600x400/FFDDC1/800000?text=Esplora+le+Curiosità", caption="[Image of Esplora le Curiosità]")

# Pulsante per tornare alla visualizzazione principale delle curiosità
if st.session_state.curiosita_sottopagina != 'principale':
    st.markdown("---")
    if st.button("Torna alle Curiosità Principali"):
        st.session_state.curiosita_sottopagina = 'principale'
