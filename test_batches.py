from datetime import date, timedelta
import pytest

from model import Batch, OrderLine

today = date.today()
tomorrow = today + timedelta(days=1)
later = tomorrow + timedelta(days=10)

def test_allocating_to_a_batch_reduces_available_quantity():
    batch = Batch("batch-001", "SMALL-TABLE", qty=20, eta=today)
    line = OrderLine("order-ref", "SMALL-TABLE", 2)

    batch.allocate(line)

    assert batch.available_quantity == 18