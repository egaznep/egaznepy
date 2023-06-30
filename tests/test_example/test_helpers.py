"""Tests for hello function."""
import shutil
from pathlib import Path

import matplotlib as mpl
import pytest

from egaznepy.helpers import invoke_command


@pytest.mark.parametrize(
    ("command", "result"),
    [
        ("echo TEST", "TEST"),
    ],
)
def test_invoke(command, result):
    assert result in invoke_command(command)
