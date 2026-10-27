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

from dias import dias_en as _dias_en

TAG_ARCHIVO_URL = "https://calcularsueldo.com.ar/tag/mercado-pago/"
# Los títulos cambian mes a mes ("supermercados-con-mercado-pago-en-junio", "supermercados-los-descuentos-de-
# mercado-pago-para-agosto", "supermercados-todos-los-descuentos-dia-por-dia-con-mercado-pago-en-septiembre"...)
ARTICULO_SUPERMERCADOS_PATRON = re.compile(r"supermercados.*mercado-pago|mercado-pago.*supermercados", re.I)
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
    tope: str = ""


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


MESES = "enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre"
def _mes_de_url(url: str) -> str:
    m = re.search(rf"({MESES})-(\d{{4}})", url)
    return f"{m.group(1)} {m.group(2)}" if m else ""


def _parsear_dia_por_dia(body: str, categoria: str, fuente: str) -> list[Promo]:
    """Cubre las dos formas que usa la guía: grandes cadenas con el día en la frase
    ("COTO: 25% de descuento los viernes, y 20% los sábados y domingos") y listas por
    encabezado de día ("Lunes" / "Supermercado La Reina: 15% de descuento")."""
    mes = _mes_de_url(fuente)
    origen = f"guía de {mes}" if mes else "guía editorial"
    bloques = [b.strip() for b in re.split(r"\n{2,}", body) if b.strip()]
    dia_actual = None
    promos = []
    for b in bloques:
        if b in DIAS_VALIDOS or b.startswith("Todos los días"):
            dia_actual = "Todos los días" if b.startswith("Todos los días") else (_dias_en(b) or b)
            continue
        m = re.match(r"^([^:]{1,60}):\s*(.+)$", b, re.S)
        if not m:
            continue
        comercio, resto = m.group(1).strip(), m.group(2).strip()
        coincidencias = list(re.finditer(r"(\d+)%\s*de descuento", resto))
        for i, c in enumerate(coincidencias):
            fin_trozo = coincidencias[i + 1].start() if i + 1 < len(coincidencias) else len(resto)
            trozo = resto[c.end():fin_trozo]
            dias = _dias_en(re.sub(r"\([^)]*\)", "", trozo)) or dia_actual
            if not dias:
                continue
            nota = re.search(r"\(([^)]*)\)", trozo)
            nota = nota.group(1).strip() if nota else ""
            descuento = f"{c.group(1)}% de descuento"
            promos.append(
                Promo(
                    id=f"{comercio}:{dias}:{descuento}",
                    banco="Mercado Pago",
                    categoria=categoria,
                    comercio=comercio,
                    dias=dias,
                    descuento=descuento,
                    medio_pago=f"Pagando con Mercado Pago ({origen})" + (f" · {nota}" if nota else ""),
                    fuente=fuente,
                    tope="sin tope" if "sin tope" in nota.lower() else "",
                )
            )
    return promos


def _parsear_combustible_prosa(body: str, fuente: str) -> list[Promo]:
    """Nota mensual en prosa: "Todos los lunes ... 10% de descuento ... App YPF ... hasta $6.000 por semana"."""
    marca = next((m for m in ("ypf", "shell", "axion", "puma") if m in fuente.lower()), None)
    pct = re.search(r"(\d+)%", body)
    dias = _dias_en(body.split("\n\n")[0])
    if not (marca and pct and dias):
        return []
    tope_m = re.search(r"hasta \$\s?([\d.]+)\s*por\s*(semana|mes)", body, re.I)
    tope = f"${tope_m.group(1)}/{'semanal' if tope_m.group(2).lower() == 'semana' else 'mensual'}" if tope_m else ""
    mes = _mes_de_url(fuente)
    nombre = marca.upper() if marca == "ypf" else marca.capitalize()
    descuento = f"{pct.group(1)}% de descuento"
    return [
        Promo(
            id=f"{nombre}:{dias}:{descuento}:mercadopago",
            banco="Mercado Pago",
            categoria="Combustible",
            comercio=f"{nombre} — con tarjeta Mercado Pago",
            dias=dias,
            descuento=descuento,
            medio_pago=f"QR desde la App {nombre}, con tarjeta de crédito o prepaga Mercado Pago" + (f" (nota de {mes})" if mes else ""),
            fuente=fuente,
            tope=tope,
        )
    ]


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
        promos.extend(_parsear_combustible_prosa(body, url_combustible))

    return promos


if __name__ == "__main__":
    promos = obtener_promos()
    print(f"{len(promos)} promos encontradas en Mercado Pago\n")
    for p in promos:
        print(f"- [{p.dias}] {p.comercio} — {p.descuento} | {p.medio_pago}")

    print("\n--- JSON ---")
    print(json.dumps([asdict(p) for p in promos], ensure_ascii=False, indent=2))
