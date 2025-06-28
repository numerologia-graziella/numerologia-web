import streamlit as st
from datetime import datetime
import pandas as pd

st.set_page_config(
    page_title="Compatibilità di Coppia Numerologica",
    page_icon="❤️",
    layout="centered"
)

st.title("Analisi Approfondita di Compatibilità di Coppia ✨")
st.write("Esplora le complesse dinamiche energetiche tra due persone attraverso i loro numeri numerologici chiave, con dettagliate interpretazioni sulle forze e le sfide di ogni combinazione.")
st.markdown("---")

# --- FUNZIONI DI CALCOLO NUMEROLOGICO (COPIATE E ADATTATE DA 1_mappa_numerologica.py) ---

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
    """Riduce un numero fino a una singola cifra (senza mantenere maestri/karmici intermedi)."""
    if n is None:
        return 0
    while n > 9:
        n = sum(int(d) for d in str(n))
    return n

def analizza_nome_base(nome_input):
    """Analizza il nome per ottenere somma vocali, consonanti e totale."""
    vocali = "AEIOU"
    nome_input = nome_input.upper().replace(" ", "") # Rimuovi spazi per il calcolo
    
    total_val = 0
    vowels_sum = 0
    consonants_sum = 0

    for char in nome_input:
        val = valore_lettera(char)
        if val != 0: # Solo se la lettera ha un valore numerico
            total_val += val
            if char in vocali:
                vowels_sum += val
            else:
                consonants_sum += val
    
    return {
        "total": total_val,
        "vowels_sum": vowels_sum,
        "consonants_sum": consonants_sum
    }

def calcola_numeri_compatibilita_persona(nome, cognome, giorno, mese, anno):
    """
    Calcola tutti i numeri chiave (core e dinamici) per una persona.
    """
    
    # Sentiero di Vita (Metodo semplificato, coerente con 'riduci_fino_1_singolo')
    giorno_ridotto = riduci_fino_1_singolo(giorno)
    mese_ridotto = riduci_fino_1_singolo(mese)
    anno_somma_cifre = sum(int(d) for d in str(anno))
    anno_ridotto_sv = riduci_fino_1_singolo(anno_somma_cifre)
    
    sentiero_di_vita_base = giorno_ridotto + mese_ridotto + anno_somma_cifre
    sentiero_di_vita = riduci_fino_1_singolo(sentiero_di_vita_base)

    # Analisi Nome e Cognome
    analisi_nome = analizza_nome_base(nome)
    analisi_cognome = analizza_nome_base(cognome)

    full_total = analisi_nome["total"] + analisi_cognome["total"]
    
    # Numeri Core
    espressione = riduci_fino_1_singolo(full_total)
    anima = riduci_fino_1_singolo(analisi_nome["vowels_sum"] + analisi_cognome["vowels_sum"])
    persona = riduci_fino_1_singolo(analisi_nome["consonants_sum"] + analisi_cognome["consonants_sum"])
    forza = riduci_fino_1_singolo(giorno + mese) # Nota: qui uso il giorno e mese non ridotti per la base, come in mappa_numerologica (forza_intero)
    quintessenza = riduci_fino_1_singolo(full_total + sentiero_di_vita_base) # Quintessenza base come in mappa_numerologica

    # === CICLI DI VITA ===
    fine_exp = 36 - sentiero_di_vita # Usiamo il Sentiero di Vita ridotto a singola cifra
    fine_pot = fine_exp + 27
    esperienza_val = mese_ridotto
    potere_val = giorno_ridotto
    saggezza_val = anno_ridotto_sv # anno_rid2_sv in mappa_numerologica

    # === PINNACOLI ===
    p1_val_r2 = riduci_fino_1_singolo(giorno_ridotto + mese_ridotto)
    p2_val_r2 = riduci_fino_1_singolo(giorno_ridotto + anno_ridotto_sv)
    p3_val_r2 = riduci_fino_1_singolo(p1_val_r2 + p2_val_r2) # Somma dei pinnacoli ridotti
    p4_val_r2 = riduci_fino_1_singolo(mese_ridotto + anno_ridotto_sv)

    # === SFIDE ===
    s1_val_r2 = riduci_fino_1_singolo(abs(giorno_ridotto - mese_ridotto))
    s2_val_r2 = riduci_fino_1_singolo(abs(anno_ridotto_sv - giorno_ridotto))
    s3_val_r2 = riduci_fino_1_singolo(abs(s1_val_r2 - s2_val_r2)) # Differenza delle sfide ridotte
    s4_val_r2 = riduci_fino_1_singolo(abs(anno_ridotto_sv - mese_ridotto))

    return {
        "core": {
            "sentiero_di_vita": sentiero_di_vita,
            "espressione": espressione,
            "anima": anima,
            "personalita": persona,
            "forza": forza,
            "quintessenza": quintessenza
        },
        "dinamici": {
            "cicli": {
                "esperienza": esperienza_val,
                "potere": potere_val,
                "saggezza": saggezza_val
            },
            "pinnacoli": {
                "p1": p1_val_r2,
                "p2": p2_val_r2,
                "p3": p3_val_r2,
                "p4": p4_val_r2
            },
            "sfide": {
                "s1": s1_val_r2,
                "s2": s2_val_r2,
                "s3": s3_val_r2,
                "s4": s4_val_r2
            },
            # Aggiungiamo anche le età di transizione per Pinnacoli/Sfide per riferimento
            "eta_pinnacoli": {
                "fine_p1": fine_exp,
                "fine_p2": fine_exp + 9, # fine P2
                "fine_p3": fine_exp + 18 # fine P3
            }
        }
    }

