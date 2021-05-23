class Team:
    def __init__(self, teammates=None, base=None):
        self.teammates = set(teammates) if teammates is not None else set()
        self.base = base

    def add(self, teammate):
        self.teammates.add(teammate)

    @property
    def alive(self):
        return ((self.base is None or self.base.health > 0) and
                 any(e.health > 0 for e in self.teammates))

    def update(self):
        for e in self.teammates:
            e.update()

    def kill(self):
        for e in self.teammates:
            e.kill()
