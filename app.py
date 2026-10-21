"""
TV e telecomando virtuali con Gradio e Google Gemini.
Fatto Da Francesco Lauriola

Installazione:  pip install gradio google-genai
Avvio:          python app.py
"""

import os
import gradio as gr
from google import genai

# Inizializzazione del client Google GenAI (legge la chiave dalla variabile d'ambiente GEMINI_API_KEY)
try:
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
except Exception:
    client = None

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
<div style="background: linear-gradient(135deg, rgba(34, 197, 94, 0.1), rgba(16, 185, 129, 0.05)); border-left: 5px solid #22c55e; padding: 15px; border-radius: 8px;">
    <h3 style="color: #22c55e; margin-top: 0;">⚡ Accensione: Cosa succede dentro la TV</h3>
    <ol style="margin-bottom: 0; line-height: 1.6;">
        <li><b>Premi il Tasto Rosso POWER:</b> Il tasto chiude un contatto e il microchip interno genera un codice binario specifico.</li>
        <li><b>Lampi Infrarossi:</b> Il LED in cima al telecomando emette lampi di luce invisibile all'occhio umano (visibili però con la fotocamera dello smartphone!).</li>
        <li><b>Il ruolo dello Standby:</b> La TV non era spenta del tutto; il sensore e un piccolo circuito ricevente erano già alimentati in attesa del comando.</li>
        <li><b>Elaborazione:</b> Il sensore cattura i lampi, il processore li decodifica e riconosce che deve avviarsi.</li>
        <li><b>Attivazione generale:</b> L'alimentatore distribuisce corrente a schermo, retroilluminazione e audio.</li>
        <li><b>Risultato:</b> Il LED diventa verde e compare l'immagine dell'ultimo canale!</li>
    </ol>
</div>
""",
    "spegni": """
<div style="background: linear-gradient(135deg, rgba(239, 68, 68, 0.1), rgba(220, 38, 38, 0.05)); border-left: 5px solid #ef4444; padding: 15px; border-radius: 8px;">
    <h3 style="color: #ef4444; margin-top: 0;">🛑 Spegnimento in Standby</h3>
    <ol style="margin-bottom: 0; line-height: 1.6;">
        <li><b>Comando di Standby:</b> Premendo di nuovo il tasto POWER, viene inviato il codice per lo spegnimento logico.</li>
        <li><b>Disattivazione componenti:</b> Il processore spegne lo schermo e l'audio, ma mantiene attivo il circuito di ricezione IR.</li>
        <li><b>Consumo minimo:</b> La TV resta in ascolto per poter ripartire subito alla prossima pressione del tasto rosso.</li>
    </ol>
</div>
""",
    "ignorato": """
<div style="background: linear-gradient(135deg, rgba(245, 158, 11, 0.1), rgba(217, 119, 6, 0.05)); border-left: 5px solid #f59e0b; padding: 15px; border-radius: 8px;">
    <h3 style="color: #f59e0b; margin-top: 0;">⚠️ Comando Ignorato (TV in Standby)</h3>
    <p style="margin-bottom: 0; line-height: 1.6;">
        La TV è spenta (in standby). In questo stato il sensore riconosce <b>unicamente il tasto rosso POWER</b>. 
        Tutti gli altri tasti (volume, canali) vengono scartati perché non c'è alcun flusso audio/video da regolare. 
        <br><br><b>Premi il grande tasto rosso POWER per accenderla!</b>
    </p>
</div>
""",
    "volume": """
<div style="background: linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(37, 99, 235, 0.05)); border-left: 5px solid #3b82f6; padding: 15px; border-radius: 8px;">
    <h3 style="color: #3b82f6; margin-top: 0;">🔊 Regolazione del Volume</h3>
    <p style="margin-bottom: 0; line-height: 1.6;">
        Il telecomando invia il codice audio. Il processore della TV modifica istantaneamente il guadagno dell'amplificatore e mostra la barra grafica OSD (On-Screen Display) sullo schermo.
    </p>
</div>
""",
    "muto": """
