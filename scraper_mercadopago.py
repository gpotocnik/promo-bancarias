"""
Scraper de promociones de supermercados de Mercado Pago.

Mercado Pago NO publica el detalle día-por-día de sus descuentos QR en un sitio
web público (confirmado en su propia ayuda: "el detalle de cada beneficio se
encuentra disponible dentro de la aplicación"). promociones.mercadopago.com.ar
solo tiene campañas de marcas (Mercado Libre, Farmacity, etc.), no el calendario
de supermercados.

Por eso esta fuente usa un fallback editorial: calcularsueldo.com.ar publica una
guía mensual "Supermercados con Mercado Pago" con día/comercio/%/medio de pago,
generada a partir del JSON-LD (articleBody) del artículo, sin necesidad de parsear
el HTML de marketing. Limitación conocida: el artículo del mes se publica con
algunos días de rezago (ej: el de julio puede no estar disponible el 1-2 de julio),
en cuyo caso se usa el más reciente disponible.

No se encontró actualmente un artículo equivalente para combustible/estaciones de
servicio de Mercado Pago en este sitio — si aparece, ARTICULO_COMBUSTIBLE_PATRON
ya está preparado para tomarlo.
"""
from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass

import requests
from bs4 import BeautifulSoup

TAG_ARCHIVO_URL = "https://calcularsueldo.com.ar/tag/mercado-pago/"
ARTICULO_SUPERMERCADOS_PATRON = re.compile(r"supermercados-con-mercado-pago", re.I)
ARTICULO_COMBUSTIBLE_PATRON = re.compile(r"(nafta|combustible)-.*mercado-pago|mercado-pago.*(nafta|combustible)", re.I)

DIAS_VALIDOS = {
    "Lunes", "Martes", "Miércoles", "Jueves", "Viernes",
    "Sábado", "Domingo", "Sábados", "Domingos",
    "Sábados y Domingos", "Fines de semana", "Todos los días",
}

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
    fuente: str


def _link_mas_reciente(patron: re.Pattern) -> str | None:
    r = requests.get(TAG_ARCHIVO_URL, headers=HEADERS, timeout=15)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    candidatos = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "/finanzas/" in href and patron.search(href):
            m = re.search(r"/finanzas/(\d+)/", href)
            if m:
                candidatos.append((int(m.group(1)), href))
    if not candidatos:
        return None
    candidatos.sort(reverse=True)
    return candidatos[0][1]


def _articulo_body(url: str) -> str:
    r = requests.get(url, headers=HEADERS, timeout=15)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    script = soup.find("script", class_="gnpub-schema-markup-output")
    data = json.loads(script.string)
    return data["articleBody"]


def _parsear_dia_por_dia(body: str, categoria: str, fuente: str) -> list[Promo]:
    bloques = [b.strip() for b in re.split(r"\n{2,}", body) if b.strip()]
    dia_actual = None
    promos = []
    for b in bloques:
        if b in DIAS_VALIDOS:
            dia_actual = b
            continue
        if dia_actual is None:
            continue
        m = re.match(r"^([^:]+):\s*(\d+%\s*de descuento)\s*(.*?)\.", b, re.S)
        if not m:
            continue
        comercio, descuento, condicion = m.group(1).strip(), m.group(2).strip(), m.group(3).strip()
        promos.append(
            Promo(
                id=f"{comercio}:{dia_actual}:{descuento}",
                banco="Mercado Pago",
                categoria=categoria,
                comercio=comercio,
                dias=dia_actual,
                descuento=descuento,
                medio_pago=condicion,
                fuente=fuente,
            )
        )
    return promos


def obtener_promos() -> list[Promo]:
    promos = []

    url_super = _link_mas_reciente(ARTICULO_SUPERMERCADOS_PATRON)
    if url_super:
        body = _articulo_body(url_super)
        promos.extend(_parsear_dia_por_dia(body, "Supermercados", url_super))
    else:
        print("[WARN] no se encontró artículo de supermercados de Mercado Pago")

    url_combustible = _link_mas_reciente(ARTICULO_COMBUSTIBLE_PATRON)
    if url_combustible:
        body = _articulo_body(url_combustible)
        promos.extend(_parsear_dia_por_dia(body, "Combustible", url_combustible))

    return promos


if __name__ == "__main__":
    promos = obtener_promos()
    print(f"{len(promos)} promos encontradas en Mercado Pago\n")
    for p in promos:
        print(f"- [{p.dias}] {p.comercio} — {p.descuento} | {p.medio_pago}")

    print("\n--- JSON ---")
    print(json.dumps([asdict(p) for p in promos], ensure_ascii=False, indent=2))
