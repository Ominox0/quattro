from sim.core import Chip


class AND(Chip):
    def run(self):
        if len(self.inputs) != 2:
            return

        self.outputs["A"] = self._and(self.inputs["A"], self.inputs["B"])

        super().run()

    @staticmethod
    def _and(_inA, _inB):
        return min(_inA, _inB)