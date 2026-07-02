"""Control de calidad sobre las promos ya scrapeadas: descarta vencidas,
duplicadas e incompletas antes de armar la tabla/mail."""
from datetime import date


def filtrar_validas(promos: list, hoy: str = None) -> list:
    hoy = hoy or date.today().isoformat()
    vistos = set()
    resultado = []
    descartadas = {"incompleta": 0, "vencida": 0, "duplicada": 0}

    for p in promos:
        if not p.comercio.strip() or not p.descuento.strip():
            descartadas["incompleta"] += 1
            continue

        if p.vigencia and p.vigencia < hoy:
            descartadas["vencida"] += 1
            continue

        clave = (p.banco, p.comercio.strip().lower(), p.dias.strip().lower(), p.descuento.strip().lower())
        if clave in vistos:
            descartadas["duplicada"] += 1
            continue
        vistos.add(clave)
        resultado.append(p)

    total_descartadas = sum(descartadas.values())
    if total_descartadas:
        print(
            f"[QA] {total_descartadas} promos descartadas — "
            f"{descartadas['vencida']} vencidas, {descartadas['duplicada']} duplicadas, "
            f"{descartadas['incompleta']} incompletas"
        )
    return resultado


if __name__ == "__main__":
    from unify import obtener_todas_las_promos

    crudas = obtener_todas_las_promos()
    validas = filtrar_validas(crudas)
    print(f"{len(crudas)} scrapeadas -> {len(validas)} válidas")