# --- DIZIONARI PER LE INTERPRETAZIONI DI COMPATIBILITÀ DETTAGLIATE ---

# Funzione helper per ottenere la chiave simmetrica
def get_symmetric_key(n1, n2):
    return tuple(sorted((n1, n2)))

# --- SENTIERO DI VITA (Come già espanso) ---
sentiero_di_vita_compatibilita = {
    get_symmetric_key(1, 1): "**1 e 1:** Partnership di due leader e pionieri. C'è un'innata comprensione del bisogno di indipendenza e di prendere l'iniziativa. Forza: grande spinta comune verso obiettivi ambiziosi, energia inesauribile. Sfida: rischio di forte competizione per il controllo, difficoltà a cedere il passo o a trovare un terreno comune quando le visioni divergono. Necessaria la delega e il riconoscimento reciproco.",
    get_symmetric_key(2, 2): "**2 e 2:** Grande armonia, cooperazione e profonda empatia. Entrambi cercano pace, equilibrio e connessione emotiva. Forza: supporto reciproco eccezionale, grande capacità di comprensione e diplomazia. Sfida: tendenza a evitare i conflitti a tutti i costi, accumulando rancori. Possibile indecisione e dipendenza emotiva reciproca. Imparare ad esprimere i propri bisogni.",
    get_symmetric_key(3, 3): "**3 e 3:** Gioia, creatività e comunicazione vibrante. Relazione dinamica, divertente e socialmente attiva. Forza: grande espressione artistica e sociale, ispirazione reciproca. Sfida: superficialità, difficoltà a gestire le responsabilità e tendenza a disperdere le energie e a evitare i problemi seri con l'umorismo.",
    get_symmetric_key(4, 4): "**4 e 4:** Stabilità, affidabilità e un forte desiderio di costruire. Partnership pratica, orientata alla sicurezza e al lavoro duro. Forza: base solida e duratura per la relazione, grande capacità di realizzazione concreta. Sfida: rigidità, routine eccessiva, resistenza al cambiamento e difficoltà a esprimere spontaneamente emozioni profonde.",
    get_symmetric_key(5, 5): "**5 e 5:** Avventura, libertà e costante cambiamento. Relazione stimolante, dinamica e imprevedibile. Forza: eccitazione continua, apertura a nuove esperienze, mai noiosa. Sfida: impulsività, mancanza di radicamento, difficoltà a impegnarsi a lungo termine e tendenza a fuggire dai problemi. Necessaria stabilità per non bruciarsi.",
    get_symmetric_key(6, 6): "**6 e 6:** Amore, responsabilità e un profondo senso di cura. Partnership dedicata alla famiglia, alla casa e al benessere reciproco. Forza: forte legame emotivo, dedizione incondizionata, grande capacità di creare un ambiente accogliente. Sfida: perfezionismo, iper-controllo, tendenza a sacrificarsi eccessivamente e a trascurare i bisogni individuali per il 'bene comune'.",
    get_symmetric_key(7, 7): "**7 e 7:** Profondità, introspezione e ricerca intellettuale/spirituale. Connessione basata sulla mente e sull'anima. Forza: grande comprensione reciproca su un piano profondo, amano esplorare misteri e verità. Sfida: tendenza all'isolamento, eccessiva analisi e difficoltà a connettersi emotivamente a un livello superficiale.",
    get_symmetric_key(8, 8): "**8 e 8:** Potere, ambizione e orientamento al successo materiale. Partnership focalizzata sul raggiungimento di grandi obiettivi e sulla prosperità. Forza: forza di volontà enorme, capacità di manifestare abbondanza, ispirazione reciproca al successo. Sfida: lotta per il controllo, materialismo e tendenza a trascurare l'aspetto emotivo.",
    get_symmetric_key(9, 9): "**9 e 9:** Compassione, altruismo e visione globale. Partnership idealista che mira a servire un bene superiore o l'umanità. Forza: profonda empatia, saggezza e un grande senso di umanitarismo. Sfida: idealismo eccessivo che può portare a frustrazione, tendenza a sacrificare i bisogni personali e della coppia per cause esterne. Rischio di sentirsi non compresi nel proprio bisogno di dare.",

    # Combinazioni Complementari
    get_symmetric_key(1, 2): "**1 e 2:** L'energia del 1 (azione) e del 2 (cooperazione). Forza: il 1 porta iniziativa e leadership, il 2 armonia e diplomazia. Possono creare un grande equilibrio. Sfida: il 1 deve imparare la pazienza, il 2 l'assertività. Il 2 può sentirsi sopraffatto dal 1, il 1 frustrato dalla prudenza del 2.",
    get_symmetric_key(1, 3): "**1 e 3:** Il leader espressivo. Il 1 dà direzione, il 3 porta gioia e creatività. Forza: energia dinamica e divertente, grande potenziale di successo in progetti creativi o sociali. Sfida: il 1 può trovare il 3 superficiale, il 3 il 1 troppo serio. Bilanciare disciplina per il 3 e flessibilità per il 1.",
    get_symmetric_key(1, 4): "**1 e 4:** Il pioniere e il costruttore. Il 1 vuole muoversi velocemente, il 4 vuole costruire solide basi. Forza: capacità di iniziare e portare a termine progetti con solidità. Sfida: il 1 può percepire il 4 come lento, il 4 il 1 come sconsiderato. Necessaria pazienza e rispetto per i diversi ritmi.",
    get_symmetric_key(1, 5): "**1 e 5:** Unione dinamica di leadership e libertà. Il 1 fornisce direzione, il 5 porta flessibilità e spontaneità. Forza: relazione eccitante, sempre in movimento, capace di adattarsi. Sfida: il 1 può percepire il 5 come instabile o irresponsabile, il 5 il 1 come limitante o troppo controllante.",
    get_symmetric_key(1, 6): "**1 e 6:** Il leader e il custode. Il 1 si focalizza sull'individuo, il 6 sulla famiglia e la responsabilità. Forza: il 1 porta indipendenza, il 6 stabilità e cura. Sfida: il 1 può sentirsi soffocato dalle aspettative del 6, il 6 può vedere il 1 come egoista o irresponsabile. Necessaria negoziazione su responsabilità e autonomia.",
    get_symmetric_key(1, 7): "**1 e 7:** Combinazione di azione e pensiero. Il 1 è il pioniere pratico, il 7 il filosofo introspettivo. Forza: il 1 aiuta il 7 a concretizzare le idee, il 7 porta profondità al 1. Sfida: il 1 può trovare il 7 troppo distaccato o analitico, il 7 il 1 troppo impulsivo o superficiale. Necessario spazio per entrambi.",
    get_symmetric_key(1, 8): "**1 e 8:** Due leader potenti e ambiziosi. Entrambi con una forte spinta al successo. Forza: grande potenziale per obiettivi grandiosi e successo materiale. Sfida: lotta per il controllo, ego e tendenza a competere anziché collaborare. Devono imparare a condividere il potere.",
    get_symmetric_key(1, 9): "**1 e 9:** L'inizio e la fine del ciclo. Il 1 è incentrato sull'auto-realizzazione, il 9 sull'umanitarismo. Forza: il 1 porta il fuoco dell'iniziativa, il 9 la saggezza e la compassione. Sfida: il 9 può trovare il 1 egoista, il 1 il 9 troppo idealista o non pratico. Bilanciare individualismo e servizio universale.",

    get_symmetric_key(2, 3): "**2 e 3:** Sensibilità e espressione. Il 2 cerca armonia, il 3 gioia e socialità. Forza: relazione vivace e affettuosa, grande comunicazione emotiva e divertimento. Sfida: il 2 può sentirsi sopraffatto dall'estroversione del 3, il 3 può trovare il 2 troppo serio o emotivo. Bisogno di equilibrio tra profondità e leggerezza.",
    get_symmetric_key(2, 4): "**2 e 4:** Armonia e costruzione. Il 2 porta sensibilità e diplomazia, il 4 stabilità e dedizione. Forza: unione solida e affidabile, ideale per costruire una famiglia e una vita sicura. Sfida: rischio di diventare troppo prevedibili o noiosi, mancanza di spontaneità. Necessario coltivare la passione.",
    get_symmetric_key(2, 5): "**2 e 5:** Cooperazione e libertà. Il 2 cerca stabilità e connessione, il 5 movimento e avventura. Forza: il 2 offre un porto sicuro, il 5 porta eccitazione. Sfida: il 2 può trovare il 5 imprevedibile e inaffidabile, il 5 può sentire il 2 troppo appiccicoso o limitante. Necessaria molta tolleranza e compromesso.",
    get_symmetric_key(2, 6): "**2 e 6:** Amore, cura e armonia domestica. Entrambi orientati alla relazione e al benessere. Forza: profondo affetto, comprensione emotiva, grande capacità di creare un ambiente amorevole. Sfida: tendenza a sacrificarsi troppo l'uno per l'altro, possibili aspettative irrealistiche. Rischio di stagnazione se non ci sono stimoli esterni.",
    get_symmetric_key(2, 7): "**2 e 7:** Emotività e intelletto. Il 2 cerca connessione emotiva, il 7 cerca comprensione intellettuale e solitudine. Forza: il 2 può aiutare il 7 a connettersi con le emozioni, il 7 può portare profondità al 2. Sfida: il 2 può sentirsi non capito o solo, il 7 può sentirsi invaso o emotivamente drenato. Necessario grande rispetto per lo spazio altrui.",
    get_symmetric_key(2, 8): "**2 e 8:** Diplomazia e potere. Il 2 vuole armonia e pace, l'8 controllo e successo. Forza: il 2 può ammorbidire l'approccio dell'8, l'8 può dare direzione e forza al 2. Sfida: il 2 può sentirsi intimidito o manipolato, l'8 può vedere il 2 come debole o indeciso. Bilanciare potere e sensibilità.",
    get_symmetric_key(2, 9): "**2 e 9:** Sensibilità e compassione universale. Entrambi empatici e orientati al servizio. Forza: profonda comprensione emotiva, desiderio condiviso di aiutare gli altri, grande umanitarismo. Sfida: il 2 può sentirsi trascurato se il 9 è troppo distante con le sue cause universali, il 9 può sentire il 2 troppo focalizzato sul personale. Rischio di esaurimento per la troppa donazione.",

    # --- E così via per tutte le altre combinazioni fino a (9, 9) ---
    "default": "Le vostre direzioni di vita possono essere complementari o richiedere comprensione reciproca. Esplorate come le vostre direzioni individuali possono arricchirsi a vicenda, trasformando le differenze in punti di forza."
}


