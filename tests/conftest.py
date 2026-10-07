from pathlib import Path

import pytest

from portfolio.loader import read_transactions_csv

SAMPLE_FILE = Path(__file__).parent.parent / "sample_data.csv"


@pytest.fixture
def sample_tx():
    """The 13 transactions in sample_data.csv."""
    return read_transactions_csv(SAMPLE_FILE)
