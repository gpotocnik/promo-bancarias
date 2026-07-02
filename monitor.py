"""
Orquestador: scrapea Galicia/BBVA/Mercado Pago, dedup, resume con Claude
y manda mail. Dos modos:
  --modo semanal -> resumen completo de todas las promos vigentes (lunes AM)
  --modo alerta  -> solo promos nuevas desde la última corrida (diario)
"""
import argparse
from datetime import datetime

from dedup import cargar_vistos, guardar_vistos, separar_nuevas
from mailer import construir_html, enviar_mail
from summarizer import resumir_promos
from unify import obtener_todas_las_promos


def main(modo: str):
    print(f"[{datetime.now()}] corriendo monitor en modo={modo}")

    promos = obtener_todas_las_promos()
    print(f"  {len(promos)} promos scrapeadas")

    vistos = cargar_vistos()
    nuevas, vistos_actualizado = separar_nuevas(promos, vistos)
    print(f"  {len(nuevas)} promos nuevas desde la última corrida")

    if modo == "semanal":
        a_resumir = promos
        es_alerta = False
        asunto = f"🏦 Promos bancarias — semana del {datetime.now().strftime('%d/%m/%Y')}"
    else:
        if not nuevas:
            print("  sin novedades, no se envía mail")
            guardar_vistos(vistos_actualizado)
            return
        a_resumir = nuevas
        es_alerta = True
        asunto = f"🏦 Nuevas promos bancarias — {datetime.now().strftime('%d/%m/%Y')}"

    resumen = resumir_promos(a_resumir)
    html = construir_html(resumen, es_alerta=es_alerta)
    enviar_mail(asunto, html)

    guardar_vistos(vistos_actualizado)
    print("  listo")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--modo", choices=["semanal", "alerta"], default="alerta")
    args = parser.parse_args()
    main(args.modo)
