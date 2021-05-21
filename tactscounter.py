class TactsCounter:
    def __init__(self, *, count, tact_length=1, cycled=True):
        self._frame = 0
        self.count = count
        self.tact_length = tact_length
        self.active = True
        self.cycled = cycled

    @property
    def tact(self):
        return self._frame // self.tact_length

    @property
    def stopped(self):
        return not self.cycled and self.tact == self.count - 1

    def update(self):
        if self.active and (self.cycled or self.tact < self.count - 1):
            self._frame = ((self._frame + 1) % 
                           (self.tact_length * self.count))
    
    def reset(self):
        self._frame = 0