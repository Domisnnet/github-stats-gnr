import matplotlib.pyplot as plt
from utils.plot_theme import apply_dark_tech_theme
from utils.github_api import get_repos

USERNAME = "Domisnnet"

def generate_language_graph():
    apply_dark_tech_theme()

    repos = get_repos(USERNAME)

    lang_count = {}

    for repo in repos:
        if repo["language"]:
            lang = repo["language"]
            lang_count[lang] = lang_count.get(lang, 0) + 1

    labels = list(lang_count.keys())
    sizes = list(lang_count.values())

    fig, ax = plt.subplots(figsize=(6, 6))

    ax.pie(sizes, labels=labels, autopct="%1.1f%%")

    ax.set_title("Linguagens Mais Utilizadas")

    plt.tight_layout()
    plt.savefig("output/languages.png", dpi=300)
    plt.close()

if __name__ == "__main__":
    generate_language_graph()
