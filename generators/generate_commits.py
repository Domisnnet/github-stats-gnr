import os
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
from utils.plot_theme import apply_dark_tech_theme
from utils.github_api import get_repos, get_commit_activity

OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

USERNAME = "Domisnnet"


def generate_premium_graph():
    apply_dark_tech_theme()

    repos = get_repos(USERNAME)

    # KPIs
    total_stars = sum(repo.get("stargazers_count", 0) for repo in repos)
    repo_count = len(repos)

    # Commit activity semanal
    weekly_commits = []
    for repo in repos:
        commit_data = get_commit_activity(repo["full_name"])
        if isinstance(commit_data, list):
            for week in commit_data:
                weekly_commits.append(week["total"])

    # Caso não haja dados suficientes
    if not weekly_commits:
        weekly_commits = [0]

    total_commits_year = sum(weekly_commits)

    # === GRÁFICO ===
    fig, ax = plt.subplots(figsize=(12, 5))

    x = np.arange(len(weekly_commits))
    y = np.array(weekly_commits)

    # Linha premium neon com glow
    ax.plot(
        x, y, linewidth=2.5, color="#00A8FF", alpha=0.9, zorder=3
    )

    # Glow (duplicar várias vezes com alpha menor)
    for glow_size in [6, 12, 18]:
        ax.plot(
            x,
            y,
            linewidth=glow_size,
            color="#00A8FF",
            alpha=0.06,
            zorder=2,
        )

    # Área com gradiente
    ax.fill_between(
        x,
        y,
        color="#00A8FF",
        alpha=0.18,
        zorder=1
    )

    # Títulos premium
    ax.set_title(
        "Commits no Último Ano – Dashboard Premium",
        fontsize=18,
        pad=20,
        weight="bold",
        color="#FFFFFF"
    )

    # Remover bordas poluídas
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # Grid discreto
    ax.grid(color="#666666", alpha=0.2)

    # KPIs no topo (TEXTOS)
    fig.text(
        0.02, 0.96,
        f"Commits no Ano: {total_commits_year}",
        fontsize=12,
        color="#00A8FF",
        weight="bold"
    )

    fig.text(
        0.22, 0.96,
        f"Repositórios: {repo_count}",
        fontsize=12,
        color="#00FFBF",
        weight="bold"
    )

    fig.text(
        0.40, 0.96,
        f"Stars: {total_stars}",
        fontsize=12,
        color="#FFD86B",
        weight="bold"
    )

    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/github-stats.png", dpi=300)
    plt.close()


if __name__ == "__main__":
    generate_premium_graph()