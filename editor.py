import pygame
import json
import os
from sim import userInput
from sim.chip import AND, OR, NOT, PRINT, SPLIT, COMPOSITE, load_composite_from_json

class Node:
    def __init__(self, nid, t, pos):
        self.id = nid
        self.type = t
        self.pos = pos
        self.rect = pygame.Rect(pos[0], pos[1], 120, 60)
        self.value = 0
        if t == "INPUT":
            self.obj = userInput()
            self.inputs = []
            self.outputs = ["A"]
        elif t == "AND":
            self.obj = AND()
            self.inputs = ["A", "B"]
            self.outputs = ["A"]
        elif t == "OR":
            self.obj = OR()
            self.inputs = ["A", "B"]
            self.outputs = ["A"]
        elif t == "NOT":
            self.obj = NOT()
            self.inputs = ["A"]
            self.outputs = ["A"]
        elif t == "PRINT":
            self.obj = PRINT()
            self.inputs = ["A"]
            self.outputs = ["A"]
        elif t == "SPLIT":
            self.obj = SPLIT()
            self.inputs = ["A"]
            self.outputs = ["A"]
        else:
            self.obj = None
            self.inputs = []
            self.outputs = []
        self._ensure_rect_size()

    def _ensure_rect_size(self):
        pins = max(len(self.inputs), len(self.outputs))
        base = 30
        extra = pins * 20
        button_space = 22 if self.type == "SPLIT" else 0
        h = max(60, base + extra + button_space)
        self.rect.height = h

    def add_output(self):
        if self.type != "SPLIT":
            return
        next_label = chr(ord('A') + len(self.outputs))
        self.outputs.append(next_label)
        if self.obj:
            try:
                self.obj.add_output(next_label)
            except Exception:
                pass
        self._ensure_rect_size()

    def add_button_rect(self):
        return pygame.Rect(self.rect.centerx - 10, self.rect.bottom - 18, 20, 16)

    def pin_at(self, pos):
        for i, label in enumerate(self.inputs):
            cx = self.rect.left
            cy = self.rect.top + 15 + i * 20
            r = pygame.Rect(cx - 6, cy - 6, 12, 12)
            if r.collidepoint(pos):
                return ("in", label)
        for i, label in enumerate(self.outputs):
            cx = self.rect.right
            cy = self.rect.top + 15 + i * 20
            r = pygame.Rect(cx - 6, cy - 6, 12, 12)
            if r.collidepoint(pos):
                return ("out", label)
        return None