# --- ESPRESSIONE (Già parzialmente espanso) ---
espressione_compatibilita = {
    get_symmetric_key(1, 1): "**1 e 1:** Stile comunicativo diretto e leader. Entrambi amano essere al centro dell'attenzione e prendere l'iniziativa. Forza: grande energia nel perseguire obiettivi comuni e manifestare le idee. Sfida: rischio di competizione verbale, di non ascoltarsi e di voler sempre avere l'ultima parola.",
    get_symmetric_key(1, 2): "**1 e 2:** Il 1 è assertivo e diretto, il 2 è diplomatico e gentile. Forza: il 1 porta iniziativa e chiarezza, il 2 armonia e capacità di mediazione. Si bilanciano bene nelle interazioni sociali. Sfida: il 1 può sembrare brusco o insensibile al 2, il 2 troppo passivo o indeciso per il 1. Necessaria la comunicazione aperta e la comprensione reciproca.",
    get_symmetric_key(1, 3): "**1 e 3:** Il 1 è leader e il 3 è creativo e socievole. Forza: combinazione eccellente per la comunicazione carismatica, piena di energia e idee brillanti. Ottima per progetti che richiedono iniziativa e storytelling. Sfida: il 1 può trovare il 3 dispersivo o superficiale, il 3 il 1 troppo serio o dominante. Bilanciare divertimento e focus.",
    get_symmetric_key(2, 3): "**2 e 3:** Il 2 è sensibile e cooperativo, il 3 è espressivo e gioioso. Forza: relazione che favorisce la comunicazione emotiva profonda, piena di calore e comprensione. Grande armonia nelle interazioni sociali intime. Sfida: il 2 può ritirarsi dall'eccessiva socialità del 3, il 3 può trovare il 2 troppo emotivo. Necessaria la ricerca di equilibrio tra vita sociale e momenti privati.",
    # Aggiungi qui tutte le 81 combinazioni per l'espressione, seguendo la stessa logica
    "default": "Le vostre modalità espressive sono uniche. Questo può portare a creatività e nuove prospettive, ma anche a incomprensioni se non gestite con pazienza e reciproca comprensione. Imparare a comunicare in modi che risuonino con entrambi è fondamentale."
}

