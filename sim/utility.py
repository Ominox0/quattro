def from2bites(b1, b2):
    return {
        (0, 0): 0,
        (0, 1): 1,
        (1, 0): 2,
        (1, 1): 3,
    }[(b1, b2)]


def to2bites(q1):
    return {
        0: (0, 0),
        1: (0, 1),
        2: (1, 0),
        3: (1, 1),
    }[q1]