class Editor:
    def __init__(self):
        pygame.init()
        self.w, self.h = 1000, 700
        self.screen = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption("4pc Circuit Editor")
        self.clock = pygame.time.Clock()
        self.nodes = []
        self.connections = []
        self.menu_open = False
        self.menu_pos = (0, 0)
        self.selected_pin = None
        self.selected_connection = None
        self.dragging = False
        self.drag_offset = (0, 0)
        self.selected_node = None
        self.font = pygame.font.SysFont(None, 18)
        self.running = True

    def add_node(self, t, pos):
        nid = str(len(self.nodes))
        n = Node(nid, t, pos)
        self.nodes.append(n)

    def node_at(self, pos):
        for n in reversed(self.nodes):
            if n.rect.collidepoint(pos):
                return n
        return None

    def connect(self, src, src_label, dst, dst_label):
        if src.type == "INPUT":
            src.obj.connectTo(dst.obj, dst_label)
            self.connections.append({"src_id": src.id, "src_label": "A", "dst_id": dst.id, "dst_label": dst_label})
        else:
            src.obj.addConnection(dst.obj, dst_label, src_label)
            self.connections.append({"src_id": src.id, "src_label": src_label, "dst_id": dst.id, "dst_label": dst_label})

    def draw_node(self, n):
        pygame.draw.rect(self.screen, (40, 40, 50), n.rect, border_radius=6)
        pygame.draw.rect(self.screen, (200, 200, 220), n.rect, 1, border_radius=6)
        t = self.font.render(n.type, True, (240, 240, 240))
        self.screen.blit(t, (n.rect.centerx - t.get_width() // 2, n.rect.top + 2))
        for i, label in enumerate(n.inputs):
            cx = n.rect.left
            cy = n.rect.top + 15 + i * 20
            pygame.draw.circle(self.screen, (100, 180, 240), (cx, cy), 6)
            l = self.font.render(label, True, (240, 240, 240))
            self.screen.blit(l, (cx + 8, cy - 8))
        for i, label in enumerate(n.outputs):
            cx = n.rect.right
            cy = n.rect.top + 15 + i * 20
            pygame.draw.circle(self.screen, (240, 180, 100), (cx, cy), 6)
            l = self.font.render(label, True, (240, 240, 240))
            self.screen.blit(l, (cx - 8 - l.get_width(), cy - 8))
        if n.type == "INPUT":
            v = self.font.render(str(n.value), True, (180, 255, 180))
            self.screen.blit(v, (n.rect.centerx - v.get_width() // 2, n.rect.bottom - 20))
        if n.type == "PRINT":
            val = n.obj.outputs.get("A") if n.obj else None
            if val is not None:
                v = self.font.render(str(val), True, (255, 230, 160))
                self.screen.blit(v, (n.rect.centerx - v.get_width() // 2, n.rect.bottom - 20))
        if n.type == "SPLIT":
            br = n.add_button_rect()
            pygame.draw.rect(self.screen, (60, 160, 80), br, border_radius=3)
            pygame.draw.rect(self.screen, (20, 40, 20), br, 1, border_radius=3)
            plus_h = self.font.render("+", True, (250, 255, 250))
            self.screen.blit(plus_h, (br.centerx - plus_h.get_width() // 2, br.centery - plus_h.get_height() // 2))

    def draw_connections(self):
        for idx, c in enumerate(self.connections):
            a = self._node_by_id(c["src_id"])
            b = self._node_by_id(c["dst_id"])
            ai = a.outputs.index(c["src_label"])
            bi = b.inputs.index(c["dst_label"])
            ax = a.rect.right
            ay = a.rect.top + 15 + ai * 20
            bx = b.rect.left
            by = b.rect.top + 15 + bi * 20
            color = (255, 220, 120) if self.selected_connection == idx else (160, 160, 160)
            width = 3 if self.selected_connection == idx else 2
            pygame.draw.line(self.screen, color, (ax, ay), (bx, by), width)

    def _dist_to_segment(self, p, a, b):
        (px, py), (ax, ay), (bx, by) = p, a, b
        vx, vy = bx - ax, by - ay
        wx, wy = px - ax, py - ay
        l2 = vx * vx + vy * vy
        t = 0 if l2 == 0 else max(0, min(1, (wx * vx + wy * vy) / l2))
        cx, cy = ax + t * vx, ay + t * vy
        dx, dy = px - cx, py - cy
        return (dx * dx + dy * dy) ** 0.5

    def hit_connection(self, pos):
        best = (None, 99999)
        for idx, c in enumerate(self.connections):
            a = self._node_by_id(c["src_id"])
            b = self._node_by_id(c["dst_id"])
            ai = a.outputs.index(c["src_label"])
            bi = b.inputs.index(c["dst_label"])
            ax = a.rect.right
            ay = a.rect.top + 15 + ai * 20
            bx = b.rect.left
            by = b.rect.top + 15 + bi * 20
            d = self._dist_to_segment(pos, (ax, ay), (bx, by))
            if d < best[1]:
                best = (idx, d)
        if best[0] is not None and best[1] <= 6:
            return best[0]
        return None

    def _node_by_id(self, nid):
        for n in self.nodes:
            if n.id == nid:
                return n
        return None

    def open_menu(self, pos):
        self.menu_open = True
        self.menu_pos = pos

    def draw_menu(self):
        if not self.menu_open:
            return
        items = ["INPUT", "AND", "OR", "NOT", "PRINT", "SPLIT"]
        w = 120
        h = 22 * len(items)
        x, y = self.menu_pos
        r = pygame.Rect(x, y, w, h)
        pygame.draw.rect(self.screen, (30, 30, 32), r)
        pygame.draw.rect(self.screen, (200, 200, 220), r, 1)
        for i, it in enumerate(items):
            t = self.font.render(it, True, (240, 240, 240))
            self.screen.blit(t, (x + 6, y + 4 + i * 22))

    def click_menu(self, pos):
        items = ["INPUT", "AND", "OR", "NOT", "PRINT", "SPLIT"]
        x, y = self.menu_pos
        for i, it in enumerate(items):
            r = pygame.Rect(x, y + i * 22, 120, 22)
            if r.collidepoint(pos):
                self.add_node(it, pos)
                self.menu_open = False
                return True
        self.menu_open = False
        return False

    def save(self, path):
        data = {
            "nodes": [{"id": n.id, "type": n.type, "pos": n.pos, "value": n.value, "outputs": n.outputs} for n in self.nodes],
            "connections": self.connections
        }
        d = os.path.dirname(path)
        if d and not os.path.exists(d):
            os.makedirs(d)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f)

    def load(self, path):
        if not os.path.exists(path):
            return
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.nodes = []
        self.connections = []
        for n in data.get("nodes", []):
            node = Node(n["id"], n["type"], tuple(n["pos"]))
            node.value = n.get("value", 0)
            outs = n.get("outputs", node.outputs)
            node.outputs = outs
            if node.type == "SPLIT" and node.obj:
                for lbl in outs[1:]:
                    try:
                        node.obj.add_output(lbl)
                    except Exception:
                        pass
            node._ensure_rect_size()
            self.nodes.append(node)
        for c in data.get("connections", []):
            a = self._node_by_id(c["src_id"])
            b = self._node_by_id(c["dst_id"])
            if a.type == "INPUT":
                a.obj.connectTo(b.obj, c["dst_label"])
            else:
                a.obj.addConnection(b.obj, c["dst_label"], c["src_label"])
            self.connections.append(c)

    def compile(self, path):
        interface_inputs = []
        used_inputs = set()
        for c in self.connections:
            a = self._node_by_id(c["src_id"])
            b = self._node_by_id(c["dst_id"])
            if a.type == "INPUT":
                interface_inputs.append({"chip_id": b.id, "label": c["dst_label"]})
                used_inputs.add((b.id, c["dst_label"]))
        fanout = {}
        for c in self.connections:
            k = (c["src_id"], c["src_label"])
            fanout[k] = fanout.get(k, 0) + 1
        sinks = []
        for n in self.nodes:
            if n.type == "INPUT":
                continue
            for ol in n.outputs:
                k = (n.id, ol)
                if fanout.get(k, 0) == 0:
                    sinks.append((n.id, ol))
        interface_outputs = []
        for chip_id, out_label in sinks:
            interface_outputs.append({"chip_id": chip_id, "label": "A", "out_label": out_label})
        nodes_spec = []
        for n in self.nodes:
            if n.type == "INPUT":
                continue
            entry = {"id": n.id, "type": n.type}
            if n.type == "SPLIT":
                entry["outputs"] = n.outputs
            nodes_spec.append(entry)
        spec = {
            "nodes": nodes_spec,
            "connections": [{"src_id": c["src_id"], "src_label": c["src_label"], "dst_id": c["dst_id"], "dst_label": c["dst_label"]} for c in self.connections if self._node_by_id(c["src_id"]).type != "INPUT"],
            "interface_inputs": interface_inputs,
            "interface_outputs": interface_outputs
        }
        d = os.path.dirname(path)
        if d and not os.path.exists(d):
            os.makedirs(d)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(spec, f)

    def run_sim(self):
        for n in self.nodes:
            if n.type == "INPUT":
                try:
                    n.obj.run(n.value)
                except Exception:
                    pass

    def draw_help(self):
        bar_h = 26
        r = pygame.Rect(0, self.h - bar_h, self.w, bar_h)
        pygame.draw.rect(self.screen, (28, 30, 34), r)
        pygame.draw.line(self.screen, (50, 52, 58), (0, self.h - bar_h), (self.w, self.h - bar_h), 1)
        text = "Right-click: Add  |  Left-click OUT then IN: Connect  |  Drag: Move  |  Keys: 0–3 INPUT, R Run, S Save, L Load, C Compile"
        t = self.font.render(text, True, (220, 220, 230))
        self.screen.blit(t, (8, self.h - bar_h + (bar_h - t.get_height()) // 2))

    def loop(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 3:
                        self.open_menu(event.pos)
                    elif event.button == 1:
                        if self.menu_open:
                            if self.click_menu(event.pos):
                                continue
                        hit = self.hit_connection(event.pos)
                        if hit is not None:
                            self.selected_connection = hit
                            self.selected_node = None
                            self.selected_pin = None
                            continue
                        n = self.node_at(event.pos)
                        if n:
                            p = n.pin_at(event.pos)
                            if p:
                                if not self.selected_pin:
                                    self.selected_pin = (n, p[0] == "out", p[1])
                                else:
                                    src_node, src_is_out, src_label = self.selected_pin
                                    if src_is_out and p[0] == "in":
                                        self.connect(src_node, src_label, n, p[1])
                                        self.selected_pin = None
                                    elif (not src_is_out) and p[0] == "out":
                                        self.connect(n, p[1], src_node, src_label)
                                        self.selected_pin = None
                                    else:
                                        self.selected_pin = (n, p[0] == "out", p[1])
                            else:
                                if n.type == "SPLIT" and n.add_button_rect().collidepoint(event.pos):
                                    n.add_output()
                                else:
                                    self.selected_node = n
                                    self.dragging = True
                                    self.drag_offset = (event.pos[0] - n.rect.x, event.pos[1] - n.rect.y)
                        else:
                            self.selected_node = None
                            self.selected_pin = None
                            self.selected_connection = None
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.dragging = False
                elif event.type == pygame.MOUSEMOTION:
                    if self.dragging and self.selected_node:
                        self.selected_node.rect.x = event.pos[0] - self.drag_offset[0]
                        self.selected_node.rect.y = event.pos[1] - self.drag_offset[1]
                        self.selected_node.pos = (self.selected_node.rect.x, self.selected_node.rect.y)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_s:
                        self.save(os.path.join("circuits", "circuit.json"))
                    elif event.key == pygame.K_l:
                        self.load(os.path.join("circuits", "circuit.json"))
                    elif event.key == pygame.K_c:
                        self.compile(os.path.join("compiled", "composite.json"))
                    elif event.key == pygame.K_r:
                        self.run_sim()
                    elif event.key in (pygame.K_DELETE, pygame.K_BACKSPACE):
                        if self.selected_connection is not None:
                            c = self.connections[self.selected_connection]
                            src = self._node_by_id(c["src_id"])
                            dst = self._node_by_id(c["dst_id"])
                            if src.type == "INPUT":
                                src.obj.disconnect()
                            else:
                                src.obj.removeConnection(dst.obj, c["dst_label"], c["src_label"])
                            del self.connections[self.selected_connection]
                            self.selected_connection = None
                    elif event.unicode in ["0", "1", "2", "3"]:
                        if self.selected_node and self.selected_node.type == "INPUT":
                            self.selected_node.value = int(event.unicode)
                            try:
                                self.selected_node.obj.run(self.selected_node.value)
                            except Exception:
                                pass
            self.screen.fill((20, 22, 25))
            for n in self.nodes:
                self.draw_node(n)
            self.draw_connections()
            self.draw_menu()
            self.draw_help()
            pygame.display.flip()
            self.clock.tick(60)

def main():
    Editor().loop()

if __name__ == "__main__":
    main()
