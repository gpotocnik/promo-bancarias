"""Calcula la mejor opción del día: por precio real en combustible, por % en supermercados
(no hay una fuente pública liviana de precio promedio por cadena de supermercado — ver README)."""
from tabla import _pct

DIAS_SEMANA = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

MARCA_COMBUSTIBLE_EN_COMERCIO = {
    "ypf": "YPF",
    "shell": "Shell",
    "axion": "Axion",
    "puma": "Puma",
}


def dia_de_hoy() -> str:
    from datetime import datetime

    return DIAS_SEMANA[datetime.now().weekday()]


def aplica_hoy(dias_promo: str, hoy: str = None) -> bool:
    hoy = hoy or dia_de_hoy()
    dias_promo_l = dias_promo.lower()
    return "todos los días" in dias_promo_l or hoy.lower() in dias_promo_l


def mejor_supermercado_hoy(promos: list, hoy: str = None) -> dict:
    """Mejor por % de descuento entre las promos de supermercado vigentes hoy."""
    candidatas = [
        p for p in promos
        if p.categoria == "Supermercados" and aplica_hoy(p.dias, hoy)
    ]
    if not candidatas:
        return None
    return max(candidatas, key=lambda p: _pct(p.descuento))


def mejor_combustible_hoy(promos: list, precios_por_marca: dict, hoy: str = None) -> dict:
    """Mejor por precio efectivo real (precio oficial de la marca * descuento del banco)."""
    candidatas = [p for p in promos if p.categoria == "Combustible" and aplica_hoy(p.dias, hoy)]
    if not candidatas or not precios_por_marca:
        return None

    mejor = None
    mejor_precio_efectivo = None
    for p in candidatas:
        comercio_l = p.comercio.lower()
        marca = next((v for k, v in MARCA_COMBUSTIBLE_EN_COMERCIO.items() if k in comercio_l), None)
        if not marca or marca not in precios_por_marca:
            continue
        precio_efectivo = precios_por_marca[marca] * (1 - _pct(p.descuento) / 100)
        if mejor_precio_efectivo is None or precio_efectivo < mejor_precio_efectivo:
            mejor, mejor_precio_efectivo = p, precio_efectivo

    if mejor is None:
        return None
    return {"promo": mejor, "precio_efectivo": mejor_precio_efectivo}
