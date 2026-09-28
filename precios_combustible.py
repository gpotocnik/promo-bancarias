"""
Precio promedio de combustible por marca, usando el dataset oficial y en vivo de la
Secretaría de Energía (Resolución 314/2016) — actualizado por las propias estaciones
de servicio dentro de las 8hs de cualquier cambio de precio.

Filtra por zona: CABA + GBA Norte (no toda la provincia de Buenos Aires, que es enorme
e incluye zonas tan lejanas como La Plata o Mar del Plata — la zona real del usuario es
Florida, Vicente López). CABA se identifica por provincia="CAPITAL FEDERAL"; GBA Norte
no es una provincia aparte, así que se filtra por localidad dentro de provincia="BUENOS
AIRES", usando los nombres de localidad tal como aparecen en el propio dataset.
"""
import csv
import io

import requests

CSV_URL = (
    "http://datos.energia.gob.ar/dataset/1c181390-5045-475e-94dc-410429be4b17/"
    "resource/80ac25de-a44a-4445-9215-090cf55cfda5/download/precios-en-surtidor-resolucin-3142016.csv"
)

PRODUCTO_DEFAULT = "Nafta (súper) entre 92 y 95 Ron"

# Localidades de GBA Norte (Vicente López, San Isidro, San Fernando, Tigre, San Martín,
# San Miguel, Malvinas Argentinas, José C. Paz, Escobar, Pilar), nombres tal como figuran
# en la columna "localidad" del dataset de la Secretaría de Energía.
LOCALIDADES_GBA_NORTE = {
    "VICENTE LOPEZ", "OLIVOS", "MARTINEZ", "FLORIDA", "MUNRO", "BECCAR", "VILLA ADELINA", "ACASSUSO",
    "SAN ISIDRO",
    "SAN FERNANDO",
    "TIGRE", "DON TORCUATO", "BENAVIDEZ", "EL TALAR DE PACHECO", "GRAL. PACHECO",
    "SAN MARTIN", "VILLA MAIPU", "JOSE LEON SUAREZ", "CASEROS",
    "SAN MIGUEL", "JOSE C. PAZ", "MALVINAS ARGENTINAS", "GRAND BOURG", "VILLA DE MAYO", "BELLA VISTA",
    "ESCOBAR", "GARIN", "DEL VISO", "DERQUI", "ING. MASCHWITZ",
    "PILAR",
}


MARCA_NORMALIZADA = {
    "YPF": "YPF",
    "SHELL C.A.P.S.A.": "Shell",
    "AXION": "Axion",
    "PUMA": "Puma",
}


def _en_zona(row: dict) -> bool:
    if row.get("provincia") == "CAPITAL FEDERAL":
        return True
    if row.get("provincia") == "BUENOS AIRES" and row.get("localidad") in LOCALIDADES_GBA_NORTE:
        return True
    return False


def obtener_precios_promedio(producto: str = PRODUCTO_DEFAULT) -> dict:
    """Devuelve {marca: precio_promedio} para el producto pedido, en CABA + GBA Norte."""
    r = requests.get(CSV_URL, timeout=30)
    r.raise_for_status()

    sumas = {}
    conteos = {}
    reader = csv.DictReader(io.StringIO(r.content.decode("utf-8-sig")))
    for row in reader:
        if row.get("producto") != producto:
            continue
        if not _en_zona(row):
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
        print(f"{marca}: ${precio:.2f}/litro (CABA + GBA Norte)")
