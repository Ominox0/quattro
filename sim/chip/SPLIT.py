from sim.core import Chip

class SPLIT(Chip):
    def __init__(self):
        super().__init__()
        self._outs = ["A"]

    def add_output(self, label):
        if label not in self._outs:
            self._outs.append(label)

    def run(self):
        if len(self.inputs) != 1:
            return
        v = self.inputs.get("A")
        for lbl in self._outs:
            self.outputs[lbl] = v
        super().run()
