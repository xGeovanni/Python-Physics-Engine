#angle.py

#This is a library for helping with angles and 2D vectors

import math
import pygame.math
import random

UP = pygame.math.Vector2((0, -1))
DOWN = pygame.math.Vector2((0, 1))
LEFT = pygame.math.Vector2((-1, 0))
RIGHT = pygame.math.Vector2((1, 0))
IDENTITY = pygame.math.Vector2((1, 1))
ZERO = pygame.math.Vector2((0, 0))

def fromRadians(angle):
    return pygame.math.Vector2((math.cos(angle), math.sin(angle)))

def toRadians(vector):
    return math.atan2(vector[0], -vector[1]);
    
def fromDegrees(angle):
    return fromRadians(math.radians(angle))
    
def toDegrees(vector):
    return math.degrees(toRadians(vector))

def angleBetween(a, b):
    dx = b[0] - a[0]
    dy = b[1] - a[1]

    if (dx == 0 and dy == 0):
        return pygame.math.Vector2(0, 0)
    
    return pygame.math.Vector2(dx, dy).normalize()

def facing(vector):
    """Get a vector angle's general facing in terms of the eight
       cardinal points."""
       
    return pygame.math.Vector2([round(i) for i in vector.normalize()]).normalize()

def slerp(a, b, t=0):
    if a == ZERO or b == ZERO:
        return ZERO
    
    omega = np.arcsin(np.dot(a / np.linalg.norm(a), b / np.linalg.norm(b)))
    so = np.sin(omega)
    return pygame.math.Vector2(math.sin((1.0-t) * omega) / so * a + math.sin(t * omega) / so * b)

def randAngle():
    mul = (1, -1)
    
    return pygame.math.Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize()
    
def anglesApproxEqual(a, b, deviation = .2):
    return abs(a[0] - b[0]) <= deviation and abs(a[1] - b[1]) <= deviation
    
