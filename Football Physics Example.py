import pygame
import game as gameEngine
import physics
import shapes
import angle
import random
import gui
from math import floor
from os.path import exists

doubleAI = False

class Player(physics.PhysicsObject, shapes.Circle):
    def __init__(self, game, player):
        self.game = game
        self.player = player
        
        self.speed = 400
        radius = 15
        
        pos = [self.game.WIDTH * (1/8 if self.player == 1 else 7/8), self.game.HEIGHT / 2 - radius]
        colour = (255, 0, 0) if player == 1 else (0, 0, 255)
        
        shapes.Circle.__init__(self, pos, radius, game.screen, colour)
        physics.PhysicsObject.__init__(self, pos, self, kinematic = False)
        
        self.score = 0
        self.scoreAtLastRender = None
        self.scoreImage = None
        
        self.v = pygame.math.Vector2(0, 0)
        self.timeBetweenCalcDirection = .2
        self.timeUntilCalcDirection = 0
        self.lastCentre = pygame.math.Vector2(self.centre)
        
        self.timeUntilEndMotion = 0
        
        self.followedBallLast = False
        
    def oldAI(self):
        self.timeUntilCalcDirection -= self.game.deltaTime
        self.timeUntilEndMotion -= self.game.deltaTime
        
        if self.timeUntilCalcDirection <= 0:
            aimPos = pygame.math.Vector2(self.game.balls[0].centre)
            angle_to_ball = angle.angleBetween(self.centre, aimPos)
            
            self.v = angle_to_ball * self.speed
            
            if self.centre == self.lastCentre:
                self.v[0] *= random.uniform(-1, 1)
                self.v[1] *= random.uniform(-1, 1)
        
            self.lastCentre = None
            
            self.timeUntilCalcDirection = self.timeBetweenCalcDirection
            
        self.velocity = self.v
    
    def AI(self):
        self.timeUntilCalcDirection -= self.game.deltaTime
        self.timeUntilEndMotion -= self.game.deltaTime
        
        if self.timeUntilCalcDirection <= 0 and self.timeUntilEndMotion <= 0:
            
            aimPos = pygame.math.Vector2(self.game.balls[0].centre)
            angle_to_ball = angle.angleBetween(self.centre, aimPos)
            
            turnPoint = aimPos[0] + (self.radius + self.game.balls[0].radius)
            
            if (self.followedBallLast and ((self.centre[0] < aimPos[0] and self.player == 1) or (self.centre[0] > aimPos[0] and self.player != 1))) or (self.centre[0] < turnPoint and self.player == 1) or (self.centre[0] > turnPoint and self.player != 1):
                self.followedBallLast = True
                
                direction = angle_to_ball
                
                if self.game.balls[0].centre[1] > self.game.HEIGHT / 2 and self.game.balls[0].centre[1] > self.centre[1]:
                    direction[1] += .5
                
                elif self.game.balls[0].centre[1] < self.game.HEIGHT / 2 and self.game.balls[0].centre[1] < self.centre[1]:
                    direction[1] -= .5
                
            else:
                self.followedBallLast = False
                
                goalPos = (1 if self.player == 1 else self.game.WIDTH, self.game.HEIGHT / 2)
                
                angle_to_own_goal = angle.angleBetween(self.centre, goalPos)
                angle_ball_to_goal = angle.angleBetween(self.game.balls[0].centre, goalPos)
                
                direction = angle_to_own_goal
                
                if self.game.balls[0].velocity.length_squared() > 0 and angle.anglesApproxEqual(self.game.balls[0].velocity.normalize(), angle_ball_to_goal):
                    direction[1] = angle_to_ball[1]
                else:
                    direction[1] = ((angle_to_ball * (((self.game.balls[0].centre[1] - self.centre[1])) / self.game.HEIGHT) * -1) + angle_to_own_goal).normalize()[1]
                    
            if self.centre == self.lastCentre:
                direction[0] *= -random.random()
                direction[1] *= -random.random()
                
                self.timeUntilEndMotion = .3
            
            self.v = direction.normalize() * self.speed
        
            self.lastCentre = pygame.math.Vector2(self.centre)
            self.timeUntilCalcDirection = self.timeBetweenCalcDirection
        
        self.velocity = self.v
    
    def playerControl(self):
        self.velocity = angle.angleBetween(self.centre, pygame.mouse.get_pos()) * self.speed
    
    def update(self):
        if doubleAI or not self.player:
            self.AI()
        else:
            self.playerControl()
    
    def drawScore(self):
        if self.score != self.scoreAtLastRender:
            self.scoreImage = self.game.font.render(str(self.score), True, self.colour)
            self.scoreAtLastRender = self.score
            
        self.game.screen.blit(self.scoreImage, (self.game.WIDTH * ((3/5) if self.player != 1 else (2/5)), 20))
        
class Ball(physics.PhysicsObject, shapes.Circle):
    def __init__(self, game):
        self.game = game
        
        self.spawnPoint = [self.game.WIDTH / 2, self.game.HEIGHT / 2]
        
        self.startSpeed = 200
        
        pos = self.spawnPoint[:]
        colour = 0xFFFFFF
       
        shapes.Circle.__init__(self, pos, 7, game.screen, colour)
        physics.PhysicsObject.__init__(self, pos, self, bounciness = 1, density = 4)
    
    def update(self):
        if not self.game.SCREENRECT.collidepoint(self.centre):
            
            if self.centre[0] < 0:
                self.game.players[1].score += 1
            elif self.centre[0] > self.game.WIDTH:
                self.game.players[0].score += 1
            
            self.centre = self.spawnPoint[:]
            self.velocity = angle.randAngle() * self.startSpeed
        
