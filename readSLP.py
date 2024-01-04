import math
import pandas as pd
import slippi as slp
import os
from time import sleep 

game = slp.Game("slpFiles\\2023-12\\Game_20231230T142737.slp")
# print(game.start.random_seed)
# ports = [game.start.players.index(port) if port != None else
#                   None for port in game.start.players]
# opened = slp()
# opened.event.Start(False, (0, 1),  game.start.random_seed, game, game.start.stage)
# print(game.frames[60].ports[0])

NUM_LOGICAL = 22
NUM_PHY = 12

"""
ONLY USE FOR TRAINING
WHEN ACTUALLY PLAYING AGAINST THIS BOT ANOTHER AI WILL NEED TO BE USED

"""

FLAGMAP ={
        16: 1, 
        1024: 2,
        2048: 3, 
        8192: 4,
        8388608: 5,
        33554432: 6,
        67108864: 7,
        536870912: 8,
        34359738368: 9,
        68719476736: 10,
        274877906944: 11,
        549755813888: 12
        }

class slippiReader():
    """
    Creates input array[
    
    ]
    """
    def __init__(self, game: slp.Game, pPort: int, ePort: int) -> None:

        self.game = game #gamedata
        self.pPort = pPort #player port 
        self.ePort = ePort #enemy port
        self.frame = 0
        self.stage = 0
        self.chars = [0, 0, 0, 0 ]
        self.frameMax = game.metadata.duration

    def translateLogical(self, logic):
        """
        NO LONGER IN USE, USE TRANSLATE PHYSICAL AND GET STICK INPUTS FROM FRAMEDATA
        Translates binary string to a zero padded list of bits
        Each bit represents an input
        See https://py-slippi.readthedocs.io/en/latest/source/slippi.html#slippi.event.Buttons
        for details
        """

        bits = "{0:b}".format(logic)
        inputs = [0] * (31 - len(bits))  + [int(val) for val in list(bits)]
        # REMOVE BITS THAT ARE ALWAYS 0
        del inputs[1:7]
        del inputs[-8]
        return inputs 
    
    def getPhysical(self, buttons):
        """
        Translates input ENUMS to list of pressed values"
        see https://py-slippi.readthedocs.io/en/latest/source/slippi.html#slippi.event.Buttons
        for enums
        """
        pressed = buttons.pressed()

        inputs = [0] * 9
        for input in pressed:
            idx = NUM_PHY - int(math.log2(int(input)))  

            inputs[idx] = 1
        return inputs
    
    def getStick(self, data):
        return [data.joystick.x,data.joystick.y, data.cstick.x, data.cstick.y]

    def getTrigger(self, data):
        return [data.logical]
    
    
    def getDamage(self, data):
        return [data.damage, data.stocks, data.hit_stun]
    
    def getPosition(self, data):
        return [
            int(data.airborne),
            int(data.direction),
            data.ground if data.ground != None else 0,
            data.position.x,
            data.position.y,
            data.jumps
        ]
    def getState(self, data):
        return [FLAGMAP[data.flags], data.state, data.state_age]

    def getChar(self, data):
        return int(data.character)

    def getPlayer(self, num):
        playerData = [self.chars[num]]
        currFrame = self.game.frames[self.frame].ports[num]

        playerData.extend( 
        self.getPhysical(currFrame.leader.pre.buttons.physical) + 
        self.getStick(currFrame.leader.pre) + 
        self.getTrigger(currFrame.leader.pre.triggers) +
        self.getDamage(currFrame.leader.post) + 
        self.getPosition(currFrame.leader.post)
        )
        return playerData
    

    def initStage(self):
        self.stage = int(self.game.start.stage)

    def setChars(self):
        initFrame = self.game.frames[0].ports[self.pPort]
        self.chars[self.pPort]  = self.getChar(initFrame.leader.post)

        initFrame = self.game.frames[0].ports[self.ePort]
        self.chars[self.ePort]  = self.getChar(initFrame.leader.post)


    def getData(self):
        data = []

        player = self.getPlayer(self.pPort )
        enemy = self.getPlayer(self.ePort)
        data.extend([self.stage] + player + enemy)
        print(data)
        # format(player, enemy)
    
    def incrimentFrame(self):
        self.frame += 1


reader = slippiReader(game, 2,3)
reader.initStage()
reader.setChars()
for i in range(reader.frameMax):
    reader.getData()
    reader.incrimentFrame()