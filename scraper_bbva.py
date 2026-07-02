"""
Scraper de promociones de BBVA Argentina.
No requiere Playwright: bbva.com.ar/beneficios/ es un shell JS, pero su API
(go.bbva.com.ar/willgo/fgo/API) responde JSON público sin auth ni sesión.
"""
from dataclasses import asdict, dataclass

import requests

API_COMMUNICATIONS = "https://go.bbva.com.ar/willgo/fgo/API/v3/communications"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Accept": "application/json",
}


@dataclass
class Promo:
    id: str
    banco: str
    titulo: str
    descripcion: str
    fecha_desde: str
    fecha_hasta: str
    monto_tope: str
    grupo_tarjeta: str


def obtener_promos() -> list[Promo]:
    r = requests.get(
        API_COMMUNICATIONS,
        params={"destacado": "true", "pager": 0},
        headers=HEADERS,
        timeout=15,
    )
    r.raise_for_status()
    items = r.json().get("data", [])
    return [
        Promo(
            id=it["id"],
            banco="BBVA",
            titulo=it.get("cabecera") or "",
            descripcion=it.get("subcabecera") or "",
            fecha_desde=it.get("fechaDesde") or "",
            fecha_hasta=it.get("fechaHasta") or "",
            monto_tope=str(it.get("montoTope") or ""),
            grupo_tarjeta=it.get("grupoTarjeta") or "",
        )
        for it in items
    ]


if __name__ == "__main__":
    import json

    promos = obtener_promos()
    print(f"{len(promos)} promos encontradas en BBVA\n")
    for p in promos:
        print(f"- {p.titulo} — {p.descripcion} ({p.fecha_desde} a {p.fecha_hasta})")

    print("\n--- JSON ---")
    print(json.dumps([asdict(p) for p in promos], ensure_ascii=False, indent=2))
