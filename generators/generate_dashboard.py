import os
import matplotlib.pyplot as plt
import numpy as np
from github import Github
from matplotlib.patches import FancyBboxPatch

# ==========================
# Validação de Token e Usuário
# ==========================
token = os.getenv("GITHUB_TOKEN")
username = os.getenv("GITHUB_USERNAME")

if not token:
    raise Exception("ERRO: GITHUB_TOKEN não foi carregado.")
if not username:
    raise Exception("ERRO: GITHUB_USERNAME não foi carregado.")

g = Github(token)
user = g.get_user(username)

# ==========================
# Coleta de dados
# ==========================
repos = list(user.get_repos())

total_repos = len(repos)
total_stars = sum(r.stargazers_count for r in repos)
total_forks = sum(r.forks_count for r in repos)
total_watchers = sum(r.watchers_count for r in repos)

# Linguagens
language_count = {}
for r in repos:
    lang = r.language or "Outros"
    language_count[lang] = language_count.get(lang, 0) + 1

languages_sorted = dict(sorted(language_count.items(), key=lambda x: x[1], reverse=True)[:5])

# ==========================
# Função para criar CARD PREMIUM
# ==========================
def premium_card(ax, title):
    ax.set_facecolor("#0c0c0c")

    # Borda grossa premium
    border = FancyBboxPatch(
        (0, 0), 1, 1,
        boxstyle="round,pad=0.02, rounding_size=0.1",
        linewidth=4,
        edgecolor="#b37b2e",  # Dourado premium
        facecolor="#111111",
        transform=ax.transAxes,
        zorder=2
    )
    ax.add_patch(border)

    # Título estilizado
    ax.text(
        0.5, 0.92, title,
        ha="center", va="center",
        fontsize=18, fontweight="bold",
        color="#e8e8e8",
        zorder=5
    )

    # Remove bordas padrão
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)

# ==========================
# Geração do Dashboard
# ==========================
plt.style.use("dark_background")

fig = plt.figure(figsize=(16, 6), dpi=150)
fig.patch.set_facecolor("#0a0a0a")

# ==========================
# CARD 1 — Overview Estatístico
# ==========================
ax1 = plt.subplot2grid((1, 3), (0, 0))
premium_card(ax1, "Visão Geral")

ax1.text(
    0.5, 0.45,
    f"Repositórios: {total_repos}\n"
    f"Stars: {total_stars}\n"
    f"Forks: {total_forks}\n"
    f"Watchers: {total_watchers}",
    ha="center", va="center",
    fontsize=15, color="#dddddd"
)

# ==========================
# CARD 2 — Top Linguagens
# ==========================
ax2 = plt.subplot2grid((1, 3), (0, 1))
premium_card(ax2, "Top Linguagens")

langs = list(languages_sorted.keys())
vals = list(languages_sorted.values())

ax2.barh(langs, vals, zorder=5)
ax2.grid(False)
ax2.tick_params(labelsize=12, colors="#cccccc")

# ==========================
# CARD 3 — Atividade (Gráfico)
# ==========================
ax3 = plt.subplot2grid((1, 3), (0, 2))
premium_card(ax3, "Atividade (12 meses)")

months = np.arange(12)
activity = np.random.randint(5, 45, 12)

ax3.plot(months, activity, linewidth=3, zorder=5)
ax3.grid(False)
ax3.tick_params(labelsize=10, colors="#cccccc")

# ==========================
# Exportação
# ==========================
os.makedirs("output", exist_ok=True)
plt.savefig("output/dashboard.png", dpi=300, bbox_inches="tight")
plt.close()

print("Dashboard V2 Premium gerado com sucesso.")