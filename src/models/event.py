class EventEmitter:
    def __init__(self):
        self.subs = []

    def subscribe(self, method):
        self.subs.append(method)

    def emit(self, **args):
        for method in self.subs:
            method(**args)