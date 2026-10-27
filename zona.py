"""
Filtro de zona (CABA + GBA Norte) para promos de supermercado.

La zona real del usuario es Florida (Vicente López) — CABA + GBA Norte, NO toda la
provincia de Buenos Aires. GBA Norte = Vicente López, San Isidro, San Fernando,
Tigre, San Martín, San Miguel, Malvinas Argentinas, José C. Paz, Escobar, Pilar.

Los bancos NO exponen ubicación de sucursal en sus promos (la promoción aplica "en
cualquier sucursal adherida"), así que el filtro es una lista CURADA A MANO de las
cadenas con sucursales confirmadas en CABA/GBA Norte (ZONA_PERMITIDA). Todo lo que no
está en la lista se descarta y se loguea, para poder revisarlo.

Cambio de criterio (2026-10): antes se excluía solo lo confirmado fuera de zona y
"ante la duda se dejaba". Ya no alcanza: el catálogo de Galicia pasó a incluir decenas
de cadenas chicas de otras provincias (Santa Fe, Córdoba, Entre Ríos...) y una lista
de exclusión no puede seguirle el ritmo. Si una cadena relevante falta, agregarla acá
tras confirmar sucursales en la zona.

Cadenas revisadas y NO permitidas (sin sucursales en la zona): La Anónima, Toledo,
Kilbel, Alvear, Almacenes Pampas, Almacenes de Marca, El Nene, Nini Mayorista,
La Gallega, Cooperativa Obrera/CoopeHogar (en CABA solo Supercoop), Mas Go (sin datos).
"""
import re
import unicodedata

# Cada entrada es un conjunto de palabras (sin acentos, minúsculas). Una cadena está
# permitida si TODAS las palabras de alguna entrada aparecen en el nombre del comercio,
# en cualquier orden — las fuentes agregan sufijos ("... QR Modo") o invierten el orden.
ZONA_PERMITIDA = [
    {"coto"},
    {"carrefour"},
    {"changomas"}, {"hiperchangomas"}, {"superchangomas"},
    {"dia"},
    {"disco"},
    {"jumbo"},
    {"vea"},
    {"makro"},
    {"diarco"},
    {"supercoop"},
    {"masonline"},
    {"thefoodmarket"}, {"food", "market"},
    {"elten"},  # Tiendas Elten, CABA
    {"don", "angel"},  # Don Torcuato / Maschwitz
]


def _palabras(texto: str) -> set:
    sin_acentos = unicodedata.normalize("NFD", texto.lower())
    sin_acentos = "".join(c for c in sin_acentos if unicodedata.category(c) != "Mn")
    return set(re.findall(r"[a-z0-9]+", sin_acentos))


def en_zona(comercio: str) -> bool:
    palabras = _palabras(comercio)
    return any(entrada <= palabras for entrada in ZONA_PERMITIDA)


def filtrar_por_zona(promos: list) -> list:
    descartados = sorted({p.comercio.strip() for p in promos if p.categoria == "Supermercados" and not en_zona(p.comercio)})
    if descartados:
        print(f"[ZONA] {len(descartados)} comercios fuera de la lista permitida: {', '.join(descartados)}")
    return [p for p in promos if p.categoria != "Supermercados" or en_zona(p.comercio)]
