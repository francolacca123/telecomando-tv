"""
TV e telecomando virtuali con Gradio.
Fatto Da Francesco Lauriola

Installazione:  pip install gradio
Avvio:          python app.py
"""

import os
import gradio as gr

# ----------------------------------------------------------------------------
# Dati del programma
# ----------------------------------------------------------------------------

CANALI = [
    ("Meteo", "#2b6cb0", "#63b3ed"),
    ("Cartoni", "#b83280", "#f6ad55"),
    ("Notizie", "#2d3748", "#718096"),
    ("Documentari", "#276749", "#9ae6b4"),
]

STATO_INIZIALE = {"acceso": False, "volume": 10, "canale": 0, "muto": False, "n": 0}

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

Il tasto MUTE invia un codice che dice al processore di azzerare l'uscita audio
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
# Grafica: TV e Rimozione elementi di default Gradio
# ----------------------------------------------------------------------------

CSS_LAYOUT = """
/* Nasconde il footer predefinito di Gradio e gli elementi di sistema */
footer { display: none !important; }
#gradio-app { background-color: transparent !important; }
.gradio-container { max-width: 900px !important; margin: 0 auto !important; }
.meta-text { display: none !important; }

/* Intestazione personalizzata */
.custom-header {
    text-align: center;
    margin-bottom: 25px;
}
.custom-header h1 {
    font-size: 2.2rem;
    font-weight: 800;
    margin-bottom: 8px;
}
.custom-header h2 {
    font-size: 1.6rem;
    color: #ef4444;
    font-weight: 700;
    margin-top: 5px;
}

/* Stili TV */
.tv-wrap { display:flex; flex-direction:column; align-items:center; font-family: Georgia, serif; }
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
.tv-stand { width:120px; height:14px; background:#292524; border-radius:0 0 10px 10px; }
.tv-state { margin-top:12px; font-size:1rem; }
"""


def disegna_tv(stato):
    if stato["acceso"]:
        nome, c1, c2 = CANALI[stato["canale"]]
        if stato["muto"]:
            osd = '<div class="tv-osd">Audio disattivato (muto)</div>'
        else:
            osd = (
                '<div class="tv-osd">Vol <div class="tv-bar"><span style="width:%d%%"></span></div> %d</div>'
                % (stato["volume"] * 5, stato["volume"])
            )
        schermo = (
            '<div class="tv-screen" style="background:linear-gradient(135deg,%s,%s)">'
            '<div><div class="tv-title">%s</div><div class="tv-sub">Canale %d</div></div>'
            '<div class="tv-ch">%d</div>%s</div>'
        ) % (c1, c2, nome, stato["canale"] + 1, stato["canale"] + 1, osd)
        led = '<span class="led led-green"></span>Acceso'
        testo = "La TV è <b>accesa</b>."
    else:
        schermo = '<div class="tv-screen tv-off"></div>'
        led = '<span class="led led-red"></span>Standby'
        testo = "La TV è in <b>standby</b>: lo schermo è nero, ma il LED rosso è ancora acceso."

    return (
        "<style>" + CSS_LAYOUT + "</style>"
        '<div class="tv-wrap"><div class="tv-body">'
        + schermo
        + '<div class="tv-footer"><span>' + led + "</span><span>Sensore IR</span></div>"
        "</div>"
        '<div class="tv-stand"></div>'
        '<div class="tv-state">' + testo + "</div></div>"
    )


# ----------------------------------------------------------------------------
# Grafica: telecomando
# ----------------------------------------------------------------------------