# --- ANIMA (Già parzialmente espanso) ---
anima_compatibilita = {
    get_symmetric_key(1, 1): "**1 e 1:** Desideri del cuore simili: entrambi bramano indipendenza, auto-affermazione e nuovi inizi. Forza: si ispirano a vicenda nell'autonomia e nel perseguire aspirazioni individuali. Condividono una profonda motivazione al successo personale. Sfida: possono essere troppo focalizzati sui propri bisogni individuali, trascurando la connessione emotiva profonda e il supporto reciproco. Rischio di competizione interna.",
    get_symmetric_key(1, 2): "**1 e 2:** Il 1 desidera autonomia e leadership, il 2 armonia e connessione. Forza: il 1 porta la spinta all'azione e alla realizzazione personale, il 2 offre empatia, supporto e attenzione alle dinamiche relazionali. Possono bilanciarsi. Sfida: il 2 può sentirsi poco apprezzato o insicuro a causa dell'indipendenza del 1, il 1 può percepire il 2 come troppo dipendente emotivamente. Richiede ascolto e compromesso per allineare i desideri.",
    get_symmetric_key(2, 4): "**2 e 4:** Il 2 desidera armonia e il 4 stabilità. Forza: entrambi cercano sicurezza e una base solida. La loro unione può creare un ambiente di grande fiducia e sostegno reciproco, ideale per costruire una vita stabile. Sfida: possono diventare troppo cauti o resistenti al cambiamento, limitando la spontaneità e la crescita. Necessario aprirsi a nuove esperienze per evitare la stagnazione.",
    # Aggiungi qui tutte le 81 combinazioni per l'anima
    "default": "I vostri desideri del cuore sono unici. Con comunicazione e rispetto, le vostre diverse motivazioni e aspirazioni intime possono arricchirvi a vicenda, portando a una crescita condivisa e a una comprensione più profonda dell'amore."
}

# --- PERSONALITÀ (Già parzialmente espanso) ---
personalita_compatibilita = {
    get_symmetric_key(1, 1): "**1 e 1:** L'esterno è forte, indipendente e deciso per entrambi. Forza: appaiono come una coppia potente, sicura di sé e con una chiara direzione. Esercitano una forte influenza sugli altri. Sfida: possono sembrare intimidatori o troppo dominanti al mondo esterno, e all'interno della relazione, potrebbero non essere aperti a mostrare vulnerabilità o chiedere aiuto, percependo l'altro come un rivale.",
    get_symmetric_key(1, 2): "**1 e 2:** Il 1 si presenta come diretto e orientato all'azione, il 2 è gentile, diplomatico e accomodante. Forza: il 1 apre le strade e prende l'iniziativa, il 2 smussa gli angoli e facilita le interazioni sociali. Possono avere una dinamica affascinante. Sfida: il 1 può percepire il 2 come troppo passivo o indeciso, il 2 il 1 come troppo brusco o arrogante. Devono bilanciare l'assertività con la sensibilità.",
    # Aggiungi qui tutte le 81 combinazioni per la personalità
    "default": "Le vostre personalità si differenziano nel modo in cui vi presentate al mondo. Questo può portare a un sano equilibrio o a piccole incomprensioni nelle interazioni esterne. La chiave è apprezzare la forza nelle reciproche diversità e presentare un fronte unito quando necessario."
}

