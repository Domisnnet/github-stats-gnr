import os
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from datetime import datetime
from collections import Counter
import requests
import time # Necessário para a API mais robusta

# Importações CORRIGIDAS: Usando 'utils'
from utils.github_api import get_repos, get_commit_activity
from utils.plot_theme import apply_dark_tech_theme, apply_vertical_gradient

# --- Constantes de Estilo ---
CARD_BORDER_COLOR = "#4cc9f0"
CARD_FACE_COLOR = "#111827"
KPI_TEXT_COLOR = "#c3dafe"
OUTPUT_PATH = "output/dashboard.png" # Usando o nome correto que você quer para o Actions

class DashboardGenerator:
    """Gera um dashboard de estatísticas do GitHub usando Matplotlib."""

    def __init__(self, username):
        self.username = username
        self.repos = []
        self.total_commits = 0
        self.active_repos = 0
        self.total_repos = 0
        self.langs = Counter()
        self.fig = None
        self.ax = None

    # --- Método Auxiliar para Desenho de Cards ---
    def _draw_card(self, x, y, w, h, label="", fontsize=18):
        """Desenha um card premium com bordas arredondadas."""
        card = FancyBboxPatch((x, y), w, h,
                              boxstyle="round,pad=0.03,rounding_size=0.05",
                              linewidth=1.2,
                              edgecolor=CARD_BORDER_COLOR,
                              facecolor=CARD_FACE_COLOR,
                              alpha=0.85,
                              transform=self.ax.transAxes)
        self.ax.add_patch(card)

        if label:
            self.ax.text(x + 0.02, y + h - 0.06,
                         label, fontsize=fontsize, color="#e0eaff",
                         fontweight="bold", transform=self.ax.transAxes)

    # --- Coleta de Dados ---
    def _collect_data(self):
        """Coleta todos os dados necessários da API do GitHub."""
        print(f"Coletando dados para o usuário: {self.username}...")
        
        self.repos = get_repos(self.username)
        if self.repos is None:
            print("ERRO: Falha ao obter repositórios. Verifique o Token e o usuário.")
            return
            
        self.total_repos = len(self.repos)
        all_languages = []
        
        for repo in self.repos:
            repo_commits = 0
            
            # ATENÇÃO: Essa requisição é sequencial (lenta), mas é a forma atual.
            activity = get_commit_activity(repo["full_name"]) 
            
            if isinstance(activity, list):
                # Conta commits
                for week in activity:
                    repo_commits += week.get("total", 0)
                
                if repo_commits > 0:
                    self.active_repos += 1

                self.total_commits += repo_commits

            if repo.get("language"):
                all_languages.append(repo["language"])

        # Contar a frequência das linguagens
        self.langs = Counter(all_languages)
        print("Coleta de dados concluída.")

    # --- Configuração de Layout e Figura ---
    def _setup_figure(self):
        """Inicializa a figura e aplica o tema premium."""
        apply_dark_tech_theme()
        
        self.fig = plt.figure(figsize=(15, 9), dpi=300)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor("#0a0f1f")
        
        apply_vertical_gradient(self.ax)
        
        plt.axis("off")
        
    def _draw_layout(self):
        """Desenha a estrutura e os cards principais."""
        self._draw_card(0.05, 0.60, 0.40, 0.30, "GitHub Overview")
        self._draw_card(0.50, 0.60, 0.40, 0.30, "Total Commits (Donut)")
        # Renomeado o label para refletir o novo gráfico de barras
        self._draw_card(0.05, 0.15, 0.85, 0.40, "Top Linguagens (Ranking)")

    def _draw_kpis(self):
        """Preenche o card de Overview com os KPIs."""
        self.ax.text(0.07, 0.82,
                     f"Repositórios Totais: {self.total_repos}",
                     color=KPI_TEXT_COLOR, fontsize=16, transform=self.ax.transAxes)

        self.ax.text(0.07, 0.78,
                     f"Repositórios Ativos: {self.active_repos}",
                     color=KPI_TEXT_COLOR, fontsize=16, transform=self.ax.transAxes)

        self.ax.text(0.07, 0.74,
                     f"Commits Totais: {self.total_commits}",
                     color=KPI_TEXT_COLOR, fontsize=16, transform=self.ax.transAxes)

    # --- Gráfico 1: Donut de Commits (Original) ---
    def _draw_commits_donut(self):
        """Desenha o gráfico Donut de commits."""
        commit_ax = self.fig.add_axes([0.58, 0.63, 0.23, 0.23], facecolor=CARD_FACE_COLOR)
        
        commit_ax.pie(
            [self.total_commits, 1],
            colors=[CARD_BORDER_COLOR, "#1f2937"],
            startangle=90,
            wedgeprops=dict(width=0.35, edgecolor='none')
        )
        commit_ax.text(0, 0, "Commits",
                         ha="center", va="center",
                         fontsize=14, color="#ffffff")

    # --- Gráfico 2: BARRAS HORIZONTAIS (NOVO e MELHORADO) ---
    def _draw_languages_bar(self, max_langs=7):
        """Desenha um gráfico de barras horizontais para as linguagens mais usadas."""
        
        if not self.langs or self.total_repos == 0:
            lang_ax = self.fig.add_axes([0.10, 0.20, 0.75, 0.30], facecolor=CARD_FACE_COLOR)
            lang_ax.text(0.5, 0.5, "Dados de Linguagem Indisponíveis.", 
                         ha="center", va="center", fontsize=16, color="#ff4d6d", 
                         transform=lang_ax.transAxes)
            lang_ax.axis('off')
            return

        top_langs = self.langs.most_common(max_langs)
        labels = [lang[0] for lang in top_langs]
        sizes = [lang[1] for lang in top_langs]
        
        # Calcular percentuais
        percentages = [(s / self.total_repos) * 100 for s in sizes]
        
        # Inverter para ranking (maior no topo)
        labels.reverse()
        percentages.reverse()

        lang_ax = self.fig.add_axes([0.10, 0.20, 0.75, 0.30], facecolor=CARD_FACE_COLOR)
        
        # Desenho das barras
        bars = lang_ax.barh(labels, percentages, height=0.6, color=CARD_BORDER_COLOR)

        # Estilização
        lang_ax.set_xticks([])
        lang_ax.tick_params(axis='y', length=0, labelsize=14, pad=10)

        # Adicionar o percentual ao lado de cada barra
        for bar in bars:
            width = bar.get_width()
            lang_ax.text(width + 1.5, bar.get_y() + bar.get_height()/2,
                         f'{width:.1f}%',
                         va='center', color=KPI_TEXT_COLOR, fontsize=12, fontweight='bold')

        lang_ax.spines['right'].set_visible(False)
        lang_ax.spines['top'].set_visible(False)
        lang_ax.spines['left'].set_color('#334155')
        lang_ax.spines['bottom'].set_color('#334155')

    def _add_footer(self):
        """Adiciona o rodapé com a data de atualização."""
        now = datetime.now().strftime("%d/%m/%Y %H:%M")
        self.ax.text(0.50, 0.05,
                     f"Atualizado automaticamente em {now}",
                     color="#6b7280",
                     fontsize=10,
                     ha="center",
                     transform=self.ax.transAxes)

    # --- Método Principal de Geração ---
    def generate(self, output_path=OUTPUT_PATH):
        """Método principal para gerar o dashboard."""
        self._collect_data()
        self._setup_figure()
        self._draw_layout()
        self._draw_kpis()
        self._draw_commits_donut()
        self._draw_languages_bar() # Chamando o novo gráfico de barras
        self._add_footer()

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        plt.savefig(output_path, dpi=300, bbox_inches="tight")
        plt.close(self.fig)

        print(f"Dashboard gerado com sucesso em {output_path}")


if __name__ == "__main__":
    generator = DashboardGenerator(username="Domisnnet")
    generator.generate()