"""
HelloWorker — minimal example

Logs a message every 5 seconds. No equipment needed.
"""
import time
from netcrawl import WorkerClass


class HelloWorker(WorkerClass):
    class_name = "HelloWorker"
    class_id = "helloworker"

    def on_startup(self):
        self.info("Hello, World!")

    def on_loop(self):
        self.info("I am alive!")
        time.sleep(5)
