"""Solver worker — handles compute-node puzzles."""

import math
import time
from netcrawl import WorkerClass, Route, ComputeNode


class Solver(WorkerClass):
    class_name = "Solver"
    class_id = "solver"

    route = Route("Path to compute node")

    def on_startup(self):
        self.solves = 0
        self.edge_id = self.route if isinstance(self.route, str) else None
        self.info(f"Solver online! Edge: {self.edge_id}")

    def on_loop(self):
        if not self.edge_id:
            self.error("No edge configured")
            time.sleep(5)
            return

        if self._current_node == "hub":
            self.move_edge(self.edge_id)

        node = self.get_current_node()
        if not isinstance(node, ComputeNode):
            self.warn(f"Not a compute node: {node.type}")
            self.move_edge(self.edge_id)
            time.sleep(3)
            return

        try:
            task = node.get_task()
        except ValueError as exc:
            self.warn(f"get_task() failed: {exc}")
            time.sleep(3)
            return

        answer = self.solve(task.parameters)
        if answer is None:
            self.warn(f"Unknown op: {task.parameters.get('op')}")
            time.sleep(2)
            return

        result = node.submit(task.task_id, answer)
        if result.get("correct"):
            reward = result.get("reward", {})
            self.solves += 1
            self.info(f"Correct! +{reward.get('amount', 0)} {reward.get('type', '')} (#{self.solves})")
        else:
            self.warn(f"Wrong! Expected {result.get('expected')}, got {answer}")
        self.move_edge(self.edge_id)

    def solve(self, params: dict):
        op = params.get("op", "")
        a = params.get("a", 0)
        b = params.get("b", 0)
        numbers = params.get("numbers", [])
        if op == "add": return a + b
        if op == "subtract": return a - b
        if op == "multiply": return a * b
        if op == "floor_divide": return a // b
        if op == "modulo": return a % b
        if op == "max": return max(numbers)
        if op == "sum": return sum(numbers)
        if op == "count_evens": return sum(1 for n in numbers if n % 2 == 0)
        if op == "length": return len(params.get("text", ""))
        if op == "power": return params.get("base", 0) ** params.get("exp", 1)
        if op == "fibonacci":
            n = params.get("n", 0)
            fa, fb = 0, 1
            for _ in range(n):
                fa, fb = fb, fa + fb
            return fa
        if op == "median":
            ordered = sorted(numbers)
            return ordered[len(ordered) // 2]
        if op == "unique_count": return len(set(numbers))
        if op == "gcd": return math.gcd(a, b)
        return None
