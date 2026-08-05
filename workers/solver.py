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
        self.route_suspended = False
        self.info(f"Solver online! Route: {self.route}")

    def on_loop(self):
        if self.route_suspended:
            time.sleep(5)
            return

        if not self.route:
            self.error("No route configured")
            time.sleep(5)
            return

        route_nodes = self.route.nodes
        if self.current_node not in route_nodes:
            self.error(
                f"Current node {self.current_node!r} is not on configured route "
                f"{route_nodes!r}; solver suspended. Return it to the route or redeploy it."
            )
            self.route_suspended = True
            time.sleep(5)
            return

        current_index = route_nodes.index(self.current_node)
        for edge in self.route.edges[current_index:]:
            self.move(edge)

        node = self.get_current_node()
        if not isinstance(node, ComputeNode):
            self.warn(f"Not a compute node: {node.type}")
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
        for edge in reversed(self.route):
            self.move(edge)

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
