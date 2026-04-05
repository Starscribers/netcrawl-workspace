# NetCrawl Workspace

Starter workspace for **NetCrawl** — a programmable idle game where you write Python workers to automate a network.

## Quick Start

```bash
# 1. Clone this workspace
git clone https://github.com/Starscribers/netcrawl-workspace.git workspace
cd workspace

# 2. Install dependencies (installs netcrawl-sdk from PyPI)
uv sync

# 3. Edit main.py — set the correct server URL (check the Connect button in-game)
# 4. Start the code server
uv run main.py
```

## Structure

```
workspace/
├── main.py              # Entry point — registers workers with the game server
├── workers/
│   ├── helloworker.py   # Minimal example (no equipment)
│   ├── miner.py         # Mining worker (Pickaxe + Edge)
│   ├── guardian.py      # Patrol & repair worker (Shield + Sensor)
│   └── scout.py         # Exploration worker (Route + Sensor)
└── pyproject.toml       # Python dependencies
```

## Writing Your Own Worker

```python
from netcrawl import WorkerClass, Edge
from netcrawl.items.equipment import Pickaxe

class MyMiner(WorkerClass):
    class_name = "My Miner"
    class_id = "my_miner"

    pickaxe = Pickaxe()
    edge = Edge("hub ↔ mine")

    def on_loop(self):
        self.move(self.edge)            # hub → mine
        self.pickaxe.mine_and_collect() # mine + pick up

        # Filter bad data
        if self.holding and self.holding.type == "bad_data":
            self.discard()
            return

        self.move(self.edge)            # mine → hub
        self.deposit()
```

Then register it in `main.py`:

```python
from workers.my_miner import MyMiner
app.register(MyMiner)
```

## SDK API

| Method | Description |
|---|---|
| `self.move(target)` | Move along Edge, Route, edge ID, or node ID |
| `self.collect()` | Pick up drop → `CollectResult` |
| `self.deposit()` | Deposit at Hub → `DepositResult` |
| `self.discard()` | Throw away held item |
| `self.scan()` | Scan adjacent nodes → `List[ScannedNode]` |
| `self.repair(node_id)` | Repair infected node |
| `self.info(msg)` | Log message (visible in UI) |
| `self.holding` | Currently held item (`Drop` with `.type`, `.amount`) |

## License

MIT