<div style="background: linear-gradient(135deg, rgba(168, 85, 247, 0.1), rgba(147, 51, 234, 0.05)); border-left: 5px solid #a855f7; padding: 15px; border-radius: 8px;">
    <h3 style="color: #a855f7; margin-top: 0;">🔇 Funzione Muto</h3>
    <p style="margin-bottom: 0; line-height: 1.6;">
        Il tasto MUTE azzera temporaneamente l'uscita audio senza alterare il livello numerico del volume impostato. Premendolo di nuovo, l'audio viene ripristinato esattamente dov'era.
    </p>
</div>
""",
    "canale": """
<div style="background: linear-gradient(135deg, rgba(236, 72, 153, 0.1), rgba(219, 39, 119, 0.05)); border-left: 5px solid #ec4899; padding: 15px; border-radius: 8px;">
    <h3 style="color: #ec4899; margin-top: 0;">📺 Cambio Canale</h3>
    <p style="margin-bottom: 0; line-height: 1.6;">
        Il sintonizzatore interno cambia il flusso dei dati video ricevuti, aggiornando istantaneamente grafica, colori e titolo del programma sullo schermo della TV.
    </p>
</div>
""",
    "inizio": """
<div style="background: linear-gradient(135deg, rgba(99, 102, 241, 0.1), rgba(79, 70, 229, 0.05)); border-left: 5px solid #6366f1; padding: 15px; border-radius: 8px;">
    <h3 style="color: #6366f1; margin-top: 0;">👋 Benvenuto! Come iniziare</h3>
    <p style="margin-bottom: 0; line-height: 1.6;">
        Questo simulatore interattivo ti mostra cosa succede nei circuiti di una TV. 
        <br>👉 <b>Inizia subito premendo il grande TASTO ROSSO POWER</b> in alto sul telecomando per accendere la televisione!
    </p>
</div>
""",
}

# ----------------------------------------------------------------------------
# Grafica avanzata e Responsive (CSS)
# ----------------------------------------------------------------------------

CSS_LAYOUT = """
footer { display: none !important; }
#gradio-app { background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%) !important; min-height: 100vh; }
.gradio-container { max-width: 1050px !important; margin: 0 auto !important; font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif !important; }

.custom-header {
    text-align: center;
    padding: 25px 20px;
    background: rgba(30, 41, 59, 0.7);
    backdrop-filter: blur(12px);
    border-radius: 16px;
    border: 1px solid rgba(255, 255, 255, 0.1);
    box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    margin-bottom: 20px;
}
.custom-header h1 {
    font-size: 2.2rem;
    font-weight: 800;
    color: #f8fafc;
    margin: 0;
    letter-spacing: -0.5px;
}

.custom-footer {
    text-align: center;
    padding: 20px;
    margin-top: 30px;
    background: rgba(15, 23, 42, 0.8);
    border-top: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 12px;
}
.custom-footer h2 {
    font-size: 1.5rem;
    color: #38bdf8;
    font-weight: 700;
    margin: 0;
    letter-spacing: 0.5px;
}

