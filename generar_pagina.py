"""Genera docs/index.html: día de hoy, destacadas de la semana, mejor opción y tabla completa."""
from datetime import datetime
from pathlib import Path

from logos import logo_banco
from mejor_opcion import dia_de_hoy, mejor_combustible_hoy, mejor_supermercado_hoy
from tabla import _con_link, _img, construir_tabla

DOCS_DIR = Path("docs")


def _seccion_destacadas(nuevas: list) -> str:
    if not nuevas:
        return ""
    items = "".join(
        f"<li><b>{p.comercio}</b> ({p.banco}) — {p.descuento}</li>" for p in nuevas
    )
    return f"""
    <div style="background:#fff8e1;border:1px solid #ffe082;border-radius:8px;padding:12px 16px;margin:16px 0;">
      <b>🌟 Novedades esta semana</b>
      <ul style="margin:8px 0 0;">{items}</ul>
    </div>
    """


def _seccion_mejor_opcion(promos: list, precios_combustible: dict) -> str:
    hoy = dia_de_hoy()
    mejor_super = mejor_supermercado_hoy(promos, hoy)
    mejor_comb = mejor_combustible_hoy(promos, precios_combustible, hoy)

    bloques = []

    if mejor_super:
        nombre = _con_link(f"{_img(mejor_super.logo_comercio, 24)}{mejor_super.comercio}", mejor_super.detalle_url)
        bloques.append(
            f'<div style="flex:1;min-width:220px;background:#e8f5e9;border-radius:8px;padding:12px 16px;">'
            f"<b>🛒 Mejor súper hoy</b><br>"
            f"{nombre} — {mejor_super.descuento}<br>"
            f'<span style="font-size:13px;color:#555;">{_img(logo_banco(mejor_super.banco), 14)}{mejor_super.medio_pago} · {mejor_super.banco}</span>'
            f"</div>"
        )
    else:
        bloques.append(
            '<div style="flex:1;min-width:220px;background:#f5f5f5;border-radius:8px;padding:12px 16px;">'
            "<b>🛒 Mejor súper hoy</b><br>"
            '<span style="font-size:13px;color:#777;">Sin promos de supermercado activas hoy</span></div>'
        )

    if mejor_comb:
        p, precio_efectivo = mejor_comb["promo"], mejor_comb["precio_efectivo"]
        nombre = _con_link(f"{_img(p.logo_comercio, 24)}{p.comercio}", p.detalle_url)
        bloques.append(
            f'<div style="flex:1;min-width:220px;background:#e3f2fd;border-radius:8px;padding:12px 16px;">'
            f"<b>⛽ Mejor combustible hoy</b><br>"
            f"{nombre} — {p.descuento}<br>"
            f'<span style="font-size:13px;color:#555;">Precio efectivo estimado: ${precio_efectivo:,.0f}/litro</span>'
            f"</div>"
        )
    else:
        bloques.append(
            '<div style="flex:1;min-width:220px;background:#f5f5f5;border-radius:8px;padding:12px 16px;">'
            "<b>⛽ Mejor combustible hoy</b><br>"
            '<span style="font-size:13px;color:#777;">Ningún banco ofrece promo de combustible esta semana</span></div>'
        )

    return f'<div style="display:flex;gap:12px;flex-wrap:wrap;margin:16px 0;">{"".join(bloques)}</div>'


def generar_pagina(promos: list, nuevas: list = None, precios_combustible: dict = None):
    nuevas = nuevas or []
    precios_combustible = precios_combustible or {}
    actualizado = datetime.now().strftime("%d/%m/%Y %H:%M")
    hoy = dia_de_hoy()
    ids_nuevas = {p.id for p in nuevas}
    tabla_html = construir_tabla(promos, destacadas_ids=ids_nuevas)

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Promos supermercados y combustible</title>
<style>
  body {{ font-family: sans-serif; max-width: 900px; margin: 2rem auto; padding: 0 1rem; }}
  table {{ width: 100%; border-collapse: collapse; }}
</style>
</head>
<body>
<p style="font-size:14px;color:#888;margin-bottom:0;">Hoy es</p>
<h1 style="margin-top:4px;">{hoy}</h1>
{_seccion_destacadas(nuevas)}
{_seccion_mejor_opcion(promos, precios_combustible)}
<h2>🛒 Todas las promos de la semana</h2>
<p>Dónde conviene comprar según el día, con qué comercio y qué medio de pago. Fuentes: Banco Galicia, BBVA, Mercado Pago.
Filtrado a CABA + provincia de Buenos Aires (combustible: precio oficial real de esa zona; supermercados: se excluyeron a mano las cadenas sin sucursales en la zona, ver <a href="https://github.com/gpotocnik/promo-bancarias#zona">detalle</a>).</p>
{tabla_html}
<hr>
<p style="font-size:12px;color:#666;">Última actualización: {actualizado}. Verificá vigencia y tope antes de comprar.</p>
</body>
</html>
"""
    DOCS_DIR.mkdir(exist_ok=True)
    (DOCS_DIR / "index.html").write_text(html, encoding="utf-8")
    print(f"  docs/index.html actualizado ({len(promos)} promos, {actualizado})")


if __name__ == "__main__":
    from calidad import filtrar_validas
    from dedup import cargar_vistos, separar_nuevas
    from precios_combustible import obtener_precios_promedio
    from unify import obtener_todas_las_promos

    promos = filtrar_validas(obtener_todas_las_promos())
    nuevas, _ = separar_nuevas(promos, cargar_vistos())
    try:
        precios = obtener_precios_promedio()
    except Exception as e:
        print(f"[WARN] no se pudieron obtener precios de combustible: {e}")
        precios = {}
    generar_pagina(promos, nuevas, precios)
