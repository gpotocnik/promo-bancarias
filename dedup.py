"""Dedup de promos ya notificadas, mismo patrón que monitor-parques."""
import json
from pathlib import Path

SEEN_FILE = Path("seen_promos.json")


def cargar_vistos() -> set:
    if SEEN_FILE.exists():
        return set(json.loads(SEEN_FILE.read_text()))
    return set()


def guardar_vistos(vistos: set):
    SEEN_FILE.write_text(json.dumps(sorted(vistos), ensure_ascii=False, indent=2))


def separar_nuevas(promos: list, vistos: set):
    """Devuelve (nuevas, vistos_actualizado)."""
    nuevas = [p for p in promos if p.id not in vistos]
    vistos_actualizado = vistos | {p.id for p in promos}
    return nuevas, vistos_actualizado
