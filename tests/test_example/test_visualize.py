"""Tests for hello function."""

import shutil
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import pytest

import egaznepy.visualize as vis


@pytest.fixture()
def figure():
    fig, axs = plt.subplots(2, 1)
    cm1 = vis.librosa.display.specshow(vis.np.random.randn(100, 100), ax=axs[0])
    cm2 = vis.librosa.display.specshow(vis.np.random.randn(100, 100), ax=axs[1])
    return fig, axs, [cm1, cm2]


@pytest.mark.parametrize(
    ("file_name"),
    [("asd/efg"), ("efg"), ("efg.png")],
)
def test_figsave(file_name):
    # figure creation
    vis.apply_plot_style()
    mpl.rcParams["text.usetex"] = False  # disable LaTeX
    figures_root = Path("test_output_temp")
    extensions = [".pgf", ".pdf", ".png"]

    # generate mock figure and write
    fig = vis.Figure()
    writer = vis.FigureWriter(figures_root, extensions)
    writer.write(file_name, fig)

    # test if files exist
    for e in extensions:
        assert (figures_root / file_name).with_suffix(e).exists()

    # do not leave garbage
    shutil.rmtree(figures_root)


@pytest.mark.parametrize(
    ("fig", "expected_num_entries"),
    [
        (vis.Figure(), 0),
        # todo: add more test cases: e.g. reduce
        # subplot of 4 to 1 entry
    ],
)
def test_legend_filter(fig, expected_num_entries):
    vis.apply_plot_style()
    mpl.rcParams["text.usetex"] = False  # disable LaTeX
    vis.legend_with_unique_entries(fig)
    assert len(fig.gca().get_legend_handles_labels()[0]) == expected_num_entries


def test_update_specshow():
    fig = vis.Figure()
    cm = vis.librosa.display.specshow(vis.np.random.randn(100, 100), ax=fig.gca())
    vis.update_specshow(
        cm,
        vis.np.random.randn(100, 200),
        sr=22050,
        hop_length=512,
        x_axis="time",
        y_axis="linear",
    )


def test_add_or_update_colorbar(figure):
    fig, axs, cms = figure
    # add colorbar
    cbar = vis.add_or_update_colorbar(fig, axs[0], cms[0])
    cbar2 = vis.add_or_update_colorbar(fig, axs[1], cms[1])

    # update colorbar
    cbar3 = vis.add_or_update_colorbar(fig, axs[0], cms[0])
    assert cbar3 == cbar  # the new colorbar should be the same as the old one
