import game as gameEngine
import pygame
import physics
import shapes
import angle
import random

class Player(shapes.Circle, physics.PhysicsObject):
    def __init__(self, game):
        self.game = game
        
        shapes.Circle.__init__(self, self.game.playerSpawn[:], self.game.playerRadius, self.game.screen, 0xFF0000)
        physics.PhysicsObject.__init__(self, self.game.playerSpawn[:], self)
        
        self.speed = 200
        self.v = pygame.math.Vector2(0, 0)
        
        self.jump = False
        self.grounded = False
        
        self.lastHitPlatform = 0
        
    def handleKey(self, key, boolean):
        if (key in (gameEngine.key("a"), gameEngine.key("d"))) and not boolean:
            self.v[0] = 0
        elif key == gameEngine.key("a"):
            self.v[0] = -self.speed
        elif key == gameEngine.key("d"):
            self.v[0] = self.speed
            
        if key == gameEngine.key("w") and boolean:
            self.jump = True
            
    def onOwnCollision(self, hit):
        for object_ in hit[0] + hit[1]:
            if isinstance(object_, Platform):
                if object_.topleft[1] > self.centre[1]:
                    self.grounded = True
                    self.lastHitPlatform = self.game.elapsedTime

    def update(self):
        self.velocity[0] = self.v[0]
        
        if self.jump:
            if self.grounded:
                self.velocity[1] -= 300
                self.grounded = False
            self.jump = False
            
        if self.game.elapsedTime - self.lastHitPlatform > self.game.deltaTime * 10:
            self.grounded = False
            
class Ball(physics.PhysicsObject, shapes.Circle):
    def __init__(self, game):
        self.game = game
        
        pos = (random.randrange(self.game.WIDTH), random.randrange(self.game.HEIGHT))
        colour = 0x00FF00
        
        shapes.Circle.__init__(self, pos, 12, game.screen, colour)
        physics.PhysicsObject.__init__(self, pos, self, bounciness = .9, density = 2)
            
class Platform(shapes.Rect, physics.PhysicsObject):
    def __init__(self, pos, size, game, colour=0x777777, bounciness=0.3, attractiveness=0):
        shapes.Rect.__init__(self, pos, size, game.screen, colour)
        physics.PhysicsObject.__init__(self, pos, self, kinematic=True, immobile=True, bounciness=bounciness, attractiveness=attractiveness)

class Platformer(gameEngine.Game):
    def __init__(self):
        gameEngine.Game.__init__(self, 800, 600, "Platformer", fillcolour=0x2245EF, RENDERRATE=60)
        
    def setup(self):
        self.playerRadius = 25
        self.playerSpawn = (self.WIDTH / 2, self.HEIGHT / 2)
        
        self.initPhysics(pixelsPerMetre=(self.playerRadius * 2 / 1.7), resistance=angle.ZERO)
        
        self.player = Player(self)
        
        self.balls = [Ball(self) for i in range(0)]
        
        self.platforms = (Platform((100, 400), (400, 100), self),
                          Platform((-400, 500), (400, 100), self),
                          Platform((600, 500), (400, 100), self),
                          Platform((800, 200), (80, 80), self, colour=0x7DF9FF, attractiveness=10000000),
                          Platform((650, 200), (80, 80), self, colour=0x7DF9FF, attractiveness=10000000),
                          Platform((-800, 500), (200, 80), self, colour=0xBB0000, bounciness=1))
        
        self.oldPlayerPos = self.player.collider.centre[:]
        self.totalDelta = pygame.math.Vector2(0, 0)
        
        self.elapsedTime = 0
        
    def update(self):
        self.elapsedTime += self.deltaTime
        
        self.player.update()
        
        self.scroll(self.player.collider.centre - self.oldPlayerPos)
        self.oldPlayerPos = self.player.collider.centre[:]
        
    def render(self):
        self.player.draw()
        
        for ball in self.balls:
            ball.draw()
        
        for platform in self.platforms:
            platform.draw()
    
    def handleEvent(self, event):
        if event.type == pygame.KEYDOWN:
            self.player.handleKey(event.key, True)
        elif event.type == pygame.KEYUP:
            self.player.handleKey(event.key, False)
            
    def scroll(self, delta):
        for object_ in self.physicsManager.objects:
            object_.collider.move_ip(-delta)
            self.totalDelta += delta
        
def main():
    Platformer().run()
    
if __name__ == "__main__":
    main()
        
        
