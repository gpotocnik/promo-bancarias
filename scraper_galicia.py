"""
Scraper de promociones de supermercados de Banco Galicia.
No requiere Playwright: su BFF público expone un catálogo filtrable por categoría
con día de aplicación y medios de pago (loyalty.bff.bancogalicia.com.ar).

El listado (catalogo) NO trae tope de reintegro ni especifica si el pago tiene que
ser vía MODO — eso solo está en el endpoint de detalle por promo
(catalogo/v1/promociones/idPromocion/{id}), que se consulta una vez por promo.

Nota: se relevaron las 14 categorías/subcategorías del banco (1343 promos totales,
2026-07-02) y ninguna corresponde a combustible/estaciones de servicio — Galicia
no ofrece ese tipo de promo actualmente. Si en el futuro agregan una categoría de
combustible, sumarla a CATEGORIAS.
"""
from dataclasses import asdict, dataclass

import requests

CATALOGO_URL = "https://loyalty.bff.bancogalicia.com.ar/api/portal/personalizacion/v1/promociones/catalogo"
DETALLE_PROMO_URL = "https://loyalty.bff.bancogalicia.com.ar/api/portal/catalogo/v1/promociones/idPromocion/{id}"
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
    tope: str
    vigencia_hasta: str
    logo_url: str
    detalle_url: str


def _medios_de_pago_catalogo(item: dict) -> str:
    """Fallback si no se pudo traer el detalle: lista de tarjetas + QR genérico."""
    tarjetas = [m["tarjeta"] for m in item.get("mediosDePago", [])]
    if item.get("pagoQR"):
        tarjetas.append("QR")
    return ", ".join(tarjetas) if tarjetas else ""


def _fetch_detalle(id_promocion: int) -> dict:
    r = requests.get(DETALLE_PROMO_URL.format(id=id_promocion), headers=HEADERS, timeout=15)
    if r.status_code != 200:
        return {}
    return r.json().get("data") or {}


def _tope_legible(detalle: dict) -> str:
    tope = detalle.get("topeReintegro")
    if not tope:
        return ""
    periodicidad = (detalle.get("periodicidad") or "").lower()
    return f"${tope:,.0f}".replace(",", ".") + (f"/{periodicidad}" if periodicidad else "")


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

            try:
                detalle = _fetch_detalle(it["id"])
            except Exception:
                detalle = {}

            medio_pago = detalle.get("leyendaPaga") or _medios_de_pago_catalogo(it)
            tope = _tope_legible(detalle)

            promos.append(
                Promo(
                    id=it["id"],
                    banco="Galicia",
                    categoria=nombre_categoria,
                    comercio=it.get("titulo") or "",
                    dias=it.get("leyendaDiasAplicacion") or "",
                    descuento=it.get("promocion") or "",
                    medio_pago=medio_pago,
                    tope=tope,
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
        print(f"- [{p.dias}] {p.comercio} — {p.descuento} | {p.medio_pago} | tope {p.tope or 'sin dato'}")

    print("\n--- JSON ---")
    print(json.dumps([asdict(p) for p in promos], ensure_ascii=False, indent=2))
