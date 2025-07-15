import pandas as pd
from datetime import datetime, timedelta
import os
import time
from utils import get_coordinates, pobierz_prognoze, make_chart
from generate_pdf import generuj_pdf, generuj_podsumowanie_pdf
from reportlab.platypus import Paragraph, Spacer, Image as RLImage, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# === Ścieżki i parametry ===
MIASTA_CSV = "data/miasta.csv"
START_DATE = datetime.now().date()
END_DATE = START_DATE + timedelta(days=0)
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
    if not opady.empty:
        opady_text = ", ".join(
            f"{row['precipitation']:.1f} mm o godz. {row['godzina']}"
            for _, row in opady.iterrows()
        )
    else:
        opady_text = "Brak opadów"

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
    podsumowania_miast = []
    dane_dla_tabeli = []

    if os.path.exists(FONT_PATH):
        pdfmetrics.registerFont(TTFont("DejaVuSans", FONT_PATH))
    else:
        print("⚠️ Czcionka DejaVuSans.ttf nie znaleziona — raport może nie zawierać polskich znaków.")

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="PolishTitle", fontName="DejaVuSans", fontSize=14, spaceAfter=12))

    os.makedirs(CHART_DIR, exist_ok=True)
    miasta_df = pd.read_csv(MIASTA_CSV, encoding="utf-8")

    current_date = START_DATE
    while current_date <= END_DATE:
        elements = []
        chart_files = []

        for _, row in miasta_df.iterrows():
            miasto = row["miasto"]
            lat, lon = get_coordinates(miasto)
            if lat is None or lon is None:
                continue

            try:
                df = pobierz_prognoze(lat, lon)
                time.sleep(1)
            except Exception:
                continue

            day_df = df[df["date"] == current_date]
            if day_df.empty or len(day_df) < 12:
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

            # Dodaj narracyjne podsumowanie
            podsumowania_miast.append(formatuj_podsumowanie(miasto, day_df))

            # Dodaj dane do tabeli
            dane_dla_tabeli.append({
                "miasto": miasto,
                "max_temp": day_df["temperature_2m"].max(),
                "min_temp": day_df["temperature_2m"].min(),
                "opady_text": ", ".join(
                    f"{row['precipitation']:.1f} mm o godz. {row['time'].strftime('%H:%M')}"
                    for _, row in day_df[day_df["precipitation"] > 0].iterrows()
                ) or "Brak opadów",
                "wiatr_max": day_df["windspeed_10m"].max(),
                "wilg_max": day_df["relative_humidity_2m"].max(),
                "wilg_min": day_df["relative_humidity_2m"].min()
            })

        # Generuj główny raport PDF
        if elements:
            generuj_pdf(elements, str(current_date))

        # Generuj PDF z podsumowaniem
        if podsumowania_miast:
            generuj_podsumowanie_pdf(podsumowania_miast, str(current_date))

        for chart in chart_files:
            if os.path.exists(chart):
                os.remove(chart)

        current_date += timedelta(days=1)

if __name__ == "__main__":
    main()
