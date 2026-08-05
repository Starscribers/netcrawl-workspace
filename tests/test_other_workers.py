import unittest
from unittest.mock import patch

from workers.guardian import Guardian
from workers.handler import Handler
from workers.scout import Scout


class IdleWorker:
    def __init__(self):
        self.messages = []

    def info(self, message):
        self.messages.append(message)


class WorkerExampleSmokeTest(unittest.TestCase):
    @patch("workers.guardian.time.sleep")
    def test_guardian_handles_empty_scan(self, _sleep):
        worker = IdleWorker()
        worker.scan = lambda: []
        Guardian.on_loop(worker)
        self.assertIn("Network clean, standing by...", worker.messages)

    @patch("workers.scout.time.sleep")
    def test_scout_handles_empty_exploration(self, _sleep):
        worker = IdleWorker()
        worker.discovered = set()
        worker.sensor = type("Sensor", (), {"explore": lambda _self: []})()
        worker.route = []
        worker.move = lambda _edge: self.fail("empty route must not move")
        Scout.on_loop(worker)

    @patch("workers.handler.time.sleep")
    def test_handler_handles_empty_request_queue(self, _sleep):
        worker = IdleWorker()
        worker.poll_request = lambda: None
        Handler.on_loop(worker)


if __name__ == "__main__":
    unittest.main()
