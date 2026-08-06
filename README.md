# NetCrawl Workspace

Starter workspace for **NetCrawl** — a programmable idle game where you write Python workers to automate a network.

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/Starscribers/netcrawl-workspace/tree/main?quickstart=1)

## Quick Start

```bash
# 1. Clone this workspace
git clone https://github.com/Starscribers/netcrawl-workspace.git workspace
cd workspace

# 2. Install dependencies (installs the pinned SDK and test tools from PyPI)
uv sync

# 3. Edit main.py — set the correct server URL (check the Connect button in-game)
# 4. Start the code server
uv run main.py
```

## GitHub Codespaces

Use the badge above to create or resume a Codespace directly from this repository's `main` branch. The repository's default devcontainer starts with Python 3.12, installs the Python extension and `uv`, creates the pinned `.venv`, selects `.venv/bin/python` as the interpreter, and configures **NetCrawl: Start Code Server** in VS Code.

After the Codespace is ready:

1. Open `main.py` and paste the server URL and API key shown by NetCrawl's **Connect** dialog.
2. Open **Run and Debug** and click the green play button (or press F5). You can also run `uv run main.py` in the terminal.
3. If setup fails, run `uv sync --frozen` in the repository root. If that still fails, rebuild the container from the Command Palette with **Codespaces: Rebuild Container**; do not run from a partially installed environment.

The game server must be reachable from the Codespace. `localhost` refers to the Codespace itself, so a game running only on your own computer needs a publicly reachable development URL or the local clone workflow above.

## Structure

```
workspace/
├── main.py              # Entry point — registers workers with the game server
├── workers/
│   ├── helloworker.py   # Minimal example (no equipment)
│   ├── miner.py         # Mining worker (Pickaxe + Edge)
│   ├── guardian.py      # Patrol & repair worker (Shield + Sensor)
│   ├── scout.py         # Exploration worker (Route + Sensor)
│   ├── handler.py       # API request handler
│   └── solver.py        # Compute puzzle solver
├── .vscode/tasks.json   # Start code server task
├── .vscode/launch.json  # One-click Run and Debug configuration
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
        if any(item.type == "bad_data" for item in self.holding):
            self.discard("bad_data")

        self.move(self.edge)            # mine → hub
        if self.holding:
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
| `self.discard(type)` | Throw away held items of a type |
| `self.scan()` | Scan adjacent nodes → `List[ScannedNode]` |
| `self.repair(node_id)` | Repair infected node |
| `self.info(msg)` | Log message (visible in UI) |
| `self.holding` | Currently held items (`list[Drop]`) |

## License

MIT