# --- FORZA (DESTINO) (Già parzialmente espanso) ---
forza_compatibilita = {
    get_symmetric_key(1, 1): "**1 e 1:** Affrontano le sfide con determinazione e coraggio individuali. Forza: entrambi sono intrinsecamente motivati, risoluti e non temono gli ostacoli. Si spronano a vicenda a superare i limiti. Sfida: possono volere fare tutto da soli, non chiedere aiuto all'altro o competere nelle difficoltà, anziché collaborare. Rischio di esaurimento per la troppa indipendenza.",
    get_symmetric_key(1, 2): "**1 e 2:** Il 1 affronta le sfide con azione e iniziativa, il 2 con diplomazia e ricerca di armonia. Forza: il 1 porta nuove strade e soluzioni audaci, il 2 trova modi armoniosi per attuarle o gestire le conseguenze. Sfida: il 1 può trovare il 2 troppo esitante o accomodante, il 2 il 1 troppo impulsivo o insensibile alle dinamiche relazionali. Richiede pazienza e negoziazione.",
    # Aggiungi qui tutte le 81 combinazioni per la forza
    "default": "I vostri approcci alle sfide e ai talenti innati sono diversi. Questo può essere una fonte di forza complementare se imparate dalle reciproche prospettive, o una fonte di attrito se non riuscite a valorizzare le differenze nei vostri modi di affrontare la vita."
}

# --- QUINTESSENZA (Già parzialmente espanso) ---
quintessenza_compatibilita = {
    get_symmetric_key(1, 1): "**1 e 1:** Le vostre essenze più profonde risuonano con l'indipendenza, l'originalità e la spinta iniziale. Forza: una connessione spirituale che spinge entrambi verso l'autenticità e la realizzazione individuale. Entrambi hanno un forte senso del proprio scopo e della propria identità. Sfida: rischio di non fondersi a livello animico, mantenendo forte il senso del 'io' separato e faticando a trovare una vera fusione come coppia.",
    get_symmetric_key(1, 2): "**1 e 2:** L'essenza del 1 è pionieristica e assertiva, quella del 2 è armoniosa e cooperativa. Forza: il 1 porta la visione e l'energia per avviare, il 2 la capacità di attuare con equilibrio e sensibilità. Possono completarsi a vicenda in modo meraviglioso. Sfida: comprendere che il 1 ha bisogno di spazio per creare e agire, mentre il 2 cerca la fusione e la connessione profonda. La relazione prospera quando entrambi rispettano i reciproci bisogni animici.",
    # Aggiungi qui tutte le 81 combinazioni per la quintessenza
    "default": "Le vostre quintessenze offrono una base per la crescita e l'apprendimento reciproco. La vostra essenza più profonda può trovare nuove risonanze scoprendo la verità dell'altro, portando a una partnership spirituale e profonda."
}

# --- CICLI DI VITA ---
# L'analisi dei cicli è più complessa perché cambiano per età.
# Qui facciamo un confronto basato sui valori del ciclo (Esperienza, Potere, Saggezza).
cicli_di_vita_compatibilita = {
    get_symmetric_key(1, 1): "**1 e 1:** In un ciclo di esperienza o potere con valori identici, entrambi affronteranno periodi con lezioni simili di leadership e iniziativa. Forza: grande comprensione reciproca delle sfide e opportunità del periodo. Sfida: il rischio di non vedere prospettive alternative o di competere invece di collaborare.",
    get_symmetric_key(2, 2): "**2 e 2:** I vostri cicli di vita si allineano nella ricerca di armonia e cooperazione. Forza: capacità di creare un ambiente di supporto reciproco e di superare le sfide attraverso la diplomazia. Sfida: evitare l'indecisione o la dipendenza eccessiva, e imparare a gestire i conflitti in modo costruttivo.",
    get_symmetric_key(3, 6): "**3 e 6:** Se i vostri cicli si incontrano con queste energie, c'è un'ottima base per la creatività e la cura. Forza: il 3 porta gioia e ispirazione, il 6 stabilità e dedizione. Ottimo per creare un ambiente familiare vivace. Sfida: bilanciare il bisogno di libertà del 3 con la tendenza al controllo del 6.",
    "default": "I vostri cicli di vita possono presentare energie diverse. Questo offre opportunità uniche di crescita reciproca, imparando a sostenervi attraverso le rispettive fasi di sviluppo e lezioni di vita."
}

# --- PINNACOLI ---
# Analisi per ciascuno dei 4 pinnacoli (P1 vs P1, P2 vs P2, etc.)
pinnacoli_compatibilita = {
    get_symmetric_key(1, 1): "**1 e 1:** Durante questo pinnacolo, entrambi affrontano opportunità legate alla leadership e all'indipendenza. Forza: si ispirano a vicenda a prendere l'iniziativa e a realizzare obiettivi ambiziosi. Sfida: evitare la competizione e l'eccessiva focalizzazione sui successi individuali a discapito della relazione.",
    get_symmetric_key(2, 4): "**2 e 4:** Un pinnacolo con il 2 (cooperazione) e il 4 (costruzione). Forza: ideale per realizzare obiettivi pratici attraverso la collaborazione e il supporto reciproco. Sfida: rischio di rigidità o di eccessiva attenzione ai dettagli, perdendo di vista il quadro generale o la spontaneità.",
    get_symmetric_key(5, 7): "**5 e 7:** Un pinnacolo con il 5 (libertà) e il 7 (introspezione). Forza: questo periodo può portare a scoperte significative e a una crescita personale profonda, con la libertà di esplorare nuove idee. Sfida: la tendenza del 5 all'irrequietezza può scontrarsi con il bisogno di solitudine del 7. Bilanciare azione e riflessione.",
    "default": "Durante questi periodi di pinnacolo, le vostre energie possono essere diverse, offrendo opportunità per imparare e crescere l'uno dall'altro. La comprensione delle reciproche opportunità vi aiuterà a navigare questi momenti cruciali."
}

