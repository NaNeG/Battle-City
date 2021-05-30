from objects import Wall
from typing import Collection, Counter, Union
from pygame import Rect
from pygame.sprite import Sprite
from constants import RIGHT, UP, scale, screen_size


class Map:
    def __init__(self, cell_size=scale, screen_size=screen_size):
        self.cell_size = cell_size
        self.screen_size = screen_size

        self._wall = {Wall}

        self.size = (round(screen_size[0] // cell_size + 1),
                     round(screen_size[1] // cell_size + 1))

        self._cells = [[set() for _ in range(self.size[1])] for _ in range(self.size[0])]

    def clear_cells(self):
        for col in self._cells:
            for set in col:
                set.clear()

    def place(self, obj: Sprite, rect: Rect=None):
        if rect is None:
            rect = obj.rect
        cells = self.get_rect_cells(rect)

        for x, y in cells:
            self.get_cell(x,y).add(obj)

    def outdate(self, obj: Sprite, rect: Rect=None):
        if rect is None:
            rect = obj.rect
        cells = self.get_rect_cells(rect)

        for x, y in cells:
            self.get_cell(x,y).discard(obj)

    # def replace(self, obj: Collection[Sprite], rect: Rect=None, to_be_replaced=()):
    #     if rect is None:
    #         rect = obj.rect
    #     cells = self.get_rect_cells(rect)

    #     if len(to_be_replaced) > 0:
    #         extra = self.get_content(cells, lambda x: x not in to_be_replaced)
    #         if len(extra) > 0:
    #             return extra

    #     for x, y in cells:
    #         self.cells[x][y].add(obj)
    #     return ()

    def jump(self, obj: Sprite, newrect: Rect, oldrect: Rect=None):
        self.outdate(obj, oldrect)
        self.place(obj, newrect)        

    def iter_content(self, cells, selector=lambda obj: True):
        for x, y in cells:
            cell = self.get_cell(x,y)
            yield from filter(selector, cell)

    def get_content(self, cells, selector=lambda obj: True):
        return set(self.iter_content(cells, selector))

    def count_content(self, cells, selector=lambda obj: True):
        return Counter(self.iter_content(cells, selector))

    def get_rect_content(self, rect: Rect, selector=lambda obj: True):
        return self.get_content(self.get_rect_cells(rect), selector)

    def count_rect_content(self, rect: Rect, selector=lambda obj: True):
        return self.count_content(self.get_rect_cells(rect), selector)

    def get_rect_cells(self, rect: Rect):
        'Построчно возвращает клетки, соответствующие прямоугольнику'
        t, l, b, r = (round(e / self.cell_size) for e in (rect.top, rect.left, rect.bottom, rect.right))
        return [(x, y) for y in range(t, b) for x in range(l, r)]

    def get_cell(self, x, y):
        return self._cells[x][y] if 0 <= x < self.size[0] and 0 <= y < self.size[1] else self._wall
