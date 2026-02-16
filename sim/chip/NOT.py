from sim.core import Chip


class NOT(Chip):
    def run(self):
        if len(self.inputs) != 1:
            return

        self.outputs["A"] = self._not(self.inputs["A"])

        super().run()

    @staticmethod
    def _not(_in):
        return (3, 2, 1, 0)[_in]