CSS_REMOTE = """
#telecomando {
  width:230px !important; max-width:230px !important; min-width:230px !important; flex:none !important;
  background:linear-gradient(165deg,#47474a 0%,#232325 45%,#151517 100%) !important;
  border:1px solid #0b0b0c !important; border-radius:38px 38px 46px 46px !important;
  padding:16px 14px 20px !important; gap:14px !important; align-items:center !important;
  box-shadow:0 18px 34px rgba(0,0,0,.5), inset 0 2px 2px rgba(255,255,255,.14), inset 0 -4px 8px rgba(0,0,0,.5) !important;
}
#telecomando .rem-row { justify-content:center !important; gap:10px !important; flex-wrap:nowrap !important;
  background:transparent !important; border:none !important; padding:0 !important; box-shadow:none !important; }
#telecomando .gap, #telecomando .form { background:transparent !important; border:none !important; }

/* finestrella infrarossa */
.ir-window { width:96px; height:16px; margin:0 auto; border-radius:10px;
  background:linear-gradient(#2a0707,#120202); border:1px solid #000;
  box-shadow: inset 0 1px 3px rgba(0,0,0,.9), 0 1px 0 rgba(255,255,255,.12);
  display:flex; align-items:center; justify-content:center; }
.ir-led { width:60px; height:5px; border-radius:3px; background:#5b1010; }
.ir-a { animation: ir-flash-a .5s ease-out; }
.ir-b { animation: ir-flash-b .5s ease-out; }
@keyframes ir-flash-a { 0%{background:#ff2a2a; box-shadow:0 0 14px 5px #ff2a2a;} 100%{background:#5b1010; box-shadow:none;} }
@keyframes ir-flash-b { 0%{background:#ff2a2a; box-shadow:0 0 14px 5px #ff2a2a;} 100%{background:#5b1010; box-shadow:none;} }

/* tasti */
#telecomando button { font-family: Helvetica, Arial, sans-serif !important; padding:0 !important; }
.rem-btn { background:linear-gradient(#515154,#2e2e30) !important; color:#ececec !important;
  border:1px solid #0b0b0c !important; font-weight:600 !important;
  box-shadow:0 3px 0 #0b0b0c, 0 6px 8px rgba(0,0,0,.45), inset 0 1px 0 rgba(255,255,255,.18) !important; }
.rem-btn:active { transform:translateY(2px); box-shadow:0 1px 0 #0b0b0c, inset 0 1px 0 rgba(255,255,255,.1) !important; }

.rem-power { width:58px !important; height:58px !important; min-width:58px !important; flex:none !important;
  border-radius:50% !important; font-size:1.5rem !important;
  background:radial-gradient(circle at 35% 28%,#ff7a6e,#c1121f 70%) !important; color:#fff !important; }
.rem-num { width:40px !important; height:40px !important; min-width:40px !important; flex:none !important;
  border-radius:50% !important; font-size:1rem !important; }
.rem-mute { width:110px !important; height:32px !important; min-width:110px !important; flex:none !important;
  border-radius:18px !important; font-size:.8rem !important; }

/* tasti a bilanciere (volume / canale) */
#telecomando .rocker { width:74px !important; min-width:74px !important; max-width:74px !important; flex:none !important;
  background:linear-gradient(#1b1b1d,#2c2c2f) !important; border:1px solid #000 !important;
  border-radius:38px !important; padding:6px 0 !important; gap:0 !important; align-items:center !important;
  box-shadow:inset 0 3px 8px rgba(0,0,0,.75), 0 1px 0 rgba(255,255,255,.1) !important; }
.rem-key { width:56px !important; height:54px !important; min-width:56px !important; flex:none !important;
  border-radius:28px !important; font-size:1.7rem !important; line-height:1 !important; }
.rlabel { text-align:center; color:#c9c9cc; font-family:Helvetica,Arial,sans-serif; font-size:.78rem;
  font-weight:700; padding:0 !important; min-height:0 !important; margin:4px 0; }
.rem-brand { text-align:center; color:#8b8b90; font-family:Helvetica,Arial,sans-serif; font-size:.72rem;
  padding:0 !important; min-height:0 !important; }
"""


def disegna_ir(n):
    classe = "" if n == 0 else ("ir-a" if n % 2 else "ir-b")
    return '<div class="ir-window"><div class="ir-led %s"></div></div>' % classe


