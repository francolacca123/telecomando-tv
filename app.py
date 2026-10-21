"""
TV e telecomando virtuali con Streamlit.
Spiega passo dopo passo cosa succede quando si accende e si spegne una TV.
"""

import streamlit as st

# Configurazione della pagina Streamlit
st.set_page_config(page_title="TV e telecomando virtuali", layout="centered")

# ----------------------------------------------------------------------------
# Dati del programma
# ----------------------------------------------------------------------------

CANALI = [
    ("Meteo", "#2b6cb0", "#63b3ed"),
    ("Cartoni", "#b83280", "#f6ad55"),
    ("Notizie", "#2d3748", "#718096"),
    ("Documentari", "#276749", "#9ae6b4"),
]

SPIEGAZIONI = {
    "accendi": """
### Accensione: cosa succede

1. **Premi POWER sul telecomando.** Il tasto chiude un contatto e il microchip
   interno prepara un codice binario che corrisponde al comando "accendi".
2. **Il telecomando lo invia come lampi di luce infrarossa.** Il LED in cima
   lampeggia molto velocemente. A occhio nudo non si vede, ma una fotocamera
   del telefono lo mostra.
3. **La TV era in standby.** Non era davvero spenta: il LED rosso indica che
   il sensore infrarosso e un piccolo circuito restano alimentati, in attesa.
4. **Il sensore riceve i lampi e il processore li decodifica.** Se il codice
   è quello giusto, il processore capisce che deve accendersi.
5. **L'alimentatore manda corrente a tutto il resto:** schermo, retroilluminazione,
   audio e sintonizzatore.
6. **Compare l'immagine.** Il LED diventa verde e la TV mostra l'ultimo canale.
""",
    "spegni": """
### Spegnimento: cosa succede

1. **Premi di nuovo POWER.** Il telecomando invia lo stesso tipo di segnale
   infrarosso, ma il codice vuol dire "vai in standby".
2. **Il processore della TV decodifica il comando** e avvia lo spegnimento.
3. **Schermo, retroilluminazione e audio vengono disattivati.** L'immagine sparisce.
4. **La TV non si scollega dalla rete elettrica.** Resta in standby con un consumo
   minimo, per poter ascoltare il prossimo comando.
5. **Il LED torna rosso:** la TV non è accesa, ma è pronta a riaccendersi.
6. **Per spegnerla del tutto** bisogna staccare la spina o usare l'interruttore
   fisico, se presente.
""",
    "ignorato": """
### Comando ignorato

La TV è in standby. In questo stato il sensore infrarosso riconosce **solo il tasto POWER**.
Gli altri comandi (volume, canale, muto) vengono ricevuti ma scartati, perché
non c'è nessuna immagine o audio da modificare.

**Premi POWER per accenderla.**
""",
    "volume": """
### Regolazione del volume

Il telecomando invia il codice "volume su" o "volume giù". Il processore
cambia il livello dell'amplificatore audio e mostra la barra sullo schermo.
""",
    "muto": """
### Muto

The tasto MUTE invia un codice che dice al processore di azzerare l'uscita audio
senza cambiare il livello del volume. Premendolo di nuovo, l'audio torna
al volume di prima.
""",
    "canale": """
### Cambio canale

Il telecomando invia il codice "canale successivo", "precedente" o il numero
scelto. Il sintonizzatore cambia flusso video e l'immagine sullo schermo si aggiorna.
""",
    "inizio": """
### Come usarlo

Premi i tasti del telecomando. Qui sotto compariranno le spiegazioni di
ciò che succede dentro la TV a ogni pressione.

**Prova a premere il tasto rosso POWER.**
""",
}

# ----------------------------------------------------------------------------
# Inizializzazione dello Stato (Session State)
# ----------------------------------------------------------------------------
if "stato" not in st.session_state:
    st.session_state.stato = {"acceso": False, "volume": 10, "canale": 0, "muto": False, "n": 0}
    st.session_state.ultimo_evento = "inizio"

s = st.session_state.stato