# --- SFIDE ---
# Analisi per ciascuna delle 4 sfide (S1 vs S1, S2 vs S2, etc.)
sfide_compatibilita = {
    get_symmetric_key(1, 1): "**1 e 1:** Entrambi potrebbero affrontare sfide legate all'affermazione di sé o all'indipendenza. Forza: si possono capire e supportare nel superare ostacoli simili. Sfida: rischio di una forte competizione su chi è più forte o di non volere ammettere le proprie vulnerabilità all'altro.",
    get_symmetric_key(2, 2): "**2 e 2:** Le vostre sfide si concentrano su questioni di dipendenza, equilibrio e gestione delle emozioni. Forza: profonda empatia reciproca nell'affrontare queste lezioni. Sfida: evitare la codipendenza o il rinunciare ai propri bisogni per l'armonia, e affrontare i problemi direttamente anziché evitarli.",
    get_symmetric_key(4, 7): "**4 e 7:** Sfide di costruzione e introspezione. Il 4 può lottare con la rigidità, il 7 con l'isolamento. Forza: possono aiutarsi a vicenda a trovare struttura nella spiritualità (4 aiuta 7) o a dare profondità alla praticità (7 aiuta 4). Sfida: la necessità di un approccio strutturato del 4 può scontrarsi con il bisogno di libertà intellettuale del 7. Bisogno di rispettare i reciproci processi di apprendimento.",
    "default": "Le vostre sfide presentano lezioni uniche. Comprendere e supportare l'altro nelle proprie aree di crescita può rafforzare notevolmente il vostro legame, trasformando gli ostacoli in opportunità condivise."
}


# --- FUNZIONE DI ANALISI DI COMPATIBILITÀ ESTESA ---
def get_compatibilita_analysis(p1_num, p2_num, compatibility_map, context_description=""):
    """
    Recupera l'analisi di compatibilità da una mappa predefinita.
    Gestisce la simmetria (es. (1,2) è uguale a (2,1)).
    Aggiunge una descrizione di contesto opzionale.
    """
    key_ordered = get_symmetric_key(p1_num, p2_num)
    analysis_text = compatibility_map.get(key_ordered, compatibility_map.get("default", "Analisi non disponibile per questa combinazione specifica. Controlla la tua KB."))
    return f"{context_description} {analysis_text}"


# --- INPUT UTENTE ---

st.subheader("Dati di Persona 1")
col1, col2 = st.columns(2)
with col1:
    nome1 = st.text_input("Nome Persona 1", key="nome1").strip()
    cognome1 = st.text_input("Cognome Persona 1", key="cognome1").strip()
with col2:
    data_nascita_str1 = st.text_input("Data di nascita Persona 1 (GG/MM/AAAA)", key="data1").strip()

st.markdown("---")

st.subheader("Dati di Persona 2")
col3, col4 = st.columns(2)
with col3:
    nome2 = st.text_input("Nome Persona 2", key="nome2").strip()
    cognome2 = st.text_input("Cognome Persona 2", key="cognome2").strip()
with col4:
    data_nascita_str2 = st.text_input("Data di nascita Persona 2 (GG/MM/AAAA)", key="data2").strip()

# --- VALIDAZIONE E CALCOLO ---

# Funzione per validare e parsare la data
def parse_date_input(date_str, person_label):
    if not date_str:
        st.error(f"Inserisci la data di nascita per {person_label}.")
        return None, 0, 0, 0
    try:
        date_obj = datetime.strptime(date_str, "%d/%m/%Y").date()
        if date_obj > datetime.now().date():
            st.error(f"La data di nascita per {person_label} non può essere nel futuro.")
            return None, 0, 0, 0
        return date_obj, date_obj.day, date_obj.month, date_obj.year
    except ValueError:
        st.error(f"Formato data non valido per {person_label}. Usa GG/MM/AAAA (es. 01/01/1990).")
        return None, 0, 0, 0

st.markdown("---")

