"""
Beneficios propios de las petroleras (sin banco de por medio) — YPF, Shell, etc.

No hay una fuente pública con estructura fija para scrapear esto de forma confiable
(las notas periodísticas que lo cubren cambian de formato mes a mes, y el único sitio
"especializado" que encontramos tenía números duplicados entre marcas distintas,
señal de contenido genérico/no verificado). Por eso esta lista es curada a mano y
revisada periódicamente — ver FECHA_VERIFICADO.

Corroborado cruzando Perfil, Canal26 e iProfesional (todos coinciden) el 2026-07-10.
Si en algún momento aparece una fuente oficial estructurada (ej: la propia App YPF
expone un endpoint público), reemplazar esto por un scraper real.
"""
from dataclasses import dataclass

FECHA_VERIFICADO = "2026-07-10"

BENEFICIOS = [
    {
        "banco": "YPF",
        "comercio": "YPF — Carga nocturna",
        "dias": "Todos los días",
        "descuento": "6% de descuento",
        "medio_pago": "App YPF, cargando entre las 00 y las 06hs",
        "tope": "sin tope",
    },
    {
        "banco": "YPF",
        "comercio": "YPF — Autodespacho",
        "dias": "Todos los días",
        "descuento": "3% de descuento",
        "medio_pago": "App YPF, autodespacho (acumulable con carga nocturna)",
        "tope": "sin tope",
    },
    {
        "banco": "YPF",
        "comercio": "YPF — Socios ACA",
        "dias": "Todos los días",
        "descuento": "5% de descuento",
        "medio_pago": "App YPF, socios ACA en estaciones adheridas",
        "tope": "$18.000/mes",
    },
    {
        "banco": "Shell",
        "comercio": "Shell — V-Power",
        "dias": "Miércoles",
        "descuento": "10% de descuento",
        "medio_pago": "Combustibles V-Power",
        "tope": "$4.000/semana",
    },
]


@dataclass
class Promo:
    id: str
    banco: str
    categoria: str
    comercio: str
    dias: str
    descuento: str
    medio_pago: str
    tope: str


def obtener_promos() -> list[Promo]:
    return [
        Promo(
            id=f"propio:{b['banco']}:{b['comercio']}",
            banco=b["banco"],
            categoria="Combustible",
            comercio=b["comercio"],
            dias=b["dias"],
            descuento=b["descuento"],
            medio_pago=b["medio_pago"],
            tope=b["tope"],
        )
        for b in BENEFICIOS
    ]


if __name__ == "__main__":
    for p in obtener_promos():
        print(f"- [{p.dias}] {p.comercio} — {p.descuento} | {p.medio_pago} | tope {p.tope}")
    print(f"\n(verificado por última vez: {FECHA_VERIFICADO})")
