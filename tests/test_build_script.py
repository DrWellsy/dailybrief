from __future__ import annotations

import platform
import pytest

from scripts.build_binary import get_binary_name


def test_get_binary_name() -> None:
    name = get_binary_name()
    assert "dailybrief-" in name
    if platform.system() == "Windows":
        assert name.endswith(".exe")
        assert "windows" in name
    elif platform.system() == "Darwin":
        assert "macos" in name
    elif platform.system() == "Linux":
        assert "linux" in name
