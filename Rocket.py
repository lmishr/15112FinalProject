

from direct.showbase.ShowBase import ShowBase
from panda3d.core import TextNode, TransparencyAttrib
from panda3d.core import LPoint3, LVector3
from direct.gui.OnscreenText import OnscreenText
from panda3d.core import Filename, AmbientLight, DirectionalLight
from direct.task.Task import Task
from direct.actor.Actor import Actor
from random import randint, choice, random
from direct.interval.MetaInterval import Sequence
from direct.interval.FunctionInterval import Wait, Func
import sys
import math
import random

# Constants:
SPRITE_POS = 55


def loadObject(tex=None, pos=LPoint3(0, 0), depth=SPRITE_POS, scale=1,
               transparency=True):
    # This helps reduce the amount of code used by loading objects, since all of
    # the objects are pretty much the same.
    # this function is taken from the Panda 3D samples
    
    # Every object uses the plane model and is parented to the camera
    # so that it faces the screen.
    obj = loader.loadModel("models/plane")
    obj.reparentTo(camera)

    # Set the initial position and scale.
    obj.setPos(pos.getX(), depth, pos.getY())
    obj.setScale(scale)

    # This tells Panda not to worry about the order that things are drawn in
    # (ie. disable Z-testing).  This prevents an effect known as Z-fighting.
    obj.setBin("unsorted", 0)
    obj.setDepthTest(False)

    return obj

def drawText(text, i):
    # code adapted from Panda 3D samples
    # draws text at given position
    return OnscreenText(text=text, parent=base.a2dTopLeft,
                        pos=(0.07, -.07 * i - 0.1),
                        fg=(1, 1, 1, 1), align=TextNode.ALeft,
                        shadow=(0, 0, 0, 0.5), scale=.07)

