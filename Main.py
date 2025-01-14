#!/usr/bin/env python3
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib import colors
import json

# Arxiu de sortida
filename = "donePlantilla04.pdf"

# Colors personalitzats
custom_colors = {
    'primary': colors.HexColor('#6f937d'),
}

# Estils
styles = {
    "MainTitle": ParagraphStyle(
        name="MainTitle",
        fontName="Helvetica-Bold",
        fontSize=24,
        leading=30,
        textColor=custom_colors['primary'],
        alignment=TA_CENTER,
        spaceAfter=20,
    ),
    "PreTitle": ParagraphStyle(
        name="PreTitle",
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=25,
        textColor=custom_colors['primary'],
        alignment=TA_LEFT,
        spaceAfter=10,
    )
}

# Funció per carregar JSON
def cargar_json():
    global data
    with open('clients.json') as file:
        data = json.load(file)

# Funció per escriure el pre-títol i el títol
def draw_titles(c, pre_title_text, title_text, style, pre_title_style, x, y, width):
    # Afegir pre-títol
    preP = Paragraph(pre_title_text, pre_title_style)
    preP.wrap(width, float('inf'))  # Calcula l'amplada i l'altura
    pre_height = preP.height

    # Afegir títol
    p = Paragraph(title_text, style)
    p.wrap(width, float('inf'))  # Calcula l'amplada i l'altura
    title_height = p.height

    # Dibuixar els textos
    preP.drawOn(c, x, y)
    p.drawOn(c, x, y - pre_height - title_height)
    
    return pre_height + title_height

# Carregar dades
data = None
cargar_json()

# Configurar PDF
c = canvas.Canvas(filename, pagesize=A4)
page_width, page_height = A4
margin = 50
width = page_width - (2 * margin)

# Iterar sobre cada client i crear una pàgina nova
for entrada in data["clients"]:
    current_y = page_height - 50

    draw_titles(
        c,
        pre_title_text="Factura",
        title_text=f"{entrada['companyia']}",
        style=styles["MainTitle"],
        pre_title_style=styles["PreTitle"],
        x=margin,
        y=current_y,
        width=width
    )
    
    c.showPage()

c.save()
