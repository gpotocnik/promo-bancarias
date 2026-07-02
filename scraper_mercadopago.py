"""
Scraper de promociones de Mercado Pago.
No requiere Playwright: promociones.mercadopago.com.ar es un sitio WordPress
estático (plugin Kiyo), todo el contenido está en el HTML server-rendered.
"""
from dataclasses import asdict, dataclass

import requests
from bs4 import BeautifulSoup

LISTADO_URL = "https://promociones.mercadopago.com.ar/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
}


@dataclass
class Promo:
    id: str
    banco: str
    marca: str
    badges: str
    descripcion: str
    vigencia: str
    link: str


def obtener_promos() -> list[Promo]:
    r = requests.get(LISTADO_URL, headers=HEADERS, timeout=15)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    promos = []
    for col in soup.select(".kiyo__cards--col"):
        modal = col.select_one(".kiyo__data--modal")
        if not modal:
            continue
        instance = col.select_one("[data-instance]")
        marca = modal.select_one(".kiyo__data--details-logo h3")
        badges = [b.get_text(strip=True) for b in modal.select(".kiyo__cards--badge span")]
        descripcion = modal.select_one(".kiyo__data--details-row1 p")
        vigencia = modal.select_one(".kiyo__data--details-row2 small")
        link = modal.select_one(".kiyo__data--details-btn a")

        if not marca:
            continue

        promos.append(
            Promo(
                id=instance.get("data-instance", "") if instance else "",
                banco="Mercado Pago",
                marca=marca.get_text(strip=True),
                badges=" | ".join(badges),
                descripcion=descripcion.get_text(strip=True) if descripcion else "",
                vigencia=vigencia.get_text(strip=True) if vigencia else "",
                link=link.get("href", "") if link else "",
            )
        )
    return promos


if __name__ == "__main__":
    import json

    promos = obtener_promos()
    print(f"{len(promos)} promos encontradas en Mercado Pago\n")
    for p in promos:
        print(f"- {p.marca} — {p.badges} ({p.vigencia})")

    print("\n--- JSON ---")
    print(json.dumps([asdict(p) for p in promos], ensure_ascii=False, indent=2))
