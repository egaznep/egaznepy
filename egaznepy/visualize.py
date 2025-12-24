# visualization aids
from typing import Optional

import os
from collections import defaultdict
from collections.abc import Iterable
from pathlib import Path

import cycler
import librosa.display
import matplotlib as mpl
import matplotlib.collections as mcoll
import matplotlib.pyplot as plt
import matplotlib.ticker as mplticker
import numpy as np
import seaborn as sns
from matplotlib.axes import Axes
from matplotlib.colorbar import Colorbar
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


def apply_plot_style(font_scale: float = 0.7):
    """Applies my personal academic plot style. Requires LaTeX for correct
    operation.
    """
    plt.rcdefaults()
    sns.set_style(style="white")
    sns.set_context("paper", font_scale=font_scale)
    plt.style.use(Path(__file__).parent / "egaznepy.mplstyle")


def legend_with_unique_entries(fig: Figure, ax: Optional[Axes] = None):
    """Putting a legend to a figure with multiple subplots is troublesome as
    identical elements might be repeated. Filter out already defined entries
    and re-create a legend.

    Args:
        fig (Figure): the matplotlib figure object to operate on
        ax (Axes, optional): the axis to place the figure on. by default it corresponds to fig.gca()
    """
    if ax is None:
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

    def write(self, file_name: str, fig: Optional[Figure] = None, tight: bool = True):
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
            path.parent.mkdir(parents=True, exist_ok=True)
            fig.savefig(str(path), **kwargs)


def apply_hatch_barplot(obj: Axes, hatches: Optional[Iterable] = None):
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


def update_specshow(
    cm: mcoll.QuadMesh,
    data: np.ndarray,
    sr: int,
    hop_length: int,
    x_axis: str,
    y_axis: str,
):
    """
    A convenience function to dynamically update a librosa specshow (e.g.,)
    in an interactive environment.

    Args:
        cm (mcoll.QuadMesh): The QuadMesh object to update.
        data (np.ndarray): The new data to display.
        sr (int): The sample rate of the audio.
        hop_length (int): The hop length used in the STFT.
        x_axis (str): The label for the x-axis.
        y_axis (str): The label for the y-axis.
    """
    # first obtain new coordinates
    x_coords = librosa.display.__mesh_coords(
        x_axis, None, data.shape[1], sr=sr, hop_length=hop_length
    )
    y_coords = librosa.display.__mesh_coords(
        y_axis, None, data.shape[0], sr=sr, hop_length=hop_length
    )
    X, Y, C, _ = cm.axes._pcolorargs(
        "pcolormesh", x_coords, y_coords, data, rasterized=True, shading="auto"
    )

    # update the QuadMesh object
    if y_axis not in ["off", None, "none"]:
        cm.axes.yaxis.set_tick_params(reset=True)
    cm._coordinates = np.stack([X, Y], axis=-1)
    cm.set_array(C)
    # if ticks were removed, this is necessary to have them again
    cm.axes.yaxis.set_major_locator(mplticker.AutoLocator())
    librosa.display.__decorate_axis(
        cm.axes.xaxis, x_axis, fmin=None, n_bins=data.shape[1], bins_per_octave=12
    )
    librosa.display.__decorate_axis(
        cm.axes.yaxis, y_axis, fmin=None, n_bins=data.shape[0], bins_per_octave=12
    )
    librosa.display.__scale_axes(cm.axes, x_axis, "x", tempo_min=None, tempo_max=None)
    librosa.display.__scale_axes(cm.axes, y_axis, "y", tempo_min=None, tempo_max=None)
    # set bounds
    minx, miny = np.min(cm._coordinates.reshape(-1, 2), axis=0)
    maxx, maxy = np.max(cm._coordinates.reshape(-1, 2), axis=0)
    cm.sticky_edges.x[:] = [minx, maxx]
    cm.sticky_edges.y[:] = [miny, maxy]
    corners = (minx, miny), (maxx, maxy)
    cm.axes.update_datalim(corners)
    cm.axes.set_xlim(minx, maxx)
    cm.axes.set_ylim(miny, maxy)
    return cm


def add_or_update_colorbar(
    fig: Figure,
    ax: Axes,
    mappable: mcoll.QuadMesh,
):
    """
    A convenience function to add or update a colorbar for a given mappable
    in a figure.

    Args:
        fig (Figure): The Matplotlib figure object.
        ax (Axes): The axes object where the mappable is displayed.
        mappable (mcoll.QuadMesh): The mappable object (e.g., QuadMesh) to
        associate the colorbar with.
    """
    # Check if a colorbar already exists for the given axes
    existing_colorbars = ax._colorbars if hasattr(ax, "_colorbars") else []

    if existing_colorbars:
        # Update the existing colorbar
        cbar = existing_colorbars[0]._colorbar
        cbar.update_normal(mappable)
    else:
        # Create a new colorbar
        cbar = fig.colorbar(mappable, ax=ax)
    return cbar


def unshare_axes_if_shared(ax: Axes):
    """
    Unshare the x and y axes of the given Axes object, if they are shared.

    Args:
        ax (Axes): The axes object to unshare.
    """
    if hasattr(ax, "_shared_axes"):
        ax._sharex = None
        ax._sharey = None
        ax._shared_axes["x"].remove(ax)
        ax._shared_axes["y"].remove(ax)


def format_coord(ax: Axes, x: float, y: float):
    """Format the coordinate display for a given Axes object.

    Args:
        ax (Axes): The axes object to format coordinates for.
        x (float): The x-coordinate.
        y (float): The y-coordinate.

    Returns:
        str: Formatted coordinate string.
    """
    twins = ax._twinned_axes.get_siblings(ax)
    if len(twins) == 1:
        s = "(x, y) = ({}, {})".format(
            "???" if x is None else ax.format_xdata(x),
            "???" if y is None else ax.format_ydata(y),
        )
    else:
        raise NotImplementedError(
            "custom format_coord is not implemented for axes with multiple twins."
        )
    # determine the value at (x, y)
    if ax.collections:
        coll = ax.collections[0]
        if isinstance(coll, mcoll.QuadMesh):
            # get the data array
            data = coll.get_array()
            # get the coordinates
            coords = coll._coordinates
            idx_x = np.searchsorted(coords[0, :, 0], x)
            idx_y = np.searchsorted(coords[:, 0, 1], y)
            val = data[idx_y - 1, idx_x - 1]
            s += f" [{val:.4f}]"
    return s


def monkey_patch_format_coord(ax: Axes):
    """Monkey patch the format_coord method of the given Axes object.

    Args:
        ax (Axes): The axes object to patch.
    """
    ax.format_coord = lambda x, y: format_coord(ax, x, y)