.tv-wrap { display: flex; flex-direction: column; align-items: center; width: 100%; }
.tv-body { background: #09090b; border-radius: 20px; padding: 20px 20px 12px; width: 100%; max-width: 540px;
           box-shadow: 0 20px 40px rgba(0,0,0,0.6), inset 0 1px 1px rgba(255,255,255,0.1); border: 2px solid #27272a; }
.tv-screen { position: relative; height: 310px; border-radius: 10px; overflow: hidden;
             display: flex; align-items: center; justify-content: center; }
.tv-off { background: radial-gradient(circle, #18181b 0%, #09090b 100%); box-shadow: inset 0 0 50px rgba(0,0,0,0.9); }
.tv-title { color: #fff; font-size: 2.4rem; font-weight: 800; text-shadow: 0 4px 15px rgba(0,0,0,0.7); text-align: center; }
.tv-sub { color: rgba(255,255,255,0.9); font-size: 1.1rem; margin-top: 6px; text-align: center; font-weight: 500; }
.tv-osd { position: absolute; left: 16px; right: 16px; bottom: 14px; color: #fff; font-size: 0.95rem;
          display: flex; align-items: center; gap: 12px; background: rgba(0,0,0,0.65); backdrop-filter: blur(5px); padding: 8px 14px; border-radius: 8px; }
.tv-bar { flex: 1; height: 10px; background: rgba(255,255,255,0.2); border-radius: 5px; overflow: hidden; }
.tv-bar > span { display: block; height: 100%; background: #38bdf8; border-radius: 5px; }
.tv-ch { position: absolute; top: 14px; right: 16px; color: #fff; font-size: 1.1rem; font-weight: 700; background: rgba(0,0,0,0.5);
         padding: 4px 12px; border-radius: 6px; backdrop-filter: blur(4px); }
.tv-footer { display: flex; align-items: center; justify-content: space-between; padding: 12px 8px 4px; color: #a1a1aa; font-size: 0.85rem; font-weight: 600; }
.led { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 8px; vertical-align: middle; }
.led-red { background: #ef4444; box-shadow: 0 0 10px #ef4444, 0 0 20px #ef4444; }
.led-green { background: #22c55e; box-shadow: 0 0 10px #22c55e, 0 0 20px #22c55e; }
.tv-stand { width: 140px; height: 12px; background: linear-gradient(to bottom, #3f3f46, #27272a); border-radius: 0 0 8px 8px; box-shadow: 0 5px 15px rgba(0,0,0,0.5); }
.tv-state { margin-top: 15px; font-size: 1.05rem; color: #e2e8f0; text-align: center; background: rgba(30, 41, 59, 0.5); padding: 8px 16px; border-radius: 8px; width: 100%; max-width: 540px; }
"""

CSS_REMOTE = """
#telecomando {
  width: 100% !important; max-width: 250px !important; margin: 0 auto;
  background: linear-gradient(165deg, #334155 0%, #1e293b 50%, #0f172a 100%) !important;
  border: 1px solid rgba(255, 255, 255, 0.15) !important; 
  border-radius: 40px !important;
  padding: 20px 16px 24px !important; gap: 14px !important; align-items: center !important;
  box-shadow: 0 20px 40px rgba(0,0,0,0.5), inset 0 2px 4px rgba(255,255,255,0.2) !important;
}
#telecomando .rem-row { justify-content: center !important; gap: 10px !important; flex-wrap: nowrap !important;
  background: transparent !important; border: none !important; padding: 0 !important; box-shadow: none !important; }
#telecomando .gap, #telecomando .form { background: transparent !important; border: none !important; }

.ir-window { width: 100px; height: 18px; margin: 0 auto; border-radius: 10px;
  background: linear-gradient(#09090b, #18181b); border: 1px solid rgba(0,0,0,0.8);
  box-shadow: inset 0 2px 4px rgba(0,0,0,0.9);
  display: flex; align-items: center; justify-content: center; }
.ir-led { width: 64px; height: 6px; border-radius: 3px; background: #3f1010; }
.ir-a { animation: ir-flash-a .4s ease-out; }
.ir-b { animation: ir-flash-b .4s ease-out; }
@keyframes ir-flash-a { 0%{background:#ef4444; box-shadow:0 0 16px 6px #ef4444;} 100%{background:#3f1010; box-shadow:none;} }
@keyframes ir-flash-b { 0%{background:#ef4444; box-shadow:0 0 16px 6px #ef4444;} 100%{background:#3f1010; box-shadow:none;} }

#telecomando button { font-family: inherit !important; padding: 0 !important; }
.rem-btn { background: linear-gradient(#475569, #334155) !important; color: #f1f5f9 !important;
  border: 1px solid rgba(255,255,255,0.1) !important; font-weight: 600 !important;
  box-shadow: 0 4px 6px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.15) !important; transition: all 0.1s ease; }
.rem-btn:active { transform: translateY(2px); box-shadow: 0 1px 2px rgba(0,0,0,0.3) !important; }

.power-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  background: rgba(239, 68, 68, 0.08);
  border: 2px dashed rgba(239, 68, 68, 0.4);
  padding: 10px;
  border-radius: 20px;
  width: 100%;
}
.power-label {
  color: #fca5a5;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 6px;
  text-align: center;
}
.rem-power { 
  width: 66px !important; height: 66px !important; min-width: 66px !important; flex: none !important;
  border-radius: 50% !important; font-size: 1.8rem !important;
  background: radial-gradient(circle at 35% 30%, #f87171, #dc2626 70%, #991b1b 100%) !important; 
  color: #fff !important;
  border: 2px solid #fca5a5 !important;
  box-shadow: 0 0 20px rgba(239, 68, 68, 0.6), 0 6px 12px rgba(0,0,0,0.4), inset 0 2px 4px rgba(255,255,255,0.4) !important;
  animation: pulse-power 2s infinite;
}
@keyframes pulse-power {
  0% { box-shadow: 0 0 15px rgba(239, 68, 68, 0.5), 0 6px 12px rgba(0,0,0,0.4), inset 0 2px 4px rgba(255,255,255,0.4); }
  50% { box-shadow: 0 0 25px rgba(239, 68, 68, 0.9), 0 6px 12px rgba(0,0,0,0.4), inset 0 2px 4px rgba(255,255,255,0.4); }
  100% { box-shadow: 0 0 15px rgba(239, 68, 68, 0.5), 0 6px 12px rgba(0,0,0,0.4), inset 0 2px 4px rgba(255,255,255,0.4); }
}

.rem-num { width: 42px !important; height: 42px !important; min-width: 42px !important; flex: none !important;
  border-radius: 50% !important; font-size: 1rem !important; }
.rem-mute { width: 116px !important; height: 34px !important; min-width: 116px !important; flex: none !important;
  border-radius: 17px !important; font-size: 0.8rem !important; letter-spacing: 0.5px; }

#telecomando .rocker { width: 76px !important; min-width: 76px !important; max-width: 76px !important; flex: none !important;
  background: linear-gradient(#1e293b, #0f172a) !important; border: 1px solid rgba(255,255,255,0.1) !important;
  border-radius: 38px !important; padding: 6px 0 !important; gap: 0 !important; align-items: center !important;
  box-shadow: inset 0 4px 8px rgba(0,0,0,0.8), 0 2px 4px rgba(0,0,0,0.2) !important; }
.rem-key { width: 58px !important; height: 52px !important; min-width: 58px !important; flex: none !important;
  border-radius: 26px !important; font-size: 1.6rem !important; line-height: 1 !important; }
.rlabel { text-align: center; color: #94a3b8; font-family: inherit; font-size: 0.75rem;
  font-weight: 700; padding: 0 !important; min-height: 0 !important; margin: 4px 0; letter-spacing: 0.5px; }
.rem-brand { text-align: center; color: #64748b; font-family: inherit; font-size: 0.7rem;
  padding: 0 !important; min-height: 0 !important; font-weight: 600; letter-spacing: 1px; text-transform: uppercase; }
"""


def disegna_tv(stato):
    if stato["acceso"]:
        nome, c1, c2 = CANALI[stato["canale"]]
        if stato["muto"]:
            osd = '<div class="tv-osd">🔇 Audio disattivato (Muto)</div>'
        else:
            osd = (
                '<div class="tv-osd">🔊 Vol <div class="tv-bar"><span style="width:%d%%"></span></div> %d</div>'
                % (stato["volume"] * 5, stato["volume"])
            )
        schermo = (
            '<div class="tv-screen" style="background:linear-gradient(135deg,%s,%s)">'
            '<div><div class="tv-title">%s</div><div class="tv-sub">Canale %d</div></div>'
            '<div class="tv-ch">CH %d</div>%s</div>'
        ) % (c1, c2, nome, stato["canale"] + 1, stato["canale"] + 1, osd)
        led = '<span class="led led-green"></span>Acceso'
        testo = "La TV è <b>accesa</b> e pronta all'uso."
    else:
        schermo = '<div class="tv-screen tv-off"></div>'
        led = '<span class="led led-red"></span>Standby'
        testo = "La TV è in <b>standby</b> (premi il tasto rosso POWER sul telecomando per accenderla)."

    return (
        "<style>" + CSS_LAYOUT + "</style>"
        '<div class="tv-wrap"><div class="tv-body">'
        + schermo
        + '<div class="tv-footer"><span>' + led + "</span><span>Sensore IR 📡</span></div>"
        "</div>"
        '<div class="tv-stand"></div>'
        '<div class="tv-state">' + testo + "</div></div>"
    )


def disegna_ir(n):
    classe = "" if n == 0 else ("ir-a" if n % 2 else "ir-b")
    return '<div class="ir-window"><div class="ir-led %s"></div></div>' % classe


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
    else:
        stato["canale"] = int(tasto) - 1
        chiave = "canale"

    return stato, disegna_tv(stato), SPIEGAZIONI[chiave], disegna_ir(stato["n"])


# Funzione di risposta dell'assistente IA con Google Gemini
def rispondi_ia(messaggio, cronologia):
    if not client:
        return "⚠️ Chiave API di Google Gemini non configurata. Aggiungi GEMINI_API_KEY nelle variabili d'ambiente."
    try:
        # Prompt di sistema per istruire Gemini a rispondere in modo semplice, ideale per anziani
        prompt_sistema = (
            "Sei un assistente digitale molto gentile, paziente e chiaro. "
            "Stai aiutando una persona anziana o poco esperta a capire come usare la televisione e il telecomando. "
            "Usa un linguaggio semplicissimo, rassicurante, amichevole e usa frasi brevi."
        )
        
        # Converte la cronologia nel formato supportato o usa direttamente models.generate_content
        risposta = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"{prompt_sistema}\n\nUtente: {messaggio}"
        )
        return risposta.text
    except Exception as e:
        return f"Si è verificato un errore nel contattare l'intelligenza artificiale: {str(e)}"


# ----------------------------------------------------------------------------
# Interfaccia Gradio
# ----------------------------------------------------------------------------

TEMA = gr.themes.Soft(primary_hue="red", neutral_hue="slate")

with gr.Blocks(title="Impara ad usare il telecomando della TV") as demo:
    gr.HTML("<style>" + CSS_LAYOUT + CSS_REMOTE + "</style>")
    
    gr.HTML("""
        <div class="custom-header">
            <h1>Impara ad usare il telecomando della TV , Guida facile per anziani</h1>
        </div>
    """)

    stato = gr.State(dict(STATO_INIZIALE))

    with gr.Row():
        with gr.Column(scale=3):
            tv = gr.HTML(disegna_tv(STATO_INIZIALE))

        with gr.Column(scale=0, min_width=260):
            with gr.Column(elem_id="telecomando"):
                ir = gr.HTML(disegna_ir(0))

                gr.HTML('<div class="power-container"><div class="power-label">Tasto Principale</div>')
                b_power = gr.Button("⏻", elem_classes=["rem-btn", "rem-power"])
                gr.HTML('</div>')

                with gr.Row(elem_classes=["rem-row"]):
                    b_n = [gr.Button(str(i), elem_classes=["rem-btn", "rem-num"]) for i in (1, 2, 3, 4)]

                b_mute = gr.Button("MUTE", elem_classes=["rem-btn", "rem-mute"])

                with gr.Row(elem_classes=["rem-row"]):
                    with gr.Column(elem_classes=["rocker"], min_width=76):
                        b_vol_su = gr.Button("+", elem_classes=["rem-btn", "rem-key"])
                        gr.HTML("<div class='rlabel'>VOL</div>")
                        b_vol_giu = gr.Button("−", elem_classes=["rem-btn", "rem-key"])
                    with gr.Column(elem_classes=["rocker"], min_width=76):
                        b_ch_su = gr.Button("▲", elem_classes=["rem-btn", "rem-key"])
                        gr.HTML("<div class='rlabel'>CH</div>")
                        b_ch_giu = gr.Button("▼", elem_classes=["rem-btn", "rem-key"])

                gr.HTML("<div class='rem-brand'>Smart Remote</div>")

    spiegazione = gr.Markdown(SPIEGAZIONI["inizio"])

    # --- SEZIONE CHAT CON GOOGLE GEMINI ---
    gr.Markdown("--- \n### 🤖 Chiedi aiuto all'Assistente IA")
    gr.Markdown("Hai dubbi su come funziona la TV o il telecomando? Scrivi qui sotto una domanda e fatti aiutare dall'intelligenza artificiale:")
    
    chat_ia = gr.ChatInterface(
        fn=rispondi_ia,
        chatbot=gr.Chatbot(height=240, label="Assistente Virtuale"),
        textbox=gr.Textbox(placeholder="Scrivi qui la tua domanda (es. Come si accende la TV?)...", container=False, scale=7),
        submit_btn="Invia",
        theme="soft"
    )

    # --- FIRMA SOTTO TUTTO ---
    gr.HTML("""
        <div class="custom-footer">
            <h2>Fatto Da Francesco Lauriola</h2>
        </div>
    """)

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
    demo.launch(theme=TEMA, server_name="0.0.0.0", server_port=port)
