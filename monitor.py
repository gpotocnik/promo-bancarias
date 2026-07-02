"""
Orquestador: scrapea Galicia/BBVA/Mercado Pago (supermercados/combustible),
filtra por calidad, calcula qué es nuevo desde la última corrida (para destacar
en la página) y genera docs/index.html.
"""
from datetime import datetime

from calidad import filtrar_validas
from dedup import cargar_vistos, guardar_vistos, separar_nuevas
from generar_pagina import generar_pagina
from precios_combustible import obtener_precios_promedio
from unify import obtener_todas_las_promos


def main():
    print(f"[{datetime.now()}] corriendo monitor")

    crudas = obtener_todas_las_promos()
    print(f"  {len(crudas)} promos scrapeadas")

    promos = filtrar_validas(crudas)
    print(f"  {len(promos)} promos válidas tras control de calidad")

    vistos = cargar_vistos()
    nuevas, vistos_actualizado = separar_nuevas(promos, vistos)
    print(f"  {len(nuevas)} promos nuevas desde la última corrida")

    try:
        precios_combustible = obtener_precios_promedio()
    except Exception as e:
        print(f"[WARN] no se pudieron obtener precios de combustible: {e}")
        precios_combustible = {}

    generar_pagina(promos, nuevas, precios_combustible)
    guardar_vistos(vistos_actualizado)
    print("  listo")


if __name__ == "__main__":
    main()
