class Movement:
    CLOSING = -1
    STOPPED = 0
    OPENING = 1
    UNKNOWN = 2

    description = {-1: "Closing", 0: "Stopped", 1: "Opening", 2: "Unknown"}


class Position:
    CLOSED = -1
    PART_OPEN = 0
    OPEN = 1
    UNKNOWN = 2

    description = {-1: "Closed", 0: "Part Open", 1: "Open", 2: "Unknown"}

