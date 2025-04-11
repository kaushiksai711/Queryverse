import warnings
import pytest

# Suppress httpx deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning, module="httpx")

@pytest.fixture(autouse=True)
def suppress_warnings():
    """Automatically suppress httpx deprecation warnings for all tests"""
    warnings.filterwarnings("ignore", category=DeprecationWarning, module="httpx") 