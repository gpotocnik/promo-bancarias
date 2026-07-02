"""
Scraper de promociones de supermercados de BBVA Argentina.
No requiere Playwright: su API pública expone el detalle de la campaña
"Supermercados" (id 2474) con comercio, tope y medio de pago.

Nota: se relevó el catálogo completo de BBVA (368 promos, 2026-07-02) y no hay
ninguna de combustible/estaciones de servicio actualmente. BBVA tampoco expone
"día de aplicación" para supermercados (diasPromo viene null = todos los días).
Si en el futuro agregan una campaña de combustible, sumar su id a CAMPANIAS.
"""
import re
from dataclasses import asdict, dataclass

import requests

CAMPAIGN_URL = "https://go.bbva.com.ar/willgo/fgo/API/v3/campaign/{id_campania}"
CAMPANIAS = {"2474": "Supermercados"}  # id de campaña -> categoría; ver docstring

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Accept": "application/json",
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


def _comercio_y_medio_pago(cabecera: str, grupo_tarjeta: str) -> tuple[str, str]:
    """'Supermercados Dia Beneficio exclusivo MODO' -> ('Supermercados Dia', 'MODO')."""
    if "Beneficio exclusivo MODO" in cabecera:
        return cabecera.replace("Beneficio exclusivo MODO", "").strip(), "MODO"
    return cabecera.strip(), grupo_tarjeta


def _promos_de_campania(id_campania: str, nombre_categoria: str) -> list[Promo]:
    promos = []
    pager = 0
    while True:
        r = requests.get(
            CAMPAIGN_URL.format(id_campania=id_campania),
            params={"pager": pager},
            headers=HEADERS,
            timeout=15,
        )
        r.raise_for_status()
        items = r.json().get("data", [])
        if not items:
            break
        for it in items:
            m = re.search(r"(\d+%[^.]*)", it.get("subcabecera") or "")
            if not m:
                continue  # entrada sin porcentaje publicado todavía (placeholder)
            comercio, medio_pago = _comercio_y_medio_pago(it.get("cabecera", ""), it.get("grupoTarjeta", ""))
            descuento = m.group(1).strip()
            monto_tope = it.get("montoTope")
            promos.append(
                Promo(
                    id=it["id"],
                    banco="BBVA",
                    categoria=nombre_categoria,
                    comercio=comercio,
                    dias=it.get("diasPromo") or "Todos los días",
                    descuento=descuento,
                    medio_pago=medio_pago,
                    tope=f"${monto_tope}" if monto_tope else "",
                    vigencia_hasta=it.get("fechaHasta") or "",
                )
            )
        if len(items) < 10:  # tamaño de página observado
            break
        pager += 1
        if pager > 20:
            break
    return promos


def obtener_promos() -> list[Promo]:
    promos = []
    for id_campania, categoria in CAMPANIAS.items():
        promos.extend(_promos_de_campania(id_campania, categoria))
    return promos


if __name__ == "__main__":
    import json

    promos = obtener_promos()
    print(f"{len(promos)} promos encontradas en BBVA\n")
    for p in promos:
        print(f"- {p.comercio} — {p.descuento} | {p.medio_pago} | tope {p.tope or 'sin tope'} | hasta {p.vigencia_hasta}")

    print("\n--- JSON ---")
    print(json.dumps([asdict(p) for p in promos], ensure_ascii=False, indent=2))
