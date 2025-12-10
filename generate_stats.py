
"""
generate_stats.py
Gerador de estatísticas premium (PNG + SVG) para README / GitHub Pages.

Como funciona:
- coleta contribuições do ano via scraping do perfil público (mesmo número do gráfico verde)
- coleta commits oficiais via /repos/:owner/:repo/stats/contributors
- estima commits ampliados via /repos/:owner/:repo/commits?author= usando Link header
- agrega linguagens por bytes
- gera assets/github-stats.png (premium card) e assets/github-stats.svg (fallback)
"""

import os
import re
import time
import math
import requests
from collections import Counter
from datetime import datetime
from io import BytesIO
from typing import List, Dict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ---------- CONFIG ----------
GITHUB_USER = os.getenv("GITHUB_USER", "Domisnnet")
OUT_DIR = "assets"
PNG_PATH = os.path.join(OUT_DIR, "github-stats.png")
SVG_PATH = os.path.join(OUT_DIR, "github-stats.svg")
API_BASE = "https://api.github.com"
TOKEN = os.getenv("GITHUB_TOKEN")  # inject via GitHub Actions for higher rate limits
HEADERS = {"Accept": "application/vnd.github+json"}
if TOKEN:
    HEADERS["Authorization"] = f"Bearer {TOKEN}"

REQUEST_TIMEOUT = 12
# cache small local to avoid repeated requests in same run
_repo_cache = None

# ---------- HELPERS ----------
def ensure_out():
    os.makedirs(OUT_DIR, exist_ok=True)

def safe_json_get(url: str, params: dict = None) -> dict:
    try:
        r = requests.get(url, headers=HEADERS, params=params, timeout=REQUEST_TIMEOUT)
        r.raise_for_status()
        return r.json()
    except Exception:
        return {}

def paginate_repos() -> List[dict]:
    global _repo_cache
    if _repo_cache is not None:
        return _repo_cache
    repos = []
    page = 1
    while True:
        url = f"{API_BASE}/users/{GITHUB_USER}/repos"
        params = {"per_page": 100, "page": page, "type": "all", "sort": "updated"}
        r = requests.get(url, headers=HEADERS, params=params, timeout=REQUEST_TIMEOUT)
        if r.status_code != 200:
            break
        batch = r.json()
        if not isinstance(batch, list) or len(batch) == 0:
            break
        repos.extend(batch)
        if len(batch) < 100:
            break
        page += 1
        time.sleep(0.1)
    _repo_cache = repos
    return repos

def get_contributions_year() -> int:
    """
    Scrape profile page to extract "X contributions in the last year"
    """
    try:
        r = requests.get(f"https://github.com/{GITHUB_USER}", timeout=REQUEST_TIMEOUT)
        r.raise_for_status()
        m = re.search(r'([\d,]+)\s+contributions\s+in\s+the\s+last\s+year', r.text)
        if m:
            return int(m.group(1).replace(",", ""))
    except Exception:
        pass
    # fallback: try REST user endpoint for possible field
    try:
        u = safe_json_get(f"{API_BASE}/users/{GITHUB_USER}")
        if isinstance(u, dict) and "contributions" in u and isinstance(u["contributions"], int):
            return u["contributions"]
    except Exception:
        pass
    return 0

def get_official_commits(repos: List[dict]) -> int:
    total = 0
    for repo in repos:
        owner = repo.get("owner", {}).get("login")
        name = repo.get("name")
        if not owner or not name:
            continue
        try:
            url = f"{API_BASE}/repos/{owner}/{name}/stats/contributors"
            r = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
            if r.status_code != 200:
                # stats endpoint may return 202 if it is being generated. skip.
                continue
            data = r.json()
            if not isinstance(data, list):
                continue
            for entry in data:
                author = entry.get("author") or {}
                if author.get("login", "").lower() == GITHUB_USER.lower():
                    total += int(entry.get("total", 0))
                    break
        except Exception:
            continue
        time.sleep(0.08)
    return total

def get_expanded_commits(repos: List[dict]) -> int:
    """
    For each repo, request commits?author=username&per_page=1 and use Link header to infer count.
    """
    total = 0
    for repo in repos:
        owner = repo.get("owner", {}).get("login")
        name = repo.get("name")
        if not owner or not name:
            continue
        try:
            url = f"{API_BASE}/repos/{owner}/{name}/commits"
            params = {"author": GITHUB_USER, "per_page": 1}
            r = requests.get(url, headers=HEADERS, params=params, timeout=REQUEST_TIMEOUT)
            if r.status_code == 200:
                link = r.headers.get("Link", "")
                if 'rel="last"' in link:
                    m = re.search(r'[?&]page=(\d+)[^>]*>;\s*rel="last"', link)
                    if m:
                        pages = int(m.group(1))
                        # per_page=1 so pages == count
                        total += pages
                    else:
                        total += len(r.json() or [])
                else:
                    total += len(r.json() or [])
            else:
                continue
        except Exception:
            continue
        time.sleep(0.05)
    return total

def aggregate_languages(repos: List[dict]) -> Dict[str, int]:
    counter = Counter()
    for repo in repos:
        name = repo.get("name")
        if not name:
            continue
        try:
            url = f"{API_BASE}/repos/{GITHUB_USER}/{name}/languages"
            r = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
            if r.status_code != 200:
                continue
            for lang, size in r.json().items():
                counter[lang] += int(size)
        except Exception:
            continue
        time.sleep(0.04)
    return dict(counter)

# ---------- RENDER (premium PNG) ----------
def kfmt(n: int) -> str:
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n/1000:.1f}k"
    return str(n)

