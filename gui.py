# A library for GUI / HUD elements in pygame.

import pygame

COLOURKEY = (255, 0, 255)
BLACK = (0, 0, 0)

def drawBrokenLine(colour, points, width = 1, surf=None):
    surface = surf if surf is not None else pygame.display.get_surface()

    for i, point in enumerate(points):
        if i != 0:
            pygame.draw.line(surface, colour, points[i - 1], point, width)


def multiLineRender(font, string, antialias, colour):
    colourkey = COLOURKEY if colour != COLOURKEY else BLACK

    text = [font.render(line, antialias, colour, colourkey)
            for line in string.split("\n")]

    x = max((line.get_width()  for line in text))
    y = sum((line.get_height() for line in text))
        
    s = pygame.Surface((x, y))
    s.fill(colourkey)
    s.set_colorkey(colourkey)

    blit_y = 0

    for line in text:
        s.blit(line, (0, blit_y))
        blit_y += line.get_height()

    return s


class InputBox():
    def __init__(self, font, colour, pos=None, surface = None,
                 maxlen=None, key2char=None):

        self.surface = surface if surface is not None else pygame.display.get_surface()
        
        self.text = ""
        self.font = font
        if pos is None:
            self.pos = (self.surface.get_width() / 2, self.surface.get_height() / 2)
            self.central = True
        else:
            self.pos = pos
            self.central = False
        self.colour = colour
        self.maxlen = maxlen
        self.textImg = self.font.render(self.text, True, self.colour).convert_alpha()
        
        alphabet = "abcdefghigklmnopqrstuvwxyz1234567890"
        self.key2char = key2char if key2char != None else {eval("pygame.K_" + char) : char for char in alphabet}
        self.key2upperchar = {i : j.upper() for i, j in self.key2char.items()}
        self.upperCase = False
        self.shift = False

    def draw(self):
        self.surface.blit(self.textImg, self.pos)

    def recentralise(self):
        self.pos = (self.surface.get_width() / 2 - self.textImg.get_width() / 2,
                    self.surface.get_height() / 2 - self.textImg.get_height() / 2)
    
    def key_input(self, key, boolean):
        if boolean:
            if key in self.key2char and (self.maxlen is None or len(self.text) < self.maxlen):
                if (self.upperCase and not self.shift) or (self.shift and not self.upperCase):
                    self.text += self.key2upperchar[key]
                else:
                    self.text += self.key2char[key]

                self.textImg = self.font.render(self.text, True, self.colour).convert_alpha()
                if self.central:
                    self.recentralise()

            elif key == pygame.K_BACKSPACE:
                self.text = self.text[:len(self.text) - 1]
                self.textImg = self.font.render(self.text, True, self.colour).convert_alpha()
                if self.central:
                    self.recentralise()
            elif key == pygame.K_CAPSLOCK:
                self.upperCase = not self.upperCase

            elif key == pygame.K_SPACE:
                self.text += " "
                self.textImg = self.font.render(self.text, True, self.colour).convert_alpha()
                if self.central:
                    self.recentralise()

        if key in (pygame.K_LSHIFT, pygame.K_RSHIFT):
            self.shift = boolean

class Button():
    def __init__(self, img, pos, mouseoverImg=None, clickedImg=None, surface = None):

        self.surface = surface if surface is not None else pygame.display.get_surface()
        
        self.img = img

        self.pos = pos
        self.rect = pygame.Rect(self.pos, self.img.get_size())
        self.mouseoverImg = mouseoverImg
        self.clickedImg = clickedImg

        self.mouseOver = False
        self.clicked = False

        self.mouseDown = False

    def draw(self):
        if self.mouseOver and self.mouseoverImg != None:
            self.surface.blit(self.mouseoverImg, self.pos)
        elif self.clicked and self.clickedImg != None:
            self.surface.blit(self.clickedImg, self.pos)
        else:   
            self.surface.blit(self.img, self.pos)
    def checkMouseOver(self):
        return self.rect.collidepoint(pygame.mouse.get_pos())

    def checkClicked(self, key=0):
        return self.checkMouseOver() and pygame.mouse.get_pressed()[key]

    def update(self):
        if self.checkClicked():
            if not self.mouseDown:
                self.clicked = not self.clicked
                self.mouseDown = True
        else:
            self.mouseDown = False
            
        self.mouseOver = self.checkMouseOver()

class Cursor():
    def __init__(self, img):
        pygame.mouse.set_visible(False)
        
        self.img = img
        self.screen = pygame.display.get_surface()
    def draw(self):
        pos = [pygame.mouse.get_pos()[i] - self.img.get_size()[i] / 2
               for i in (0, 1)]
        
        self.screen.blit(self.img, pos)

    
    
