#shapes.py

#This file defines Circle and Rectangle shapes to be used as colliders
#in the physics engine itself. These shape classes contain functions
#to determine whether they overlap another shape, for use in physics
#collisions, and other functions such as a function to calculate the
#area of the shape.

import pygame
import math
from numpy import clip

def calcDist(a, b):
    """Calculate the distance between two points"""
    return math.sqrt((b[0] - a[0]) ** 2 +
                     (b[1] - a[1]) ** 2)
    
def toInts(iterable):
    """Convert all numbers in an iterable to integers"""
    return [int(i) for i in iterable]

class Shape():
    """The class from which all shape classes inherit"""
    def collide(self, other):
        if isinstance(other, Circle):
            return self.collidecircle(other)
        elif isinstance(other, Rect):
            return self.colliderect(other)
        elif hasattr(other, "__iter__") and len(other) == 2:
            return self.collidepoint(other)
        else:
            message = "Argument must be Circle, Rect or point"
            raise ValueError(message)
        
    def move(self, *args, **kwargs):
        copy = self.copy()
        copy.move_ip(*args, **kwargs)
        return copy
        
    def copy(self):
        if isinstance(self, Circle):
            return Circle(*self.args)
        elif isinstance(self, Rect):
            return Rect(*self.args)
    
    def getPos(self):
        if isinstance(self, Circle):
            return self.centre
        elif isinstance(self, Rect):
            return self.topleft

class Circle(Shape):
    """This class defines a Circle shape"""
    
    def __init__(self, centre, radius, surface=None, colour=(0, 0, 0),
                 id_=None):
        
        global idCount
        
        Shape.__init__(self)
        
        if id_ is None:
            self.id = id(self)
        else:
            self.id = id_
        
        self.args = [centre, radius, surface, colour, self.id]
        
        self.centre = pygame.math.Vector2(centre)
        self.radius = radius
        
        self.area = self.calcArea()
        
        if surface is not None:
            self.surface = surface
        else:
            self.surface = pygame.display.get_surface()
            
        self.colour = colour
        
    def draw(self, width = 0, colour = None):
        pygame.draw.circle(self.surface, 
                           colour if colour else self.colour,
                           toInts(self.centre), self.radius, width)
    
    def move_ip(self, x, y = 0):
        
        if hasattr(x, "__iter__"):
            x, y = x
            
        self.centre[0] += x
        self.centre[1] += y
        
        self.args[0] = self.centre
        
    def toRect(self, surface=None, colour=None):
        
        if colour is None:
            colour = self.colour
        
        return Rect([i - self.radius for i in self.centre],
                    [self.radius * 2 for i in range(2)],
                    surface, colour)
        
    def calcArea(self):
        return math.pi * self.radius ** 2
        
    def collidecircle(self, other):
        dx = other.centre[0] - self.centre[0]
        dy = other.centre[1] - self.centre[1]
        total_radius = self.radius + other.radius
        
        return (dx ** 2  + dy ** 2) < total_radius ** 2
        
        #This derives from pythagoras' theorem. dx ^ 2 + dy ^ 2 is the
        #distance between the points squared. If this is less than the
        #radius squared then the distance between the centres is less
        #than the total of the two radii, there is thus an overlap.
    
    def collidepoint(self, point):
        return calcDist(self.centre, point) < self.radius
    
    def colliderect(self, rect):
        # Find the closest point to the circle within the rectangle
        closestX = clip(self.centre[0], rect.left, rect.right)
        closestY = clip(self.centre[1], rect.top, rect.bottom)

        # Calculate the distance between the 
        # circle's center and this closest point
        distanceX = self.centre[0] - closestX
        distanceY = self.centre[1] - closestY
        
        # If the distance is less than the circle's radius, 
        # an intersection occurs
        distanceSquared = (distanceX ** 2) + (distanceY ** 2)
        return distanceSquared < (self.radius ** 2)

class Rect(Shape, pygame.Rect):
    """This class defines a rectangle and inherits from pygame's
       built-in rectangle class while adding the needed functionality
       for physics"""
    
    def __init__(self, pos, size, surface=None, colour=(0, 0, 0), 
                 id_=None):
        
        pygame.Rect.__init__(self, pos, size)
        Shape.__init__(self)
        
        global idCount
        
        if id_ is None:
            self.id = id(self)
        else:
            self.id = id_
        
        self.args = [pos, size, surface, colour, self.id]
            
        self.centre = pygame.math.Vector2(self.center)
        
        self.area = self.calcArea()
            
        if surface is not None:
            self.surface = surface
        else:
            self.surface = pygame.display.get_surface()
                
        self.colour = colour
        
        self.float_x = float(self.x)
        self.float_y = float(self.y)
        
    def calcArea(self):
        return self.size[0] * self.size[1]
    
    def toRect(self):
        return self
    
    def move_ip(self, x, y = 0):
        
        if hasattr(x, "__iter__"):
            x, y = x
        
        self.float_x += x
        self.float_y += y
            
        self.x = self.float_x
        self.y = self.float_y
        
        self.args[0] = (self.x, self.y)
        self.centre = pygame.math.Vector2(self.center)
            
    def draw(self, width = 0, colour = None):
        pygame.draw.rect(self.surface, 
                         colour if colour else self.colour,
                         self, width)
        
    def collidecircle(self, circle):
        return circle.colliderect(self)
    
class Polygon():
    def __init__(self, *points, surface=None, colour=(0, 0, 0)):
        
        self.args = (points, surface, colour)
        
        self.points = [pygame.Vector2(point) for point in points]
        
        self.area = self.calcArea()
        
        self.colour = colour
        
        if surface is not None:
            self.surface = surface
        else:
            self.surface = pygame.display.get_surface()
            
    def move(self, x, y = 0):
        
        if hasattr(x, "__iter__"):
            x, y = x
            
        for point in self.points:
            point[0] += x
            point[1] += y
            
    def calcArea(self):
        pointlist = self.points + self.points[:1] #Append the first to the end
        
        xTotal = 0
        yTotal = 0
        
        for i in range(len(self.points)):
            xTotal += pointlist[i][0] * pointlist[i + 1][1]
            yTotal += pointlist[i][1] * pointlist[i + 1][0]
            
        return abs((xTotal - yTotal) / 2)
        
    def draw(self, width = 0, colour = None):
        pygame.draw.polygon(self.surface, colour if colour else self.colour,
                            self.points, width)
