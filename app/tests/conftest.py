"""Tests use short synthetic histories, so they run with the course's 5/9/18 and every step switched on."""
import sys
from pathlib import Path
import pytest
ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "skills" / "beedo-trade" / "scripts"), str(ROOT / "app")]
import analyze
from beedo_app import engine


@pytest.fixture(autouse=True)
def course_defaults():
    ma, off = analyze.MA, set(engine.OFF)
    analyze.MA = (5, 9, 18)
    engine.OFF.clear()
    yield
    analyze.MA = ma
    engine.OFF.clear(); engine.OFF.update(off)
