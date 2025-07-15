import requests
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

def get_coordinates(city: str) -> tuple[float | None, float | None]:
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": f"{city}, Polska", "format": "json", "limit": 1}
    headers = {"User-Agent": "weather-updater/1.0"}
    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        if data:
            return float(data[0]["lat"]), float(data[0]["lon"])
    except Exception as e:
        print(f"⚠️ Błąd współrzędnych dla {city}: {e}")
    return None, None

def pobierz_prognoze(lat: float, lon: float) -> pd.DataFrame:
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}&timezone=Europe/Warsaw&"
        f"hourly=temperature_2m,precipitation,windspeed_10m,relative_humidity_2m"
    )
    response = requests.get(url)
    response.raise_for_status()
    dane = response.json()
    df = pd.DataFrame(dane["hourly"])
    df["time"] = pd.to_datetime(df["time"])
    df["date"] = df["time"].dt.date
    return df

def make_chart(values, godziny, title, ylabel, color, filename, miasto, current_date, chart_type="line") -> str:
    fig, ax = plt.subplots(figsize=(9, 4.5))
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
