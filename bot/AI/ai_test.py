from fastapi.testclient import TestClient
from unittest.mock import AsyncMock
import pytest


def func(x):
    return x + 1

def test_answer():
    assert func(3) == 4




