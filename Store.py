

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
from math import pi, sin, cos
import random


class MyApp(ShowBase):
    def __init__(self):

        ShowBase.__init__(self)

        self.setBackgroundColor((0, 0, 0, 1))

        OnscreenText(text="ROCKET BUDDY",parent=base.a2dTopLeft,
                               pos=(1, -0.15),fg=(1, 1, 1, 1),
                               align=TextNode.ALeft,
                               shadow=(0, 0, 0, 0.5), scale=.15)

        buddyText1 = "The Rocket Buddy can accompany"
        buddyText2 = "you on your mission and help you"
        buddyText3 = "shoot enemies!" 

        buddyDescription = [buddyText1, buddyText2, buddyText3]
        z = -0.5
        for bt in buddyDescription:
            OnscreenText(text=bt,parent=base.a2dTopLeft,
                                   pos=(1, z),fg=(1, 1, 1, 1),
                                   align=TextNode.ALeft,
                                   shadow=(0, 0, 0, 0.5), scale=.1)
            z -= 0.1


        i1 = "To purchase the Rocket Buddy,"
        i2 = "press 'a' and look at the command"
        i3 = "prompt for further instructions!"
        instructions = [i1, i2, i3]
        
        for i in instructions:
            OnscreenText(text=i,parent=base.a2dTopLeft,
                                   pos=(1, z),fg=(1, 1, 1, 1),
                                   align=TextNode.ALeft,
                                   shadow=(0, 0, 0, 0.5), scale=.1)
            z -= 0.1
        
        # Disable the camera trackball controls
        self.disableMouse()
        #taskMgr.add(self.spinCameraTask, "rotateCamera")
        
        # Create some lighting
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

        self.buddy = loader.loadModel("models/miniRocket1.blend.x")
        self.buddy.setScale(0.7)
        self.buddy.reparentTo(render)
        self.buddy.setPos(-2.25, 10, 1.25)

        # read inventory file
        self.totalCoins = 0
        self.hasRocketBuddy = False
        self.hasCoinGun = False
        self.hasObstacleGun = False
        self.readingFeatures = False
        self.readingStore = False
        
        self.inventoryFile = open("RocketInventory.txt","r+")
        self.inventory = self.inventoryFile.readlines()

        for line in self.inventory:
            if ":" in line:
                i = line.index(":")
                s = line[:i]
                
            if s == "Coins":
                self.totalCoins = line[i+1:]
                
            elif s == "Features" :
                self.readingFeatures = True

            elif s == "Store":
                self.readingStore = True

            if self.readingFeatures:
                if s == "Rocket buddy":
                    if "No" in line[i:]:
                        self.hasRocketBuddy = False
                    else:
                        self.hasRocketBuddy = True
                        
            if self.readingStore:
                self.readingFeatures = False
                if s == "Rocket buddy":
                    self.priceBuddy = line[i+1:]

        if self.hasRocketBuddy:
            self.printRocketText("Bought? Yes")
        else:
            self.printRocketText("Bought? No")

        self.priceBuddy = int(self.priceBuddy)
        self.totalCoins = int(self.totalCoins)
        
        self.accept("a", self.rocketHandler)

    def printRocketText(self, text):
        self.rocketText = OnscreenText(text=text,
                                           parent=base.a2dTopLeft,
                                            pos=(0.3, -1),fg=(1, 1, 1, 1),
                                           align=TextNode.ALeft,
                                            shadow=(0, 0, 0, 0.5), scale=.1)
        if text == "Bought? No":
            self.rocketText1 = OnscreenText(text="Price: " + str(self.priceBuddy),
                                           parent=base.a2dTopLeft,
                                            pos=(0.3, -1.1),fg=(1, 1, 1, 1),
                                           align=TextNode.ALeft,
                                            shadow=(0, 0, 0, 0.5), scale=.1)
    
    def rocketHandler(self):
        if not self.hasRocketBuddy:
            userInput = input("Would you like to purchase? (y/n)")
            if userInput == "y":
                print("Coins:",str(self.totalCoins))               
                if self.totalCoins >= self.priceBuddy:
                    self.hasRocketBuddy = True
                    self.totalCoins -= self.priceBuddy
                    print("Rocket buddy has been purchased!")
                    print("Coins left:", self.totalCoins)
                    print("Have fun!")
                    self.rocketText.destroy()
                    self.printRocketText("Bought? Yes")
                    
                    # update text file
                    self.updateFile()

                else:
                    print("Sorry, you don't have enough coins to purchase this item!")
            else:
                print("Ok!")
        else:
            print("You have this item! Have fun! :)")

    def updateFile(self):
        index = self.inventory.index("Rocket buddy:No\n")
        self.inventory[index] = "Rocket buddy:Yes\n"
        self.inventoryFile.truncate(0)
        for line in self.inventory:
            self.inventoryFile.write(line)

        self.inventoryFile.close()
        
    def spinCameraTask(self, task):
        angleDegrees = task.time * 6
        angleRadians = angleDegrees * (pi / 180.0)
        self.camera.setPos(1 * sin(angleRadians), -1 * cos(angleRadians), 3)
        self.camera.setHpr(angleDegrees, 0, 0)
        return Task.cont
                   

app = MyApp()
app.run()




