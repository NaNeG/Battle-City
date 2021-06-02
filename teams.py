class Team:
    def __init__(self, teammates=None, controllers=None, base=None):
        self.teammates = set(teammates) if teammates is not None else set()
        self.controllers = set(controllers) if controllers is not None else set()
        self.base = base

    # def add(self, teammate):
    #     self.teammates.add(teammate)

    @property
    def alive(self):
        return ((self.base is None or self.base.health > 0) and
                 any(e.health > 0 for e in self.teammates))

    def update(self, keystate):
        for e in self.controllers:
            e.update(keystate)

    def kill(self):
        for e in self.teammates:
            if e.health > 0:
                e.kill()
