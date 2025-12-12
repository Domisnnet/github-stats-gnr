import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np

def apply_dark_tech_theme():
    # Definições globais de estilo
    plt.rcParams.update({
        "figure.facecolor": "#0A0A0D",
        "axes.facecolor": "#0A0A0D",
        "axes.edgecolor": "#1F1F2B",
        "axes.labelcolor": "#D9D9D9",
        "xtick.color": "#D9D9D9",
        "ytick.color": "#D9D9D9",
        "text.color": "#FFFFFF",
        "axes.titleweight": "bold",
        "axes.titlesize": 18,
        "font.size": 13,
        "savefig.facecolor": "#0A0A0D",
        "savefig.edgecolor": "#0A0A0D"
    })

def apply_vertical_gradient(ax, color_top="#0F0F1A", color_bottom="#0A0A0D"):
    import matplotlib.patches as patches
    import matplotlib.colors as mcolors

    gradient = np.linspace(0, 1, 256)
    gradient = np.vstack((gradient, gradient))

    ax.imshow(
        gradient,
        aspect='auto',
        cmap=mcolors.LinearSegmentedColormap.from_list(
            "", [color_bottom, color_top]
        ),
        extent=[-1, 1, -1, 1],
        zorder=0
    )