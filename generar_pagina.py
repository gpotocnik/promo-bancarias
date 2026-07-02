"""Genera docs/index.html con la tabla completa siempre actualizada, para GitHub Pages."""
from datetime import datetime
from pathlib import Path

from mailer import construir_tabla

DOCS_DIR = Path("docs")


def generar_pagina(promos: list):
    actualizado = datetime.now().strftime("%d/%m/%Y %H:%M")
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
<h1>🛒 Promos de supermercados y combustible</h1>
<p>Dónde conviene comprar según el día, con qué comercio y qué medio de pago. Fuentes: Banco Galicia, BBVA, Mercado Pago.</p>
<p style="font-size:13px;color:#666;">Última actualización: {actualizado}</p>
{construir_tabla(promos)}
<hr>
<p style="font-size:12px;color:#666;">Generado automáticamente. Verificá vigencia y tope antes de comprar.</p>
</body>
</html>
"""
    DOCS_DIR.mkdir(exist_ok=True)
    (DOCS_DIR / "index.html").write_text(html, encoding="utf-8")
    print(f"  docs/index.html actualizado ({len(promos)} promos, {actualizado})")


if __name__ == "__main__":
    from calidad import filtrar_validas
    from unify import obtener_todas_las_promos

    promos = filtrar_validas(obtener_todas_las_promos())
    generar_pagina(promos)
