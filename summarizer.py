"""Resume promos crudas con Claude API en JSON estructurado por banco."""
import json
import os

from anthropic import Anthropic

MODEL = "claude-sonnet-5"

PROMPT_TEMPLATE = """Tenés una lista de promociones bancarias en Argentina, con texto crudo scrapeado
de cada sitio (a veces repetitivo, con símbolos de marketing como "¡" o emojis).

Para cada promo, generá una versión limpia y breve con:
- resumen: una línea clara (ej: "20% de descuento, tope $6.000 por semana")
- dias: días de la semana o "todos los días" si aplica (si no hay dato, dejalo vacío)
- vigencia: fecha de fin en formato DD/MM/AAAA si se puede inferir, si no dejalo vacío

Devolvé ÚNICAMENTE un JSON con este formato exacto, sin texto adicional:
{{
  "Galicia": [{{"titulo": "...", "resumen": "...", "dias": "...", "vigencia": "..."}}],
  "BBVA": [...],
  "Mercado Pago": [...]
}}

Promos crudas:
{promos_json}
"""


def resumir_promos(promos: list) -> dict:
    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    crudas = [
        {"banco": p.banco, "titulo": p.titulo, "descripcion": p.descripcion, "vigencia": p.vigencia}
        for p in promos
    ]

    resp = client.messages.create(
        model=MODEL,
        max_tokens=4096,
        messages=[
            {
                "role": "user",
                "content": PROMPT_TEMPLATE.format(
                    promos_json=json.dumps(crudas, ensure_ascii=False, indent=2)
                ),
            }
        ],
    )

    texto = resp.content[0].text.strip()
    if texto.startswith("```"):
        texto = texto.split("\n", 1)[1].rsplit("```", 1)[0]
    return json.loads(texto)


if __name__ == "__main__":
    from unify import obtener_todas_las_promos

    promos = obtener_todas_las_promos()
    resumen = resumir_promos(promos)
    print(json.dumps(resumen, ensure_ascii=False, indent=2))
