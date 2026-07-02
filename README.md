# 🛒 Monitor de Promociones de Supermercados y Combustible

Scrapea las promociones de **supermercados** (y combustible, si aparecen) de **Banco Galicia**, **BBVA** y **Mercado Pago**, y manda un mail semanal (lunes AM) + alertas diarias cuando aparece una promo nueva. El mail es una tabla ordenada por día de la semana con comercio, descuento, medio de pago y banco — pensada para decidir dónde conviene comprar cada día.

No usa Claude API: los datos ya vienen estructurados (día/comercio/%/medio de pago) directo de las fuentes, así que armar la tabla es directo — pasar eso por un LLM solo arriesgaría que reescriba mal un número o un porcentaje.

Ninguno de los tres bancos necesita un browser real en producción: los tres tienen HTML server-rendered o una API JSON pública detrás del sitio (ver detalle en cada `scraper_*.py`). Playwright está en `requirements.txt` solo como herramienta de diagnóstico para investigar nuevas fuentes, no lo usa el pipeline.

**Estado de combustible/estaciones de servicio (relevado 2026-07):** Galicia y BBVA no tienen esa categoría activa ahora mismo (se revisó su catálogo completo de promos, ninguna es de combustible). Mercado Pago sí ofreció combustible en el pasado vía su fuente editorial, pero no hay artículo vigente al momento — `scraper_mercadopago.py` ya está preparado para tomarlo automáticamente en cuanto vuelva a publicarse.

---

## ⚙️ Setup en GitHub Actions

### 1. Crear el repositorio

```bash
gh repo create promo-bancarias --private
cd promo-bancarias
git add . && git commit -m "init" && git push
```

### 2. Configurar los secrets

En el repo → **Settings → Secrets and variables → Actions → New repository secret**

| Secret              | Valor                                        |
|----------------------|-----------------------------------------------|
| `EMAIL_FROM`         | tu-email@gmail.com                           |
| `EMAIL_TO`           | donde-recibir@email.com                      |
| `EMAIL_PASSWORD`     | contraseña de aplicación (ver monitor-parques para el paso a paso de Gmail) |
| `SMTP_HOST`          | `smtp.gmail.com`                             |
| `SMTP_PORT`          | `587`                                        |

### 3. Probar manualmente

Repo → **Actions → Monitor Promos Bancarias → Run workflow** (elegí `semanal` o `alerta`).

---

## 📅 Horario

- **Lunes 08:00 AM ART**: tabla completa de todas las promos vigentes
- **Todos los días 08:00 AM ART**: alerta solo si hay promos nuevas desde la última corrida

Editar los cron en `.github/workflows/monitor.yml` (están en UTC, ART = UTC-3).

---

## 🗂️ Archivos

```
promo-bancarias/
├── scraper_galicia.py       # API BFF pública de Galicia, categoría Supermercados (loyalty.bff.bancogalicia.com.ar)
├── scraper_bbva.py          # API pública de BBVA, campaña Supermercados (go.bbva.com.ar/willgo/fgo/API)
├── scraper_mercadopago.py   # Fallback editorial (calcularsueldo.com.ar) — MP no publica el detalle día/comercio en su propio sitio
├── unify.py                 # Normaliza los 3 bancos a un esquema único (día/comercio/descuento/medio de pago)
├── calidad.py                # Filtra promos vencidas, duplicadas o incompletas antes de armar la tabla
├── dedup.py                 # seen_promos.json — evita re-notificar
├── mailer.py                # Arma la tabla HTML (agrupada por día) y envía por SMTP
├── monitor.py                # Orquestador (--modo semanal | alerta)
├── requirements.txt
└── .github/workflows/monitor.yml
```

## 🔧 Correr localmente

```bash
pip install -r requirements.txt
export EMAIL_FROM=... EMAIL_TO=... EMAIL_PASSWORD=... SMTP_HOST=smtp.gmail.com SMTP_PORT=587
python monitor.py --modo alerta
```
