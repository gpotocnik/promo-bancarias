"""
Logos para bancos y comercios.

- Bancos: siempre el ícono del sitio oficial (vía Google favicons).
- Comercios: si la fuente ya trae una imagen (Galicia/BBVA), se usa esa. Si no
  (Mercado Pago, o comercios sin imagen), se intenta el ícono del sitio oficial
  del comercio a partir de un mapeo de dominios conocidos — no se adivina para
  los que no están confirmados, en esos casos no se muestra logo.
"""

GALICIA_IMG_BASE = "https://www.galicia.ar/content/dam/galicia/banco-galicia/personas/promociones/catalogo-de-beneficios/"

BANCO_LOGO = {
    "Galicia": "https://www.google.com/s2/favicons?domain=galicia.ar&sz=64",
    "BBVA": "https://www.google.com/s2/favicons?domain=bbva.com.ar&sz=64",
    "Mercado Pago": "https://www.google.com/s2/favicons?domain=mercadopago.com.ar&sz=64",
    "YPF": "https://www.google.com/s2/favicons?domain=ypf.com.ar&sz=64",
    "Shell": "https://www.google.com/s2/favicons?domain=shell.com.ar&sz=64",
}

DOMINIO_POR_COMERCIO = {
    "coto": "coto.com.ar",
    "carrefour": "carrefour.com.ar",
    "dia": "dia.com.ar",
    "changomas": "changomas.com.ar",
    "jumbo": "jumbo.com.ar",
    "makro": "makro.com.ar",
    "disco": "disco.com.ar",
    "vea": "vea.com.ar",
    "diarco": "diarco.com.ar",
    "supercoop": "supercoop.coop",
    "masonline": "masonline.com.ar",
    "el nene": "grupoelnene.com.ar",
    "thefoodmarket": "thefoodmarket.com.ar",
    "food market": "thefoodmarket.com.ar",
    "ypf": "ypf.com.ar",
    "shell": "shell.com.ar",
    "axion": "axionenergy.com.ar",
    "puma": "puma-energy.com",
}


def logo_banco(banco: str) -> str:
    return BANCO_LOGO.get(banco, "")


def logo_comercio(comercio: str, logo_url: str = "") -> str:
    if logo_url:
        return logo_url
    comercio_l = comercio.lower()
    for clave, dominio in DOMINIO_POR_COMERCIO.items():
        if clave in comercio_l:
            return f"https://www.google.com/s2/favicons?domain={dominio}&sz=64"
    return ""
