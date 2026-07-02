"""Arma el mail HTML (tabla por día) y lo envía por SMTP, mismo patrón que monitor-parques."""
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from unify import orden_dia

BANCO_COLOR = {
    "Galicia": "#EA580C",
    "BBVA": "#1447E6",
    "Mercado Pago": "#00A3E0",
}


def _pct(descuento: str) -> int:
    digitos = "".join(c for c in descuento.split("%")[0] if c.isdigit())
    return int(digitos) if digitos else 0


def construir_html(promos: list, es_alerta: bool = False) -> str:
    intro = (
        "<p>Promociones nuevas de supermercados/combustible detectadas hoy:</p>"
        if es_alerta
        else "<p>Resumen semanal — dónde conviene comprar según el día y con qué medio de pago:</p>"
    )

    ordenadas = sorted(promos, key=lambda p: (orden_dia(p.dias), -_pct(p.descuento), p.banco))

    filas = []
    dia_anterior = None
    for p in ordenadas:
        if p.dias != dia_anterior:
            filas.append(
                f'<tr><td colspan="4" style="background:#f2f2f2;font-weight:bold;'
                f'padding:8px 6px;border-top:2px solid #ccc;">{p.dias}</td></tr>'
            )
            dia_anterior = p.dias
        color = BANCO_COLOR.get(p.banco, "#666")
        tope = f" (tope {p.tope})" if p.tope else ""
        filas.append(
            "<tr>"
            f'<td style="padding:6px;border-bottom:1px solid #eee;"><b>{p.comercio}</b></td>'
            f'<td style="padding:6px;border-bottom:1px solid #eee;">{p.descuento}{tope}</td>'
            f'<td style="padding:6px;border-bottom:1px solid #eee;">{p.medio_pago}</td>'
            f'<td style="padding:6px;border-bottom:1px solid #eee;color:{color};font-weight:bold;">{p.banco}</td>'
            "</tr>"
        )

    tabla = (
        '<table style="width:100%;border-collapse:collapse;font-size:14px;">'
        "<thead><tr>"
        '<th style="text-align:left;padding:6px;border-bottom:2px solid #333;">Comercio</th>'
        '<th style="text-align:left;padding:6px;border-bottom:2px solid #333;">Descuento</th>'
        '<th style="text-align:left;padding:6px;border-bottom:2px solid #333;">Medio de pago</th>'
        '<th style="text-align:left;padding:6px;border-bottom:2px solid #333;">Banco</th>'
        "</tr></thead><tbody>" + "".join(filas) + "</tbody></table>"
    )

    return f"""
    <html><body style="font-family: sans-serif;">
        <h2>🛒 Promos de supermercados y combustible</h2>
        {intro}
        {tabla}
        <hr>
        <p style="font-size:12px;color:#666;">Generado automáticamente. Verificá vigencia y tope antes de comprar.</p>
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
