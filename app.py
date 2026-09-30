import time
import requests
from flask import Flask, render_template_string
import folium

app = Flask(__name__)

# URL API TruckersMP per la lista dei server e traffico
TRUCKERSMP_API_SERVERS = "https://api.truckersmp.com/v2/servers"
TRUCKERSMP_API_TRAFFIC = "https://api.truckersmp.com/v2/traffic"

def get_truckersmp_traffic():
    """Recupera le informazioni sulla congestione stradale da TruckersMP."""
    try:
        response = requests.get(TRUCKERSMP_API_TRAFFIC, timeout=5)
        if response.status_code == 200:
            return response.json().get("response", [])
    except Exception as e:
        print(f"[ERROR] Impossibile recuperare i dati del traffico: {e}")
    return []

@app.route("/")
def render_map():
    """Genera e visualizza la mappa HTML del traffico."""
    traffic_data = get_truckersmp_traffic()

    # Mappe con punto centrale indicativo (Europa Centrale)
    map_center = [51.1657, 10.4515]
    ets_map = folium.Map(location=map_center, zoom_start=6, tiles="CartoDB dark_matter")

    # Aggiunge i punti caldi di traffico sulla mappa
    for zone in traffic_data[:50]:  # Limita ai primi 50 punti critici
        name = zone.get("name", "Zona Sconosciuta")
        players = zone.get("players", 0)
        severity = zone.get("severity", "Low")
        
        # Selezione colore in base alla densità
        color = "green"
        if players > 30:
            color = "orange"
        if players > 70:
            color = "red"

        # Esempio di coordinate indicativi (mapping indicativo per mod UI)
        folium.CircleMarker(
            location=[50.0 + (players % 5), 8.0 + (players % 10)],
            radius=min(players / 2, 20),
            popup=f"<b>{name}</b><br>Giocatori: {players}<br>Livello traffico: {severity}",
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.6
        ).add_to(ets_map)

    return ets_map._repr_html_()

if __name__ == "__main__":
    print("Avvio del server Mappa Traffico ETS2/TruckersMP su http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=True)

import os
import threading
import asyncio
import requests
import discord
from discord.ext import commands
from flask import Flask
import folium

# --- 1. CONFIGURAZIONE FLASK ---
app = Flask(__name__)

TRUCKERSMP_API_TRAFFIC = "https://api.truckersmp.com/v2/traffic"

def get_truckersmp_traffic():
    try:
        response = requests.get(TRUCKERSMP_API_TRAFFIC, timeout=5)
        if response.status_code == 200:
            return response.json().get("response", [])
    except Exception as e:
        print(f"[ERROR API] {e}")
    return []

@app.route("/")
def render_map():
    traffic_data = get_truckersmp_traffic()
    map_center = [51.1657, 10.4515]
    ets_map = folium.Map(location=map_center, zoom_start=6, tiles="CartoDB dark_matter")

    for zone in traffic_data[:50]:
        name = zone.get("name", "Zona Sconosciuta")
        players = zone.get("players", 0)
        severity = zone.get("severity", "Low")
        
        color = "green"
        if players > 30: color = "orange"
        if players > 70: color = "red"

        folium.CircleMarker(
            location=[50.0 + (players % 5), 8.0 + (players % 10)],
            radius=min(players / 2, 20),
            popup=f"<b>{name}</b><br>Giocatori: {players}<br>Traffico: {severity}",
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.6
        ).add_to(ets_map)

    return ets_map._repr_html_()

def run_flask():
    # Prende la porta assegnata da Railway (default 5000 se in locale)
    port = int(os.environ.get("PORT", 5000))
    # '0.0.0.0' è OBBLIGATORIO per Railway
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)

# --- 2. CONFIGURAZIONE BOT DISCORD ---
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"=== BOT DISCORD ONLINE: {bot.user} ===")

@bot.command()
async def ping(ctx):
    await ctx.send("Pong! Il bot ETS2 è attivo.")


# --- 3. AVVIO PARALLELO ---
if __name__ == "__main__":
    # Avvia Flask in un thread separato
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    # Avvia il Bot Discord nel thread principale
    token = os.environ.get("DISCORD_TOKEN")
    if token:

        @bot.command()
async def mappa(ctx):
    # Sostituisci con l'URL pubblico generato da Railway
    url_mappa = os.environ.get("RAILWAY_STATIC_URL", "https://tuo-app.up.railway.app")
    if not url_mappa.startswith("http"):
        url_mappa = f"https://{url_mappa}"
        
    embed = discord.Embed(
        title="🗺️ Mappa Traffico Live ETS2 / TruckersMP",
        description=f"Consulta lo stato del traffico e i punti caldi in tempo reale:\n[Clicca qui per aprire la mappa]({url_mappa})",
        color=discord.Color.blue()
    )
    await ctx.send(embed=embed)
        print("Avvio del bot Discord in corso...")
        bot.run(token)
    else:
        print("[ERRORE] Variabile DISCORD_TOKEN non trovata su Railway!")
