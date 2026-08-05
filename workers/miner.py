"""
Miner — basic mining worker

Mining loop: move along edge to resource node, mine, collect, move back, deposit.

Deploy requirements:
  - pickaxe: 1x Pickaxe (from inventory)
  - edge:    select one edge connecting Hub to a mine
"""
from netcrawl import WorkerClass, Edge
from netcrawl.items.equipment import Pickaxe


class Miner(WorkerClass):
    class_name = "Miner"
    class_id = "miner"

    pickaxe = Pickaxe()
    edge = Edge("hub ↔ mine")

    def on_loop(self):
        self.move(self.edge)            # hub → mine
        self.pickaxe.mine_and_collect() # mine + pick up

        # Filter bad data
        if any(item.type == "bad_data" for item in self.holding):
            self.discard("bad_data")
            self.info("Discarded bad data")

        self.move(self.edge)            # mine → hub
        if self.holding:
            self.deposit()
