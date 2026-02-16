from sim.core import Chip
from sim.chip import AND, OR, NOT, PRINT, SPLIT
import json

class COMPOSITE(Chip):
    def __init__(self, spec):
        super().__init__()
        self._nodes = {}
        self._inputs_map = []
        self._outputs_map = []
        for n in spec.get("nodes", []):
            t = n["type"]
            if t == "AND":
                obj = AND()
            elif t == "OR":
                obj = OR()
            elif t == "NOT":
                obj = NOT()
            elif t == "PRINT":
                obj = PRINT()
            elif t == "SPLIT":
                obj = SPLIT()
                outs = n.get("outputs", ["A"])
                for lbl in outs[1:]:
                    obj.add_output(lbl)
            else:
                obj = None
            self._nodes[n["id"]] = obj
        for c in spec.get("connections", []):
            a = self._nodes[c["src_id"]]
            b = self._nodes[c["dst_id"]]
            a.addConnection(b, c["dst_label"], c["src_label"])
        for m in spec.get("interface_inputs", []):
            self._inputs_map.append((m["chip_id"], m["label"]))
        for m in spec.get("interface_outputs", []):
            self._outputs_map.append((m["chip_id"], m["label"], m["out_label"]))

    def run(self):
        for i, (chip_id, label) in enumerate(self._inputs_map):
            self._nodes[chip_id].inputs[label] = self.inputs.get(str(i), None)
        for node in self._nodes.values():
            node.run()
        for i, (chip_id, label, out_label) in enumerate(self._outputs_map):
            self.outputs[str(i)] = self._nodes[chip_id].outputs.get(out_label, None)

def load_composite_from_json(path):
    with open(path, "r", encoding="utf-8") as f:
        spec = json.load(f)
    return COMPOSITE(spec)
