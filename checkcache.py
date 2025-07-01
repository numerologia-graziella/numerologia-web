import os

def cerca_cache(directory):
    print("\n🔍 INIZIO SCANSIONE per @st.cache...\n")
    trovati = 0
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                with open(path, "r", encoding="utf-8") as f:
                    for i, line in enumerate(f, 1):
                        if "@st.cache" in line:
                            trovati += 1
                            print(f"⚠️  @st.cache trovato in: {path} (riga {i})")
    if trovati == 0:
        print("✅ Nessun uso di @st.cache trovato.")
    print("\n✅ Scansione completata.")

# Scansiona la tua cartella 'numerologia-web'
cerca_cache("numerologia-web")
