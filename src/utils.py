import requests
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

# 🔍 Pobieranie współrzędnych geograficznych z OpenStreetMap
def get_coordinates(city: str) -> tuple[float | None, float | None]:
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": f"{city}, Polska", "format": "json", "limit": 1}
    headers = {"User-Agent": "weather-updater/1.0"}

    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data:
            return float(data[0]["lat"]), float(data[0]["lon"])
    except Exception as e:
        print(f"⚠️ Błąd współrzędnych dla {city}: {e}", flush=True)

    return None, None

# ☁️ Pobieranie prognozy pogody z Open-Meteo (dla wielu dni)
def pobierz_prognoze(lat: float, lon: float, start_date: str, end_date: str, timeout: int = 30) -> pd.DataFrame:
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}&timezone=Europe/Warsaw&"
        f"start_date={start_date}&end_date={end_date}&"
        f"hourly=temperature_2m,precipitation,windspeed_10m,relative_humidity_2m"
    )
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        dane = response.json()

        # Sprawdź, czy dane zawierają sekcję 'hourly'
        if "hourly" not in dane or not isinstance(dane["hourly"], dict):
            print(f"⚠️ Niepoprawna odpowiedź API — brak danych 'hourly'", flush=True)
            return pd.DataFrame()

        df = pd.DataFrame(dane["hourly"])

        # Weryfikuj obecność kolumny 'time'
        if "time" not in df.columns:
            print("⚠️ Odpowiedź API nie zawiera kolumny 'time'", flush=True)
            return pd.DataFrame()

        df["time"] = pd.to_datetime(df["time"])
        df["date"] = df["time"].dt.date
        return df

    except Exception as e:
        print(f"❌ Błąd pobierania prognozy z Open-Meteo: {e}", flush=True)
        return pd.DataFrame()

# 📊 Generowanie wykresów dla prognozowanych danych
def make_chart(values, godziny, title, ylabel, color, filename, miasto, current_date, chart_type="line") -> str:
    try:
        fig, ax = plt.subplots(figsize=(9, 4.5))

        # Upewnij się, że dane nie są puste
        if values.empty or godziny.empty:
            print(f"⚠️ Brak danych do wykresu: {filename}_{miasto}_{current_date}", flush=True)
            plt.close(fig)
            return ""

        if chart_type == "bar":
            ax.bar(godziny, values, color=color, width=0.03)
        else:
            ax.plot(godziny, values, color=color, linewidth=1.8)

        ax.set_title(title, fontsize=13)
        ax.set_ylabel(ylabel)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        ax.xaxis.set_major_locator(mdates.HourLocator(interval=2))
        ax.set_xlim([godziny.min(), godziny.max()])
        ax.grid(True, linestyle="--", alpha=0.3)
        fig.autofmt_xdate()
        plt.tight_layout()

        chart_path = f"charts/{filename}_{miasto}_{current_date}.png"
        fig.savefig(chart_path)
        plt.close(fig)
        return chart_path

    except Exception as e:
        print(f"❌ Błąd tworzenia wykresu dla {miasto}: {e}", flush=True)
        return ""
