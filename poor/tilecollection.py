# -*- coding: utf-8 -*-

# Copyright (C) 2014 Osmo Salomaa
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""A collection of map tiles visible on screen."""

import poor
import threading
import time

__all__ = ("TileCollection",)


class Tile:

    """Properties of a map tile."""

    def __init__(self, uid):
        """Initialize a :class:`Tile` instance."""
        self.uid = uid
        self.reset()

    def assign(self, key, xmin, xmax, ymin, ymax, zoom):
        """Assign properties."""
        self.key  = key
        self.time = time.time()
        self.xmin = xmin
        self.xmax = xmax
        self.ymin = ymin
        self.ymax = ymax
        self.zoom = zoom

    def reset(self):
        """Reset properties."""
        self.key  = ""
        self.time = -1
        self.xmin = -1
        self.xmax = -1
        self.ymin = -1
        self.ymax = -1
        self.zoom = -1


class TileCollection:

    """A collection of map tiles visible on screen."""

    def __init__(self):
        """Initialize a :class:`TileCollection` instance."""
        self._lock = threading.Lock()
        # Keep most recently used tiles on the right.
        # Requires an external call to sort.
        self._tiles = []

    @poor.util.locked_method
    def get(self, key):
        """Return requested tile ``None``."""
        for tile in reversed(self._tiles):
            if tile.key == key:
                return tile
        return None

    @poor.util.locked_method
    def get_free(self, key, xmin, xmax, ymin, ymax, zoom, tile_corners):
        """Assign and return a random tile outside bounds."""
        txmin = min(corner[0] for corner in tile_corners)
        txmax = max(corner[0] for corner in tile_corners)
        tymin = min(corner[1] for corner in tile_corners)
        tymax = max(corner[1] for corner in tile_corners)
        props = (key, txmin, txmax, tymin, tymax, zoom)
        for tile in self._tiles:
            if (tile.xmin > xmax or tile.xmax < xmin or
                tile.ymin > ymax or tile.ymax < ymin or
                tile.zoom != zoom):
                tile.assign(*props)
                return tile
        # If no free tile found, grow collection.
        self._tiles.append(Tile(self.size+1))
        self._tiles[-1].assign(*props)
        return self._tiles[-1]

    @poor.util.locked_method
    def grow(self, size):
        """Grow amount of tiles in collection to `size`."""
        while self.size < size:
            self._tiles.append(Tile(self.size+1))
        self._tiles.sort(key=lambda x: x.time)

    @poor.util.locked_method
    def reset(self):
        """Reset tile properties."""
        for tile in self._tiles:
            tile.reset()

    @property
    def size(self):
        """Amount of tiles in collection."""
        return len(self._tiles)

    @poor.util.locked_method
    def sort(self):
        """Sort tiles in collection to optimize queries."""
        self._tiles.sort(key=lambda x: x.time)