# ----------------------------------------------------------------------------
# Grafica CSS (TV + Telecomando)
# ----------------------------------------------------------------------------
CSS_TV = """
.tv-wrap { display:flex; flex-direction:column; align-items:center; font-family: Georgia, serif; margin-bottom: 20px; }
.tv-body { background:#1c1917; border-radius:18px; padding:18px 18px 10px; width:100%; max-width:520px;
           box-shadow:0 12px 30px rgba(0,0,0,.35); }
.tv-screen { position:relative; height:290px; border-radius:6px; overflow:hidden;
             display:flex; align-items:center; justify-content:center; }
.tv-off { background:#0a0a0a; box-shadow: inset 0 0 40px rgba(255,255,255,.04); }
.tv-title { color:#fff; font-size:2.2rem; font-weight:bold; text-shadow:0 2px 12px rgba(0,0,0,.5); text-align:center; }
.tv-sub { color:rgba(255,255,255,.85); font-size:1rem; margin-top:6px; text-align:center; }
.tv-osd { position:absolute; left:16px; right:16px; bottom:14px; color:#fff; font-size:.9rem;
          display:flex; align-items:center; gap:10px; background:rgba(0,0,0,.45); padding:6px 10px; border-radius:6px; }
.tv-bar { flex:1; height:8px; background:rgba(255,255,255,.25); border-radius:4px; overflow:hidden; }
.tv-bar > span { display:block; height:100%; background:#fff; }
.tv-ch { position:absolute; top:12px; right:16px; color:#fff; font-size:1.1rem; background:rgba(0,0,0,.4);
         padding:2px 10px; border-radius:4px; }
.tv-footer { display:flex; align-items:center; justify-content:space-between; padding:10px 6px 2px; color:#a8a29e; font-size:.8rem; }
.led { display:inline-block; width:11px; height:11px; border-radius:50%; margin-right:8px; vertical-align:middle; }
.led-red { background:#ef4444; box-shadow:0 0 8px #ef4444; }
.led-green { background:#22c55e; box-shadow:0 0 8px #22c55e; }
.tv-stand { width:120px; height:14px; background:#292524; border-radius:0 0 10px 10px; margin: 0 auto; }
.tv-state { margin-top:12px; font-size:1rem; text-align:center; color: #fff; }

.ir-window { width:96px; height:16px; margin:0 auto 10px auto; border-radius:10px;
  background:linear-gradient(#2a0707,#120202); border:1px solid #000;
  box-shadow: inset 0 1px 3px rgba(0,0,0,.9), 0 1px 0 rgba(255,255,255,.12);
  display:flex; align-items:center; justify-content:center; }
.ir-led { width:60px; height:5px; border-radius:3px; background:#5b1010; }
.ir-flash { background:#ff2a2a !important; box-shadow:0 0 14px 5px #ff2a2a !important; }
"""

