import os
import matplotlib.pyplot as plt
import numpy as np
from github import Github

# ==========================
# Valida Token e Usuário
# ==========================
token = os.getenv("GITHUB_TOKEN")
username = os.getenv("GITHUB_USERNAME")

if not token:
    raise Exception("ERRO FATAL: GITHUB_TOKEN não foi carregado no ambiente.")

if not username:
    raise Exception("ERRO FATAL: GITHUB_USERNAME não foi carregado no ambiente.")

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

# Linguagens (top 5)
language_count = {}
for r in repos:
    lang = r.language or "Outros"
    language_count[lang] = language_count.get(lang, 0) + 1

language_sorted = dict(sorted(language_count.items(), key=lambda x: x[1], reverse=True)[:5])

# ==========================
# Geração do Dashboard Premium
# ==========================
plt.style.use("dark_background")
fig = plt.figure(figsize=(12, 8), dpi=150)
fig.patch.set_facecolor("#0a0a0a")

# Card 1 - Visão Geral
ax1 = plt.subplot2grid((2, 3), (0, 0), colspan=3)
ax1.set_facecolor("#111111")
ax1.set_title("GitHub Dashboard Premium", fontsize=22, pad=20)

texto = (
    f"Repositórios públicos: {total_repos}\n"
    f"Total de Stars: {total_stars}\n"
    f"Total de Forks: {total_forks}\n"
    f"Total de Watchers: {total_watchers}\n"
)

ax1.text(0.02, 0.3, texto, fontsize=16, va="center")
ax1.axis("off")

# Card 2 - Linguagens
ax2 = plt.subplot2grid((2, 3), (1, 0))
ax2.set_facecolor("#141414")
langs = list(language_sorted.keys())
vals = list(language_sorted.values())
ax2.barh(langs, vals)
ax2.set_title("Top Linguagens")
ax2.grid(False)

# Card 3 - Distribuições
ax3 = plt.subplot2grid((2, 3), (1, 1))
ax3.set_facecolor("#141414")
sizes = vals
ax3.pie(sizes, labels=langs, autopct='%1.1f%%', startangle=90)
ax3.set_title("Distribuição (%)")

# Card 4 - Atividade (mock premium)
ax4 = plt.subplot2grid((2, 3), (1, 2))
ax4.set_facecolor("#141414")
ax4.plot(np.random.randint(0, 50, 12), linewidth=3)
ax4.set_title("Atividade (12 meses)")
ax4.grid(False)

plt.tight_layout()

# ==========================
# Exportação
# ==========================
os.makedirs("output", exist_ok=True)
plt.savefig("output/dashboard.png", dpi=300, bbox_inches="tight")
plt.close()

print("Dashboard gerado com sucesso.")