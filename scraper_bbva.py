"""
Scraper de promociones de supermercados de BBVA Argentina.
No requiere Playwright: su API pública expone la campaña "Supermercados" (id 2474)
y, por promo, un detalle (communication/{id}) con día, tope y compra mínima.

El listado de la campaña NO trae los días ni la compra mínima (diasPromo viene null
siempre) — eso está solo en el detalle, en beneficios[0].requisitos, por ejemplo:
"En compras mayores a $100.000 con QR MODO. / Viernes y sábados." Antes se asumía que
diasPromo=null significaba "todos los días", y era falso.

Nota: BBVA no tiene promos de combustible propias en su catálogo de campañas.
"""
import re
from dataclasses import asdict, dataclass

import requests

from dias import dias_en

BASE = "https://go.bbva.com.ar/willgo/fgo/API/v3"
CAMPAIGN_URL = BASE + "/campaign/{id_campania}"
COMUNICACION_URL = BASE + "/communication/{id}"
CAMPANIAS = {"2474": "Supermercados"}  # id de campaña -> categoría
DETALLE_URL_TPL = "https://www.bbva.com.ar/beneficios/campania.html?id={id_campania}"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Accept": "application/json",
}

DIA_NO_INFORMADO = "Día no informado (ver bases)"


@dataclass
class Promo:
    id: str
    banco: str
    categoria: str
    comercio: str
    dias: str
    descuento: str
    medio_pago: str
    tope: str
    vigencia_hasta: str
    logo_url: str
    detalle_url: str


def _limpiar_comercio(cabecera: str) -> str:
    """'Jumbo QR Modo 20%' / 'Supermercados Dia Beneficio exclusivo MODO' -> 'Jumbo' / 'Supermercados Dia'."""
    c = re.sub(r"\s*Beneficio exclusivo MODO", "", cabecera, flags=re.I)
    c = re.sub(r"\s*QR\s*Modo(\s*\d+\s*%?)?", "", c, flags=re.I)
    return c.strip()


def _porcentaje(item: dict, detalle: dict) -> str:
    for texto in (item.get("cabecera"), item.get("subcabecera"), detalle.get("cabecera")):
        m = re.search(r"(\d+)\s*%", texto or "")
        if m:
            return m.group(1)
    m = re.search(r"consta\s+de\s+(\d+)\s*%", detalle.get("basesCondiciones") or "", re.I)
    return m.group(1) if m else ""


def _tope(beneficio: dict, monto_listado) -> str:
    tope = beneficio.get("tope") or monto_listado
    if not tope:
        return "sin tope" if beneficio.get("tipoTope") == "ninguno" else ""
    texto = f"${int(tope):,}".replace(",", ".")
    frecuencia = (beneficio.get("frecuenciaTope") or "").strip().lower()
    if frecuencia == "por mes":
        return texto + "/mensual"
    return texto + (f"/{frecuencia.replace('por ', '')}" if frecuencia else "")


def _detalle(id_promo: str) -> dict:
    try:
        r = requests.get(COMUNICACION_URL.format(id=id_promo), headers=HEADERS, timeout=15)
        r.raise_for_status()
        return r.json().get("data") or {}
    except Exception:
        return {}


def _items_de_campania(id_campania: str) -> list[dict]:
    """El parámetro `pager` no pagina realmente: hay que leer el total de páginas del mensaje."""
    items, vistos = [], set()
    pager = 0
    while True:
        r = requests.get(CAMPAIGN_URL.format(id_campania=id_campania), params={"pager": pager}, headers=HEADERS, timeout=15)
        r.raise_for_status()
        cuerpo = r.json()
        for it in cuerpo.get("data", []):
            if it["id"] not in vistos:
                vistos.add(it["id"])
                items.append(it)
        m = re.search(r"paginas:\s*(\d+)", cuerpo.get("message", ""))
        total_paginas = int(m.group(1)) if m else 1
        pager += 1
        if pager >= total_paginas or pager > 20:
            return items


def _promos_de_campania(id_campania: str, nombre_categoria: str) -> list[Promo]:
    promos = []
    for it in _items_de_campania(id_campania):
        detalle = _detalle(it["id"])
        beneficio = (detalle.get("beneficios") or [{}])[0]
        requisitos = " / ".join(beneficio.get("requisitos") or [])

        pct = _porcentaje(it, detalle)
        if not pct:
            continue  # sin porcentaje publicado todavía (placeholder)

        tipo = "descuento en punto de venta" if "punto de venta" in requisitos.lower() else "reintegro"
        minimo = re.search(r"mayores a\s*\$\s*([\d.]+)", requisitos, re.I)
        medio_pago = "QR MODO desde la app BBVA" + (f", compra mínima ${minimo.group(1)}" if minimo else "")

        promos.append(
            Promo(
                id=it["id"],
                banco="BBVA",
                categoria=nombre_categoria,
                comercio=_limpiar_comercio(it.get("cabecera", "")),
                dias=dias_en(requisitos) or DIA_NO_INFORMADO,
                descuento=f"{pct}% de {tipo}",
                medio_pago=medio_pago,
                tope=_tope(beneficio, it.get("montoTope")),
                vigencia_hasta=it.get("fechaHasta") or "",
                logo_url=it.get("imagen") or "",
                detalle_url=DETALLE_URL_TPL.format(id_campania=id_campania),
            )
        )
    return promos


def obtener_promos() -> list[Promo]:
    promos = []
    for id_campania, categoria in CAMPANIAS.items():
        promos.extend(_promos_de_campania(id_campania, categoria))
    return promos


if __name__ == "__main__":
    import json

    promos = obtener_promos()
    print(f"{len(promos)} promos encontradas en BBVA\n")
    for p in promos:
        print(f"- [{p.dias}] {p.comercio} — {p.descuento} | {p.medio_pago} | tope {p.tope or 'sin dato'} | hasta {p.vigencia_hasta}")

    print("\n--- JSON ---")
    print(json.dumps([asdict(p) for p in promos], ensure_ascii=False, indent=2))
