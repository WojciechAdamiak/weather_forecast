import pandas as pd
from datetime import datetime, timedelta
import os
import time
import random
from utils import get_coordinates, pobierz_prognoze, make_chart
from generate_pdf import generuj_pdf, generuj_podsumowanie_pdf
from reportlab.platypus import Paragraph, Spacer, Image as RLImage, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# === Parametry projektu ===
MIASTA_CSV = "data/miasta.csv"
START_DATE = datetime.now().date()
DNI_RAPORTU = 3
CHART_DIR = "charts"
FONT_PATH = "fonts/DejaVuSans.ttf"

def formatuj_podsumowanie(miasto, df):
    df = df.copy()
    df["godzina"] = df["time"].dt.strftime('%H:%M')
    temp_max = df["temperature_2m"].max()
    temp_max_hour = df[df["temperature_2m"] == temp_max]["godzina"].iloc[0]
    temp_min = df["temperature_2m"].min()
    temp_min_hour = df[df["temperature_2m"] == temp_min]["godzina"].iloc[0]

    opady = df[df["precipitation"] > 0][["godzina", "precipitation"]]
    opady_text = (
        ", ".join(f"{row['precipitation']:.1f} mm o godz. {row['godzina']}" for _, row in opady.iterrows())
        if not opady.empty else "Brak opadów"
    )

    wiatr_max = df["windspeed_10m"].max()
    wiatr_hour = df[df["windspeed_10m"] == wiatr_max]["godzina"].iloc[0]
    wilg_max = df["relative_humidity_2m"].max()
    wilg_max_hour = df[df["relative_humidity_2m"] == wilg_max]["godzina"].iloc[0]
    wilg_min = df["relative_humidity_2m"].min()
    wilg_min_hour = df[df["relative_humidity_2m"] == wilg_min]["godzina"].iloc[0]

    return (
        f"<b>{miasto}</b>:<br/>"
        f"• Najwyższa temperatura: {temp_max:.1f}°C o godz. {temp_max_hour}<br/>"
        f"• Najniższa temperatura: {temp_min:.1f}°C o godz. {temp_min_hour}<br/>"
        f"• Opady: {opady_text}<br/>"
        f"• Najsilniejszy wiatr: {wiatr_max:.0f} km/h o godz. {wiatr_hour}<br/>"
        f"• Wilgotność: max {wilg_max:.0f}% o godz. {wilg_max_hour}, min {wilg_min:.0f}% o godz. {wilg_min_hour}<br/><br/>"
    )

def main():
    print("🚀 Startuję raport pogodowy...", flush=True)

    # Czcionka PDF
    if os.path.exists(FONT_PATH):
        pdfmetrics.registerFont(TTFont("DejaVuSans", FONT_PATH))
        print("🔤 Czcionka DejaVuSans zarejestrowana", flush=True)

    # Style i foldery
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="PolishTitle", fontName="DejaVuSans", fontSize=14, spaceAfter=12))
    os.makedirs(CHART_DIR, exist_ok=True)
    os.makedirs("raporty", exist_ok=True)

    # Miasta
    print(f"📥 Wczytuję dane z: {MIASTA_CSV}", flush=True)
    miasta_df = pd.read_csv(MIASTA_CSV, encoding="utf-8")

    start_str = START_DATE.strftime('%Y-%m-%d')
    end_str = (START_DATE + timedelta(days=DNI_RAPORTU - 1)).strftime('%Y-%m-%d')

    for i in range(DNI_RAPORTU):
        current_date = START_DATE + timedelta(days=i)
        print(f"\n📆 Generuję raport dla dnia: {current_date}", flush=True)
        elements = []
        chart_files = []
        podsumowania_miast = []

        for _, row in miasta_df.iterrows():
            miasto = row["miasto"]
            print(f"🌍 Przetwarzam miasto: {miasto}", flush=True)

            lat, lon = get_coordinates(miasto)
            if lat is None or lon is None:
                print(f"⚠️ Brak współrzędnych dla {miasto}", flush=True)
                continue

            # Retry z opóźnieniem
            df = pd.DataFrame()
            for attempt in range(3):
                try:
                    df = pobierz_prognoze(lat, lon, start_str, end_str, timeout=60)
                    df["date"] = pd.to_datetime(df["time"]).dt.date
                    break
                except Exception as e:
                    print(f"⏳ Próba {attempt+1} dla {miasto} nieudana: {e}", flush=True)
                    time.sleep(5)

            # Sprawdzenie wyniku
            if df.empty or "time" not in df.columns:
                print(f"❌ Brak danych prognozy dla {miasto} — pomijam", flush=True)
                continue

            day_df = df[df["date"] == current_date]
            if day_df.empty or len(day_df) < 12:
                print(f"⚠️ Brak danych godzinowych dla {miasto} w dniu {current_date}", flush=True)
                continue

            godziny = day_df["time"]
            charts = [
                make_chart(day_df["temperature_2m"], godziny, "Temperatura godzinowa", "Temp (°C)", "firebrick", "temp", miasto, current_date),
                make_chart(day_df["precipitation"], godziny, "Opady godzinowe", "Opady (mm)", "dodgerblue", "opady", miasto, current_date, chart_type="bar"),
                make_chart(day_df["windspeed_10m"], godziny, "Wiatr godzinowy", "Wiatr (km/h)", "forestgreen", "wiatr", miasto, current_date),
                make_chart(day_df["relative_humidity_2m"], godziny, "Wilgotność godzinowa", "Wilgotność (%)", "darkorchid", "wilg", miasto, current_date)
            ]

            elements.append(Paragraph(f"<b>{miasto} – {current_date} (Prognoza)</b>", styles["PolishTitle"]))
            for chart in charts:
                elements.append(RLImage(chart, width=470, height=260))
                elements.append(Spacer(1, 12))
                chart_files.append(chart)
            elements.append(PageBreak())

            podsumowania_miast.append(formatuj_podsumowanie(miasto, day_df))

            # Opóźnienie między miastami
            time.sleep(random.uniform(1.5, 4.0))

        # PDF-y
        if elements:
            generuj_pdf(elements, str(current_date))
            print(f"📄 Raport PDF wygenerowany: raport_{current_date}.pdf", flush=True)

        if podsumowania_miast:
            generuj_podsumowanie_pdf(podsumowania_miast, str(current_date))
            print(f"📑 Podsumowanie PDF wygenerowane: podsumowanie_{current_date}.pdf", flush=True)

        # Czyść wykresy
        for chart in chart_files:
            if os.path.exists(chart):
                os.remove(chart)

    print("✅ Wszystkie raporty gotowe — koniec procesu.\n", flush=True)

if __name__ == "__main__":
    try:
        main()
    except Exception as err:
        print(f"❌ Błąd ogólny: {err}", flush=True)



