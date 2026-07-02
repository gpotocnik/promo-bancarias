"""
Orquestador: scrapea Galicia/BBVA/Mercado Pago (supermercados/combustible),
dedup y manda mail con tabla día/comercio/descuento/medio de pago. Dos modos:
  --modo semanal -> tabla completa de todas las promos vigentes (lunes AM)
  --modo alerta  -> solo promos nuevas desde la última corrida (diario)
"""
import argparse
from datetime import datetime

from calidad import filtrar_validas
from dedup import cargar_vistos, guardar_vistos, separar_nuevas
from generar_pagina import generar_pagina
from mailer import construir_html, enviar_mail
from unify import obtener_todas_las_promos


def main(modo: str):
    print(f"[{datetime.now()}] corriendo monitor en modo={modo}")

    crudas = obtener_todas_las_promos()
    print(f"  {len(crudas)} promos scrapeadas")

    promos = filtrar_validas(crudas)
    print(f"  {len(promos)} promos válidas tras control de calidad")

    generar_pagina(promos)

    vistos = cargar_vistos()
    nuevas, vistos_actualizado = separar_nuevas(promos, vistos)
    print(f"  {len(nuevas)} promos nuevas desde la última corrida")

    if modo == "semanal":
        a_mostrar = promos
        es_alerta = False
        asunto = f"🛒 Promos supermercados/combustible — semana del {datetime.now().strftime('%d/%m/%Y')}"
    else:
        if not nuevas:
            print("  sin novedades, no se envía mail")
            guardar_vistos(vistos_actualizado)
            return
        a_mostrar = nuevas
        es_alerta = True
        asunto = f"🛒 Nuevas promos supermercados/combustible — {datetime.now().strftime('%d/%m/%Y')}"

    try:
        html = construir_html(a_mostrar, es_alerta=es_alerta)
        enviar_mail(asunto, html)
    except Exception as e:
        print(f"[WARN] no se pudo enviar el mail (¿faltan los secrets de SMTP?): {e}")

    guardar_vistos(vistos_actualizado)
    print("  listo")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--modo", choices=["semanal", "alerta"], default="alerta")
    args = parser.parse_args()
    main(args.modo)
