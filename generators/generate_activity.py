import matplotlib.pyplot as plt
from utils.plot_theme import apply_dark_tech_theme
from utils.github_api import get_repos, get_commit_activity
from datetime import datetime

USERNAME = "Domisnnet"

def generate_monthly_activity():
    apply_dark_tech_theme()

    repos = get_repos(USERNAME)
    monthly = [0]*12

    for repo in repos:
        activity = get_commit_activity(repo["full_name"])
        if isinstance(activity, list):
            for week in activity:
                date = datetime.fromtimestamp(week["week"])
                if date.year == datetime.now().year:
                    monthly[date.month-1] += week["total"]

    months = ["Jan","Fev","Mar","Abr","Mai","Jun","Jul","Ago","Set","Out","Nov","Dez"]

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(months, monthly, linewidth=2)

    ax.set_title("Atividade Mensal")

    plt.tight_layout()
    plt.savefig("output/activity.png", dpi=300)
    plt.close()

if __name__ == "__main__":
    generate_monthly_activity()