import pygame

COLOURKEY = (255, 0, 255)

def split(atlas, tileSize, colourKey = COLOURKEY, gapSize = 1, scaleTo = None):
    sprites = []
    
    for i in range(0, atlas.get_width(), tileSize[0] + gapSize):
        sprites.append([])
        
        for j in range(0, atlas.get_height(), tileSize[1] + gapSize):
            
            img = atlas.subsurface((i, j, tileSize[0], tileSize[1]))
            
            if scaleTo is not None:
                img = pygame.transform.scale(img, scaleTo).convert()
                
            img.set_colorkey(colourKey)
            
            sprites[len(sprites) - 1].append(img)
            
    return sprites

def createBlank(tileSize, gridSize, background = COLOURKEY, lineWidth = 1, lineColour = (0, 0, 0)):
    
    width  = tileSize[0] * gridSize[0] + lineWidth * gridSize[0] - 1
    height = tileSize[1] * gridSize[1] + lineWidth * gridSize[1] - 1
    
    s = pygame.Surface((width, height))
    s.fill(background)
    
    if lineWidth > 0:
        for i in range(tileSize[0], width, tileSize[0] + 1):
            pygame.draw.line(s, lineColour, (i, 0), (i, height), lineWidth)

        for i in range(tileSize[1], height, tileSize[1] + 1):
            pygame.draw.line(s, lineColour, (0, i), (width, i), lineWidth)

    return s

def saveBlank(filename, *args, **kwargs):
    pygame.image.save(createBlank(*args, **kwargs), filename)
    
