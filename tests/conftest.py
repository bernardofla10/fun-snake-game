"""Run pygame tests without an interactive display or audio device."""

import pytest


@pytest.fixture(autouse=True)
def headless_sdl(monkeypatch: pytest.MonkeyPatch) -> None:
    """Select SDL dummy drivers before pygame is initialized."""
    monkeypatch.setenv("SDL_VIDEODRIVER", "dummy")
    monkeypatch.setenv("SDL_AUDIODRIVER", "dummy")
