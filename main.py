"""
NetCrawl Workspace — Entry Point
================================
Clone this repository and start editing.

Usage:
    uv sync
    uv run main.py

The code server will:
  1. Register all worker classes with the game server
  2. Open a persistent channel to receive deploy commands
  3. Fork subprocesses when you deploy workers from the UI
"""
import os
from pathlib import Path

from netcrawl import NetCrawl

from scripts.bootstrap_compute_starters import ensure_compute_starters
from workers.miner import Miner
from workers.guardian import Guardian
from workers.scout import Scout
from workers.handler import Handler
from workers.helloworker import HelloWorker

app = NetCrawl(
    api_key="sk-local",             # local 版隨便填，cloud 版換成你的 API key
    server=os.getenv("NETCRAWL_SERVER", "http://localhost:4800"),  # game server 位置
)

# Safe on every start: a workspace refresh repairs only absent Compute Lab
# starters and deliberately leaves player-authored files byte-for-byte intact.
ensure_compute_starters(Path(__file__).resolve().parent)

app.register(Miner)
app.register(Guardian)
app.register(Scout)
app.register(Handler)
app.register(HelloWorker)

# 新增你的 worker class 就在這裡 register 就好
# from workers.my_custom_worker import MyWorker
# app.register(MyWorker)
# To automate a Compute node after solving it once in Compute Lab:
# from workers.solver import Solver
# app.register(Solver)

if __name__ == "__main__":
    app.run()
