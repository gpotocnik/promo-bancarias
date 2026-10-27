"""Extrae los días de la semana de un texto libre ("Todos los martes", "Viernes y sábados",
"De viernes a domingo", "los sábados y domingos", "todos los días")."""
import re

SEMANA = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
_IDX = {"lunes": 0, "martes": 1, "miercoles": 2, "jueves": 3, "viernes": 4,
        "sabado": 5, "sabados": 5, "domingo": 6, "domingos": 6}
_PAT = r"(lunes|martes|mi[eé]rcoles|jueves|viernes|s[aá]bados?|domingos?)"


def _indice(token: str) -> int:
    return _IDX[token.lower().replace("é", "e").replace("á", "a")]


def dias_en(texto: str) -> str:
    """Devuelve "" si el texto no menciona ningún día."""
    t = texto.lower()
    if "todos los días" in t or "todos los dias" in t:
        return "Todos los días"
    rango = re.search(rf"{_PAT}\s+a\s+{_PAT}", t)
    if rango:
        a, b = _indice(rango.group(1)), _indice(rango.group(2))
        idx = list(range(a, b + 1)) if a <= b else list(range(a, 7)) + list(range(0, b + 1))
    else:
        idx = []
        for d in re.findall(_PAT, t):
            i = _indice(d)
            if i not in idx:
                idx.append(i)
    nombres = [SEMANA[i] for i in idx]
    if len(nombres) <= 1:
        return "".join(nombres)
    return ", ".join(nombres[:-1]) + " y " + nombres[-1]
