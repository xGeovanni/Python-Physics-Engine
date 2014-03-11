# Grid library for Pygame by Bobby Clarke
# GNU General Public License 3.0

# Version 1.1

import pygame
import math
from fractions import gcd
from functools import reduce

def _isEven(i):
    return i % 2 == 0

def product(_list):
    return reduce(lambda x, y: x * y, _list, 1)

def _range(start, stop, step=1):
    """Range function which can handle floats."""
    while start < stop:
        yield start
        start += step
        
def _simplify(a, b):
    hcf = gcd(a, b)
    return (a / hcf, b / hcf)

class Tile(pygame.Rect):
    def __init__(self, point, size, colour = None, imgs = [], tags = []):
        self.size = [int(i) for i in size]
        self.point = point
        self.colour = colour

        for img in imgs:
            if isinstance(img, tuple):
                imgs[imgs.index(img)] = pygame.image.fromstring(img[0],
                                                                img[1],
                                                                img[2])
        self.imgs = imgs[:]
        self.tags = tags[:]

        pygame.Rect.__init__(self, self.point, self.size)

    def __lt__(self, other):
        return (self.point[0] < other.point[0] or
                self.point[1] < other.point[1])
    def __gt__(self, other):
        return (self.point[0] > other.point[0] or
                self.point[1] > other.point[1])
    def __le__(self, other):
        return (self.point[0] <= other.point[0] or
                self.point[1] <= other.point[1])
    def __ge__(self, other):
        return (self.point[0] >= other.point[0] or
                self.point[1] >= other.point[1])

    def toData(self, imgFormat = "RGBA"):
        return (self.point, self.size, self.colour,
               [(pygame.image.tostring(img, imgFormat),
                 img.get_size(), imgFormat) for img in self.imgs], self.tags)

    def fromData(data, baseTile = None):
        tile = Tile(*data)

        if baseTile and isinstance(baseTile, Tile):
            baseTile = tile
        else:
            return tile

    def getRect(self):
        return self
    def getColour(self):
        return self.colour
    def setColour(self, colour):
        self.colour = colour
    def getPoint(self):
        return self.point
    def addTag(self, *tags):
        if isinstance(tags[0], list):
            self.tags.extend(tags[0])
        else:
            self.tags.extend(tags)
    def hasTag(self, tag):
        return (tag in self.tags)
    def delTag(self, tag):
        self.tags.remove(tag)
    def clearTags(self):
        self.tags = []
    def addImg(self, img, resize = False):
        if isinstance(img, pygame.Surface):
            if img.get_rect() != self and resize:
                img = pygame.transform.scale(img, (self.size))
            self.imgs.append(img)
        elif img is not None:
            raise TypeError("Images must be pygame.Surface object")
    def delImg(self, img):
        self.imgs.remove(img)
    def clearImgs(self):
        self.imgs = []

    def isClicked(self):
        return self.collidepoint(pygame.mouse.get_pos())
        
    def draw(self, surface):
        if self.colour is not None:
            surface.fill(self.colour, self)
        for img in self.imgs:
            surface.blit(img, self)

