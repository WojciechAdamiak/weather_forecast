# 🌤️ Automatyczny raport pogodowy — Python + PDF

Projekt generuje codzienne raporty pogodowe dla wybranych miast w Polsce. Dane pobierane są z API Open-Meteo, przetwarzane, wizualizowane za pomocą wykresów oraz opisane narracyjnie w formacie PDF.

## 🚀 Funkcje

- Pobieranie prognozy godzinowej: temperatura, opady, wiatr, wilgotność
- Czytelne wykresy pogodowe (liniowe i słupkowe)
- Tekstowe podsumowanie dla każdego miasta: najwyższa/najniższa temperatura, opady, wiatr, wilgotność
- Automatyczna generacja pliku PDF
- Obsługa wielu miast z pliku CSV
- Integracja z GitHub Actions — codzienne raporty PDF

## 🗂️ Struktura raportu PDF

Każdy raport zawiera:

- Stronę tytułową z datą
- Wykresy godzinowe dla każdego miasta:
  - Temperatura
  - Opady
  - Wiatr
  - Wilgotność
- Opisowe podsumowanie parametrów pogodowych (bez tabeli)

## 🖼️ Przykładowy raport

![Zrzut wykresu](preview/wykres_temp_Krakow.png)

![Zrzut PDF](preview/fragment_pdf.png)

## 📦 Technologie

- `Python` (3.10+)
- `pandas`, `requests`, `matplotlib`, `reportlab`
- `GitHub Actions` (automatyzacja)
- `Open-Meteo API`, `Nominatim`

## 🧠 Czego się nauczyłem

- Praca z zewnętrznymi API
- Przetwarzanie danych czasowych i generowanie wykresów
- Tworzenie raportów PDF
- Automatyzacja z GitHub Actions

## 🗺️ Jak uruchomić lokalnie

```bash
# Instalacja zależności
pip install -r requirements.txt

# Uruchomienie głównego skryptu
python src/main.py


