from reportlab.lib import colors
from reportlab.pdfgen import canvas
from django.conf import settings
import os
from datetime import date

def generer_pdf(response, width, height):
    p = canvas.Canvas(response)

    # ton entête ici
    p.setFillColor(colors.HexColor("#e6e6e6"))
    p.rect(30, height - 70, width - 60, 35, fill=1, stroke=0)

    logo_path = os.path.join(settings.BASE_DIR, "static", "images", "logo.png")

    if os.path.exists(logo_path):
        p.drawImage(logo_path, 40, height - 67, 30, 25)

    p.setFont("Helvetica-Bold", 14)
    p.drawCentredString(width / 2, height - 115, "JOURNAL DES ACTIVITES")

    p.drawString(40, height - 140, f"Date : {date.today():%d/%m/%Y}")

    return p