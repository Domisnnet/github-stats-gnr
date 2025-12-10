import matplotlib.pyplot as plt
from utils.plot_theme import apply_dark_tech_theme
from utils.github_api import get_repos, get_commit_activity
from datetime import datetime

USERNAME = "Domisnnet"

def generate_commits_graph():
    apply_dark_tech_theme()

    repos = get_repos(USERNAME)

    total_commits = 0

    for repo in repos:
        activity = get_commit_activity(repo["full_name"])
        if isinstance(activity, list):
            for week in activity:
                total_commits += week["total"]

    fig, ax = plt.subplots(figsize=(8, 3))

    ax.bar(["Commits no ano"], [total_commits], width=0.5)
    ax.set_title("Commits no Último Ano", pad=12)

    plt.tight_layout()
    plt.savefig("output/commits.png", dpi=300)
    plt.close()

if __name__ == "__main__":
    generate_commits_graph()
