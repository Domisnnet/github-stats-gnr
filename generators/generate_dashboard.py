import os
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from datetime import datetime
from collections import Counter

from utils.github_api import get_repos, get_commit_activity
from utils.plot_theme import apply_dark_tech_theme, apply_vertical_gradient

CARD_BORDER_COLOR = "#4cc9f0"
CARD_FACE_COLOR = "#111827"
KPI_TEXT_COLOR = "#c3dafe"
OUTPUT_PATH = "output/dashboard.png"


class DashboardGenerator:
    def __init__(self, username):
        self.username = username
        self.repos = []
        self.total_commits = 0
        self.active_repos = 0
        self.total_repos = 0
        self.langs = Counter()
        self.fig = None
        self.ax = None

    def _draw_card(self, x, y, w, h, label="", fontsize=18):
        card = FancyBboxPatch(
            (x, y),
            w,
            h,
            boxstyle="round,pad=0.03,rounding_size=0.05",
            linewidth=1.2,
            edgecolor=CARD_BORDER_COLOR,
            facecolor=CARD_FACE_COLOR,
            alpha=0.85,
            transform=self.ax.transAxes,
        )
        self.ax.add_patch(card)
        if label:
            self.ax.text(
                x + 0.02,
                y + h - 0.06,
                label,
                fontsize=fontsize,
                color="#e0eaff",
                fontweight="bold",
                transform=self.ax.transAxes,
            )

    def _collect_data(self):
        self.repos = get_repos(self.username)
        if self.repos is None:
            return
        self.total_repos = len(self.repos)
        all_languages = []
        for repo in self.repos:
            repo_commits = 0
            activity = get_commit_activity(repo["full_name"])
            if isinstance(activity, list):
                for week in activity:
                    repo_commits += week.get("total", 0)
                if repo_commits > 0:
                    self.active_repos += 1
                self.total_commits += repo_commits
            if repo.get("language"):
                all_languages.append(repo["language"])
        self.langs = Counter(all_languages)

    def _setup_figure(self):
        apply_dark_tech_theme()
        self.fig = plt.figure(figsize=(24, 12), dpi=300)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor("#0a0f1f")
        apply_vertical_gradient(self.ax)
        plt.axis("off")

    def _draw_layout(self):
        self._draw_card(0.06, 0.60, 0.35, 0.30, "GitHub Overview")
        self._draw_card(0.59, 0.60, 0.35, 0.30, "Total Commits (Donut)")
        self._draw_card(0.06, 0.15, 0.88, 0.40, "Top Linguagens (Ranking)")

    def _draw_kpis(self):
        self.ax.text(0.08, 0.86, f"Repositórios Totais: {self.total_repos}", color=KPI_TEXT_COLOR, fontsize=16, transform=self.ax.transAxes)
        self.ax.text(0.08, 0.77, f"Repositórios Ativos: {self.active_repos}", color=KPI_TEXT_COLOR, fontsize=16, transform=self.ax.transAxes)
        self.ax.text(0.08, 0.68, f"Commits Totais: {self.total_commits}", color=KPI_TEXT_COLOR, fontsize=16, transform=self.ax.transAxes)

    def _draw_commits_donut(self):
        from mpl_toolkits.axes_grid1.inset_locator import inset_axes
        commit_ax = inset_axes(self.ax, width="20%", height="35%", bbox_to_anchor=(0.60, 0.60, 0.35, 0.30), bbox_transform=self.ax.transAxes, loc="center")
        commit_ax.set_facecolor(CARD_FACE_COLOR)
        commit_ax.set_xticks([])
        commit_ax.set_yticks([])
        total = max(self.total_commits, 1)
        commit_ax.pie(
            [total, 1],
            colors=[CARD_BORDER_COLOR, "#1f2937"],
            startangle=90,
            wedgeprops=dict(width=0.35, edgecolor="none"),
        )
        commit_ax.text(0, 0, "Commits", ha="center", va="center", fontsize=14, color="#ffffff")

    def _draw_languages_bar(self, max_langs=7):
        from mpl_toolkits.axes_grid1.inset_locator import inset_axes
        if not self.langs or self.total_repos == 0:
            lang_ax = inset_axes(self.ax, width="85%", height="55%", bbox_to_anchor=(0.06, 0.15, 0.88, 0.40), bbox_transform=self.ax.transAxes, loc="center")
            lang_ax.set_axis_off()
            lang_ax.text(0.5, 0.5, "Dados de Linguagem Indisponíveis.", ha="center", va="center", fontsize=16, color="#ff4d6d", transform=lang_ax.transAxes)
            return
        top_langs = self.langs.most_common(max_langs)
        labels = [lang[0] for lang in top_langs]
        sizes = [lang[1] for lang in top_langs]
        percentages = [(s / self.total_repos) * 100 for s in sizes]
        labels.reverse()
        percentages.reverse()
        lang_ax = inset_axes(self.ax, width="85%", height="55%", bbox_to_anchor=(0.06, 0.15, 0.88, 0.40), bbox_transform=self.ax.transAxes, loc="center")
        lang_ax.set_facecolor(CARD_FACE_COLOR)
        bars = lang_ax.barh(labels, percentages, height=0.6, color=CARD_BORDER_COLOR)
        lang_ax.set_xticks([])
        lang_ax.tick_params(axis="y", length=0, labelsize=14, pad=30)
        for bar in bars:
            width = bar.get_width()
            lang_ax.text(width + 3.5, bar.get_y() + bar.get_height() / 2, f"{width:.1f}%", va="center", color=KPI_TEXT_COLOR, fontsize=12, fontweight="bold")
        lang_ax.spines["right"].set_visible(False)
        lang_ax.spines["top"].set_visible(False)
        lang_ax.spines["left"].set_color("#334155")
        lang_ax.spines["bottom"].set_color("#334155")

    def _add_footer(self):
        now = datetime.now().strftime("%d/%m/%Y %H:%M")
        self.ax.text(0.50, 0.08, f"Atualizado automaticamente em {now}", color="#6b7280", fontsize=10, ha="center", transform=self.ax.transAxes)

    def generate(self, output_path=OUTPUT_PATH):
        self._collect_data()
        self._setup_figure()
        self._draw_layout()
        self._draw_kpis()
        self._draw_commits_donut()
        self._draw_languages_bar()
        self._add_footer()
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        plt.savefig(output_path, dpi=300)
        plt.close(self.fig)


if __name__ == "__main__":
    generator = DashboardGenerator(username="Domisnnet")
    generator.generate()