"""
Filtro de zona (CABA + GBA Norte) para promos de supermercado.

La zona real del usuario es Florida (Vicente López) — CABA + GBA Norte, NO toda la
provincia de Buenos Aires, que es enorme e incluye lugares tan lejanos como La Plata,
Mar del Plata o Bahía Blanca. GBA Norte = Vicente López, San Isidro, San Fernando,
Tigre, San Martín, San Miguel, Malvinas Argentinas, José C. Paz, Escobar, Pilar.

Los 3 bancos NO exponen ubicación de sucursal en sus APIs de promos — la promoción
aplica "en cualquier sucursal adherida" a nivel nacional. Por eso este filtro no es
tan preciso como el de combustible (que usa datos oficiales de cada estación, filtrados
por localidad — ver precios_combustible.py): es una lista curada a mano, investigada
cadena por cadena (2026-07 y revisada 2026-09), de comercios que NO tienen alcance en
CABA/GBA Norte y por lo tanto no le sirven a alguien en esa zona.

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
    "alvear supermercados",  # Santa Fe capital (Santo Tomé, Recreo, Coronda), sin sucursales en Buenos Aires
    "almacenes pampas",  # GBA Sur: Hudson/Berazategui (Grupo El Nene)
    "almacenes de marca",  # La Plata (Grupo El Nene)
    "supermercados el nene",  # La Plata
    "nini mayorista",  # La Plata y Moreno (GBA Oeste), lejos de GBA Norte
    "supermercados la gallega",  # Rosario / Santa Fe
    "coopehogar",  # Cooperativa Obrera, origen Bahía Blanca; sin sucursal confirmada en CABA/GBA Norte
}


def en_zona(comercio: str) -> bool:
    return comercio.strip().lower() not in FUERA_DE_ZONA


def filtrar_por_zona(promos: list) -> list:
    return [p for p in promos if p.categoria != "Supermercados" or en_zona(p.comercio)]