st.markdown(f"<style>{CSS_TV}</style>", unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# Funzioni di rendering visivo
# ----------------------------------------------------------------------------
def disegna_tv():
    if s["acceso"]:
        nome, c1, c2 = CANALI[s["canale"]]
        if s["muto"]:
            osd = '<div class="tv-osd">Audio disattivato (muto)</div>'
        else:
            osd = (
                '<div class="tv-osd">Vol <div class="tv-bar"><span style="width:%d%%"></span></div> %d</div>'
                % (s["volume"] * 5, s["volume"])
            )
        schermo = (
            '<div class="tv-screen" style="background:linear-gradient(135deg,%s,%s)">'
            '<div><div class="tv-title">%s</div><div class="tv-sub">Canale %d</div></div>'
            '<div class="tv-ch">%d</div>%s</div>'
        ) % (c1, c2, nome, s["canale"] + 1, s["canale"] + 1, osd)
        led = '<span class="led led-green"></span>Acceso'
        testo = "La TV è <b>accesa</b>."
    else:
        schermo = '<div class="tv-screen tv-off"></div>'
        led = '<span class="led led-red"></span>Standby'
        testo = "La TV è in <b>standby</b>: lo schermo è nero, ma il LED rosso è ancora acceso."

    return (
        f'<div class="tv-wrap"><div class="tv-body">{schermo}'
        f'<div class="tv-footer"><span>{led}</span><span>Sensore IR</span></div>'
        f'</div><div class="tv-stand"></div>'
        f'<div class="tv-state">{testo}</div></div>'
    )

# ----------------------------------------------------------------------------
# Logica di aggiornamento stato al click
# ----------------------------------------------------------------------------
def gestisci_input(tasto):
    s["n"] += 1
    if tasto == "power":
        s["acceso"] = not s["acceso"]
        st.session_state.ultimo_evento = "accendi" if s["acceso"] else "spegni"
    elif not s["acceso"]:
        st.session_state.ultimo_evento = "ignorato"
    elif tasto in ("vol+", "vol-"):
        delta = 1 if tasto == "vol+" else -1
        s["volume"] = max(0, min(20, s["volume"] + delta))
        s["muto"] = False
        st.session_state.ultimo_evento = "volume"
    elif tasto == "mute":
        s["muto"] = not s["muto"]
        st.session_state.ultimo_evento = "muto"
    elif tasto in ("ch+", "ch-"):
        delta = 1 if tasto == "ch+" else -1
        s["canale"] = (s["canale"] + delta) % len(CANALI)
        st.session_state.ultimo_evento = "canale"
    else:  # Numeri 1..4
        s["canale"] = int(tasto) - 1
        st.session_state.ultimo_evento = "canale"

# ----------------------------------------------------------------------------
# Interfaccia Grafica Streamlit
# ----------------------------------------------------------------------------
st.title("TV e telecomando virtuali")
st.markdown("Scopri cosa succede quando accendi e spegni una TV.")

col_tv, col_tel = st.columns([3, 2])

with col_tv:
    st.markdown(disegna_tv(), unsafe_allow_html=True)

with col_tel:
    # Finestrella infrarossa dinamica
    flash_class = "ir-flash" if s["n"] > 0 and s["n"] % 2 == 1 else ""
    st.markdown(f'<div class="ir-window"><div class="ir-led {flash_class}"></div></div>', unsafe_allow_html=True)
    
    # Pulsante Power
    if st.button("⏻ POWER", use_container_width=True):
        gestisci_input("power")
        st.rerun()

    # Tasti Numerici
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if st.button("1", use_container_width=True): gestisci_input("1"); st.rerun()
    with c2:
        if st.button("2", use_container_width=True): gestisci_input("2"); st.rerun()
    with c3:
        if st.button("3", use_container_width=True): gestisci_input("3"); st.rerun()
    with c4:
        if st.button("4", use_container_width=True): gestisci_input("4"); st.rerun()

    # Tasto Mute
    if st.button("MUTE", use_container_width=True):
        gestisci_input("mute")
        st.rerun()

    # Bilancieri Volume e Canale
    col_vol, col_ch = st.columns(2)
    with col_vol:
        st.markdown("<p style='text-align:center; font-weight:bold; margin-bottom:0;'>VOL</p>", unsafe_allow_html=True)
        if st.button("+", use_container_width=True): gestisci_input("vol+"); st.rerun()
        if st.button("−", use_container_width=True): gestisci_input("vol-"); st.rerun()
    with col_ch:
        st.markdown("<p style='text-align:center; font-weight:bold; margin-bottom:0;'>CH</p>", unsafe_allow_html=True)
        if st.button("▲", use_container_width=True): gestisci_input("ch+"); st.rerun()
        if st.button("▼", use_container_width=True): gestisci_input("ch-"); st.rerun()
        
    st.markdown("<p style='text-align:center; color:#8b8b90; font-size:0.8rem; margin-top:10px;'>Telecomando TV</p>", unsafe_allow_html=True)

# Sezione Spiegazioni in basso
st.markdown("---")
evento_corrente = st.session_state.ultimo_evento
st.markdown(SPIEGAZIONI[evento_corrente])