def render_png(official:int, expanded:int, year:int, languages:Dict[str,int], repo_count:int):
    ensure_out()
    # Canvas
    W, H = 1200, 420
    fig = plt.figure(figsize=(W/100, H/100), dpi=100)
    ax = fig.add_axes([0,0,1,1])
    ax.set_facecolor("#0b1220")  # dark background
    ax.axis("off")

    # Title
    ax.text(0.04, 0.88, f"{GITHUB_USER} — GitHub Activity", fontsize=22, fontweight="bold", color="#D7E6FF")

    # Cards positions and styles
    card_w = 0.28
    card_h = 0.42
    xs = [0.04, 0.36, 0.68]
    values = [official, expanded, year]
    labels = ["Commits oficiais", "Commits ampliados", "Contribuições (ano)"]
    subt = ["/stats/contributors", "/commits?author=", "GitHub profile graph"]
    colors = ["#7DD3FC", "#A78BFA", "#60A5FA"]

    for i, x in enumerate(xs):
        rect = plt.Rectangle((x, 0.38), card_w, card_h, facecolor="#0f1724", edgecolor="#233044", linewidth=1.2, zorder=1, joinstyle="round")
        ax.add_patch(rect)
        ax.text(x+0.04, 0.68, labels[i], fontsize=12, fontweight="600", color="#cfe8ff")
        ax.text(x+0.04, 0.46, kfmt(values[i]), fontsize=28, fontweight="700", color=colors[i])
        ax.text(x+0.04, 0.38, subt[i], fontsize=9, color="#98a8bf")

    # Right-side languages box (larger)
    lang_rect = plt.Rectangle((0.04, 0.04), 0.92, 0.28, facecolor="#071024", edgecolor="#20304a", linewidth=1.0, zorder=1)
    ax.add_patch(lang_rect)
    ax.text(0.06, 0.28, f"Linguagens (top {min(6, len(languages))}) — {repo_count} repositórios", fontsize=12, fontweight="600", color="#cfe8ff")

    # Draw top languages as horizontal bars
    top_langs = sorted(languages.items(), key=lambda x: x[1], reverse=True)[:6]
    if not top_langs:
        ax.text(0.06, 0.18, "Nenhuma linguagem detectada.", fontsize=11, color="#9fb3c9")
    else:
        max_val = max(v for _, v in top_langs)
        for i, (lang, val) in enumerate(top_langs):
            y = 0.22 - i*0.035
            bar_w = (val / max_val) * 0.6 if max_val > 0 else 0.0
            ax.add_patch(plt.Rectangle((0.06, y), bar_w, 0.025, facecolor="#4c9ed9", alpha=0.95))
            ax.text(0.69, y+0.01, f"{lang}  {kfmt(val)}", fontsize=10, color="#dff2ff", ha="right")

    # Footer small text
    ax.text(0.04, 0.02, f"Gerado em {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}", fontsize=8, color="#6b7c8f")

    fig.savefig(PNG_PATH, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)

def render_svg(official:int, expanded:int, year:int, languages:Dict[str,int], repo_count:int):
    ensure_out()
    # Simple SVG fallback showing the three numbers
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="980" height="240">
  <rect width="100%" height="100%" fill="#071025"/>
  <text x="24" y="36" fill="#D7E6FF" font-size="20" font-weight="700">{GITHUB_USER} — GitHub Activity</text>

  <g transform="translate(24,64)">
    <rect width="280" height="72" rx="8" fill="#0f1724" stroke="#233044"/>
    <text x="16" y="24" fill="#cfe8ff" font-size="12" font-weight="600">Commits oficiais</text>
    <text x="16" y="52" fill="#7DD3FC" font-size="24" font-weight="700">{kfmt(official)}</text>
  </g>

  <g transform="translate(340,64)">
    <rect width="280" height="72" rx="8" fill="#0f1724" stroke="#233044"/>
    <text x="16" y="24" fill="#cfe8ff" font-size="12" font-weight="600">Commits ampliados</text>
    <text x="16" y="52" fill="#A78BFA" font-size="24" font-weight="700">{kfmt(expanded)}</text>
  </g>

  <g transform="translate(656,64)">
    <rect width="280" height="72" rx="8" fill="#0f1724" stroke="#233044"/>
    <text x="16" y="24" fill="#cfe8ff" font-size="12" font-weight="600">Contribuições (ano)</text>
    <text x="16" y="52" fill="#60A5FA" font-size="24" font-weight="700">{kfmt(year)}</text>
  </g>

  <text x="24" y="220" fill="#6b7c8f" font-size="10">Dados gerados — {repo_count} repositórios analisados</text>
</svg>'''
    with open(SVG_PATH, "w", encoding="utf-8") as f:
        f.write(svg)

# ---------- MAIN ----------
def main():
    print("Iniciando coleta de dados...")
    repos = paginate_repos()
    repo_count = len(repos)
    print(f"Repositórios encontrados: {repo_count}")

    year = get_contributions_year()
    print(f"Contribuições (ano): {year}")

    # official commits (soma do endpoint stats/contributors)
    print("Coletando commits oficiais (stats/contributors)...")
    official = get_official_commits(repos)
    print(f"Commits oficiais (soma): {official}")

    # expanded commits (inferencia via commits?author=)
    print("Coletando commits ampliados (commits?author=)...")
    expanded = get_expanded_commits(repos)
    print(f"Commits ampliados (estimativa): {expanded}")

    print("Agregando linguagens...")
    langs = aggregate_languages(repos)
    print(f"Linguagens detectadas: {len(langs)}")

    print("Renderizando imagens...")
    render_png(official, expanded, year, langs, repo_count)
    render_svg(official, expanded, year, langs, repo_count)

    print("Arquivos gerados:")
    print(f"- {PNG_PATH}")
    print(f"- {SVG_PATH}")

if __name__ == "__main__":
    main()
