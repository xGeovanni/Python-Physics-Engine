import sys
import pygame
import threading
from fractions import gcd
from grid import Grid

def getKeycodes():
    """A method to get all the keycodes
     used in pygame in to a dictionary"""
    
    keycodes = {item[2:].lower() : eval("pygame." + item)
                for item in dir(pygame) if "K_" in item}
    
    return keycodes

KEYCODES = getKeycodes()

def key(key):
    return KEYCODES[key]

def calcAspectRatio(width, height):
    hcf = gcd(width, height)
    return (width / hcf, height / hcf)

class Renderer(threading.Thread):
    def __init__(self, RENDERRATE, *renderFuncs):
        self.clock = pygame.time.Clock()
        
        self.renderFuncs = list(renderFuncs)
        self.RENDERRATE = RENDERRATE
        self.deltaTime = self.clock.tick(self.RENDERRATE)

        threading.Thread.__init__(self)
        
    def addRenderFunc(self, func):
        self.renderFuncs.append(func)
        
    def run(self):
        while True:
            self.deltaTime = self.clock.tick(self.RENDERRATE)
            
            for func in self.renderFuncs:
                func()
                
class Game():
    def __init__(self, WIDTH, HEIGHT, gameName = "", gridsize = None,
                 FRAMERATE = 0, RENDERRATE = None, fillcolour = (0, 0, 0),
                 screenModifiers = (), timeScale = 1, dt_threshold = 0.2):
        
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), 
                                              *screenModifiers)
            
        self.gameName = gameName
        pygame.display.set_caption(self.gameName)
            
        self.SCREENSIZE = pygame.math.Vector2(self.screen.get_size())
        self.SCREENRECT = pygame.Rect((0, 0), self.SCREENSIZE)
        self.screenModifiers = screenModifiers
        self.WIDTH, self.HEIGHT = self.SCREENSIZE
        
        self.aspectRatio = calcAspectRatio(self.WIDTH, self.HEIGHT)
            
        self.fillcolour = fillcolour
        
        self.returnValue = None
        self.paused = False
        self.dirtyRects = []
        self.oldDirtyRects = []
        
        self.clock = pygame.time.Clock()
        self.FRAMERATE = FRAMERATE
        self.timeScale = timeScale
        self.deltaTime = self.clock.tick(self.FRAMERATE) / 1000 * self.timeScale        
        self.dt_threshold = dt_threshold
        
        self.particleManager = None
        self.threadedPhysics = False
        
        self.physicsManager = None
        
        if RENDERRATE is None:
            self.renderer = None
        else:
            self.renderer = Renderer(RENDERRATE, self.render,
                                     self.updateDisplay)
        
        if gridsize:
            self.grid = Grid(self.screen, gridsize)
            
        self.ended = False

    def updateDisplay(self):
        #self.screen.unlock()
        
        if self.dirtyRects:
            pygame.display.update(self.dirtyRects + self.oldDirtyRects)
        else:
            pygame.display.update()
        
        #self.screen.lock()

        self.screen.fill(self.fillcolour)
        
    def setup(self):
        """Hook for setup"""
        pass
    
    def title(self):
        """Hook for title screen"""
        pass
        
    def update(self):
        """Hook for game update"""
        pass
    
    def render(self):
        """Hook for game render"""
        pass
    
    def drawBackground(self):
        """Hook for background drawing"""
        pass
    
    def handleEvent(self, event):
        """Hook for event handling"""
        pass
    
    def physicsUpdate(self):
        """Hook for post-physics update"""
        pass
    
    def handleInputs(self):
        """Input handling"""
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()
                
            self.handleEvent(event)
                
    def initParticles(self):
        try:
            import particles
            
        except ImportError:
            raise ImportError("Particle library not found")
        
        self.particles = particles
        self.particleManager = self.particles.ParticleManager()
        
        if self.renderer:
            self.renderer.addRenderFunc(self.particleManager.render)
        
    def initPhysics(self, threaded = False, *args, **kwargs):
        try:
            import physics
            
        except ImportError:
            raise ImportError("Physics library not found")
        
        self.physicsManager = physics.PhysicsManager(*args, **kwargs)
        
        self.physicsManager.updateFunc = self.physicsUpdate        
        self.threadedPhysics = threaded

        if threaded:
            self.physicsManager.start()
        
    def run(self):
        if self.renderer:
            self.renderer.start()
            
        self.title()
        self.setup()
        
        while not self.ended:
            
            self.deltaTime = self.clock.tick(self.FRAMERATE) / 1000 * self.timeScale
            
            if self.dt_threshold and self.deltaTime > self.dt_threshold:
                
                # A large deltaTime value indicates that the window was
                # being resized or dragged between now and the last 
                # frame. This large dt value would, if left alone,
                # cause all sorts of problems for our game, such as 
                # objects clipping through each other as their movement
                # is scaled by deltaTime. We thus skip this frame.
                
                continue
            
            self.oldDirtyRects = self.dirtyRects
            self.dirtyRects = []
            
            self.update()
            self.handleInputs()
            
            if self.particleManager:
                if self.renderer is None or True:
                    self.particleManager.update(self.deltaTime)
                    
                else:
                    self.particleManager.update(self.renderer.deltaTime)

            if self.physicsManager and not self.threadedPhysics:
                self.physicsManager.update(self.deltaTime)
                self.physicsUpdate()
                
            if not self.renderer:
                self.drawBackground()
                
                if self.particleManager:
                    self.particleManager.render()
                
                self.render()
                
                self.updateDisplay()
            
            if self.returnValue is not None:
                return self.returnValue
            
    def end(self):
        self.ended = True
    
    def quit(self):
        self.end()
        pygame.quit()
        sys.exit(0)
