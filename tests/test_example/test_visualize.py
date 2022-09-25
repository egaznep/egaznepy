"""Tests for hello function."""
import shutil
from pathlib import Path

import matplotlib as mpl
import pytest

import egaznepy.visualize as vis


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
