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
    def test_solver_recovers_from_each_route_position(self, _sleep):
        class ComputeNodeStub:
            def get_task(self):
                return type("Task", (), {"parameters": {"op": "add", "a": 2, "b": 3}, "task_id": "t1"})()

            def submit(self, task_id, answer):
                self.submission = (task_id, answer)
                return {"correct": True, "reward": {"amount": 1, "type": "rp"}}

        route = RuntimeRoute(
            ["e1", "e2", "e3"],
            [
                {"id": "e1", "source": "hub", "target": "relay-1"},
                {"id": "e2", "source": "relay-1", "target": "relay-2"},
                {"id": "e3", "source": "relay-2", "target": "compute"},
            ],
        )

        for start, forward_edges in (
            ("hub", ["e1", "e2", "e3"]),
            ("relay-1", ["e2", "e3"]),
            ("relay-2", ["e3"]),
            ("compute", []),
        ):
            with self.subTest(start=start):
                worker = IdleWorker()
                worker.route = route
                worker.current_node = start
                worker.moves = []
                worker.warn = worker.info
                worker.error = worker.info
                node = ComputeNodeStub()

                def move(edge):
                    worker.moves.append(str(edge))
                    worker.current_node = edge.target if worker.current_node == edge.source else edge.source

                worker.move = move
                worker.get_current_node = lambda: node
                worker.solve = lambda params: Solver.solve(worker, params)

                with patch("workers.solver.ComputeNode", ComputeNodeStub):
                    Solver.on_startup(worker)
                    Solver.on_loop(worker)

                self.assertEqual(worker.moves, forward_edges + ["e3", "e2", "e1"])
                self.assertEqual(worker.current_node, "hub")
                self.assertEqual(node.submission, ("t1", 5))
                self.assertEqual(worker.solves, 1)

    @patch("workers.solver.time.sleep")
    def test_solver_suspends_with_one_error_when_current_node_is_off_route(self, sleep):
        worker = IdleWorker()
        worker.route = RuntimeRoute(
            ["e1"],
            [{"id": "e1", "source": "hub", "target": "compute"}],
        )
        worker.current_node = "other-relay"
        worker.warn = worker.info
        worker.error = worker.info
        worker.move = lambda _edge: self.fail("off-route worker must not guess a move")
        worker.get_current_node = lambda: self.fail("off-route worker must not request a task")

        Solver.on_startup(worker)
        Solver.on_loop(worker)
        Solver.on_loop(worker)

        errors = [message for message in worker.messages if "not on configured route" in message]
        self.assertEqual(len(errors), 1)
        self.assertIn("other-relay", errors[0])
        self.assertIn("redeploy", errors[0].lower())
        self.assertEqual(sleep.call_count, 2)

    def test_solver_handles_live_typeof_puzzle_values(self):
        cases = (
            (42, "int"),
            (3.14, "float"),
            ("hello", "str"),
            (True, "bool"),
            ([1, 2, 3], "list"),
            ({"a": 1}, "dict"),
        )
        worker = IdleWorker()
        for value, expected in cases:
            with self.subTest(value=value):
                self.assertEqual(Solver.solve(worker, {"op": "typeof", "value": value}), expected)


if __name__ == "__main__":
    unittest.main()
