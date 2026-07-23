"""
Scraper de promociones de supermercado de American Express Argentina (The Platinum Card).
No requiere Playwright: la página de promociones es HTML server-rendered.

Fuente: página oficial de promociones de Amex, sección "Marcas adheridas" del
especial de supermercados (Cencosud: Jumbo y Disco). No se encontró fecha de
vigencia explícita — parece un beneficio permanente del programa, no mensual
como las promos bancarias.
"""
from dataclasses import asdict, dataclass

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.americanexpress.com/es-ar/beneficios/promociones/"
URL_ESPECIAL_SUPERMERCADOS = BASE_URL + "promo/especial-cencosud/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
}


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


def obtener_promos() -> list[Promo]:
    r = requests.get(URL_ESPECIAL_SUPERMERCADOS, headers=HEADERS, timeout=15)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    promos = []
    for tarjeta in soup.select(".recduadrobenf"):
        img = tarjeta.select_one("img[alt]")
        if not img:
            continue
        comercio = img["alt"].strip()

        titulos = tarjeta.select("h3")
        dias = titulos[1].get_text(strip=True) if len(titulos) > 1 else ""

        desc = tarjeta.select_one("p")
        descripcion = desc.get_text(strip=True) if desc else ""

        promos.append(
            Promo(
                id=f"amex-supermercados-{comercio.lower()}",
                banco="American Express",
                categoria="Supermercados",
                comercio=comercio,
                dias="Jueves" if "jueves" in dias.lower() else dias,
                descuento="25% de reintegro",  # $100.000 / $400.000 de consumo mínimo
                medio_pago="The Platinum Card (titular o adicional), presencial u online, consumo mínimo $400.000/mes",
                tope="$100.000/mes",
                vigencia_hasta="",
                logo_url=BASE_URL + img["src"] if img.get("src") else "",
                detalle_url=URL_ESPECIAL_SUPERMERCADOS,
            )
        )
    return promos


if __name__ == "__main__":
    import json

    promos = obtener_promos()
    print(f"{len(promos)} promos encontradas en American Express\n")
    for p in promos:
        print(f"- [{p.dias}] {p.comercio} — {p.descuento} | {p.tope} | {p.medio_pago}")

    print("\n--- JSON ---")
    print(json.dumps([asdict(p) for p in promos], ensure_ascii=False, indent=2))
