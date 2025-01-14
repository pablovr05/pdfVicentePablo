#!/usr/bin/env python3
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib import colors
import json
from datetime import datetime

filename = "PlantillaAcabada.pdf"

# ------------------------------------- COLORS ----------------------------
custom_colors = {
    'primary': colors.HexColor('#6f937d'),
    'regular': colors.white,
    'bonus': colors.lightpink,
    'exempt': colors.lightgreen
}

# --------------------------------- ESTILS ----------------------------------
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
    "PreText": ParagraphStyle(
        name="PreTitle",
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=25,
        textColor=custom_colors['primary'],
        alignment=TA_LEFT,
        spaceAfter=10,
    ),
    "NormalText": ParagraphStyle(
        name="baseText",
        fontName="Helvetica",
        fontSize=12,
        alignment=TA_LEFT
    ),
    "SignatureText": ParagraphStyle(
        name="SignatureText",
        fontName="Helvetica",
        fontSize=12,
        alignment=TA_LEFT
    )
}
#-----------------------------------------------------------------------------------
def cargar_json():
    global data
    with open('clients.json') as file:
        data = json.load(file)

def draw_titles(c, pre_title_text, title_text, style, pre_title_style, x, y, width):
    preP = Paragraph(pre_title_text, pre_title_style)
    preP.wrap(width, float('inf'))
    pre_height = preP.height
    preP.drawOn(c, x, y)
    p = Paragraph(title_text, style)
    p.wrap(width, float('inf'))
    title_height = p.height
    p.drawOn(c, x, y - pre_height)
    return pre_height + title_height

def draw_body(c, txt, style, x, y, width):
    text = Paragraph(txt, style)
    text.wrap(width, float('inf'))
    text_height = text.height
    text.drawOn(c, x, y - text_height)
    return text_height

def draw_signature(c, company_name, x, y):
    rect_width = 110
    rect_height = 50
    c.setFillColor(colors.lightgrey)
    c.rect(x, y - rect_height, rect_width, rect_height, stroke=1)
    c.setFillColor(colors.black)
    c.drawString(x + 5, y - rect_height + 35 / 2 + 5, "[imatge de la firma]")
    margin = 120
    signature_text = f"""
    Atentament,<br/><br/>
    [{company_name}]<br/><br/>
    Departament d'Atenció al Client
    """
    signature_paragraph = Paragraph(signature_text, styles["SignatureText"])
    signature_paragraph.wrap(200, float('inf'))
    signature_paragraph.drawOn(c, x + rect_width + margin, y - rect_height)

def draw_footer(c, page_number, x_left, x_right):
    c.setFillColor(colors.grey)
    c.drawString(x_left, 30, f"Pàgina {page_number}")
    current_date = "2024/12/8"
    c.drawString(x_right, 30, f"Data: {current_date}")
def draw_calendar(c, client_data, x, y, width):
    current_y = y
    draw_titles(
        c,
        pre_title_text="Factura",
        title_text="CALENDARI",
        style=styles["MainTitle"],
        pre_title_style=styles["PreText"],
        x=x,
        y=current_y,
        width=width
    )
    current_y -= 60

    for month, status in client_data["calendari_pagaments"].items():
        if status == "Regular":
            c.setFillColor(colors.white)
        elif "Bonificacio" in status:
            c.setFillColor(colors.lightblue) #NO DETECTA AQUEST ELIF 
            #CORREGIT, ERA EL ACCENT DE BONIFICACIÓ
        else:
            c.setFillColor(colors.lightgreen)
        c.rect(x, current_y - 20, width, 20, stroke=0, fill=1)
        c.setFillColor(colors.black) 
        c.drawString(x + 5, current_y - 15, f"{month}: {status}")
        current_y -= 30

    return current_y


data = None
cargar_json()

c = canvas.Canvas(filename, pagesize=A4)
page_width, page_height = A4
margin = 50
width = page_width - (2 * margin)
# -----------------------------------------------------------------
txt_template = """
Estimad@ {nom} {cognom},<br/><br/>
Ens dirigim a vostè per presentar-li el detall de la seva factura corresponent al mes de {mes}:<br/><br/>
- Quota bàsica mensual: {quota} €<br/>
- Serveis addicionals: {serveis}<br/>
- Impostos aplicats (IVA): {impostos} €<br/><br/>

Total a pagar: {total} €<br/><br/>

Recordi que pot consultar els detalls de les seves factures i gestionar els seus pagaments a través de l'àrea de clients al nostre lloc web o contactar amb el nostre servei d'atenció al client al {telefon}.<br/><br/>
Gràcies per confiar en nosaltres.<br/><br/>
"""
# ---------------------------------------------------------------------
for entrada in data["clients"]:
    current_y = page_height - margin

    title_height = draw_titles(
        c,
        pre_title_text="Factura",
        title_text=f"[{entrada['companyia']}]",
        style=styles["MainTitle"],
        pre_title_style=styles["PreText"],
        x=margin,
        y=current_y,
        width=width
    )
    current_y -= title_height + 20

    txt = txt_template.format(
        nom=entrada["nom"],
        cognom=entrada["cognom"],
        mes=entrada["mes_factura"],
        quota=entrada["detall_cobraments"]["quota_basica"],
        serveis=" · Internet Extra",
        impostos=entrada["detall_cobraments"]["impostos"],
        total=entrada["detall_cobraments"]["total"],
        telefon="NULL"
    )
    
    body_height = draw_body(c, txt, styles["NormalText"], margin, current_y, width)
    current_y -= body_height + 50

    draw_signature(c, entrada["companyia"], margin, current_y)

    page_number = c.getPageNumber()
    draw_footer(c, page_number, margin, page_width - margin - 200)

    c.showPage()

    current_y = page_height - margin
    draw_calendar(c, entrada, margin, current_y, width)

    page_number = c.getPageNumber()
    draw_footer(c, page_number, margin, page_width - margin - 200)

    c.showPage()

c.save()
