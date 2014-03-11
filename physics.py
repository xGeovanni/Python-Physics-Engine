#physics.py

#This file contains the main body of the actual physics simulation done
#in this physics engine. This is done through two classes, the Physics
#Manager, the "update" method of which should be called every frame.
#This class manages all instances of the second class, the Physics
#Object, from which objects that are to follow physics or impact those 
#that do should inherit.

import pygame #I use the pygame library for displaying the motion of
              #the objects and for the fast Vector2 class written in C.

import shapes #This is another library I have created which
              #mathmatically defines rectangle and circle shapes,
              #the classes of which contain functions to test for 
              #collision with other shapes.

import angle #This library I use for caonversion between degrees,
             #radians and normalised vectors. It also contains functions
             #for finding things such as the distance and angle between
             #two points.

from threading import Thread #To run some code in a thread is to run it
                             #concurrently with other code. In this case
                             #I am creating the option of running the
                             #physicsManager in another thread than
                             #the main one.

def vectorElementMultiply(a, b):
    return pygame.math.Vector2([elA * elB for elA, elB in zip(a, b)])

class PhysicsManager(Thread):
    _instance = None
    _objects = []
    
    #def __new__(cls, *args, **kwargs):
        #Singleton class
        
        #If an instance of PhysicsManager already exists, return it.
        #Otherwise create a new one.
        
        #if cls._instance is None:
        #    cls._instance = object.__new__(cls, *args, **kwargs)
        #
        #return cls._instance
        
    def __init__(self, pixelsPerMetre=10, gMagnitude=9.81,
                 gDirection=angle.DOWN, updateFunc=None,
                 timeScale=1, resistance = (-0, -0)):

        PhysicsManager._instance = self

        Thread.__init__(self)
        self.daemon = True #Daemon threads do not keep the program open
                           #while all non-daemon threads have been 
                           #closed.
        
        self.objects = self.__class__._objects 
        #PhysicsObjects of which this manager is keeping track.
        
        self.clock = pygame.time.Clock() #Clock for time management.
        
        self.pixelsPerMetre = pixelsPerMetre #Pixel to metre conversion 
                                             #rate.
        self.gMagnitude = gMagnitude #Magniture of gravity.
        self.gDirection = gDirection #Direction of gravity.
        self.g = self.gDirection * self.gMagnitude * self.pixelsPerMetre    
        self.updateFunc = updateFunc #External update function applied
                                     #when physics is updated.
                                     
        self.resistance = pygame.math.Vector2(resistance)
        #Represents the resistance applied due to air, liquid, friction,
        #etc.

        self.timeScale = timeScale #The amount of seconds that pass in
                                   #the simulation when one passes in
                                   #reality. Defaults to 1.
                                     
        self.frameCount = 0 #Amount of frames run since the beginning.

        self.dt = 0 #Delta Time. the change in time since the last frame
                    #in seconds.
        
    def update(self, deltaTime):
        """Update the physics for this frame"""
        
        self.dt = self.clock.tick() * self.timeScale / 1000 
        #Divide by 1000 to convert milliseconds to seconds.
        
        for object_ in self.objects:
            object_.physicsUpdate(deltaTime) #Update our objects.

        if self.updateFunc is not None:
            self.updateFunc() #If we have been passed an external
                              #function to be run when the physics is
                              #updated, do so.
            
        self.frameCount += 1
        
    def applyResistance(self, object_, dt):
        """Apply resistance from air, friction, etc."""
        
        r = pygame.math.Vector2(self.resistance) #Copy resistance so as
                                                 #to not change it
                                                 #overall while changing
                                                 #it to apply to this
                                                 #particular object.
        
        if object_.velocity[0] < 0:
            r[0] *= -1
        if object_.velocity[0] == 0:
            r[0] = 0 
        if object_.velocity[1] < 0:
            r[1] *= -1
        if object_.velocity[1] == 0:
            r[1] = 0
            
        object_.applyForce(r * object_.velocity.length_squared() * dt)
        #Resistance scales with the squared magnitude of the velocity.
         
    def collisionCheck(self, collider):
        """Check if an object is colliding with any other objects"""
        
        return [object_ for object_ in self.objects
                if collider.collide(object_.collider)
                and collider.id != object_.collider.id]

        #collider.id is unique for each enique collider, but is shared
        #between copies of the same collider. (when the copy method of
        #the collider is invoked this is shared.) This is done as the
        #Physics Objects' methods which check whether they are colliding
        #actually use copies of the object's collider, as the collider
        #copies must be moved before the actual collider can be moved, 
        #to check whether this movement would result in collision.
    
    def moveWhileColliding(self, object_, hit, minSpeedSquared=4,
                           fidelity = 0.001):
        """Move an object if it is overlapping with another until it is
           not longer doing so."""

        #It is important to do this as can occasionally become stuck in
        #one another at lower frame rates.
        
        if object_.velocity.length_squared() < minSpeedSquared:
            return #We only perform this operation on objects going
                   #over a certain speed.

        fidelity = fidelity if fidelity is not None else self.dt
        #The fidelity is the accuracy with which we perform this
        #operation. The lower the number, the closer the object will
        #be to where it collided, but also the slower this function will
        #run. This defults to the most recent delta time.
        
        for collidingObject in hit[0] + hit[1]:
            
            angle_ = angle.angleBetween(collidingObject.collider.centre,
                                        object_.collider.centre)
            
            while (object_.collider.collide(collidingObject.collider) 
                   and object_ != collidingObject):
                       
                delta = angle_ * fidelity
                object_.collider.move_ip(delta)

    def run(self):
        
        #The run method is called when calling PhysicsManager.start()
        #if using a threaded approach.
        
        while True:
            self.update(self.dt)

