from sim.core import Chip


class PRINT(Chip):
    def run(self):
        if len(self.inputs) != 1:
            return

        self.outputs["A"] = self._print(self.inputs["A"])

        super().run()

    @staticmethod
    def _print(_in):
        print(_in)

        return _in