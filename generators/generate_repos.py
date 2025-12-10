import matplotlib.pyplot as plt
from utils.plot_theme import apply_dark_tech_theme
from utils.github_api import get_repos, get_commits_per_repo

USERNAME = "Domisnnet"

def generate_repos_graph():
    apply_dark_tech_theme()

    repos = get_repos(USERNAME)

    repo_commits = {}

    for repo in repos:
        name = repo["name"]
        commits = get_commits_per_repo(repo["full_name"])

        if isinstance(commits, list):
            repo_commits[name] = len(commits)

    sorted_repos = sorted(repo_commits.items(), key=lambda x: x[1], reverse=True)[:5]

    names = [i[0] for i in sorted_repos]
    values = [i[1] for i in sorted_repos]

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.barh(names, values)
    ax.set_title("Top 5 Repositórios Mais Ativos")

    plt.tight_layout()
    plt.savefig("output/repos.png", dpi=300)
    plt.close()

if __name__ == "__main__":
    generate_repos_graph()