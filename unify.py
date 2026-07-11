"""Normaliza las promos de supermercados/combustible de cada banco a un esquema único."""
from dataclasses import dataclass

import beneficios_propios
import scraper_bbva
import scraper_galicia
import scraper_mercadopago
from logos import logo_comercio

DIAS_ORDEN = [
    "Lunes", "Martes", "Miércoles", "Jueves", "Viernes",
    "Sábado", "Sábados", "Domingo", "Domingos",
    "Sábados y Domingos", "Fines de semana", "Todos los días",
]


@dataclass
class PromoUnificada:
    id: str  # único global: "<banco>:<id original>"
    banco: str
    categoria: str
    comercio: str
    dias: str
    descuento: str
    medio_pago: str
    tope: str
    vigencia: str
    logo_comercio: str
    detalle_url: str


def _de_galicia() -> list[PromoUnificada]:
    return [
        PromoUnificada(
            id=f"galicia:{p.id}",
            banco="Galicia",
            categoria=p.categoria,
            comercio=p.comercio,
            dias=p.dias,
            descuento=p.descuento,
            medio_pago=p.medio_pago,
            tope=p.tope,
            vigencia=p.vigencia_hasta,
            logo_comercio=logo_comercio(p.comercio, p.logo_url),
            detalle_url=p.detalle_url,
        )
        for p in scraper_galicia.obtener_promos()
    ]


def _de_bbva() -> list[PromoUnificada]:
    return [
        PromoUnificada(
            id=f"bbva:{p.id}",
            banco="BBVA",
            categoria=p.categoria,
            comercio=p.comercio,
            dias=p.dias,
            descuento=p.descuento,
            medio_pago=p.medio_pago,
            tope=p.tope,
            vigencia=p.vigencia_hasta,
            logo_comercio=logo_comercio(p.comercio, p.logo_url),
            detalle_url=p.detalle_url,
        )
        for p in scraper_bbva.obtener_promos()
    ]


def _de_mercadopago() -> list[PromoUnificada]:
    return [
        PromoUnificada(
            id=f"mercadopago:{p.id}",
            banco="Mercado Pago",
            categoria=p.categoria,
            comercio=p.comercio,
            dias=p.dias,
            descuento=p.descuento,
            medio_pago=p.medio_pago,
            tope="",
            vigencia="",
            logo_comercio=logo_comercio(p.comercio, ""),
            detalle_url=p.fuente,
        )
        for p in scraper_mercadopago.obtener_promos()
    ]


def _de_beneficios_propios() -> list[PromoUnificada]:
    return [
        PromoUnificada(
            id=f"propio:{p.id}",
            banco=p.banco,
            categoria=p.categoria,
            comercio=p.comercio,
            dias=p.dias,
            descuento=p.descuento,
            medio_pago=p.medio_pago,
            tope=p.tope,
            vigencia="",
            logo_comercio=logo_comercio(p.comercio),
            detalle_url="",
        )
        for p in beneficios_propios.obtener_promos()
    ]


def obtener_todas_las_promos() -> list[PromoUnificada]:
    promos = []
    fuentes = [
        (_de_galicia, "Galicia"),
        (_de_bbva, "BBVA"),
        (_de_mercadopago, "Mercado Pago"),
        (_de_beneficios_propios, "Beneficios propios (YPF/Shell)"),
    ]
    for fn, banco in fuentes:
        try:
            promos.extend(fn())
        except Exception as e:
            print(f"[WARN] fallo scrapeando {banco}: {e}")
    return promos


def orden_dia(dias: str) -> int:
    for i, d in enumerate(DIAS_ORDEN):
        if d.lower() in dias.lower():
            return i
    return len(DIAS_ORDEN)


if __name__ == "__main__":
    todas = obtener_todas_las_promos()
    por_banco = {}
    for p in todas:
        por_banco.setdefault(p.banco, 0)
        por_banco[p.banco] += 1
    print(f"Total: {len(todas)} promos")
    for banco, n in por_banco.items():
        print(f"  {banco}: {n}")
