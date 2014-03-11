import pygame
import angle
import random
import math

def shadeRange(start = (255, 255, 255), end = (0, 0, 0), step = 1):
    currentShade = start
    
    while currentShade != end:
        currentShade = (currentShade[0] + step,
                        currentShade[1] + step,
                        currentShade[2] + step)
        
        yield currentShade

def toVector2(obj):
    if isinstance(obj, pygame.math.Vector2):
        return obj
    else:
        return pygame.math.Vector2(obj)
    
def roundVector(vector):
    return (int(vector[0]), int(vector[1]))

def isIterable(obj):
    return hasattr(obj, "__iter__")
    
def pickColour(colours):
    if isIterable(colours) and (isIterable(colours[0]) or isinstance(colours[0], pygame.Color)):
        #If it is a iterable of iterables (colours)
        return random.choice(colours)
    else:
        return colours
    
        
def calcGaussIfSigma(mu, sigma):
    if sigma is not None and mu is not None:
        return random.gauss(mu, sigma)
    else:
        return mu
    
class ParticleManager():
    particles = []
    emitters = []
        
    def __init__(self):
        self.particles = self.__class__.particles #A reference
        self.emitters = self.__class__.emitters
        
    def update(self, deltaTime):
        for particle in self.particles:
            particle.update(deltaTime)
            
        for emitter in self.emitters:
            emitter.update()
            
    def render(self):
        for particle in self.particles:
            particle.draw()
        

class Particle():
    def __init__(self, pos, colour, velocity, lifespan = None, size = (1, 1), surface = None):
        
        self.pos = toVector2(pos)
        self.velocity = toVector2(velocity)
        self.size = size
        self.colour = colour
        self.lifespan = lifespan
        
        self.timeAlive = 0
        
        ParticleManager.particles.append(self)
        
        if surface is None:
            self.surface = pygame.display.get_surface()
        else:
            self.surface = surface
            
        self.surfrect = self.surface.get_rect()
        
    def update(self, deltaTime):
        self.pos[0] += self.velocity[0] * deltaTime
        self.pos[1] += self.velocity[1] * deltaTime
        
        self.timeAlive += deltaTime
        
        if not self.surfrect.collidepoint(self.pos) or (self.lifespan is not None and self.timeAlive >= self.lifespan):
            self.die()
        
    def draw(self):
        self.surface.fill(self.colour, (self.pos, self.size))
            
    def die(self):
        ParticleManager.particles.remove(self)
        del(self)
        
class Emitter():
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        
        ParticleManager.emitters.append(self)
        
    def update(self):
        Particle(*self.args, **self.kwargs)
        
def circle(pos, speed, colours, numParticles = 100, lifespan = None, size = (1, 1), surface = None, speedSigma = None, lifespanSigma = None):
    for i in range(numParticles):
        realSpeed = calcGaussIfSigma(speed, speedSigma)
        realLifespan = calcGaussIfSigma(lifespan, lifespanSigma)
        
        Particle(pos, pickColour(colours), angle.fromRadians((2 * math.pi) / numParticles * i) * realSpeed, realLifespan, size, surface)
        
def explosion(pos, speed, colour, particlesPerCircle = 40, numCircles = 5, lifespan = None, size = (1, 1), surface = None, speedSigma = 20, lifespanSigma = 0.2):
    for i in range(numCircles):
        circle(pos, speed / (i + 1), colour, particlesPerCircle, lifespan, size, surface, speedSigma, lifespanSigma)

def arc(pos, speed, colours, minAngle, maxAngle, numParticles = 40, lifespan = None, size = (1, 1), surface = None, speedSigma = None, lifespanSigma = None, randAngle = False):
    if isinstance(minAngle, pygame.math.Vector2):
        minAngle = angle.toRadians(minAngle)
        
    if isinstance(maxAngle, pygame.math.Vector2):
        maxAngle = angle.toRadians(maxAngle)
        
    for i in range(numParticles):
        realSpeed = abs(calcGaussIfSigma(speed, speedSigma))
        realLifespan = (calcGaussIfSigma(lifespan, lifespanSigma))
            
        realColour = pickColour(colours)
        
        if randAngle:
            _angle = random.uniform(minAngle, maxAngle)
        else:
            _angle = (maxAngle - minAngle) / numParticles * i
        
        Particle(pos, realColour, angle.fromRadians(_angle) * realSpeed, lifespan, size, surface)
        
def sparks(pos, speed, colour, minAngle, maxAngle, numArcs = 4, particlesPerArc = 20, lifespan = None, size = (1, 1), surface = None, speedSigma = 20, lifespanSigma = 0.2, randAngle = True):
    for i in range(numArcs):
        arc(pos, speed / (i + 1), colour, minAngle, maxAngle, particlesPerArc, lifespan, size, surface, speedSigma, lifespanSigma, randAngle)

def smoke(pos, speed, colours = shadeRange((128, 128, 128)), direction = angle.UP):
    pass


#def line(pos, speed, colour, _angle, length, width = 1, lifespan = None, size = (1, 1), surface = None, speedSigma = 20):
#    if isinstance(_angle, float):
#        _angle = angle.fromRadians(_angle)
#        
#    pos = toVector2(pos)
#        
#    for i in range(width):
#        for j in range(length):
#            if speedSigma is not None:
#                realSpeed = random.gauss(speed, speedSigma)
#            else:
#                realSpeed = speed
#            
#            if hasattr(colour, "__iter__"):
#                Particle(pos, random.choice(colour), _angle * realSpeed, lifespan, size, surface)
#            else:
#                Particle(pos, colour, _angle * realSpeed, lifespan, size, surface)
#
#        pos[1] -= size[1]