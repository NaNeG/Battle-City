from typing import Counter
from pygame import Rect
from pygame.sprite import Sprite
from constants import scale, screen_size

class Map:
    def __init__(self, cell_size=scale, screen_size=screen_size):
        self.cell_size = cell_size
        self.screen_size = screen_size

        self.size = (round(screen_size[0] // cell_size + 1),
                     round(screen_size[1] // cell_size + 1))

        self.cells: self.cells["x"]["y"] = [[None]*(self.size[1]) for _ in range(self.size[0])]

    def place(self, obj: Sprite, rect: Rect=None, onempty=True):
        return self.replace(obj, rect, (None,) if onempty else ())

    def outdate(self, rect: Rect, expected=()):
        return self.replace(None, rect, expected)

    def replace(self, obj: "Sprite | None", rect: Rect=None, to_be_replaced=()):
        if rect is None:
            rect = obj.rect
        cells = self.get_rect_cells(rect)

        if len(to_be_replaced) > 0:
            extra = self.get_content(cells, to_be_replaced)
            if len(extra) > 0:
                return extra

        for x, y in cells:
            self.cells[x][y] = obj
        return ()

    def jump(self, obj: Sprite, newrect: Rect, oldrect: Rect=None):
        if oldrect is None:
            oldrect = obj.rect

        extra_while_outdating = self.outdate(oldrect, (obj,))
        if len(extra_while_outdating) > 0:
            return MoveResult(obj, extra_while_outdating)

        bumped_while_placing = self.place(obj, newrect)
        if len(bumped_while_placing) > 0:
            self.place(obj, oldrect)

        return MoveResult(obj, extra_while_outdating, bumped_while_placing)

    def get_content(self, cells, excluding=(None,)):
        return {self.cells[x][y] for x, y in cells if self.cells[x][y] not in excluding}

    def count_content(self, cells, excluding=(None,)):
        return Counter(self.cells[x][y] for x, y in cells if self.cells[x][y] not in excluding)

    def get_rect_content(self, rect: Rect, excluding=(None,)):
        return self.get_content(self.get_rect_cells(rect), excluding)

    def count_rect_content(self, rect: Rect, excluding=(None,)):
        return self.count_content(self.get_rect_cells(rect), excluding)

    def get_rect_cells(self, rect: Rect):
        'Построчно возвращает клетки, соответствующие прямоугольнику'
        t, l, b, r = (round(e / self.cell_size) for e in (rect.top, rect.left, rect.bottom, rect.right))
        return [(x, y) for y in range(t, b+1) for x in range(l, r+1)]

    def __repr__(self):
        def r(obj):
            if obj is None:
                return ' '
            if hasattr(obj, 'speed'):
                return 'P'
            return 'T'
        return '\n'.join(''.join(r(self.cells[x][y]) for y in range(self.size[1])) for x in range(self.size[0]))


class MoveResult:
    def __init__(self, obj, found_extra=(), bumped=()):
        self.obj = obj
        self.ok = (
            len(bumped) == 0 and
            len(found_extra) == 0
        )
        self.found_extra = found_extra
        self.bumped = bumped
