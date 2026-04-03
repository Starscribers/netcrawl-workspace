from netcrawl import WorkerClass

class HelloWorker(WorkerClass):
    class_name = "Hello"
    class_id = "hello"

    def on_startup(self):
        self.info("Hello, World!")

    def on_loop(self):
        self.info("I am alive!")
        import time; time.sleep(5)
        raise