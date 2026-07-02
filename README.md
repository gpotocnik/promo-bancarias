# 🏦 Monitor de Promociones Bancarias

Scrapea las promociones vigentes de **Banco Galicia**, **BBVA** y **Mercado Pago**, las resume con Claude API y manda un mail semanal (lunes AM) + alertas diarias cuando aparece una promo nueva.

Ninguno de los tres bancos necesita un browser real en producción: los tres tienen HTML server-rendered o una API JSON pública detrás del sitio (ver detalle en cada `scraper_*.py`). Playwright está en `requirements.txt` solo como herramienta de diagnóstico para investigar nuevas fuentes, no lo usa el pipeline.

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
| `ANTHROPIC_API_KEY`  | tu API key de Claude (console.anthropic.com) |
| `EMAIL_FROM`         | tu-email@gmail.com                           |
| `EMAIL_TO`           | donde-recibir@email.com                      |
| `EMAIL_PASSWORD`     | contraseña de aplicación (ver monitor-parques para el paso a paso de Gmail) |
| `SMTP_HOST`          | `smtp.gmail.com`                             |
| `SMTP_PORT`          | `587`                                        |

### 3. Probar manualmente

Repo → **Actions → Monitor Promos Bancarias → Run workflow** (elegí `semanal` o `alerta`).

---

## 📅 Horario

- **Lunes 08:00 AM ART**: resumen completo de todas las promos vigentes
- **Todos los días 08:00 AM ART**: alerta solo si hay promos nuevas desde la última corrida

Editar los cron en `.github/workflows/monitor.yml` (están en UTC, ART = UTC-3).

---

## 🗂️ Archivos

```
promo-bancarias/
├── scraper_galicia.py       # API BFF pública de Galicia (loyalty.bff.bancogalicia.com.ar)
├── scraper_bbva.py          # API pública de BBVA (go.bbva.com.ar/willgo/fgo/API)
├── scraper_mercadopago.py   # HTML estático (promociones.mercadopago.com.ar)
├── scraper_provincia.py     # HTML estático de Cuenta DNI (no usado por el pipeline actual)
├── unify.py                 # Normaliza los 3 bancos a un esquema único
├── dedup.py                 # seen_promos.json — evita re-notificar
├── summarizer.py            # Claude API -> JSON limpio por banco
├── mailer.py                # Arma el HTML y envía por SMTP
├── monitor.py                # Orquestador (--modo semanal | alerta)
├── explore_bancos.py         # Script de diagnóstico (static vs Playwright), no es parte del pipeline
├── requirements.txt
└── .github/workflows/monitor.yml
```

## 🔧 Correr localmente

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=...
export EMAIL_FROM=... EMAIL_TO=... EMAIL_PASSWORD=... SMTP_HOST=smtp.gmail.com SMTP_PORT=587
python monitor.py --modo alerta
```
