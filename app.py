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
