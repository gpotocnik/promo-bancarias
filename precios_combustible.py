"""
Precio promedio de combustible por marca, usando el dataset oficial y en vivo de la
Secretaría de Energía (Resolución 314/2016) — actualizado por las propias estaciones
de servicio dentro de las 8hs de cualquier cambio de precio.
"""
import csv
import io

import requests

CSV_URL = (
    "http://datos.energia.gob.ar/dataset/1c181390-5045-475e-94dc-410429be4b17/"
    "resource/80ac25de-a44a-4445-9215-090cf55cfda5/download/precios-en-surtidor-resolucin-3142016.csv"
)

PRODUCTO_DEFAULT = "Nafta (súper) entre 92 y 95 Ron"

MARCA_NORMALIZADA = {
    "YPF": "YPF",
    "SHELL C.A.P.S.A.": "Shell",
    "AXION": "Axion",
    "PUMA": "Puma",
}


def obtener_precios_promedio(producto: str = PRODUCTO_DEFAULT) -> dict:
    """Devuelve {marca: precio_promedio} para el producto pedido, a nivel nacional."""
    r = requests.get(CSV_URL, timeout=30)
    r.raise_for_status()

    sumas = {}
    conteos = {}
    reader = csv.DictReader(io.StringIO(r.content.decode("utf-8-sig")))
    for row in reader:
        if row.get("producto") != producto:
            continue
        marca_cruda = row.get("empresabandera", "")
        marca = MARCA_NORMALIZADA.get(marca_cruda)
        if not marca:
            continue
        try:
            precio = float(row["precio"])
        except (ValueError, TypeError):
            continue
        sumas[marca] = sumas.get(marca, 0) + precio
        conteos[marca] = conteos.get(marca, 0) + 1

    return {marca: sumas[marca] / conteos[marca] for marca in sumas}


if __name__ == "__main__":
    precios = obtener_precios_promedio()
    for marca, precio in sorted(precios.items(), key=lambda x: x[1]):
        print(f"{marca}: ${precio:.2f}/litro (promedio nacional)")
