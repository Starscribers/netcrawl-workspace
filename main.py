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
from netcrawl import NetCrawl

from workers.miner import Miner
from workers.guardian import Guardian
from workers.scout import Scout
from workers.handler import Handler
from workers.helloworker import HelloWorker

app = NetCrawl(
    api_key="sk-local",             # local 版隨便填，cloud 版換成你的 API key
    server="http://localhost:4800",  # game server 位置
)

app.register(Miner)
app.register(Guardian)
app.register(Scout)
app.register(Handler)
app.register(HelloWorker)

# 新增你的 worker class 就在這裡 register 就好
# from workers.my_custom_worker import MyWorker
# app.register(MyWorker)

if __name__ == "__main__":
    app.run()
