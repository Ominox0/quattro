from sim.core import Chip


class OR(Chip):
    def run(self):
        if len(self.inputs) != 2:
            return

        self.outputs["A"] = self._or(self.inputs["A"], self.inputs["B"])

        super().run()

    @staticmethod
    def _or(_inA, _inB):
        return max(_inA, _inB)