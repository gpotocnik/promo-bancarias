"""
Scraper de promociones de supermercados de Banco Galicia.
No requiere Playwright: su BFF público expone un catálogo filtrable por categoría
con día de aplicación y medios de pago (loyalty.bff.bancogalicia.com.ar).

Nota: se relevaron las 14 categorías/subcategorías del banco (1343 promos totales,
2026-07-02) y ninguna corresponde a combustible/estaciones de servicio — Galicia
no ofrece ese tipo de promo actualmente. Si en el futuro agregan una categoría de
combustible, sumarla a CATEGORIAS.
"""
from dataclasses import asdict, dataclass

import requests

CATALOGO_URL = "https://loyalty.bff.bancogalicia.com.ar/api/portal/personalizacion/v1/promociones/catalogo"
CATEGORIAS = {8: "Supermercados"}  # id de categoría -> nombre; ver docstring
IMG_BASE = "https://www.galicia.ar/content/dam/galicia/banco-galicia/personas/promociones/catalogo-de-beneficios/"
DETALLE_URL_TPL = "https://beneficios.galicia.ar/promotions-catalog-filter/idcategoria={id_categoria}"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Accept": "application/json",
}


@dataclass
class Promo:
    id: int
    banco: str
    categoria: str
    comercio: str
    dias: str
    descuento: str
    medio_pago: str
    vigencia_hasta: str
    logo_url: str
    detalle_url: str


def _medios_de_pago(item: dict) -> str:
    tarjetas = [m["tarjeta"] for m in item.get("mediosDePago", [])]
    if item.get("pagoQR"):
        tarjetas.append("QR")
    return ", ".join(tarjetas) if tarjetas else ""


def _promos_de_categoria(id_categoria: int, nombre_categoria: str, page_size: int = 20) -> list[Promo]:
    promos = []
    page = 1
    while True:
        r = requests.get(
            CATALOGO_URL,
            params={"page": page, "pageSize": page_size, "IdCategoria": id_categoria},
            headers=HEADERS,
            timeout=15,
        )
        r.raise_for_status()
        items = r.json()["data"]["list"]
        if not items:
            break
        for it in items:
            imagen = it.get("imagen") or ""
            promos.append(
                Promo(
                    id=it["id"],
                    banco="Galicia",
                    categoria=nombre_categoria,
                    comercio=it.get("titulo") or "",
                    dias=it.get("leyendaDiasAplicacion") or "",
                    descuento=it.get("promocion") or "",
                    medio_pago=_medios_de_pago(it),
                    vigencia_hasta=(it.get("fechaHasta") or "")[:10],
                    logo_url=f"{IMG_BASE}{imagen}" if imagen else "",
                    detalle_url=DETALLE_URL_TPL.format(id_categoria=id_categoria),
                )
            )
        if len(items) < page_size:
            break
        page += 1
    return promos


def obtener_promos() -> list[Promo]:
    promos = []
    for id_cat, nombre in CATEGORIAS.items():
        promos.extend(_promos_de_categoria(id_cat, nombre))
    return promos


if __name__ == "__main__":
    import json

    promos = obtener_promos()
    print(f"{len(promos)} promos encontradas en Galicia\n")
    for p in promos[:15]:
        print(f"- [{p.dias}] {p.comercio} — {p.descuento} | {p.medio_pago}")

    print("\n--- JSON ---")
    print(json.dumps([asdict(p) for p in promos], ensure_ascii=False, indent=2))
