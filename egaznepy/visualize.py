# visualization aids
import os
from collections import defaultdict
from collections.abc import Iterable
from pathlib import Path

import cycler
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.axes import Axes
from matplotlib.figure import Figure

# might be useful for figure size adjustments
golden_ratio = (1 + 5**0.5) / 2

# load plot styling
def get_custom_cycler():
    return cycler.cycler(
        "color",
        [
            "#1f77b4",
            "#ff7f0e",
            "#2ca02c",
            "#d62728",
            "#9467bd",
            "#8c564b",
            "#e377c2",
            "#7f7f7f",
            "#bcbd22",
            "#17becf",
        ],
    )


def apply_plot_style(font_scale: int = 0.7):
    """Applies my personal academic plot style. Requires LaTeX for correct
    operation.
    """
    plt.rcdefaults()
    sns.set_style(style="white")
    rc = {
        "axes.grid": True,
        "grid.color": "gray",
        "grid.linestyle": "dotted",
        "grid.linewidth": 0.8,
        "grid.alpha": 0.5,
        "lines.linewidth": 0.8,
        "figure.autolayout": True,
        # Use LaTeX to write all text
        "text.usetex": True,
        "font.family": "serif",
        "xtick.major.width": 0.5,
        "ytick.major.width": 0.5,
        "xtick.bottom": True,
        "xtick.major.pad": 2,
        "ytick.major.pad": 2,
        "xtick.major.size": 3,
        "ytick.major.size": 3,
        "ytick.left": True,
        "figure.dpi": 100,
        "legend.frameon": False,
        "lines.markerfacecolor": "gray",
        "lines.markeredgecolor": "black",
        "patch.force_edgecolor": "false",
        "text.latex.preamble": r"""
    \usepackage{lmodern}
    \usepackage{anyfontsize}
    \usepackage{stackengine}
    \mathchardef\minus="2D
    """,
        "pgf.preamble": r"""
    \usepackage{lmodern}
    \usepackage{stackengine}
    \usepackage{anyfontsize}
    \mathchardef\minus="2D
    """,
        "axes.spines.right": False,
        "axes.spines.top": False,
    }
    # plot scaling issue
    mpl.rcParams.update(rc)
    sns.set_context("paper", font_scale=font_scale, rc=rc)


def legend_with_unique_entries(fig: Figure):
    """Putting a legend to a figure with multiple subplots is troublesome as
    identical elements might be repeated. Filter out already defined entries
    and re-create a legend.

    Args:
        fig (Figure): the matplotlib figure object to operate on
    """
    ax = fig.gca()
    handles, labels = ax.get_legend_handles_labels()
    unique = [
        (h, l) for i, (h, l) in enumerate(zip(handles, labels)) if l not in labels[:i]
    ]
    ax.legend(*zip(*unique))


class FigureWriter:
    """Keeps track of figures root and writes figures in multiple
    useful formats (default: .pdf, .png, .pgf)
    """

    def __init__(self, figures_root: Path, extensions: list):
        self.figures_root = figures_root
        self.extensions = extensions

    def write(self, file_name: str, fig: Figure = None, tight: bool = True):
        """Writes a figure `fig` to the folder `self.figures_root /
        file_name.extension` for each extension in self.extensions

        Args:
        file_name (str): The file name (possibly in subfolders that may
        or may not exist in figures_root)
            fig (Figure, optional): A Matplotlib figure to be saved. If None then
        plt.gcf() is saved.
            tight (bool): Whether the saved plot should have a tight bbox
        """
        kwargs = {}
        if tight:
            kwargs["bbox_inches"] = "tight"
            kwargs["pad_inches"] = 0
        if fig is None:
            fig = plt.gcf()
        for extension in self.extensions:
            path = (self.figures_root / file_name).with_suffix(extension)
            # make new folder in case it does not exist
            print(path)
            path.parent.mkdir(parents=True, exist_ok=True)
            fig.savefig(path, **kwargs)


def apply_hatch_barplot(obj: Axes, hatches: Iterable = None):
    """This function manually adds different (and unique) hatches to
    barplots. Useful while trying to obtain black & white printable plots.

    Args:
        obj (Axes): The axes object on which barplots are already plotted.
        hatches (Iterable): Style of hatches, a rich assortment is available
            by default.
    """
    if hatches is None:
        hatches = ["", "///", "+", "x", "-", "*", "o"]
    hatches = iter(cycler.cycler("h", hatches))

    # keep a dict of matched color-hatches
    hatch_dict = defaultdict(lambda: next(hatches)["h"])
    for p in obj.patches:
        p.set_hatch(hatch_dict[p.get_facecolor()])
        p.set_edgecolor("white")
