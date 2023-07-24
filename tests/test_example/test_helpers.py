"""Tests for hello function."""
import shutil
from pathlib import Path

import matplotlib as mpl
import numpy as np
import pytest

from egaznepy.helpers import align_signals, invoke_command


@pytest.mark.parametrize(
    ("command", "result"),
    [
        ("echo TEST", "TEST"),
    ],
)
def test_invoke(command, result):
    assert result in invoke_command(command)


_case1 = np.random.randn(1000)
_case2 = np.roll(_case1, 10)
_case3 = np.roll(_case1, -10)
_case1_ext1 = np.append(_case1, np.random.randn(100))
_case1_ext2 = np.append(_case1, np.zeros(100))
_case1_ext3 = np.append(np.zeros(100), _case1)
_case1_ext3 = np.append(_case1_ext3, np.zeros(100))


@pytest.mark.parametrize(
    ("x", "x_ref", "expected"),
    [
        (_case2, _case1, _case1),
        (_case3, _case1, _case1),
        (_case1, _case1, _case1),
        (_case1, _case1_ext1, _case1_ext1[: len(_case1)]),
        (_case1, _case1_ext2, _case1_ext2[: len(_case1)]),
        (_case1, _case1_ext3, _case1_ext3[: len(_case1)]),
    ],
)
def test_align(x: np.ndarray, x_ref: np.ndarray, expected: np.ndarray):
    result = align_signals(x, x_ref)
    if not np.alltrue(
        np.logical_or(np.isclose(result, expected), np.isclose(result, 0))
    ):
        import matplotlib.pyplot as plt

        plt.plot(result, label="result")
        plt.plot(expected, label="expected")
        plt.show()
    assert np.alltrue(
        np.logical_or(np.isclose(result, expected), np.isclose(result, 0))
    )