class PhysicsObject():
    def __init__(self, pos, collider, kinematic = False,
                density = 1, velocity = (0, 0), acceleration = (0, 0),
                bounciness = 1, attractiveness = 0, immobile = False):

        self.pos = pygame.math.Vector2(pos) #Our initial position.
        self.velocity = pygame.math.Vector2(velocity) #Our initial
                                                      #velocity.
        self.acceleration = pygame.math.Vector2(acceleration)
        #Our initial acceleration.
        
        self.immobile = immobile #An immobile object is never expected
                                 #to move and thus only exists for
                                 #mobile objects to collide with.
        
        self.bounciness = bounciness #The coefficient of restitution.
                                     #the ratio of final relative speed
                                     #to initial relative speed after
                                     #collision.
                                     
        self.attractiveness = attractiveness #How attractive an object 
                                             #is, used to simulate
                                             #things such as gravity
                                             #and magnetism.
    
        self.kinematic = kinematic #A kinematic object does not respond
                                   #to forces. It will thus be
                                   #unaffected by gravity, for instance.
        
        if isinstance(collider, shapes.Shape):
            self.collider = collider #A collider is an approximation of
                                     #the shape of an object, 
                                     #represented as a circle or
                                     #rectange.
        else:
            raise ValueError("Collider must be a Shape")
            
        self.physicsManager = PhysicsManager._instance
        PhysicsManager._objects.append(self) #Add ourselves to the list
                                             #of objects which the
                                             #physics manager manages.
        
        self.density = density
        self.mass = self.density * self.collider.area #Mass = density *
                                                      #volume. Area
                                                      #replaces volume
                                                      #in 2D.
        
        self.weight = self.mass * self.physicsManager.g #F = ma
        
    def applyAcceleration(self, a, dt):
        # v = u + at
        self.velocity[0] += a[0] * dt
        self.velocity[1] += a[1] * dt
        
    def applyForce(self, f):
        # a = f / m
        self.acceleration = f / self.mass
        
    def checkMove(self, dt):
        """Check whether we can move next frame, which we
        can unless we collided with something"""
        
        hit = []
        
        #Horizontal
        
        testCol = self.collider.move(self.velocity[0] * dt, 0)
        hit.append(self.physicsManager.collisionCheck(testCol))
        
        #Vertical
        
        testCol = self.collider.move(0 , self.velocity[1] * dt)
        hit.append(self.physicsManager.collisionCheck(testCol))

        return hit
    
    def calcEnglish(self, hit):
        """Calcuate the angle on which we travel after colliding with
           a circle."""
        
        for object_ in hit:
            if isinstance(object_.collider, shapes.Circle):
                english = angle.angleBetween(object_.collider.centre,
                                             self.collider.centre)
                return english
        
        return angle.ZERO
    
    def push(self, hit, dt):
        """Pushing an object after colliding with it, transferring
           momentum."""
        
        for object_ in hit:
            object_.velocity = (self.velocity * self.mass / 
                                object_.mass) * ((object_.bounciness + 
                               self.bounciness) / 2)
            
        self.velocity = ((hit[0].velocity * hit[0].mass / self.mass) *
                         ((self.bounciness + hit[0].bounciness) / 2))
            
    def bounce(self, hit, i, dt, minSpeedSquared = 4):
        """After hitting an immobile object we bounce off of it."""
        
        if not any([object_.immobile or 
                    object_.velocity.length_squared() < minSpeedSquared 
                    for object_ in hit[i]]):
            return
        
        allBouncinessValues = ([object_.bounciness 
                                for object_ in hit[i]] 
                               + [self.bounciness])
        
        avgBounciness = (sum(allBouncinessValues) /
                         len(allBouncinessValues))
        
        self.velocity[i] *= -avgBounciness
        
        for object_ in hit[i]:
            object_.velocity *= -avgBounciness
            
    def attract(self, object_, dt):
        """Attracting other objects, simulating forces such as
           gravity and magnetism."""
        
        if self == object_:
            #Objects do not attract themselves.
            return
        
        distance = object_.collider.centre - self.collider.centre
        
        angle_to = angle.angleBetween(object_.collider.centre,
                                      self.collider.centre)
        
        object_.applyAcceleration(angle_to * self.attractiveness /
                                  distance.length_squared(), dt)
                
    def physicsMoveX(self, dt):
        # d = vt
        self.collider.move_ip(self.velocity[0] * dt, 0)
    
    def physicsMoveY(self, dt):
        # d = vt
        self.collider.move_ip(0, self.velocity[1] * dt)
        
    def onOwnCollision(self, hit):
        """Hook for user-defined function to be run when we register a
           collision"""
        
        pass
    
    def onOtherCollision(self, other, axis):
        """Hook for user-defined function to be run when another object
           registers collision with this."""
        
        pass
        
    def kinematicUpdate(self, dt, hit):
        """Runs whether object is kinematic or not"""
        
        if self.attractiveness != 0:
            for object_ in self.physicsManager.objects:
                self.attract(object_, dt)
                                          
        if self.kinematic and not self.immobile:
            self.pos = self.collider.getPos() #Update position to
                                              #reflect that of our
                                              #collider.
                                              
            if any(hit):
                self.onOwnCollision(hit)
                
                for object_ in hit[0]:
                    object_.onOtherCollision(self, 0)
                
                for object_ in hit[1]:
                    object_.onOtherCollision(self, 1)
            
            if not hit[0]: #If there was no collision in X.
                self.physicsMoveX(dt)
            else:
                self.push(hit[0], dt)
                self.physicsManager.moveWhileColliding(self, hit)
                    
            if not hit[1]: #If there was no collision in Y.
                self.physicsMoveY(dt)
            else:
                self.push(hit[1], dt)
                self.physicsManager.moveWhileColliding(self, hit)
                
        
    def nonKinematicUpdate(self, dt, hit):
        """Runs only if object is not kinematic"""
        
        if any(hit):
            self.onOwnCollision(hit)
            
            for object_ in hit[0]:
                object_.onOtherCollision(self, 0)
            
            for object_ in hit[1]:
                object_.onOtherCollision(self, 1)
        
        if not hit[0]: #If there was no collision in X.
            self.physicsMoveX(dt)
        else:
            #If we hit something bounce off of it and push it away.
            #This is only if the collision occured in our x axis.
            
            self.push(hit[0], dt)
            self.bounce(hit, 0, dt)
            
            self.physicsManager.moveWhileColliding(self, hit)
            
        if not hit[1]: #If there was no collision in Y.
            self.physicsMoveY(dt)
        else:
            #If we hit something bounce off of it and push it away.
            #This is only if the collision occured in our y axis.
            
            self.push(hit[1], dt)
            self.bounce(hit, 1, dt)
            
            if any([isinstance(object_, shapes.Circle) for object_ in hit[1]]):
                self.velocity.rotate_ip(round(angle.toDegrees(self.calcEnglish(hit[1])), 3))
            
            self.physicsManager.moveWhileColliding(self, hit)

        self.applyAcceleration(self.physicsManager.g, dt)
        self.applyAcceleration(self.acceleration, dt)
        self.physicsManager.applyResistance(self, dt)
        
    def physicsUpdate(self, dt):
        if not self.kinematic:
            self.nonKinematicUpdate(dt, self.checkMove(dt))
            
        self.kinematicUpdate(dt, self.checkMove(dt))
        