# ----------------------------------------------------------------------------
# Logica dei comandi
# ----------------------------------------------------------------------------

def premi(tasto, stato):
    stato = dict(stato)
    stato["n"] += 1

    if tasto == "power":
        stato["acceso"] = not stato["acceso"]
        chiave = "accendi" if stato["acceso"] else "spegni"
    elif not stato["acceso"]:
        chiave = "ignorato"
    elif tasto in ("vol+", "vol-"):
        delta = 1 if tasto == "vol+" else -1
        stato["volume"] = max(0, min(20, stato["volume"] + delta))
        stato["muto"] = False
        chiave = "volume"
    elif tasto == "mute":
        stato["muto"] = not stato["muto"]
        chiave = "muto"
    elif tasto in ("ch+", "ch-"):
        delta = 1 if tasto == "ch+" else -1
        stato["canale"] = (stato["canale"] + delta) % len(CANALI)
        chiave = "canale"
    else:  # tasti numerici "1".."4"
        stato["canale"] = int(tasto) - 1
        chiave = "canale"

    return stato, disegna_tv(stato), SPIEGAZIONI[chiave], disegna_ir(stato["n"])


# ----------------------------------------------------------------------------
# Interfaccia Gradio
# ----------------------------------------------------------------------------

TEMA = gr.themes.Soft(primary_hue="red", neutral_hue="stone")

with gr.Blocks(title="Impara ad usare il telecomando della TV", theme=TEMA) as demo:
    gr.HTML("<style>" + CSS_LAYOUT + CSS_REMOTE + "</style>")
    
    # Intestazione Personalizzata
    gr.HTML("""
        <div class="custom-header">
            <h1>Impara ad usare il telecomando della TV e come accenderlo</h1>
            <h2>Fatto Da Francesco Lauriola</h2>
        </div>
    """)

    stato = gr.State(dict(STATO_INIZIALE))

    with gr.Row():
        with gr.Column(scale=3):
            tv = gr.HTML(disegna_tv(STATO_INIZIALE))

        with gr.Column(scale=0, min_width=240):
            with gr.Column(elem_id="telecomando"):
                ir = gr.HTML(disegna_ir(0))

                b_power = gr.Button("⏻", elem_classes=["rem-btn", "rem-power"])

                with gr.Row(elem_classes=["rem-row"]):
                    b_n = [gr.Button(str(i), elem_classes=["rem-btn", "rem-num"]) for i in (1, 2, 3, 4)]

                b_mute = gr.Button("MUTE", elem_classes=["rem-btn", "rem-mute"])

                with gr.Row(elem_classes=["rem-row"]):
                    with gr.Column(elem_classes=["rocker"], min_width=74):
                        b_vol_su = gr.Button("+", elem_classes=["rem-btn", "rem-key"])
                        gr.HTML("<div class='rlabel'>VOL</div>")
                        b_vol_giu = gr.Button("−", elem_classes=["rem-btn", "rem-key"])
                    with gr.Column(elem_classes=["rocker"], min_width=74):
                        b_ch_su = gr.Button("▲", elem_classes=["rem-btn", "rem-key"])
                        gr.HTML("<div class='rlabel'>CH</div>")
                        b_ch_giu = gr.Button("▼", elem_classes=["rem-btn", "rem-key"])

                gr.HTML("<div class='rem-brand'>Telecomando TV</div>")

    spiegazione = gr.Markdown(SPIEGAZIONI["inizio"])

    uscite = [stato, tv, spiegazione, ir]

    def collega(bottone, codice):
        bottone.click(lambda s: premi(codice, s), stato, uscite)

    collega(b_power, "power")
    collega(b_mute, "mute")
    collega(b_vol_su, "vol+")
    collega(b_vol_giu, "vol-")
    collega(b_ch_su, "ch+")
    collega(b_ch_giu, "ch-")
    for i, b in enumerate(b_n, start=1):
        collega(b, str(i))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    demo.launch(server_name="0.0.0.0", server_port=port)
