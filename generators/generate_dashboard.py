import os
import matplotlib.pyplot as plt
import matplotlib.patches as Fancy
from matplotlib.patches import FancyBboxPatch
from utils.github_api import get_repos, get_commit_activity
from utils.plot_theme import apply_dark_tech_theme
from datetime import datetime

OUTPUT_PATH = "output/github-stats.png"


def draw_card(ax, x, y, w, h, label="", fontsize=18):
    """Desenha um card premium com bordas arredondadas."""
    card = FancyBboxPatch((x, y), w, h,
                          boxstyle="round,pad=0.03,rounding_size=0.05",
                          linewidth=1.2,
                          edgecolor="#4cc9f0",
                          facecolor="#111827",
                          alpha=0.85)
    ax.add_patch(card)

    if label:
        ax.text(x + 0.02, y + h - 0.06,
                label, fontsize=fontsize, color="#e0eaff",
                fontweight="bold")

    return ax


def generate_dashboard():
    apply_dark_tech_theme()

    # ===============================
    # 1) Coleta de dados do GitHub
    # ===============================

    USERNAME = "Domisnnet"
    repos = get_repos(USERNAME)

    total_commits = 0
    total_repos = len(repos)
    active_repos = 0

    for repo in repos:
        activity = get_commit_activity(repo["full_name"])
        if isinstance(activity, list) and any(week["total"] > 0 for week in activity):
            active_repos += 1
        if isinstance(activity, list):
            for week in activity:
                total_commits += week["total"]

    # ====================================
    # 2) INICIALIZA FIGURA PREMIUM
    # ====================================
    fig = plt.figure(figsize=(15, 9), dpi=300)
    ax = fig.add_subplot(111)
    ax.set_facecolor("#0a0f1f")
    plt.axis("off")

    # ====================================
    # LAYOUT (coordenadas normalizadas)
    # ====================================

    # Cards:
    # Overview          (card grande)
    # Commits donut     (card médio)
    # Linguagens donut  (card médio)

    draw_card(ax, 0.05, 0.60, 0.40, 0.30, "GitHub Overview")
    draw_card(ax, 0.50, 0.60, 0.40, 0.30, "Commits (Donut)")
    draw_card(ax, 0.05, 0.15, 0.85, 0.40, "Linguagens Mais Usadas")

    # ====================================
    # KPIs no card de Overview
    # ====================================

    kpi_color = "#c3dafe"

    ax.text(0.07, 0.82,
            f"Repositórios Totais: {total_repos}",
            color=kpi_color, fontsize=16)

    ax.text(0.07, 0.78,
            f"Repositórios Ativos: {active_repos}",
            color=kpi_color, fontsize=16)

    ax.text(0.07, 0.74,
            f"Commits no Último Ano: {total_commits}",
            color=kpi_color, fontsize=16)

    # ====================================
    # Gráfico DONUT — Commits
    # ====================================

    commit_ax = fig.add_axes([0.58, 0.63, 0.23, 0.23])
    commit_ax.set_facecolor("#111827")

    commit_ax.pie(
        [total_commits, 1],
        colors=["#4cc9f0", "#1f2937"],
        startangle=90,
        wedgeprops=dict(width=0.35)
    )
    commit_ax.text(0, 0, "Commits",
                   ha="center", va="center",
                   fontsize=14, color="#ffffff")

    # ====================================
    # Gráfico de LINGUAGENS
    # ====================================

    langs = {}
    for r in repos:
        if r.get("language"):
            lang = r["language"]
            langs[lang] = langs.get(lang, 0) + 1

    labels = list(langs.keys())
    sizes = list(langs.values())

    lang_ax = fig.add_axes([0.15, 0.22, 0.65, 0.23])
    lang_ax.set_facecolor("#111827")

    lang_ax.pie(
        sizes,
        labels=labels,
        autopct="%1.1f%%",
        pctdistance=0.8,
        labeldistance=1.1,
        wedgeprops=dict(width=0.35),
    )

    # ====================================
    # Rodapé
    # ====================================
    now = datetime.now().strftime("%d/%m/%Y %H:%M")
    ax.text(0.50, 0.05,
            f"Atualizado automaticamente em {now}",
            color="#6b7280",
            fontsize=10,
            ha="center")

    # ====================================
    # Finaliza
    # ====================================

    os.makedirs("output", exist_ok=True)
    plt.savefig(OUTPUT_PATH, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"Dashboard gerado com sucesso em {OUTPUT_PATH}")


if __name__ == "__main__":
    generate_dashboard()