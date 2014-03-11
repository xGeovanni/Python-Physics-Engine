import pygame
import game as gameEngine
import physics
import shapes
import angle
import random

keysdown = {pygame.K_UP : False,
            pygame.K_DOWN : False,
            pygame.K_w : False,
            pygame.K_s : False,}

class Paddle(physics.PhysicsObject, shapes.Rect):    
    def __init__(self, game, player):
        self.game = game
        self.player = player
         
        self.speed = 300
         
        size = [20, int(self.game.WIDTH / 6)]
        pos = [self.game.WIDTH * (1/8 if self.player == 1 else 7/8), (self.game.HEIGHT - size[1]) / 2]
        colour = (255, 0, 0) if player == 1 else (0, 0, 255)
         
        shapes.Rect.__init__(self, pos, size, game.screen, colour)
        physics.PhysicsObject.__init__(self, pos, self, kinematic=True)
        
        self.v = pygame.math.Vector2(0, 0)
        
        self.score = 0
        self.scoreAtLastRender = None
        self.scoreImage = None
        
    def AI(self):
        self.v = angle.angleBetween(self.centre, self.game.balls[0].centre)
        self.v[0] = 0
        if self.v.length() > 0:
            self.v.normalize_ip()
            
        self.v *= self.speed
         
    def handleKey(self, key, boolean):
        keysdown[key] = boolean
        
        if self.player == 1 and not keysdown[pygame.K_w] and not keysdown[pygame.K_s]:
            self.v = pygame.math.Vector2(0, 0)
        elif self.player == 2 and not keysdown[pygame.K_UP] and not keysdown[pygame.K_DOWN]:
            self.v = pygame.math.Vector2(0, 0)
         
        if self.player == 1:
            self.handleKeyP1(key)
        elif self.player == 2:
            self.handleKeyP2(key)
             
    def handleKeyP1(self, key):
        if keysdown[pygame.K_w]:
            self.v[1] = -1
        elif keysdown[pygame.K_s]:
            self.v[1] = 1
        
        if self.v.length() > 0:
            self.v.normalize_ip()
            self.v *= self.speed
         
    def handleKeyP2(self, key):
        if keysdown[pygame.K_UP]:
            self.v[1] = -1
        elif keysdown[pygame.K_DOWN]:
            self.v[1] = 1
        
        if self.v.length() > 0:
            self.v.normalize_ip()
            self.v *= self.speed
         
    def update(self):
        if not self.player:
            self.AI()
             
        self.velocity = self.v
        self.velocity[0] = 0
        
    def onOwnCollision(self, hit):
        bound = None
        
        for _object in hit[0] + hit[1]:
            if isinstance(_object, Bound):
                bound = _object
                break
                
        if bound is not None:
            if self.pos[1] > bound.pos[1]:
                self.move_ip(0, 1)
            else:
                self.move_ip(0, -1)
         
    def onOtherCollision(self, other, axis):        
        if isinstance(other, Ball):
            v = self.centre.angle_to(other.centre)
            v *= 12
            v += 180
            other.velocity.rotate_ip(v)

            if other.velocity.length() > 0:
                if angle.anglesApproxEqual(other.velocity.normalize(), angle.UP):
                    other.velocity.rotate_ip(45 * -1 if self.player == 1 else 1)
                elif angle.anglesApproxEqual(other.velocity.normalize(), angle.DOWN):
                    other.velocity.rotate_ip(-45 * -1 if self.player == 1 else 1)
                other.velocity.scale_to_length(other.speed)
                
            other.speed += 20
    
    def drawScore(self):
        if self.score != self.scoreAtLastRender:
            self.scoreImage = self.game.font.render(str(self.score), True, self.colour)
            self.scoreAtLastRender = self.score
            
        self.game.screen.blit(self.scoreImage, (self.game.WIDTH * ((6/11) if self.player != 1 else (5/11)), 0))
         
class Ball(physics.PhysicsObject, shapes.Circle):
    def __init__(self, game):
        self.game = game
         
        self.spawnPoint = [self.game.WIDTH / 2, self.game.HEIGHT / 2]
        pos = self.spawnPoint[:]
        colour = 0xFFFFFF
         
        self.startSpeed = 300
        self.speed = self.startSpeed
         
        shapes.Circle.__init__(self, pos, 5, game.screen, colour)
        physics.PhysicsObject.__init__(self, pos, self)
         
        self.velocity = random.choice((angle.LEFT, angle.RIGHT)) * self.speed
     
    def update(self):
         if not self.game.SCREENRECT.collidepoint(self.centre):
            
            if self.centre[0] < 0:
                self.game.paddles[1].score += 1
            elif self.centre[0] > self.game.WIDTH:
                self.game.paddles[0].score += 1
            
            self.centre = self.spawnPoint[:]
            self.speed = self.startSpeed
            self.velocity = random.choice((angle.LEFT, angle.RIGHT)) * self.speed
         
class Bound(physics.PhysicsObject, shapes.Rect):
    def __init__(self, pos, size):
        shapes.Rect.__init__(self, pos, size, colour = 0xFFFFFF)
        physics.PhysicsObject.__init__(self, pos, self, True, immobile=True)
         
class Pong(gameEngine.Game):
    def __init__(self):
        gameEngine.Game.__init__(self, 800, 600, "Pong", timeScale=2, screenModifiers=())
     
    def setup(self):
        pygame.font.init()
        self.font = pygame.font.Font("px10.ttf", 48)
        
        self.initPhysics(resistance = angle.ZERO)
        self.physicsManager.g = angle.ZERO
         
        self.numPlayers = 2
        self.numBalls = 1
         
        if self.numPlayers == 1:
            self.paddles = [Paddle(self, 1), Paddle(self, 0)]
        else:
            self.paddles = [Paddle(self, i + 1) for i in range(self.numPlayers)]
             
        self.balls = [Ball(self)]
        self.bounds = (
            Bound((0, -100), (self.WIDTH, 100)),
            Bound((0, self.HEIGHT), (self.WIDTH, 100)),
        )
     
    def update(self):
        for paddle in self.paddles:
            paddle.update()
        for ball in self.balls:
            ball.update()
     
    def render(self):
        for paddle in self.paddles:
            paddle.draw()
            paddle.drawScore()
        for ball in self.balls:
            ball.draw()
        for bound in self.bounds:
            bound.draw()
             
    def handleEvent(self, event):
        if event.type == pygame.KEYDOWN:
            for paddle in self.paddles:
                paddle.handleKey(event.key, True)
        elif event.type == pygame.KEYUP:
            for paddle in self.paddles:
                paddle.handleKey(event.key, False)
             
def main():
    Pong().run()
     
if __name__ == "__main__":
    main()
