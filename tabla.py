"""Arma la tabla HTML de promos, agrupada por día y con destacado opcional de novedades."""
from unify import orden_dia

BANCO_COLOR = {
    "Galicia": "#EA580C",
    "BBVA": "#1447E6",
    "Mercado Pago": "#00A3E0",
}


def _pct(descuento: str) -> int:
    digitos = "".join(c for c in descuento.split("%")[0] if c.isdigit())
    return int(digitos) if digitos else 0


def construir_tabla(promos: list, destacadas_ids: set = None) -> str:
    destacadas_ids = destacadas_ids or set()
    ordenadas = sorted(promos, key=lambda p: (orden_dia(p.dias), -_pct(p.descuento), p.banco))

    filas = []
    dia_anterior = None
    for p in ordenadas:
        if p.dias != dia_anterior:
            filas.append(
                f'<tr><td colspan="4" style="background:#f2f2f2;font-weight:bold;'
                f'padding:8px 6px;border-top:2px solid #ccc;">{p.dias}</td></tr>'
            )
            dia_anterior = p.dias
        color = BANCO_COLOR.get(p.banco, "#666")
        tope = f" (tope {p.tope})" if p.tope else ""
        es_nueva = p.id in destacadas_ids
        fondo = "background:#fff8e1;" if es_nueva else ""
        badge = ' <span title="Nueva esta semana">🆕</span>' if es_nueva else ""
        filas.append(
            f'<tr style="{fondo}">'
            f'<td style="padding:6px;border-bottom:1px solid #eee;"><b>{p.comercio}</b>{badge}</td>'
            f'<td style="padding:6px;border-bottom:1px solid #eee;">{p.descuento}{tope}</td>'
            f'<td style="padding:6px;border-bottom:1px solid #eee;">{p.medio_pago}</td>'
            f'<td style="padding:6px;border-bottom:1px solid #eee;color:{color};font-weight:bold;">{p.banco}</td>'
            "</tr>"
        )

    return (
        '<table style="width:100%;border-collapse:collapse;font-size:14px;">'
        "<thead><tr>"
        '<th style="text-align:left;padding:6px;border-bottom:2px solid #333;">Comercio</th>'
        '<th style="text-align:left;padding:6px;border-bottom:2px solid #333;">Descuento</th>'
        '<th style="text-align:left;padding:6px;border-bottom:2px solid #333;">Medio de pago</th>'
        '<th style="text-align:left;padding:6px;border-bottom:2px solid #333;">Banco</th>'
        "</tr></thead><tbody>" + "".join(filas) + "</tbody></table>"
    )
