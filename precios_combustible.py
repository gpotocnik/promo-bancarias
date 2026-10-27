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
from __future__ import annotations

import csv
import io
import json
import time
from datetime import date
from pathlib import Path

import requests

CSV_URL = (
    "https://datos.energia.gob.ar/dataset/1c181390-5045-475e-94dc-410429be4b17/"
    "resource/80ac25de-a44a-4445-9215-090cf55cfda5/download/precios-en-surtidor-resolucin-3142016.csv"
)

# Espejo del mismo portal gubernamental (dominio anterior del ministerio).
CSV_URLS = [CSV_URL, CSV_URL.replace("datos.energia.gob.ar", "datos.minem.gob.ar")]

# El servidor oficial corta las conexiones desde las IPs de los runners de GitHub
# (connect timeout, en HTTP y HTTPS). Cuando la descarga en vivo falla se usa esta foto
# fechada, que se regenera sola cada vez que el script corre en una máquina con acceso.
SNAPSHOT_PATH = Path(__file__).with_name("precios_combustible_snapshot.json")

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


def _descargar_csv(intentos_por_url: int = 2):
    ultimo_error = None
    for url in CSV_URLS:
        for i in range(intentos_por_url):
            try:
                r = requests.get(url, timeout=(10, 90))
                r.raise_for_status()
                return r
            except requests.RequestException as e:
                ultimo_error = e
                time.sleep(2 * (i + 1))
    raise ultimo_error


def _en_zona(row: dict) -> bool:
    if row.get("provincia") == "CAPITAL FEDERAL":
        return True
    if row.get("provincia") == "BUENOS AIRES" and row.get("localidad") in LOCALIDADES_GBA_NORTE:
        return True
    return False


def _promedios(contenido: bytes, producto: str) -> dict:

    sumas = {}
    conteos = {}
    reader = csv.DictReader(io.StringIO(contenido.decode("utf-8-sig")))
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


def obtener_precios_con_origen(producto: str = PRODUCTO_DEFAULT) -> tuple[dict, str | None]:
    """Devuelve (precios, fecha_de_la_foto). fecha_de_la_foto es None si son datos en vivo;
    si la fuente oficial no responde, se usa la última foto guardada y se informa su fecha."""
    try:
        precios = _promedios(_descargar_csv().content, producto)
        if precios:
            SNAPSHOT_PATH.write_text(
                json.dumps({"fecha": date.today().isoformat(), "producto": producto, "precios": precios},
                           ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            return precios, None
    except Exception as e:
        print(f"[WARN] fuente oficial de combustible no responde ({type(e).__name__}); se usa la última foto guardada")
    if SNAPSHOT_PATH.exists():
        foto = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))
        if foto.get("producto") == producto and foto.get("precios"):
            d = date.fromisoformat(foto["fecha"])
            return foto["precios"], d.strftime("%d/%m/%Y")
    raise RuntimeError("sin precios de combustible: la fuente oficial no responde y no hay foto guardada")


def obtener_precios_promedio(producto: str = PRODUCTO_DEFAULT) -> dict:
    """Devuelve {marca: precio_promedio} para el producto pedido, en CABA + GBA Norte."""
    return obtener_precios_con_origen(producto)[0]


if __name__ == "__main__":
    precios = obtener_precios_promedio()
    for marca, precio in sorted(precios.items(), key=lambda x: x[1]):
        print(f"{marca}: ${precio:.2f}/litro (CABA + GBA Norte)")
