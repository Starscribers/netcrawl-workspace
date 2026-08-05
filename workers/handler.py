"""Handler worker — processes requests from API nodes."""

import time
from netcrawl import WorkerClass, Route


class Handler(WorkerClass):
    class_name = "Handler"
    class_id = "handler"

    # Optional advanced route to an auth node.
    # auth_node = Route("auth route")

    def on_startup(self):
        self.info("Handler ready — waiting for requests")

    def on_loop(self):
        req = self.poll_request()
        if req is None:
            time.sleep(0.5)
            return

        self.info(f"Got request: {req.type} | auth={'yes' if req.has_token else 'NO'}")
        if not req.has_token:
            self.reject(req.id, 401)
            self.warn(f"Rejected unauthenticated {req.type} → 401")
            return

        if req.type == "compute":
            self._handle_compute(req)
        elif req.type == "echo":
            self.respond(req.id, {"value": req.body.get("value")})
        else:
            self.reject(req.id, 400)
            self.warn(f"Unknown request type: {req.type}")

    def _handle_compute(self, req):
        op = req.body.get("op")
        a = req.body.get("a", 0)
        b = req.body.get("b", 0)
        try:
            if op == "add":
                result = a + b
            elif op == "sub":
                result = a - b
            elif op == "mul":
                result = a * b
            elif op == "max":
                result = max(a, b)
            elif op == "mod":
                result = a % b if b != 0 else 0
            else:
                self.reject(req.id, 400)
                self.warn(f"Unknown op: {op}")
                return
            self.respond(req.id, {"result": result})
            self.info(f"compute/{op}({a},{b}) = {result} ✓")
        except Exception as exc:
            self.reject(req.id, 500)
            self.error(f"Compute error: {exc}")
