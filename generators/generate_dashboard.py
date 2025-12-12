import os
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from datetime import datetime
from collections import Counter

# Importações corrigidas: Usando 'src' conforme a sua estrutura de pastas
from src.github_api import get_repos, get_commit_activity
from src.plot_theme import apply_dark_tech_theme, apply_vertical_gradient

# Constantes de Estilo
CARD_BORDER_COLOR = "#4cc9f0"
CARD_FACE_COLOR = "#111827"
KPI_TEXT_COLOR = "#c3dafe"
OUTPUT_PATH = "output/github-stats.png"

class DashboardGenerator:
    """Gera um dashboard de estatísticas do GitHub usando Matplotlib."""

    def __init__(self, username):
        self.username = username
        self.repos = []
        self.total_commits = 0
        self.active_repos = 0
        self.langs = {}
        self.fig = None
        self.ax = None

    def _collect_data(self):
        """Coleta todos os dados necessários da API do GitHub."""
        print(f"Coletando dados para o usuário: {self.username}...")
        
        self.repos = get_repos(self.username)
        self.total_repos = len(self.repos)

        all_languages = []
        
        # Otimização: Coletar commits e linguagens em um único loop
        for repo in self.repos:
            repo_commits = 0
            
            # ATENÇÃO: Se houver muitos repos, isso pode demorar ou estourar o Rate Limit
            activity = get_commit_activity(repo["full_name"]) 
            
            if isinstance(activity, list):
                # Conta commits
                for week in activity:
                    repo_commits += week.get("total", 0)
                
                # Marca repositório como ativo se houver commits recentes
                if repo_commits > 0:
                    self.active_repos += 1

                self.total_commits += repo_commits

            if repo.get("language"):
                all_languages.append(repo["language"])

        # Contar a frequência das linguagens
        self.langs = Counter(all_languages)
        print("Coleta de dados concluída.")


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

    def _setup_figure(self):
        """Inicializa a figura e o tema."""
        apply_dark_tech_theme()
        
        self.fig = plt.figure(figsize=(15, 9), dpi=300)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor("#0a0f1f")
        
        # Aplica o gradiente ao fundo
        apply_vertical_gradient(self.ax)
        
        plt.axis("off")

    def _draw_layout(self):
        """Desenha a estrutura e os cards principais."""
        self._draw_card(0.05, 0.60, 0.40, 0.30, "GitHub Overview")
        self._draw_card(0.50, 0.60, 0.40, 0.30, "Total Commits (Donut)")
        self._draw_card(0.05, 0.15, 0.85, 0.40, "Linguagens Mais Usadas")

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

    def _draw_commits_donut(self):
        """Desenha o gráfico Donut de commits."""
        commit_ax = self.fig.add_axes([0.58, 0.63, 0.23, 0.23], facecolor=CARD_FACE_COLOR)
        
        # O total_commits é o principal, o valor '1' é apenas para garantir que haja um gap visível
        commit_ax.pie(
            [self.total_commits, 1],
            colors=[CARD_BORDER_COLOR, "#1f2937"],
            startangle=90,
            wedgeprops=dict(width=0.35, edgecolor='none')
        )
        commit_ax.text(0, 0, "Commits",
                         ha="center", va="center",
                         fontsize=14, color="#ffffff")

    def _draw_languages_pie(self):
        """Desenha o gráfico de Donut de linguagens."""
        if not self.langs:
            self.ax.text(0.5, 0.3, "Nenhuma linguagem encontrada.", ha="center", va="center", fontsize=16, color="#ff4d6d", transform=self.ax.transAxes)
            return

        labels = list(self.langs.keys())
        sizes = list(self.langs.values())

        lang_ax = self.fig.add_axes([0.15, 0.22, 0.65, 0.23], facecolor=CARD_FACE_COLOR)

        lang_ax.pie(
            sizes,
            labels=labels,
            autopct="%1.1f%%",
            pctdistance=0.7,
            labeldistance=1.1,
            wedgeprops=dict(width=0.35, edgecolor=CARD_FACE_COLOR, linewidth=1),
        )

    def _add_footer(self):
        """Adiciona o rodapé com a data de atualização."""
        now = datetime.now().strftime("%d/%m/%Y %H:%M")
        self.ax.text(0.50, 0.05,
                     f"Atualizado automaticamente em {now}",
                     color="#6b7280",
                     fontsize=10,
                     ha="center",
                     transform=self.ax.transAxes)

    def generate(self, output_path=OUTPUT_PATH):
        """Método principal para gerar o dashboard."""
        self._collect_data()
        self._setup_figure()
        self._draw_layout()
        self._draw_kpis()
        self._draw_commits_donut()
        self._draw_languages_pie()
        self._add_footer()

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        plt.savefig(output_path, dpi=300, bbox_inches="tight")
        plt.close(self.fig)

        print(f"Dashboard gerado com sucesso em {output_path}")


if __name__ == "__main__":
    generator = DashboardGenerator(username="Domisnnet")
    generator.generate()