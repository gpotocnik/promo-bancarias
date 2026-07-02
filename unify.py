"""Normaliza las promos de cada banco a un esquema único para dedup/resumen/mail."""
from dataclasses import dataclass

import scraper_bbva
import scraper_galicia
import scraper_mercadopago


@dataclass
class PromoUnificada:
    id: str  # único global: "<banco>:<id original>"
    banco: str
    titulo: str
    descripcion: str
    vigencia: str
    link: str


def _de_galicia() -> list[PromoUnificada]:
    return [
        PromoUnificada(
            id=f"galicia:{p.id}",
            banco="Galicia",
            titulo=p.titulo,
            descripcion=p.promocion,
            vigencia=f"hasta {p.vigencia_hasta[:10]}" if p.vigencia_hasta else p.dias,
            link="",
        )
        for p in scraper_galicia.obtener_promos()
    ]


def _de_bbva() -> list[PromoUnificada]:
    return [
        PromoUnificada(
            id=f"bbva:{p.id}",
            banco="BBVA",
            titulo=p.titulo,
            descripcion=p.descripcion,
            vigencia=f"{p.fecha_desde} a {p.fecha_hasta}",
            link="",
        )
        for p in scraper_bbva.obtener_promos()
    ]


def _de_mercadopago() -> list[PromoUnificada]:
    return [
        PromoUnificada(
            id=f"mercadopago:{p.id}",
            banco="Mercado Pago",
            titulo=p.marca,
            descripcion=f"{p.badges} — {p.descripcion}",
            vigencia=p.vigencia,
            link=p.link,
        )
        for p in scraper_mercadopago.obtener_promos()
    ]


def obtener_todas_las_promos() -> list[PromoUnificada]:
    promos = []
    for fn, banco in [(_de_galicia, "Galicia"), (_de_bbva, "BBVA"), (_de_mercadopago, "Mercado Pago")]:
        try:
            promos.extend(fn())
        except Exception as e:
            print(f"[WARN] fallo scrapeando {banco}: {e}")
    return promos


if __name__ == "__main__":
    todas = obtener_todas_las_promos()
    por_banco = {}
    for p in todas:
        por_banco.setdefault(p.banco, 0)
        por_banco[p.banco] += 1
    print(f"Total: {len(todas)} promos")
    for banco, n in por_banco.items():
        print(f"  {banco}: {n}")
