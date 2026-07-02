"""
Scraper de promociones de Banco Provincia / Cuenta DNI.
No requiere Playwright: la página de beneficios es HTML server-rendered.
"""
import re
from dataclasses import asdict, dataclass

import requests
from bs4 import BeautifulSoup

LISTADO_URL = "https://www.bancoprovincia.com.ar/cuentadni/contenidos/cdnibeneficios/"
DETALLE_URL_TPL = "https://www.bancoprovincia.com.ar/cuentadni/contenidos/cdniBeneficios/detalle/{slug}"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
}


@dataclass
class Promo:
    id: str
    banco: str
    titulo: str
    dias: str
    valor: str
    unidad: str  # "%" o "cuotas"
    detalle_url: str


def _slug_from_id(card_id: str) -> str:
    """'especial1317-1008' -> 'especial1317'; 'dia-1005' -> 'dia'."""
    return re.sub(r"-\d+$", "", card_id)


def obtener_promos() -> list[Promo]:
    r = requests.get(LISTADO_URL, headers=HEADERS, timeout=15)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    promos = []
    for card in soup.select(".callModalCDNI"):
        card_id = card.get("id", "")
        titulo = card.select_one(".tituloBeneficio")
        dias = card.select_one(".BEN_CON_dias")
        valor = card.select_one(".BEN_CON_nro")
        unidad = card.select_one(".BEN_CON_porcien")

        if not (card_id and titulo and valor):
            continue

        slug = _slug_from_id(card_id)
        promos.append(
            Promo(
                id=card_id,
                banco="Provincia",
                titulo=titulo.get_text(strip=True),
                dias=dias.get_text(strip=True) if dias else "",
                valor=valor.get_text(strip=True),
                unidad=unidad.get_text(strip=True) if unidad else "cuotas",
                detalle_url=DETALLE_URL_TPL.format(slug=slug),
            )
        )
    return promos


def obtener_detalle(promo: Promo) -> str:
    """Texto legal completo (tope de reintegro, vigencia, condiciones) de una promo."""
    r = requests.get(promo.detalle_url, headers=HEADERS, timeout=15)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    return soup.get_text(separator=" ", strip=True)


if __name__ == "__main__":
    import json

    promos = obtener_promos()
    print(f"{len(promos)} promos encontradas en Cuenta DNI\n")
    for p in promos:
        print(f"- [{p.dias}] {p.titulo} — {p.valor}{p.unidad} ({p.detalle_url})")

    print("\n--- JSON ---")
    print(json.dumps([asdict(p) for p in promos], ensure_ascii=False, indent=2))
