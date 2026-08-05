import unittest

from netcrawl import BadData, DataFragment
from workers.miner import Miner


class FakePickaxe:
    def __init__(self, calls):
        self.calls = calls

    def mine_and_collect(self):
        self.calls.append("mine_and_collect")


class FakeMiner:
    edge = "e1"

    def __init__(self, holding):
        self.calls = []
        self.holding = holding
        self.pickaxe = FakePickaxe(self.calls)

    def move(self, edge):
        self.calls.append(("move", edge))

    def discard(self, item_type=None):
        self.calls.append(("discard", item_type))
        self.holding = [item for item in self.holding if item.type != "bad_data"]

    def deposit(self):
        self.calls.append("deposit")
        self.holding = []

    def info(self, message):
        self.calls.append(("info", message))


class MinerExampleTest(unittest.TestCase):
    def run_loop(self, holding):
        worker = FakeMiner(holding)
        Miner.on_loop(worker)
        return worker

    def test_bad_data_is_discarded_from_list_and_worker_returns_home(self):
        worker = self.run_loop([BadData(type="bad_data", count=1)])
        self.assertIn(("discard", "bad_data"), worker.calls)
        self.assertEqual(worker.calls.count(("move", "e1")), 2)

    def test_good_data_is_deposited(self):
        worker = self.run_loop([DataFragment(type="data_fragment", count=1)])
        self.assertIn("deposit", worker.calls)
        self.assertNotIn(("discard", "bad_data"), worker.calls)

    def test_mixed_holding_discards_bad_data_and_deposits_good_data(self):
        worker = self.run_loop([
            BadData(type="bad_data", count=1),
            DataFragment(type="data_fragment", count=2),
        ])
        self.assertIn(("discard", "bad_data"), worker.calls)
        self.assertIn("deposit", worker.calls)

    def test_empty_holding_does_not_use_item_attributes(self):
        worker = self.run_loop([])
        self.assertNotIn(("discard", "bad_data"), worker.calls)


if __name__ == "__main__":
    unittest.main()