class Grid():
    def __init__(self, surface, num, colour = None, tiles = None, 
                 force_square = False):
        self.WIDTH = surface.get_width()
        self.HEIGHT = surface.get_height()
        self.surface = surface

        aspect_ratio = _simplify(self.WIDTH, self.HEIGHT)

        if isinstance(num, int):
            if aspect_ratio == (1, 1) or force_square:
                self.x = math.sqrt(num)
                self.y = math.sqrt(num)
            
            else:            
                self.x = aspect_ratio[0] * (num / product(aspect_ratio))
                self.y = aspect_ratio[1] * (num / product(aspect_ratio))
        else:
            try:
                self.x = num[0]
                self.y = num[1]
            except TypeError:
                raise TypeError("2nd argument must be int or subscriptable")
        
        self.tilesize = (self.WIDTH / self.x,
                         self.HEIGHT / self.y)
        self.num = num
        self.colour = colour

        if tiles:
            if hasattr(tiles, "__getitem__") and isinstance(tiles[0], Tile):
                self.tiles = tiles
            else:
                self.tiles = [[Tile.fromData(tile) for tile in column]
                              for column in tiles]
        else:
            self.tiles = self.maketiles(colour)

    def __getitem__(self, index):
        return self.tiles[index]

    def __setitem__(self, index, new):
        self.tiles[index] = new

    def __len__(self):
        return len(self.tiles)
    
    def index(self, tile):
        for column in self.tiles:
            if tile in column:
                return self.tiles.index(column), column.index(tile)

    def getTiles(self):
        """Get all tiles. Returns a generator"""
        for column in self.tiles:
            for tile in column:
                yield tile

    def tagSearch(self, tag):
        """Search for tiles by tag. Returns a generator"""
        
        for tile in self.getTiles():
            if tile.hasTag(tag):
                yield tile

    def pointSearch(self, point):
        """Search for tiles by point. Returns a tile"""
        
        for tile in self.getTiles():
            if tile.collidepoint(point):
                return tile
            
    def rectSearch(self, rect):
        """Search for tiles by rect. Returns a generator"""
        
        for tile in self.getTiles():
            if tile.colliderect(rect):
                yield tile
                
    def getColumn(self, i):
        return self.tiles[i]
    def getRow(self, i):
        return [column[i] for column in self.tiles]
            
    def checker(self, colour1, colour2 = None):
        for column in self.tiles:
            for tile in column:
                if _isEven(self.tiles.index(column) + column.index(tile)):
                    tile.setColour(colour1)
                else:
                    if colour2:
                        tile.setColour(colour2)
                        
    def getBetweenTiles(self, tile1, tile2):
        """Inefficient and badly implemented"""
        
        index1 = self.index(tile1)
        index2 = self.index(tile2)
        
        if index1[0] != index2[0] and index1[1] != index2[1]:
            raise ValueError("Tiles must be in same row or column")
        
        for column in self.tiles:
            if tile1 in column and tile2 in column:
                return column[column.index(tile1) : column.index(tile2)]
            
        for i in range(self.y):
            row = self.getRow(i)
            if tile1 in row and tile2 in row:
                    return row[row.index(tile1) : row.index(tile2)]

    def getSurroundingTiles(self, tile,  adjacent = True, diagonal = True):    
        di = (0, 1, 0, -1, 1, 1, -1, -1)
        dj = (1, 0, -1, 0, 1, -1, 1, -1)
        # indices 0 - 3 are for horizontal, 4 - 7 are for vertical
        
        index = list(self.getTiles()).index(tile)
        max_x = self.x - 1 # Offset for 0 indexing
        max_y = self.y - 1

        i = int(math.floor(index / self.x))
        j = int(index % self.y)

        surroundingTiles = []

        startat = 0 if adjacent else 4
        stopat = 8 if diagonal else 4

        for k in range(startat, stopat):
            ni = i + di[k]
            nj = j + dj[k]
            if ni >= 0 and nj >= 0 and ni <= max_x and nj <= max_y:
                surroundingTiles.append(self[ni][nj])

        surroundingTiles.reverse()

        return sorted(surroundingTiles)

    def draw(self, drawGrid = False, gridColour = (0, 0, 0), gridSize = 1, surface = None):
        if surface is None:
            surface = self.surface
        
        for tile in self.getTiles():
            tile.draw(surface)
            
            if drawGrid:
                pygame.draw.rect(surface, gridColour, tile, gridSize)
                
    def maketiles(self, colour):
        """Make the tiles for the grid"""
        
        tiles = []
        
        width = self.WIDTH / self.x
        height = self.HEIGHT / self.y
        
        for i in _range(0, self.WIDTH, width):
            column = []
            
            for j in _range(0, self.HEIGHT, height):
                sq = Tile((i, j), (width, height), colour)
                
                column.append(sq)
                              
            tiles.append(column)
            
        return tiles

    def toData(self):
        return (self.num, self.colour,
                [[tile.toData() for tile in column] for column in self.tiles])

    def fromData(data, surface):
        return Grid(*([surface] + list(data)))
    
    def toSurface(self, drawGrid = False, gridColour = (0, 0, 0), gridSize = 1):
        s = pygame.Surface((self.x * self.tilesize[0], self.y * self.tilesize[1]))
        self.draw(drawGrid, gridColour, gridSize, s)
        
        return s


        