if st.button("Calcola Compatibilità Approfondita", type="primary"):
    all_inputs_valid = True

    # Valida Persona 1
    data_obj1, giorno1, mese1, anno1 = parse_date_input(data_nascita_str1, "Persona 1")
    if not nome1 or not cognome1 or data_obj1 is None:
        all_inputs_valid = False

    # Valida Persona 2
    data_obj2, giorno2, mese2, anno2 = parse_date_input(data_nascita_str2, "Persona 2")
    if not nome2 or not cognome2 or data_obj2 is None:
        all_inputs_valid = False

    if all_inputs_valid:
        try:
            # Calcola i numeri per ogni persona
            numeri_p1 = calcola_numeri_compatibilita_persona(nome1, cognome1, giorno1, mese1, anno1)
            numeri_p2 = calcola_numeri_compatibilita_persona(nome2, cognome2, giorno2, mese2, anno2)

            st.success("Dati calcolati! Scorri per l'analisi.")
            st.markdown("---")

            # Mostra i numeri calcolati in una tabella riassuntiva per chiarezza
            df_numeri_coppia = pd.DataFrame({
                "Numero": ["Sentiero di Vita", "Espressione", "Anima", "Personalità", "Forza", "Quintessenza"],
                f"{nome1.capitalize()}": [
                    numeri_p1["core"]["sentiero_di_vita"],
                    numeri_p1["core"]["espressione"],
                    numeri_p1["core"]["anima"],
                    numeri_p1["core"]["personalita"],
                    numeri_p1["core"]["forza"],
                    numeri_p1["core"]["quintessenza"]
                ],
                f"{nome2.capitalize()}": [
                    numeri_p2["core"]["sentiero_di_vita"],
                    numeri_p2["core"]["espressione"],
                    numeri_p2["core"]["anima"],
                    numeri_p2["core"]["personalita"],
                    numeri_p2["core"]["forza"],
                    numeri_p2["core"]["quintessenza"]
                ]
            })
            st.subheader("Numeri Chiave di Coppia (Statici):")
            st.dataframe(df_numeri_coppia.set_index("Numero"), use_container_width=True)

            # Tabella per i numeri dinamici
            df_numeri_dinamici = pd.DataFrame({
                "Tipo": ["Ciclo Esperienza", "Ciclo Potere", "Ciclo Saggezza",
                         "Pinnacolo 1", "Pinnacolo 2", "Pinnacolo 3", "Pinnacolo 4",
                         "Sfida 1", "Sfida 2", "Sfida 3", "Sfida 4"],
                f"{nome1.capitalize()}": [
                    numeri_p1["dinamici"]["cicli"]["esperienza"],
                    numeri_p1["dinamici"]["cicli"]["potere"],
                    numeri_p1["dinamici"]["cicli"]["saggezza"],
                    numeri_p1["dinamici"]["pinnacoli"]["p1"],
                    numeri_p1["dinamici"]["pinnacoli"]["p2"],
                    numeri_p1["dinamici"]["pinnacoli"]["p3"],
                    numeri_p1["dinamici"]["pinnacoli"]["p4"],
                    numeri_p1["dinamici"]["sfide"]["s1"],
                    numeri_p1["dinamici"]["sfide"]["s2"],
                    numeri_p1["dinamici"]["sfide"]["s3"],
                    numeri_p1["dinamici"]["sfide"]["s4"]
                ],
                f"{nome2.capitalize()}": [
                    numeri_p2["dinamici"]["cicli"]["esperienza"],
                    numeri_p2["dinamici"]["cicli"]["potere"],
                    numeri_p2["dinamici"]["cicli"]["saggezza"],
                    numeri_p2["dinamici"]["pinnacoli"]["p1"],
                    numeri_p2["dinamici"]["pinnacoli"]["p2"],
                    numeri_p2["dinamici"]["pinnacoli"]["p3"],
                    numeri_p2["dinamici"]["pinnacoli"]["p4"],
                    numeri_p2["dinamici"]["sfide"]["s1"],
                    numeri_p2["dinamici"]["sfide"]["s2"],
                    numeri_p2["dinamici"]["sfide"]["s3"],
                    numeri_p2["dinamici"]["sfide"]["s4"]
                ]
            })
            st.subheader("Numeri Chiave di Coppia (Dinamici):")
            st.dataframe(df_numeri_dinamici.set_index("Tipo"), use_container_width=True)
            st.markdown("---")


            st.header("Analisi Dettagliata di Compatibilità Numerologica")
            
            # Analisi Core Numbers
            with st.expander("Sentiero di Vita: La Mappa del Destino"):
                st.write(get_compatibilita_analysis(numeri_p1["core"]["sentiero_di_vita"], numeri_p2["core"]["sentiero_di_vita"], sentiero_di_vita_compatibilita))
            
            with st.expander("Numero di Espressione: Come Vi Manifestate"):
                st.write(get_compatibilita_analysis(numeri_p1["core"]["espressione"], numeri_p2["core"]["espressione"], espressione_compatibilita))

            with st.expander("Numero dell'Anima: Desideri del Cuore"):
                st.write(get_compatibilita_analysis(numeri_p1["core"]["anima"], numeri_p2["core"]["anima"], anima_compatibilita))

            with st.expander("Numero della Personalità: Come Vi Percepite Esternamente"):
                st.write(get_compatibilita_analysis(numeri_p1["core"]["personalita"], numeri_p2["core"]["personalita"], personalita_compatibilita))

            with st.expander("Numero di Forza (Destino): Talenti e Sfide Innate"):
                st.write(get_compatibilita_analysis(numeri_p1["core"]["forza"], numeri_p2["core"]["forza"], forza_compatibilita))
            
            with st.expander("Quintessenza: L'Essenza Unificante"):
                st.write(get_compatibilita_analysis(numeri_p1["core"]["quintessenza"], numeri_p2["core"]["quintessenza"], quintessenza_compatibilita))

            st.markdown("---")
            st.header("Analisi delle Dinamiche di Vita e Crescita")

            # Analisi Cicli di Vita
            with st.expander("Cicli di Vita: Le Fasi di Crescita"):
                st.write(f"**Ciclo Esperienza:** {get_compatibilita_analysis(numeri_p1['dinamici']['cicli']['esperienza'], numeri_p2['dinamici']['cicli']['esperienza'], cicli_di_vita_compatibilita, 'I vostri numeri del Ciclo di Esperienza (primi anni di vita) sono:')}")
                st.write(f"**Ciclo Potere:** {get_compatibilita_analysis(numeri_p1['dinamici']['cicli']['potere'], numeri_p2['dinamici']['cicli']['potere'], cicli_di_vita_compatibilita, 'I vostri numeri del Ciclo di Potere (età adulta) sono:')}")
                st.write(f"**Ciclo Saggezza:** {get_compatibilita_analysis(numeri_p1['dinamici']['cicli']['saggezza'], numeri_p2['dinamici']['cicli']['saggezza'], cicli_di_vita_compatibilita, 'I vostri numeri del Ciclo di Saggezza (età avanzata) sono:')}")


            # Analisi Pinnacoli
            with st.expander("Pinnacoli: Le Cime di Opportunità"):
                st.write(f"**Pinnacolo 1:** {get_compatibilita_analysis(numeri_p1['dinamici']['pinnacoli']['p1'], numeri_p2['dinamici']['pinnacoli']['p1'], pinnacoli_compatibilita, 'Durante il primo Pinnacolo (fino ai ~{numeri_p1["dinamici"]["eta_pinnacoli"]["fine_p1"]} anni per P1, ~{numeri_p2["dinamici"]["eta_pinnacoli"]["fine_p1"]} per P2):')}")
                st.write(f"**Pinnacolo 2:** {get_compatibilita_analysis(numeri_p1['dinamici']['pinnacoli']['p2'], numeri_p2['dinamici']['pinnacoli']['p2'], pinnacoli_compatibilita, 'Durante il secondo Pinnacolo (età ~{numeri_p1["dinamici"]["eta_pinnacoli"]["fine_p1"]+1}-{numeri_p1["dinamici"]["eta_pinnacoli"]["fine_p2"]} per P1, ~{numeri_p2["dinamici"]["eta_pinnacoli"]["fine_p1"]+1}-{numeri_p2["dinamici"]["eta_pinnacoli"]["fine_p2"]} per P2):')}")
                st.write(f"**Pinnacolo 3:** {get_compatibilita_analysis(numeri_p1['dinamici']['pinnacoli']['p3'], numeri_p2['dinamici']['pinnacoli']['p3'], pinnacoli_compatibilita, 'Durante il terzo Pinnacolo (età ~{numeri_p1["dinamici"]["eta_pinnacoli"]["fine_p2"]+1}-{numeri_p1["dinamici"]["eta_pinnacoli"]["fine_p3"]} per P1, ~{numeri_p2["dinamici"]["eta_pinnacoli"]["fine_p2"]+1}-{numeri_p2["dinamici"]["eta_pinnacoli"]["fine_p3"]} per P2):')}")
                st.write(f"**Pinnacolo 4:** {get_compatibilita_analysis(numeri_p1['dinamici']['pinnacoli']['p4'], numeri_p2['dinamici']['pinnacoli']['p4'], pinnacoli_compatibilita, 'Durante il quarto Pinnacolo (dopo i ~{numeri_p1["dinamici"]["eta_pinnacoli"]["fine_p3"]} anni per P1, dopo i ~{numeri_p2["dinamici"]["eta_pinnacoli"]["fine_p3"]} per P2):')}")
            
            # Analisi Sfide
            with st.expander("Sfide: Le Lezioni di Crescita"):
                st.write(f"**Sfida 1:** {get_compatibilita_analysis(numeri_p1['dinamici']['sfide']['s1'], numeri_p2['dinamici']['sfide']['s1'], sfide_compatibilita, 'Durante la prima Sfida (fino ai ~{numeri_p1["dinamici"]["eta_pinnacoli"]["fine_p1"]} anni per P1, ~{numeri_p2["dinamici"]["eta_pinnacoli"]["fine_p1"]} per P2):')}")
                st.write(f"**Sfida 2:** {get_compatibilita_analysis(numeri_p1['dinamici']['sfide']['s2'], numeri_p2['dinamici']['sfide']['s2'], sfide_compatibilita, 'Durante la seconda Sfida (età ~{numeri_p1["dinamici"]["eta_pinnacoli"]["fine_p1"]+1}-{numeri_p1["dinamici"]["eta_pinnacoli"]["fine_p2"]} per P1, ~{numeri_p2["dinamici"]["eta_pinnacoli"]["fine_p1"]+1}-{numeri_p2["dinamici"]["eta_pinnacoli"]["fine_p2"]} per P2):')}")
                st.write(f"**Sfida 3:** {get_compatibilita_analysis(numeri_p1['dinamici']['sfide']['s3'], numeri_p2['dinamici']['sfide']['s3'], sfide_compatibilita, 'Durante la terza Sfida (età ~{numeri_p1["dinamici"]["eta_pinnacoli"]["fine_p2"]+1}-{numeri_p1["dinamici"]["eta_pinnacoli"]["fine_p3"]} per P1, ~{numeri_p2["dinamici"]["eta_pinnacoli"]["fine_p2"]+1}-{numeri_p2["dinamici"]["eta_pinnacoli"]["fine_p3"]} per P2):')}")
                st.write(f"**Sfida 4:** {get_compatibilita_analysis(numeri_p1['dinamici']['sfide']['s4'], numeri_p2['dinamici']['sfide']['s4'], sfide_compatibilita, 'Durante la quarta Sfida (dopo i ~{numeri_p1["dinamici"]["eta_pinnacoli"]["fine_p3"]} anni per P1, dopo i ~{numeri_p2["dinamici"]["eta_pinnacoli"]["fine_p3"]} per P2):')}")
            
            st.markdown("---")
            st.info("Questa analisi offre una panoramica numerologica. La compatibilità reale dipende da molti fattori, inclusi crescita personale, comunicazione e rispetto reciproco. Usatela come guida per una maggiore comprensione e per coltivare al meglio la vostra relazione!")

        except Exception as e:
            st.error(f"Si è verificato un errore durante il calcolo della compatibilità. Assicurati che tutti i campi siano compilati correttamente: {e}")
            st.exception(e) # Utile per il debug
