# NetCrawl Workspace

Starter workspace for [NetCrawl](https://github.com/Starscribers/netcrawl2) — a programmable idle game where you write Python workers to automate a network.

## Quick Start

```bash
# 1. Clone this workspace
git clone https://github.com/Starscribers/netcrawl-workspace.git workspace
cd workspace

# 2. Install dependencies
uv sync

# 3. Start the code server (game server must be running first)
uv run main.py
```

## Structure

```
workspace/
├── main.py           # Entry point — registers workers with the game server
├── workers/
│   ├── helloworker.py   # Minimal example
│   ├── miner.py         # Mining worker (Pickaxe + Route)
│   ├── guardian.py       # Patrol & repair worker (Shield + Sensor)
│   └── scout.py         # Exploration worker (Route + Sensor)
└── pyproject.toml    # Python dependencies
```

## Writing Your Own Worker

```python
from netcrawl import WorkerClass, Edge
from netcrawl.items.equipment import Pickaxe

class MyMiner(WorkerClass):
    class_name = "My Miner"
    class_id = "my_miner"

    pickaxe = Pickaxe()
    route = Edge("mining route")

    def on_loop(self):
        self.move_edge(self.route)   # hub → mine
        self.pickaxe.mine()          # create drop
        self.collect()               # pick it up
        self.move_edge(self.route)   # mine → hub
        self.deposit()               # convert to resources
```

Then register it in `main.py`:

```python
from workers.my_miner import MyMiner
app.register(MyMiner)
```

## License

MIT
