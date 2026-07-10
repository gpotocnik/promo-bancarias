# 🛒 Monitor de Promociones de Supermercados y Combustible

Página web que muestra las promociones de **supermercados** de **Banco Galicia**, **BBVA** y **Mercado Pago**, más **beneficios de combustible** — tanto bancarios como propios de las petroleras (YPF, Shell) — actualizada automáticamente todos los días.

**Página en vivo:** https://gpotocnik.github.io/promo-bancarias/

No manda mail — corrió esa versión pero se descartó a favor de una página siempre disponible.

## Qué muestra

- **Día de la semana actual**, arriba de todo.
- **Novedades de la semana**: promos que aparecieron desde la última corrida (🆕 en la tabla).
- **Mejor opción de hoy**:
  - Supermercado: la promo con mayor % de descuento entre las vigentes hoy.
  - Combustible: precio efectivo real (precio oficial de la Secretaría de Energía × descuento) — combina promos bancarias (Galicia/BBVA/MP, si existen) con los beneficios propios de las petroleras (ver abajo). Si no hay ninguna promo activa, la sección queda vacía.
- **Tabla completa** de la semana, agrupada por día, con comercio/descuento/medio de pago/banco.

## Zona

Filtrado a **CABA + provincia de Buenos Aires**:

- **Combustible**: preciso, usa el dataset oficial de la Secretaría de Energía filtrado por `provincia` (`CAPITAL FEDERAL` + `BUENOS AIRES`).
- **Supermercados**: los 3 bancos NO exponen ubicación de sucursal en sus APIs de promos (la promo aplica "en cualquier sucursal adherida" a nivel nacional, sin dato de dónde queda cada una). Por eso `zona.py` usa una lista curada a mano (investigada cadena por cadena en julio 2026) de comercios SIN alcance en CABA/GBA — hoy excluye **La Anónima** (Patagonia + interior bonaerense lejano), **Supermercados Toledo** (Mar del Plata) y **Supermercados Kilbel** (Santa Fe, ni siquiera Buenos Aires). Ante la duda se deja el comercio visible en vez de excluirlo — es mejor mostrar de más que esconder una promo válida. Si aparece una cadena nueva desconocida, no se filtra automáticamente.

## Beneficios propios de combustible (sin banco)

Además de lo que ofrecen Galicia/BBVA/MP, la página incluye beneficios que las propias petroleras dan sin depender de ningún banco (`beneficios_propios.py`): hoy son 3% a 6% de descuento en YPF por carga nocturna/autodespacho/socios ACA, y 10% en Shell (V-Power, miércoles). No hay una fuente pública con estructura fija para scrapear esto de forma confiable — se investigó cruzando varios medios (Perfil, Canal26, iProfesional, todos coinciden en los mismos números) y se descartó un sitio que parecía especializado por tener datos duplicados/genéricos entre marcas distintas. Por eso es una lista **curada a mano, con fecha de última verificación** (`FECHA_VERIFICADO` en el archivo) — hay que revisarla de tanto en tanto a mano, no se actualiza sola.

## Por qué no hay "mejor opción" con precio real en supermercados

Para combustible existe un dataset oficial y en vivo (Secretaría de Energía, Resolución 314/2016 — `datos.gob.ar`) con precio real por marca, actualizado por las propias estaciones dentro de las 8hs de cualquier cambio. Para supermercados no hay un equivalente liviano: la única fuente pública es **Precios Claros** (preciosclaros.gob.ar), que expone precio por producto individual por sucursal (no un promedio por cadena) a través de una API no documentada — los scrapers comunitarios que existen tardan horas en levantar el catálogo completo. Por eso el ranking de supermercados usa % de descuento, no precio real; si en algún momento se quiere hacer el cálculo real, habría que definir una canasta de productos representativa y armar ese scraper aparte.

No usa Claude API: los datos ya vienen estructurados (día/comercio/%/medio de pago) directo de las fuentes.

Ninguno de los tres bancos necesita un browser real en producción: los tres tienen HTML server-rendered o una API JSON pública detrás del sitio (ver detalle en cada `scraper_*.py`). Playwright está en `requirements.txt` solo como herramienta de diagnóstico para investigar nuevas fuentes, no lo usa el pipeline.

---

## ⚙️ Cómo corre

GitHub Actions (`.github/workflows/monitor.yml`) todos los días a las 8am ART:
1. Scrapea Galicia/BBVA/Mercado Pago.
2. Filtra vencidas/duplicadas/incompletas (`calidad.py`).
3. Calcula qué es nuevo desde la corrida anterior (`dedup.py`, vía cache de Actions).
4. Trae precios de combustible oficiales (`precios_combustible.py`).
5. Genera `docs/index.html` (`generar_pagina.py`) y lo publica en GitHub Pages (`actions/deploy-pages`, sin comittear nada al repo).

Repo público (necesario para que GitHub Pages gratis funcione).

---

## 🗂️ Archivos

```
promo-bancarias/
├── scraper_galicia.py         # API BFF pública de Galicia, categoría Supermercados
├── scraper_bbva.py            # API pública de BBVA, campaña Supermercados
├── scraper_mercadopago.py     # Fallback editorial (calcularsueldo.com.ar)
├── beneficios_propios.py      # Beneficios de petroleras sin banco (curado a mano, YPF/Shell)
├── logos.py                   # Logos de banco/comercio (favicons + imágenes de las APIs)
├── unify.py                   # Normaliza todas las fuentes a un esquema único
├── calidad.py                 # Filtra promos vencidas, duplicadas o incompletas
├── dedup.py                   # seen_promos.json — detecta qué es nuevo
├── precios_combustible.py     # Precio real por marca (Secretaría de Energía), filtrado por provincia
├── zona.py                    # Excluye cadenas de supermercado sin alcance en CABA/GBA (curado a mano)
├── mejor_opcion.py            # Calcula la mejor opción de hoy (súper y combustible)
├── tabla.py                   # Arma la tabla HTML agrupada por día
├── generar_pagina.py          # Arma docs/index.html completo
├── monitor.py                 # Orquestador
├── requirements.txt
└── .github/workflows/monitor.yml
```

## 🔧 Correr localmente

```bash
pip install -r requirements.txt
python monitor.py
open docs/index.html
```