class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.timeInitial1 = 0 # helps tracks time
        self.yInitial = 0 # helps track y position of rocket
        
        self.setBackgroundColor((0, 0, 0, 1))
        
        # Disable the camera trackball controls
        self.disableMouse()
        self.keyMap = {"left": 0, "right": 0, "up": 0, "down":0, "fire": 0}
        self.accept("arrow_left", self.setKey, ["left", True])
        self.accept("arrow_right", self.setKey, ["right", True])
        self.accept("arrow_up", self.setKey, ["up", True])
        self.accept("arrow_down", self.setKey, ["down", True])
        self.accept("space", self.setKey, ["fire", True])

        self.accept("p", self.removeHomeScreen)
                
        # Creates some lighting
        # THE FOLLOWING CODE FOR LIGHTING IS ADAPTED FROM
        # "ROAMING RALPH" SAMPLE PROVIDED BY PANDA 3D OFFICIAL WEBSITE
        ambientLight = AmbientLight("ambientLight")
        ambientLight.setColor((.2, .2, .2, 0.2))
        directionalLight = DirectionalLight("directionalLight")
        directionalLight.setDirection((-10, 10, 5))
        directionalLight.setColor((1, 1, 1, 1))
        directionalLight.setSpecularColor((1, 1, 1, 1))
        render.setLight(render.attachNewNode(ambientLight))
        render.setLight(render.attachNewNode(directionalLight))
        
        # Create rocket model
        self.rocket = loader.loadModel("models/rocket16.blend.x")
        self.rocket.setScale(1)
        self.rocket.reparentTo(render)
        self.rocket.setPos(0, 10, 0)
        self.rocketSpeed = 0.5

        self.bullets = [] # list of bullets that rocket shoots

        ##### ENEMIES #####
        self.enemies = [] #list of enemies
        self.enemySpeed = 0.04 #initial enemy speed

        self.stars = []
        self.coins = []

        ##### POWER-UPS #####
        self.speedBoosts = []
        self.isSpeeding = False
        self.endSpeedingTime = 0
        
        self.AIList = []
        self.isAI = False
        self.endAITime = 0
        
        self.coinMagnets = []
        self.isMagnetic = False
        self.endMagneticTime = 0

        
        self.obstacles = [] # list of obstacles on screen
        self.numCoins = 0 # number of coins collected

        ##### LIVES #####
        self.numLives = 3 # player starts out with 3 lives
        self.lives = [] #stores life objects
        self.getLifeObjects()

        self.gameOver = False

        self.levelNum = 1 # start on level 1

        ##### READ TEXT FILE #####
        self.inventoryFile = open("RocketInventory.txt","r+")
        self.inventory = self.inventoryFile.readlines()
        self.highScore = 0
        self.totalCoins = 0
        self.hasRocketBuddy = False
        self.hasCoinGun = False
        self.hasObstacleGun = False
        self.readingFeatures = False
        self.readingStore = False

        for line in self.inventory:
            if ":" in line:
                i = line.index(":")
                s = line[:i]

            if s == "High Score":
                self.highScore = line[i+1:]
                self.highScore = self.highScore[:-1]

            elif s == "Coins":
                self.totalCoins = line[i+1:]
                self.totalCoins = self.totalCoins[:-1]
                
            elif s== "Features":
                self.readingFeatures = True

            elif s == "Store":
                self.readingStore = True

            if self.readingFeatures:
                if s == "Rocket buddy":
                    if "No" in line[i:]:
                        self.hasRocketBuddy = False
                    else:
                        self.hasRocketBuddy = True
                        
        self.totalCoins = int(self.totalCoins)
        self.highScore = float(self.highScore)
        ## Give user appropriate powers
        if self.hasRocketBuddy:
            # if the user has rocket buddy, load model   
            self.buddy = loader.loadModel("models/miniRocket.blend.x")
            self.buddy.setScale(0.4)
            self.buddy.reparentTo(render)

            self.buddy.setPos(self.rocket.getX() + 2,
                              self.rocket.getY(),
                              self.rocket.getZ() + 2)

        ##### ON-SCREEN TEXT #####
        self.title = OnscreenText(text="SPACE RAIDERS",
                                  parent=base.a2dBottomRight, scale=.1,
                                  align=TextNode.ARight, pos=(-0.1, 0.1),
                                  fg=(1, 1, 1, 1), shadow=(0, 0, 0, 0.5))
        drawText("[Space Bar]: Fire", 1)
        drawText("Use arrow keys to move", 2)
        self.coinsText = drawText("Coins:" + str(self.totalCoins), 3)
        self.levelText = drawText("Level: " + str(self.levelNum), 4) # draw text for level number
        self.distanceText = drawText("Distance: " + str(0), 5)
        self.powerUpText = drawText("Time left for power up: " + str(0), 6)

        self.displayHomeScreen = True
            
        taskMgr.add(self.gameLoop, "moveTask")
        
    # Records the state of the arrow keys
    def setKey(self, key, value):
        self.keyMap[key] = value
        
    def removeHomeScreen(self):
        self.displayHomeScreen = False
        self.playButton.destroy()
        taskMgr.add(self.gameLoop, "moveTask")
        
        if self.gameOver == True:
            app.destroy()
            MyApp(True)

    def updateHighScore(self):
        # update high score
        newLine = ""
        for line in self.inventory:
            if "High Score" in line:
                newLine = "High Score:" + str(self.highScore) + "\n"

        self.inventory[0] = newLine
        self.inventoryFile.truncate(0)
        
        for line in self.inventory:
            self.inventoryFile.write(line)


    def updateCoin(self):
        # update total coins
        self.inventoryFile = open("RocketInventory.txt","r+")
        
        for line in self.inventory:
            if "Coins" in line:
                newLine = "Coins:" + str(self.totalCoins) + "\n"

        self.inventory[1] = newLine
        self.inventoryFile.truncate(0)
        
        for line in self.inventory:
            self.inventoryFile.write(line)

        self.inventoryFile.close()
        
    def gameLoop(self, task):
        if self.numLives <= 0:
            self.gameOver = True
            self.displayHomeScreen = True
            self.gameOverText = OnscreenText(text="Game Over!",
                                           parent=base.a2dTopLeft,
                                            pos=(1, -1),
                                            fg=(1, 1, 1, 1), align=TextNode.ALeft,
                                            shadow=(0, 0, 0, 0.5), scale=.1)
            if self.rocket.getY() > float(self.highScore):
                self.highScore = self.rocket.getY()
                self.updateHighScore()

            self.updateCoin()
            
            return 0

        elif self.displayHomeScreen:
            self.playButton = OnscreenText(text="Press 'p' to Play!",
                                           parent=base.a2dTopLeft,
                                            pos=(1, -1),
                                            fg=(1, 1, 1, 1), align=TextNode.ALeft,
                                            shadow=(0, 0, 0, 0.5), scale=.1)

        else:
            dt = globalClock.getDt()

            #replace distance text to show new distance
            self.distanceText.destroy()
            
            
            self.distanceText = drawText("Distance: " +
                                    str(self.rocket.getY()), 5)

            # Event handling
            self.keyHandling()

            self.moveBullets()
 
            time = round(task.time)
            if time % 2 == 0 and time != self.timeInitial1:         
                for i in range(self.levelNum*2):
                    self.createEnemies()
                    
                self.enemySpeed = self.levelNum / 100 * 4
                    
                self.createObstacle()
                self.createObstacle()

                self.createCoin()
                
                if not self.isSpeeding:
                    self.createSpeedBoost()
                if not self.isAI:
                    self.createAI()
                if not self.isMagnetic:
                    self.createCoinMagnet()
                self.timeInitial1 = time

            # move rocket
            rx = self.rocket.getX()
            ry = self.rocket.getY()
            rz = self.rocket.getZ()

            if self.isSpeeding and not self.isAI: # if rocket is speeding               
                self.powerUpText.destroy()
                self.powerUpText = drawText("Time left for power up: " +
                                    str(self.endSpeedingTime - time), 6)
                self.rocket.setPos(rx, ry + 4*self.rocketSpeed, rz)
                if time == self.endSpeedingTime:
                    self.isSpeeding = False
                    
                
            elif self.isAI and not self.isMagnetic and not self.isSpeeding:
                self.powerUpText.destroy()
                self.powerUpText = drawText("Time left for power up: " +
                                    str(self.endAITime - time), 6)
                self.rocket.setPos(rx, ry + self.rocketSpeed, rz)

                for y in range(int(round(ry)), int(round(ry + 50))):
                    for e in self.enemies:
                        ex = e.getX()
                        ey = e.getY()
                        ez = e.getZ()
                        if abs(rx-ex) < 3 and abs(y-ey)<3 and abs(rz-ez) < 3:
                            # shoot bullet at enemy
                            self.fire(self.rocket)
                            # remove enemy from screen and list
                            self.checkBECollision()

                # Check if there's an obstacle within 75 units ahead
                for y in range(int(round(ry)), int(round(ry + 75))):
                    for o in self.obstacles:
                        ox = o.getX()
                        oy = o.getY()
                        oz = o.getZ()

                        if abs(rx-ox) < 3 and abs(y-oy) < 3 and abs(rz-oz) < 3:
                            #print("obstacle coming.")
                            leftCount, rightCount, lowerCount, upperCount = self.getCount(self.obstacles)

                            if leftCount <= rightCount:
                                if self.rocket.getX() - 0.01 > -3.5:
                                    self.rocket.setX(self.rocket.getX() - 0.01)
                                else:
                                    if lowerCount <= upperCount:
                                        if self.rocket.getZ() - 0.01 > -3.5:
                                            self.rocket.setZ(self.rocket.getZ() - 0.01)
                                        else:
                                            self.rocket.setZ(self.rocket.getZ() - 0.01)
                                            
                                    elif upperCount > lowerCount:
                                        if self.rocket.getZ() + 0.01 < 3.5:
                                            self.rocket.setZ(self.rocket.getZ() + 0.01)
                                        else:
                                            self.rocket.setZ(self.rocket.getZ() - 0.01)
                                        
                                    
                            elif leftCount > rightCount:
                                if self.rocket.getX() + 0.01 < 3.5:
                                    self.rocket.setX(self.rocket.getX() + 0.01)
                                else:
                                    if lowerCount <= upperCount:
                                        if self.rocket.getZ() - 0.01 > -3.5:
                                            self.rocket.setZ(self.rocket.getZ() - 0.01)
                                        else:
                                            self.rocket.setZ(self.rocket.getZ() + 0.01)
                                            
                                    elif upperCount > lowerCount:
                                        if self.rocket.getZ() + 0.01 < 3.5:
                                            self.rocket.setZ(self.rocket.getZ() + 0.01)
                                        else:
                                            self.rocket.setZ(self.rocket.getZ() - 0.01)

                        
                if time == self.endAITime:
                    self.isAI = False

            elif self.isMagnetic and not self.isAI and not self.isSpeeding:
                self.powerUpText.destroy()
                self.powerUpText = drawText("Time left for power up: " +
                                    str(self.endMagneticTime - time), 6)
                for c in self.coins:
                    self.rocket.setPos(rx, ry + self.rocketSpeed, rz)

                    x = c.getX()
                    y = c.getY()
                    z = c.getZ()
                    
                    if y - ry <= 50:
                        if rx < x:
                            newX = x - 0.5
                        else:
                            newX = x + 0.5
                        if rz < z:
                            newZ = z - 0.5
                        else:
                            newZ = z + 0.5
                    else:
                        newX = x
                        newZ = z

                    newY = y - 0.5
                    
                    c.setPos(newX, newY, newZ)
                    
                if time == self.endMagneticTime:
                    self.isMagnetic = False
                
            else:
                self.rocket.setPos(rx, ry + self.rocketSpeed, rz)

            # move camera
            self.camera.setPos(0, self.rocket.getY() - 15, 1)

            # move enemies
            self.moveEnemies()

            # create stars
            self.createStars()

            # remove items once they are off-screen
            self.removeOffScreen(self.stars)
            self.removeOffScreen(self.coins)
            self.removeOffScreen(self.enemies)
            self.removeOffScreen(self.speedBoosts)
            self.removeOffScreen(self.AIList)
            self.removeOffScreen(self.coinMagnets)
            self.removeOffScreen(self.obstacles)

            # remove bullets once they are off-screen
            for b in self.bullets:
                if b.getY() >= self.rocket.getY() + 300:
                    self.bullets.remove(b)
                    b.removeNode()
     
            self.keyMap["fire"] = False

            self.checkBECollision() # check if bullet hits enemy
            self.checkRECollision() # check if rocket hits enemy
            self.checkROCollision() # check if rocket hits obstacle
            self.checkRCCollision() # check if rocket hits coin

            self.endSpeedingTime = self.checkRSCollision(task) # rocket hits speed boost
            self.endAITime = self.checkRAICollision(task) # rocket hits AI power up
            self.endMagneticTime = self.checkRCMCollision(task) # rocket hits coin magnet power up
           
            self.drawLives()

            # change level number if rocket y pos reaches certain value
            ry = self.rocket.getY()
            if round(ry) % 1000 == 0 and round(ry) != self.yInitial:
                #increase level by 1 every 1000 units
                self.levelText.destroy()                
                #print("Level:",self.levelNum)
                self.levelNum += 1
                self.levelText = drawText("Level: " + str(self.levelNum), 4)
                self.yInitial = round(ry)

            if self.hasRocketBuddy:
                self.moveBuddy()

            return task.cont

    def moveBuddy(self):
        ## The buddy rocket is not harmed by obstacles.
        ## It targets enemies and shoots them. It also teleports
        ## back to where the rocket is when it goes off-screen.
        bx = self.buddy.getX()
        by = self.buddy.getY()
        bz = self.buddy.getZ()
        
        if self.isSpeeding:
            self.buddy.setPos(bx, by + 4*self.rocketSpeed, bz)
        else:
            self.buddy.setPos(bx, by + self.rocketSpeed, bz)

        for y in range(int(round(by)), int(round(by + 50))): # fire bullet if enemy ahead
            for e in self.enemies:
                ex = e.getX()
                ey = e.getY()
                ez = e.getZ()
                if abs(bx-ex) < 2 and abs(y-ey) < 2 and abs(bz-ez) < 2:
                    # shoot bullet at enemy
                    self.fire(self.buddy)
                    # remove enemy from screen and list
                    self.checkBECollision()
                    
        # Check if there's an obstacle within 50 units ahead
        bx = self.buddy.getX()
        by = self.buddy.getY()
        bz = self.buddy.getZ()
        
        for y in range(int(round(by)), int(round(by + 50))):
            for e in self.enemies:
                ex = e.getX()
                ey = e.getY()
                ez = e.getZ()

                if abs(bx-ex) < 3 and abs(y-ey) < 3 and abs(bz-ez) < 3:
                    leftCount, rightCount, upperCount, lowerCount = self.getCount(self.enemies)
                    
                    buddySpeed = 0.01
                    if leftCount >= rightCount:
                        if self.buddy.getX() - buddySpeed > -3:
                            self.buddy.setX(self.buddy.getX() - buddySpeed)
                        else:
                            if lowerCount >= upperCount:
                                if self.buddy.getZ() - buddySpeed > -3:
                                    self.buddy.setZ(self.buddy.getZ() - buddySpeed)
                                else:
                                    self.buddy.setX(self.rocket.getX())
                                    self.buddy.setZ(self.rocket.getZ())

                            elif upperCount < lowerCount:
                                if self.buddy.getZ() + buddySpeed < 3:
                                    self.buddy.setZ(self.buddy.getZ() + buddySpeed)
                                else:
                                    self.buddy.setX(self.rocket.getX())
                                    self.buddy.setZ(self.rocket.getZ())
                                                    
                    elif leftCount < rightCount:
                        if self.buddy.getX() + buddySpeed < 3:
                            self.buddy.setX(self.buddy.getX() + buddySpeed)
                        else:
                            if lowerCount >= upperCount:
                                if self.buddy.getZ() - buddySpeed > -3:
                                    self.buddy.setZ(self.buddy.getZ() - buddySpeed)
                                else:
                                    self.buddy.setX(self.rocket.getX())
                                    self.buddy.setZ(self.rocket.getZ())
                                    
                            elif upperCount < lowerCount:
                                if self.buddy.getZ() + buddySpeed < 3:
                                    self.buddy.setZ(self.buddy.getZ() + buddySpeed)
                                else:
                                    self.buddy.setX(self.rocket.getX())
                                    self.buddy.setZ(self.rocket.getZ())

    def removeOffScreen(self, items):
        for x in items:
            if x.getY() <= 0:
                items.remove(x)
                x.removeNode()
       
    def getCount(self, items):
        leftCount, rightCount, lowerCount, upperCount = 0, 0, 0, 0
        
        for i in items:
            x = i.getX()
            z = i.getZ()
            if x < 0:
                leftCount += 1
            else:
                rightCount += 1

            if z < 0: 
                lowerCount += 1
            else:
                upperCount += 1

        return leftCount, rightCount, upperCount, lowerCount
        
    def keyHandling(self):
        # rocket reacts to arrow keys and shoots bullet if spacebar is hit
        if self.keyMap["left"]:
                self.rocket.setX(self.rocket.getX() - 0.25)
                self.keyMap["left"] = not self.keyMap["left"]
                
        elif self.keyMap["right"]:
            self.rocket.setX(self.rocket.getX() + 0.25)
            self.keyMap["right"] = not self.keyMap["right"]

        elif self.keyMap["up"]:
            self.rocket.setZ(self.rocket.getZ() + 0.25)
            self.keyMap["up"] = not self.keyMap["up"]

        elif self.keyMap["down"]:
            self.rocket.setZ(self.rocket.getZ() - 0.25)
            self.keyMap["down"] = not self.keyMap["down"]
            
        elif self.keyMap["fire"]:
            self.fire(self.rocket)

    def getLifeObjects(self):
        for count in range(self.numLives):
            self.life = loader.loadModel("models/life.blend.x")
            self.life.setScale(0.5)
            self.life.reparentTo(render)
            self.lives.append(self.life)

            listX = [-12, -10, -8]
            y = self.rocket.getY() + 25
            z = -8

            self.life.setPos(listX[count], y, z)
                                          
    def drawLives(self):
        for l in self.lives:
            x = l.getX()
            y = l.getY()
            z = l.getZ()
            if self.isSpeeding:
                l.setPos(x, y + 4*self.rocketSpeed , z)
            else:
                l.setPos(x, y + self.rocketSpeed , z)                
               
    def createStars(self):
        self.star = loader.loadModel("models/star3.blend.x")
        self.star.setScale(0.05)
        self.star.reparentTo(render)
        self.stars.append(self.star)

        x = random.randint(-20, 20)
        z = random.randint(-20, 20)

        self.star.setPos(x, self.rocket.getY() + 150, z)

    def createSpeedBoost(self):
        self.speedBoost = loader.loadModel("models/speedBoost1.blend.x")
        self.speedBoost.setScale(0.5)
        self.speedBoost.reparentTo(render)
        self.speedBoosts.append(self.speedBoost)
        
        x = random.randint(-7, 7)
        z = random.randint(-7, 7)

        self.speedBoost.setPos(x, self.rocket.getY() + 150, z)

    def createAI(self):
        self.AI = loader.loadModel("models/AI.blend.x")
        self.AI.setScale(0.5)
        self.AI.reparentTo(render)
        self.AIList.append(self.AI)

        x = random.randint(-7, 7)
        z = random.randint(-7, 7)

        self.AI.setPos(x, self.rocket.getY() + 150, z)

    def createCoinMagnet(self):
        self.coinMagnet = loader.loadModel("models/CoinMagnet1.blend.x")
        self.coinMagnet.reparentTo(render)
        self.coinMagnets.append(self.coinMagnet)

        x = random.randint(-7, 7)
        z = random.randint(-7, 7)

        self.coinMagnet.setPos(x, self.rocket.getY() + 150, z)
    
    def createCoin(self):
        self.coin = loader.loadModel("models/coin.blend.x")
        self.coin.reparentTo(render)
        self.coins.append(self.coin)

        x = random.randint(-7, 7)
        z = random.randint(-7, 7)

        self.coin.setPos(x, self.rocket.getY() + 150, z)

    def createObstacle(self):
        self.obstacle = loader.loadModel("models/obstacle.blend.x")
        self.obstacle.reparentTo(render)
        self.obstacles.append(self.obstacle)

        x = random.randint(-7, 7)
        z = random.randint(-7, 7)

        self.obstacle.setPos(x, self.rocket.getY() + 150, z)

    def fire(self, rocket): 
        xPos = rocket.getX()
        yPos = rocket.getY() + 5
        zPos = rocket.getZ()
        self.bullet = loader.loadModel("models/bullet.blend.x")
        self.bullets.append(self.bullet)
        self.bullet.setScale(0.7)
        self.bullet.reparentTo(render)
        self.bullet.setPos(xPos, yPos, zPos)

    def moveBullets(self):
        for b in self.bullets:
            y = b.getY()
            x = b.getX()
            z = b.getZ()
            b.setPos(x, y + 5, z)

    def checkBECollision(self):
        for b in self.bullets:
            x = b.getX()
            y = b.getY()
            z = b.getZ()
            for e in self.enemies:
                ex = e.getX()
                ey = e.getY()
                ez = e.getZ()
                if abs(x-ex) < 3 and abs(y-ey)<3 and abs(z-ez) < 3:
                    e.removeNode()
                    self.enemies.remove(e)

    def checkRECollision(self):
        x = self.rocket.getX()
        y = self.rocket.getY()
        z = self.rocket.getZ()
        for e in self.enemies:
            ex = e.getX()
            ey = e.getY()
            ez = e.getZ()
            if abs(x-ex) < 2 and abs(y-ey) < 2 and abs(z-ez) < 2:
                e.removeNode()
                self.enemies.remove(e)
                if self.numLives != 0 and not self.isSpeeding and not self.isAI:
                    self.numLives -= 1
                    self.lives.pop()
                else:
                    gameOver = True

    def checkROCollision(self):
        x = self.rocket.getX()
        y = self.rocket.getY()
        z = self.rocket.getZ()
        for o in self.obstacles:
            ox = o.getX()
            oy = o.getY()
            oz = o.getZ()
            if abs(x-ox) < 2 and abs(y-oy) < 2 and abs(z-oz) < 2:
                o.removeNode()
                self.obstacles.remove(o)
                if self.numLives != 0 and not self.isSpeeding and not self.isAI:
                    self.numLives -= 1
                    self.lives.pop()
                else:
                    gameOver = True

    def checkRCCollision(self): # check if rocket hits coins
        x = self.rocket.getX()
        y = self.rocket.getY()
        z = self.rocket.getZ()
        for c in self.coins:
            cx = c.getX()
            cy = c.getY()
            cz = c.getZ()
            if abs(x-cx) < 2 and abs(y-cy) < 2 and abs(z-cz) < 2:
                c.removeNode()
                self.coins.remove(c)
                self.totalCoins += 1
                self.coinsText.destroy()
                self.coinsText = drawText("Coins:" + str(self.totalCoins), 3)

    def checkRSCollision(self, task): # check if rocket hits speed boost
        x = self.rocket.getX()
        y = self.rocket.getY()
        z = self.rocket.getZ()
        for sb in self.speedBoosts:
            sbx = sb.getX()
            sby = sb.getY()
            sbz = sb.getZ()
            if abs(x-sbx) < 2 and abs(y-sby)< 2 and abs(z-sbz) < 2:
                sb.removeNode()
                self.speedBoosts.remove(sb)
                if not self.isAI and not self.isMagnetic:
                    self.isSpeeding = True
                    self.endSpeedingTime = round(task.time) + 5
                
        return self.endSpeedingTime


    def checkRAICollision(self, task): # check if rocket hits AI power up
        x = self.rocket.getX()
        y = self.rocket.getY()
        z = self.rocket.getZ()
        for a in self.AIList:
            ax = a.getX()
            ay = a.getY()
            az = a.getZ()
            if abs(x-ax) < 2 and abs(y-ay) < 2 and abs(z-az) < 2:
                a.removeNode()
                self.AIList.remove(a)
                if not self.isSpeeding and not self.isMagnetic:
                    self.isAI = True
                    self.endAITime = round(task.time) + 7

        return self.endAITime

    def checkRCMCollision(self, task): # check if rocket hits coin magnet
        x = self.rocket.getX()
        y = self.rocket.getY()
        z = self.rocket.getZ()
        for c in self.coinMagnets:
            cx = c.getX()
            cy = c.getY()
            cz = c.getZ()
            if abs(x-cx) < 2 and abs(y-cy) < 2 and abs(z-cz) < 2: 
                c.removeNode()
                self.coinMagnets.remove(c)
                if not self.isSpeeding and not self.isAI:
                    self.isMagnetic = True
                    self.endMagneticTime = round(task.time) + 10

        return self.endMagneticTime
                
    def createEnemies(self):
        self.enemy = loader.loadModel("models/enemy10.blend.x")
        self.enemies.append(self.enemy)
        self.enemy.setScale(0.8)
        self.enemy.reparentTo(render)
        x = random.randint(-7, 7)
        z = random.randint(-7, 7)
        self.enemy.setPos(x, self.rocket.getY() + 150, z)
                                
    def moveEnemies(self):
        # after y position of enemy reaches less than 75, it
        # moves towards rocket
        for e in self.enemies:
            rx = self.rocket.getX()
            ry = self.rocket.getY()
            rz = self.rocket.getZ()
               
            y = e.getY()    
            x = e.getX()
            z = e.getZ()

            if y - ry <= 75 and y - ry >= 10:
                if rx < x:
                    newX = x - self.enemySpeed
                else:
                    newX = x + self.enemySpeed
                if rz < z:
                    newZ = z - self.enemySpeed
                else:
                    newZ = z + self.enemySpeed
            else:
                newX = x
                newZ = z

            newY = y - 0.5
            
            e.setPos(newX, newY, newZ)

    def spinCameraTask(self, task):
        angleDegrees = task.time * 6.0
        angleRadians = angleDegrees * (pi / 180.0)
        self.camera.setPos(20 * sin(angleRadians), -20.0 * cos(angleRadians), 3)
        self.camera.setHpr(angleDegrees, 0, 0)
        return Task.cont

app = MyApp()
app.run()
    









