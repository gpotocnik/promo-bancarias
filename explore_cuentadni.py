"""
Exploración inicial: ¿cuentadni.com.ar es scrapeable sin JS o requiere Playwright?
Compara requests+BS4 (HTML crudo) vs Playwright (HTML renderizado) para la misma URL.
"""
import sys

import requests
from bs4 import BeautifulSoup

CANDIDATE_PATHS = [
    "https://www.bancoprovincia.com.ar/cuentadni/contenidos/cdnibeneficios/",
    "https://www.bancoprovincia.com.ar/cuentadni/index?url=cdniIndividuos",
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
}


def check_static(url: str):
    print(f"\n=== requests+BS4: {url} ===")
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        print(f"status: {r.status_code}, bytes: {len(r.content)}")
        soup = BeautifulSoup(r.text, "html.parser")
        text_len = len(soup.get_text(strip=True))
        print(f"texto visible en HTML crudo: {text_len} caracteres")
        links = soup.find_all("a", href=True)
        print(f"cantidad de <a href>: {len(links)}")
        return r.status_code, text_len
    except Exception as e:
        print(f"ERROR: {e}")
        return None, None


def check_playwright(url: str):
    print(f"\n=== Playwright (renderizado): {url} ===")
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(user_agent=HEADERS["User-Agent"])
        page.goto(url, timeout=30000, wait_until="networkidle")
        html = page.content()
        soup = BeautifulSoup(html, "html.parser")
        text_len = len(soup.get_text(strip=True))
        print(f"texto visible tras render JS: {text_len} caracteres")
        title = page.title()
        print(f"title: {title}")
        browser.close()
        return text_len


if __name__ == "__main__":
    for url in CANDIDATE_PATHS:
        status, static_len = check_static(url)
        if status == 200:
            try:
                render_len = check_playwright(url)
                ratio = render_len / max(static_len, 1)
                print(f"\n>>> {url}: static={static_len} chars, rendered={render_len} chars, ratio={ratio:.1f}x")
                if ratio > 3:
                    print(">>> Contenido cargado mayormente por JS -> requiere Playwright")
                else:
                    print(">>> Contenido ya presente en HTML crudo -> requests+BS4 alcanza")
            except Exception as e:
                print(f"Playwright ERROR en {url}: {e}")