class Bound(physics.PhysicsObject, shapes.Rect):
    def __init__(self, pos, size, colour=0xFFFFFF):
        shapes.Rect.__init__(self, pos, size, colour=colour)
        physics.PhysicsObject.__init__(self, pos, self, True, immobile = True)
        
class Football(gameEngine.Game):
    def __init__(self):
        gameEngine.Game.__init__(self, 600, 480, "Football", timeScale=.7, screenModifiers=(pygame.FULLSCREEN,))
    def setup(self):
        
        self.initPhysics(resistance=(0, 0))
        pygame.font.init()

        self.timeRemaining = 180
        self.timeString = None
        self.timeImg = None
        
        self.highScoreDir = "highscore.txt"
        
        self.name = None
        self.inputBox = None
        
        self.font = pygame.font.Font("px10.ttf", 48)
        
        self.physicsManager.g = angle.ZERO
        
        self.numPlayers = 1
        self.numBalls = 1

        self.pause_oldTimeScale = None
        self.slow_oldTimeScale = None
        
        if self.numPlayers == 1:
            self.players = [Player(self, 1), Player(self, 0)]
        else:
            self.players = [Player(self, i + 1) for i in range(self.numPlayers)]
            
        self.balls = [Ball(self) for i in range(self.numBalls)]
        
        self.bounds = (
            Bound((20, -1000), (self.WIDTH - 20, 1020), 0x0000DD),
            Bound((-1000, 0), (1020, self.HEIGHT * (1/3)), 0xDD0000),
            Bound((-1000, self.HEIGHT * (2/3)), (1020, self.HEIGHT * (1/3)), 0xDD0000),
            Bound((self.WIDTH - 20, 0), (1020, self.HEIGHT * (1/3)), 0x0000DD),
            Bound((self.WIDTH - 20, self.HEIGHT * (2/3)), (1020, self.HEIGHT * (1/3)), 0x0000DD),
            Bound((20, self.HEIGHT - 20), (self.WIDTH -20, 1020), 0xDD0000),
        )
    
    def update(self):
        if self.timeRemaining <= 0 and False:
            if self.inputBox is None:
                self.inputBox = gui.InputBox(self.font, (255, 255, 255))
                self.pause()
            if self.name is not None:
                self.storeHighScores()
                self.end()
                self.quit()
                
            return
        
        for player in self.players:
            player.update()
        for ball in self.balls:
            ball.update()

        self.timeRemaining -= self.deltaTime
    
    def render(self):
        if self.inputBox is not None:
            self.inputBox.draw()
            return
        
        self.drawTime()
        
        for player in self.players:
            player.drawScore()
            player.draw()
        for ball in self.balls:
            ball.draw()
        for bound in self.bounds:
            bound.draw()

    def pause(self):
        if self.pause_oldTimeScale is None:
            self.pause_oldTimeScale = self.timeScale
            self.timeScale = 0
        else:
            self.timeScale = self.pause_oldTimeScale
            self.pause_oldTimeScale = None

    def slow(self, timeScale=.1):
        if self.pause_oldTimeScale is None:
            if self.slow_oldTimeScale is None:
                self.slow_oldTimeScale = self.timeScale
                self.timeScale = timeScale
            else:
                self.timeScale = self.slow_oldTimeScale
                self.slow_oldTimeScale = None

    def drawTime(self):
        return
        minutes = floor(self.timeRemaining / 60)
        seconds = floor(self.timeRemaining % 60)

        timeString = str(minutes) + ":" + str(seconds)

        if self.timeString != timeString:
            self.timeString = timeString

            self.timeImg = self.font.render(timeString, True, (255, 255, 255))

        self.screen.blit(self.timeImg, ((self.HEIGHT + self.timeImg.get_height()) / 2, 20))
    
    def storeHighScores(self):
        if not exists(self.highScoreDir):
            f = open(self.highScoreDir, "w")
            f.write(str({"A" : (0, 1),
                         "B" : (0, 1),
                         "C" : (0, 1),
                         "D" : (0, 1),
                         "E" : (0, 1)}))
            f.close()
        
        f = open(self.highScoreDir, "r")
        highscores = eval(f.read())
        f.close()
        
        f = open(self.highScoreDir, "w")
        
        highscores[self.name] = (self.players[0].score, self.players[1].score + 1)
        
        ratios = [hs[0] / hs[1] for hs in highscores.values()]
        ratio = self.players[0].score / (self.players[1].score + 1)
        
        for i in range(len(ratios)):
            if ratio > ratios[i]:
                break
        else:
            f.write(str(highscores))
            f.close()
            
            highscores = dict(tuple(highscores.items())[sorted(ratios).index(ratio)] for ratio in ratios)
            
            return
            
        highscores = dict(tuple(highscores.items())[sorted(ratios).index(ratio)] for ratio in ratios)
        
        f.write(str(highscores))
        f.close()
        
    def handleEvent(self, event):
        if event.type == pygame.KEYDOWN:
            print(self.clock.get_fps())

            if event.key == pygame.K_p and self.inputBox is None:
                self.pause()
            elif event.key == pygame.K_TAB:
                self.slow()
            if self.inputBox is not None:
                self.inputBox.key_input(event.key, True)
                
                if event.key == pygame.K_RETURN:
                    self.name = self.inputBox.text
        
        elif event.type == pygame.KEYUP and self.timeRemaining <= 0:
                self.inputBox.key_input(event.key, False)
            
def main():
    Football().run()
    
if __name__ == "__main__":
    main()
