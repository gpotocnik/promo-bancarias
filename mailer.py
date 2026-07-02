"""Envío de mail HTML, mismo patrón smtplib que monitor-parques."""
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

BANCOS_ORDEN = ["Provincia", "Galicia", "BBVA", "Mercado Pago"]


def construir_html(resumen: dict, es_alerta: bool = False) -> str:
    intro = (
        "<p>Nuevas promociones detectadas hoy:</p>"
        if es_alerta
        else "<p>Resumen semanal de promociones bancarias:</p>"
    )
    secciones = []
    for banco in BANCOS_ORDEN:
        items = resumen.get(banco, [])
        if not items:
            continue
        filas_html = []
        for i in items:
            partes = [f"<b>{i.get('titulo', '')}</b> — {i.get('resumen', '')}"]
            if i.get("dias"):
                partes.append(f"Días: {i['dias']}")
            if i.get("vigencia"):
                partes.append(f"Vigencia: {i['vigencia']}")
            filas_html.append(f"<li>{' | '.join(partes)}</li>")
        filas = "".join(filas_html)
        secciones.append(f"<h3>{banco}</h3><ul>{filas}</ul>")

    return f"""
    <html><body style="font-family: sans-serif;">
        <h2>🏦 Promos bancarias</h2>
        {intro}
        {''.join(secciones)}
        <hr>
        <p style="font-size:12px;color:#666;">Generado automáticamente.</p>
    </body></html>
    """


def enviar_mail(asunto: str, html: str):
    remitente = os.environ["EMAIL_FROM"]
    destinatario = os.environ["EMAIL_TO"]
    password = os.environ["EMAIL_PASSWORD"]
    smtp_host = os.environ.get("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.environ.get("SMTP_PORT", "587"))

    msg = MIMEMultipart("alternative")
    msg["Subject"] = asunto
    msg["From"] = remitente
    msg["To"] = destinatario
    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP(smtp_host, smtp_port) as s:
        s.starttls()
        s.login(remitente, password)
        s.sendmail(remitente, destinatario, msg.as_string())
    print(f"  ✉️  {asunto}")
