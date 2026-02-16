class userInput:
    def __init__(self):
        self.chip = None
        self.inputLabel = None

    def connectTo(self, chip, inputLabel):
        self.chip = chip
        self.inputLabel = inputLabel

    def disconnect(self):
        self.chip = None
        self.inputLabel = None

    def run(self, value):
        if value > 3 or value < 0:
            raise ValueError("This system can not exceed values over 3 or lower than 0")

        self.chip.inputs[self.inputLabel] = value
        self.chip.run()


class Chip:
    def __init__(self):
        self.inputs = {}
        self.outputs = {}

        self.connections = []

    def addConnection(self, chip, label, outLabel):
        self.connections.append((chip, label, outLabel))

    def removeConnection(self, chip, label, outLabel):
        try:
            self.connections.remove((chip, label, outLabel))
        except ValueError:
            pass

    def run(self):
        for (chip, label, out) in self.connections:
            chip.inputs[label] = self.outputs[out]
            chip.run()

    def reset(self):
        self.inputs = {}
        self.outputs = {}
