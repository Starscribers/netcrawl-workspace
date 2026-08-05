import unittest
from unittest.mock import patch

from workers.guardian import Guardian
from workers.handler import Handler
from workers.scout import Scout
from workers.solver import Solver
from netcrawl.runtime import RuntimeRoute


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

    @patch("workers.solver.time.sleep")
    def test_solver_traverses_injected_route_and_submits(self, _sleep):
        class ComputeNodeStub:
            def get_task(self):
                return type("Task", (), {"parameters": {"op": "add", "a": 2, "b": 3}, "task_id": "t1"})()

            def submit(self, task_id, answer):
                self.submission = (task_id, answer)
                return {"correct": True, "reward": {"amount": 1, "type": "rp"}}

        worker = IdleWorker()
        worker.route = RuntimeRoute(
            ["e1", "e2"],
            [{"id": "e1", "source": "hub", "target": "relay"}, {"id": "e2", "source": "relay", "target": "compute"}],
        )
        worker._current_node = "hub"
        worker.moves = []
        worker.warn = worker.info
        worker.error = worker.info
        node = ComputeNodeStub()

        def move(target):
            worker.moves.append(target)
            worker._current_node = "compute" if len(worker.moves) == 1 else "hub"

        worker.move = move
        worker.get_current_node = lambda: node
        worker.solve = lambda params: Solver.solve(worker, params)

        with patch("workers.solver.ComputeNode", ComputeNodeStub):
            Solver.on_startup(worker)
            Solver.on_loop(worker)

        self.assertIs(worker.moves[0], worker.route)
        self.assertEqual([str(edge) for edge in worker.moves[1]], ["e2", "e1"])
        self.assertEqual(node.submission, ("t1", 5))
        self.assertEqual(worker.solves, 1)


if __name__ == "__main__":
    unittest.main()
