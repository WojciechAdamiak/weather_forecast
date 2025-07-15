import os
import matplotlib.pyplot as plt
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4


# === Styl globalny
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="Polish", fontName="DejaVuSans", fontSize=12, spaceAfter=12))
styles.add(ParagraphStyle(name="PolishTitle", fontName="DejaVuSans", fontSize=14, spaceAfter=18))


def generuj_pdf(elements: list, current_date: str, save_dir: str = "raporty") -> None:
    os.makedirs(save_dir, exist_ok=True)
    filename = os.path.join(save_dir, f"raport_{current_date}_prognoza.pdf")
    try:
        SimpleDocTemplate(filename, pagesize=A4).build(elements)
        print(f"✅ Wygenerowano: {filename}")
    except PermissionError:
        print(f"❌ Nie można zapisać: {filename}")


def generuj_podsumowanie_pdf(
    podsumowania: list[str],
    current_date: str,
    save_dir: str = "raporty",
    tabela_path: str = None
) -> None:
    os.makedirs(save_dir, exist_ok=True)
    filename = os.path.join(save_dir, f"raport_podsumowanie_{current_date}.pdf")

    font_path = "fonts/DejaVuSans.ttf"
    if os.path.exists(font_path):
        pdfmetrics.registerFont(TTFont("DejaVuSans", font_path))

    elements = []

    # Strona tytułowa
    elements.append(Paragraph(f"<b>📊 Podsumowanie dnia: {current_date}</b>", styles["PolishTitle"]))
    elements.append(Spacer(1, 12))

    # Narracyjne podsumowanie
    for blok in podsumowania:
        elements.append(Paragraph(blok, styles["Polish"]))
        elements.append(Spacer(1, 8))

    try:
        SimpleDocTemplate(filename, pagesize=A4).build(elements)
        print(f"✅ Podsumowanie PDF wygenerowane: {filename}")
    except PermissionError:
        print(f"❌ Nie można zapisać pliku: {filename}")
