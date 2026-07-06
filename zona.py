"""
Filtro de zona (CABA + provincia de Buenos Aires) para promos de supermercado.

Los 3 bancos NO exponen ubicación de sucursal en sus APIs de promos — la promoción
aplica "en cualquier sucursal adherida" a nivel nacional. Por eso este filtro no es
tan preciso como el de combustible (que usa datos oficiales de cada estación): es
una lista curada a mano, investigada cadena por cadena (2026-07), de comercios que
NO tienen alcance en CABA/GBA y por lo tanto no le sirven a alguien en esa zona.

Se excluye solo lo que se confirmó fuera de zona; ante la duda se deja (mejor mostrar
de más que esconder una promo válida). Si aparece una cadena nueva y desconocida,
no se excluye automáticamente.
"""

FUERA_DE_ZONA = {
    "la anónima",
    "la anonima",
    "supermercados la anonima",
    "supermercados la anónima",
    "supermercados toledo",  # Mar del Plata / sudeste de la provincia
    "supermercados kilbel",  # Santa Fe, ni siquiera provincia de Buenos Aires
}


def en_zona(comercio: str) -> bool:
    return comercio.strip().lower() not in FUERA_DE_ZONA


def filtrar_por_zona(promos: list) -> list:
    return [p for p in promos if p.categoria != "Supermercados" or en_zona(p.comercio)]
