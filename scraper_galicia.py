"""
Scraper de promociones de Banco Galicia.
No requiere Playwright: beneficios.galicia.ar es un SPA React, pero su BFF
(loyalty.bff.bancogalicia.com.ar) responde JSON público sin auth ni sesión.
"""
from dataclasses import asdict, dataclass

import requests

BFF_BASE = "https://loyalty.bff.bancogalicia.com.ar/api/portal/personalizacion/v1"
AGRUPADOR_DESTACADAS = 10  # agrupador "Destacadas" visto en la home de beneficios.galicia.ar

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Accept": "application/json",
}


@dataclass
class Promo:
    id: int
    banco: str
    titulo: str
    subtitulo: str
    promocion: str
    dias: str
    vigencia_hasta: str
    carrusel: str


def _carruseles() -> list[dict]:
    r = requests.get(
        f"{BFF_BASE}/promociones/list/agrupador/{AGRUPADOR_DESTACADAS}/carruseles",
        headers=HEADERS,
        timeout=15,
    )
    r.raise_for_status()
    return r.json()["data"]["carruseles"]


def _promos_de_carrusel(id_carrusel: int, titulo_carrusel: str, page_size: int = 20) -> list[Promo]:
    r = requests.get(
        f"{BFF_BASE}/promociones/list/carrusel/{id_carrusel}",
        params={"page": 1, "pageSize": page_size, "cardEspecial": "true"},
        headers=HEADERS,
        timeout=15,
    )
    r.raise_for_status()
    items = r.json()["data"]["promociones"]["list"]
    promos = []
    for it in items:
        promos.append(
            Promo(
                id=it["id"],
                banco="Galicia",
                titulo=it.get("titulo") or "",
                subtitulo=it.get("subtitulo") or "",
                promocion=it.get("promocion") or "",
                dias=it.get("leyendaDiasAplicacion") or "",
                vigencia_hasta=it.get("fechaHasta") or "",
                carrusel=titulo_carrusel,
            )
        )
    return promos


def obtener_promos() -> list[Promo]:
    promos = []
    for c in _carruseles():
        promos.extend(_promos_de_carrusel(c["idCarrusel"], c["titulo"]))
    return promos


if __name__ == "__main__":
    import json

    promos = obtener_promos()
    print(f"{len(promos)} promos encontradas en Galicia\n")
    for p in promos:
        print(f"- [{p.carrusel}] {p.titulo} — {p.promocion} (hasta {p.vigencia_hasta})")

    print("\n--- JSON ---")
    print(json.dumps([asdict(p) for p in promos], ensure_ascii=False, indent=2))
