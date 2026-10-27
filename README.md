# 🛒 Monitor de Promociones de Supermercados y Combustible

Página web que muestra las promociones de **supermercados** de **Banco Galicia**, **BBVA**, **Mercado Pago** y **American Express (The Platinum Card)**, más **beneficios de combustible** — tanto bancarios como propios de las petroleras (YPF, Shell) — actualizada automáticamente todos los días.

**Página en vivo:** https://gpotocnik.github.io/promo-bancarias/

No manda mail — corrió esa versión pero se descartó a favor de una página siempre disponible.

## Qué muestra

- **Día de la semana actual**, arriba de todo.
- **Novedades de la semana**: promos que aparecieron desde la última corrida (🆕 en la tabla).
- **Mejor opción de hoy**:
  - Supermercado: la promo con mayor % de descuento entre las vigentes hoy.
  - Combustible: precio efectivo real (precio oficial de la Secretaría de Energía × descuento) — combina promos bancarias (Galicia/BBVA/MP, si existen) con los beneficios propios de las petroleras (ver abajo). Si no hay ninguna promo activa, la sección queda vacía.
- **Tabla completa** de la semana, agrupada por día, con comercio/descuento/medio de pago/banco.

## Cuando una fuente falla

Si una fuente falla o no devuelve promos, la página muestra un aviso rojo arriba ("⚠️ No se pudo actualizar: …") en vez de quedar desactualizada en silencio. Incidente de referencia (oct 2026): Galicia cambió nombres de parámetros (`IdCategoria` → `idCategoria`, `criterioDeOrden`) y movió el endpoint de detalle (`catalogo/v1/promociones/idPromocion/{id}` → `personalizacion/v1/promociones/idPromocion/{id}`); BBVA movió el % al título y los días al detalle; Mercado Pago cambió los títulos de sus guías; el CSV de combustible dio timeout por HTTP desde los runners de GitHub (ahora HTTPS con reintentos).

## Zona

Filtrado a **CABA + GBA Norte** (la zona real es Florida, Vicente López — no toda la provincia de Buenos Aires, que es enorme e incluye lugares como La Plata o Mar del Plata):

- **Combustible**: preciso, usa el dataset oficial de la Secretaría de Energía filtrado por `provincia` (`CAPITAL FEDERAL`) y por `localidad` dentro de la provincia de Buenos Aires (Vicente López, San Isidro, San Fernando, Tigre, San Martín, San Miguel, Malvinas Argentinas, José C. Paz, Escobar, Pilar — ver `LOCALIDADES_GBA_NORTE` en `precios_combustible.py`).
- **Supermercados**: los bancos NO exponen ubicación de sucursal en sus APIs de promos (la promo aplica "en cualquier sucursal adherida", sin dato de dónde queda cada una). Por eso `zona.py` usa una **lista permitida curada a mano** de cadenas con sucursales confirmadas en CABA/GBA Norte (Coto, Carrefour, Changomas, Día, Disco, Jumbo, Vea, Makro, Diarco, Supercoop, MasOnline, The Food Market, Tiendas Elten, Don Ángel). Todo lo demás se descarta y se loguea (`[ZONA] ... fuera de la lista permitida`). Antes se excluía solo lo confirmado fuera de zona, pero en octubre 2026 el catálogo de Galicia pasó a traer decenas de cadenas provinciales (Santa Fe, Córdoba, Entre Ríos…) y una lista de exclusión no podía seguirle el ritmo. Si falta una cadena relevante, agregarla a `ZONA_PERMITIDA` tras confirmar sucursales en la zona (el matching es por conjunto de palabras, sin acentos y sin importar el orden).

## American Express (The Platinum Card)

`scraper_amex.py` scrapea la página oficial de promociones de Amex (HTML estático, sin Playwright). Hoy solo tiene un beneficio de supermercado activo: "Especial Supermercados" — $100.000 de reintegro por mes alcanzando $400.000 de consumo, los jueves, exclusivo para socios de The Platinum Card (titular o adicional), válido en **Jumbo y Disco** (marcas Cencosud) presencial u online. Se muestra como "25% de reintegro" (100.000/400.000) para que sea comparable con el resto de la tabla. No tiene fecha de vencimiento explícita en la página — parece un beneficio permanente del programa, no mensual como las promos bancarias.

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
├── scraper_amex.py            # HTML estático de American Express, especial supermercados Platinum
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
