import pytest
from datetime import date, timedelta

from domain import model
from adapters import repository
from service_layer import services, unit_of_work

today = date.today()
tomorrow = today + timedelta(days=1)
later = tomorrow + timedelta(days=10)

class FakeRepository(repository.AbstractRepository):
    def __init__(self, batches):
        self._batches = set(batches)

    @staticmethod
    def for_batch(ref, sku, qty, eta=None):
        return FakeRepository([
            model.Batch(ref, sku, qty, eta)
        ])

    def add(self, batch):
        self._batches.add(batch)

    def get(self, reference):
        return next(b for b in self._batches if b.reference == reference)

    def list(self):
        return list(self._batches)


class FakeSession():
    commited = False

    def commit(self):
        self.commited = True

class FakeUnitOfWork(unit_of_work.AbstractUnitOfWork):

    def __init__(self):
        self.batches = FakeRepository([])
        self.commited = False
    
    def commit(self):
        self.commited = True

    def rollback(self):
        pass

    

# service layer tests
def test_allocate_returns_allocation():
    uow = FakeUnitOfWork()

    services.add_batch("b1", "COMPLICATED-LAMP", 100, None, uow)
    result = services.allocate("o1", "COMPLICATED-LAMP", 10, uow)
    assert result == 'b1'

def test_allocate_error_for_invalid_sku():
    uow = FakeUnitOfWork()
    services.add_batch("b1", "AREALSKU", 100, None, uow)

    with pytest.raises(services.InvalidSku, match="Invalid sku NONEXISTENTSKU"):
        services.allocate("o1", "NONEXISTENTSKU", 10, uow)


def test_add_batch():
    uow = FakeUnitOfWork()
    services.add_batch("b1", "CRUNCHY-ARMCHAIR", 100, None, uow)
    assert uow.batches.get("b1") is not None
    assert uow.commited

def test_allocate_commits():
    uow = FakeUnitOfWork()
    services.add_batch("b1", "MIRROR", 100, None, uow)
    services.allocate("o1", "MIRROR", 10, uow)
    assert uow.commited

# domain layer tests
def test_prefer_current_stock_batches_to_shipments():
    in_stock_batch = model.Batch("in-stock-batch", "RETRO-CLOCK", 100, eta=None)
    shipment_batch = model.Batch("shipment-batch", "RETRO-CLOCK", 100, eta=tomorrow)
    line = model.OrderLine("oref", "RETRO-CLOCK", 10)

    model.allocate(line, [in_stock_batch, shipment_batch])

    assert in_stock_batch.available_quantity == 90
    assert shipment_batch.available_quantity == 100 




