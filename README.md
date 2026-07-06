# 🛒 Monitor de Promociones de Supermercados y Combustible

Página web que muestra las promociones de **supermercados** (y combustible, si aparecen) de **Banco Galicia**, **BBVA** y **Mercado Pago**, actualizada automáticamente todos los días.

**Página en vivo:** https://gpotocnik.github.io/promo-bancarias/

No manda mail — corrió esa versión pero se descartó a favor de una página siempre disponible.

## Qué muestra

- **Día de la semana actual**, arriba de todo.
- **Novedades de la semana**: promos que aparecieron desde la última corrida (🆕 en la tabla).
- **Mejor opción de hoy**:
  - Supermercado: la promo con mayor % de descuento entre las vigentes hoy.
  - Combustible: precio efectivo real (precio oficial de la Secretaría de Energía × descuento del banco) — hoy no hay ninguna promo de combustible activa en los 3 bancos, así que esta sección queda vacía hasta que aparezca una.
- **Tabla completa** de la semana, agrupada por día, con comercio/descuento/medio de pago/banco.

## Zona

Filtrado a **CABA + provincia de Buenos Aires**:

- **Combustible**: preciso, usa el dataset oficial de la Secretaría de Energía filtrado por `provincia` (`CAPITAL FEDERAL` + `BUENOS AIRES`).
- **Supermercados**: los 3 bancos NO exponen ubicación de sucursal en sus APIs de promos (la promo aplica "en cualquier sucursal adherida" a nivel nacional, sin dato de dónde queda cada una). Por eso `zona.py` usa una lista curada a mano (investigada cadena por cadena en julio 2026) de comercios SIN alcance en CABA/GBA — hoy excluye **La Anónima** (Patagonia + interior bonaerense lejano), **Supermercados Toledo** (Mar del Plata) y **Supermercados Kilbel** (Santa Fe, ni siquiera Buenos Aires). Ante la duda se deja el comercio visible en vez de excluirlo — es mejor mostrar de más que esconder una promo válida. Si aparece una cadena nueva desconocida, no se filtra automáticamente.

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
├── unify.py                   # Normaliza los 3 bancos a un esquema único
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
