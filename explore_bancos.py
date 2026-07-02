"""
Exploración: ¿Galicia, BBVA y Mercado Pago son scrapeables sin JS o requieren Playwright?
"""
import sys

import requests
from bs4 import BeautifulSoup

CANDIDATE_URLS = [
    ("Galicia", "https://www.galicia.ar/personas/promociones"),
    ("Galicia", "https://beneficios.galicia.ar/"),
    ("BBVA", "https://www.bbva.com.ar/beneficios/"),
    ("Mercado Pago", "https://promociones.mercadopago.com.ar/"),
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
}


def check_static(url: str):
    try:
        r = requests.get(url, headers=HEADERS, timeout=15, allow_redirects=True)
        soup = BeautifulSoup(r.text, "html.parser")
        text_len = len(soup.get_text(strip=True))
        return r.status_code, text_len, r.url
    except Exception as e:
        print(f"   requests ERROR: {e}")
        return None, None, None


def check_playwright(url: str):
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(user_agent=HEADERS["User-Agent"])
        try:
            page.goto(url, timeout=30000, wait_until="networkidle")
        except Exception as e:
            print(f"   playwright goto warning: {e}")
        html = page.content()
        soup = BeautifulSoup(html, "html.parser")
        text_len = len(soup.get_text(strip=True))
        title = page.title()
        final_url = page.url
        browser.close()
        return text_len, title, final_url


if __name__ == "__main__":
    for banco, url in CANDIDATE_URLS:
        print(f"\n{'='*70}\n{banco}: {url}\n{'='*70}")
        status, static_len, final_static_url = check_static(url)
        print(f"requests+BS4 -> status={status}, texto={static_len} chars, final_url={final_static_url}")
        if status is None:
            continue
        try:
            render_len, title, final_render_url = check_playwright(url)
            print(f"Playwright   -> texto={render_len} chars, title={title!r}, final_url={final_render_url}")
            ratio = render_len / max(static_len, 1)
            print(f">>> ratio render/static = {ratio:.1f}x")
            if ratio > 2.5:
                print(">>> Requiere Playwright (contenido cargado por JS)")
            else:
                print(">>> Posiblemente scrapeable con requests+BS4")
        except Exception as e:
            print(f"Playwright ERROR: {e}")
