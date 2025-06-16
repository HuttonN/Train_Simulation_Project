# -*- coding: utf-8 -*-
"""
Created on Tue Jan  2 15:54:30 2024

@author: Admin
"""
# Sets the current position of the train on the screen.
import math
import pygame


def setTrainPosition(self, x, y):
    global xTrain
    global yTrain
    self.xTrain = x
    self.yTrain = y

# Sets the track the train is currently on. Not used in final build.


def setCurrentTrack(self, trackID):
    global currentTrack
    self.currentTrack = trackID

# Sets the track the train is moving to next. Not used in final build.


def setNextTrack(self, trackID):
    global nextTrack
    self.nextTrack = trackID


class Train(pygame.sprite.Sprite):

    global xTrain
    global yTrain
    global currentTrack
    global nextTrack

    # Initialise the train object.
    def __init__(self, screen, x, y, playerControlled=False):
        super(Train, self).__init__()
        self.rect = pygame.rect.Rect((x, y, 100, 50))
        setTrainPosition(self, x, y)

        self.playerControlled = playerControlled

    # Load in the train image.
    def generateTrain(self, x):
        self.image = pygame.image.load(
            "Images/train_"+x+".png").convert_alpha()
        return self.image

    # Spawn the train on the screen at the x and y coordinate.
    def spawnTrain(self, x, y, screen, image, angle):
        self.rotatedImage = pygame.transform.rotate(image, angle)
        self.imageRect = self.rotatedImage.get_rect(center=(x, y))
        screen.blit(self.rotatedImage, self.imageRect)

    # Return the type.

    def getType(self):
        return "Train"

    def getPlayerControlled(self):
        return self.playerControlled

   # Move the train to a new x and y coordinate, set the position, redraw the train and return the new image.
    def moveTrain(self, currentX, currentY, trackType, screen, compass, image, angle, circleCenter, junctionDirection):
        # Checks if the current track is a straight piece.
        if trackType == "LongStraight" or trackType == "Station" or trackType == "ShortStraight" or (trackType == "JunctionRight" and junctionDirection == 0) or (trackType == "JunctionLeft" and junctionDirection == 0):
            # This is used to move the train by 0.3 units diagonally.
            trueDiagonal = math.sqrt(2*(0.15*0.15))
            # This just moves the train along a coordinate by 0.3 units in a straight line.
            if compass == "E":
                # This changes the coordinates by 0.3 units.
                setTrainPosition(self, currentX+0.3, currentY)
                # This changes the rotation to either 90 or 180 degrees in order to make sure the train is always facing the right way.
                self.rotatedImage = pygame.transform.rotate(self.image, 180)
                return self.rotatedImage
            if compass == "N":
                setTrainPosition(self, currentX, currentY-0.3)
                self.rotatedImage = pygame.transform.rotate(self.image, 90)
                return self.rotatedImage
            if compass == "S":
                setTrainPosition(self, currentX, currentY+0.3)
                self.rotatedImage = pygame.transform.rotate(self.image, 90)
                return self.rotatedImage
            if compass == "W":
                setTrainPosition(self, currentX-0.3, currentY)
                self.rotatedImage = pygame.transform.rotate(self.image, 180)
                return self.rotatedImage
            if compass == "NE":
                setTrainPosition(self, currentX+trueDiagonal,
                                 currentY-trueDiagonal)
                self.rotatedImage = pygame.transform.rotate(self.image, 180)
                return self.rotatedImage
            if compass == "NW":
                setTrainPosition(self, currentX-trueDiagonal,
                                 currentY-trueDiagonal)
                self.rotatedImage = pygame.transform.rotate(self.image, 180)
                return self.rotatedImage
            if compass == "SE":
                setTrainPosition(self, currentX+trueDiagonal,
                                 currentY+trueDiagonal)
                self.rotatedImage = pygame.transform.rotate(self.image, 180)
                return self.rotatedImage
            if compass == "SW":
                setTrainPosition(self, currentX-trueDiagonal,
                                 currentY+trueDiagonal)
                self.rotatedImage = pygame.transform.rotate(self.image, 180)
                return self.rotatedImage

        elif trackType == "LongRight" or trackType == "LongLeft" or (trackType == "JunctionRight" and junctionDirection == 1) or (trackType == "JunctionLeft" and junctionDirection == 1):
            # For curved movement, it uses a vector to get the coodinates around a curve.
            # This creates an invisible circle with the same radius as the curve itself.
            self.vectorAngle = pygame.math.Vector2(0, 150)
            self.angle = angle
            # This rotates the train object, usually by 1 or 2 degrees.
            self.vectorAngle.rotate_ip(-self.angle)
            # This moves the vector to the centre of the circle of the track piece.
            self.vectorAngle = self.vectorAngle + circleCenter
            # This brings the image of the train to a new image.
            self.rotatedImage = image
            # The trains position is set to the new coordinates.
            setTrainPosition(self, self.vectorAngle[0], self.vectorAngle[1])
            return self.rotatedImage
        elif trackType == "ShortRight" or trackType == "ShortLeft":
            self.vectorAngle = pygame.math.Vector2(0, 75)
            self.angle = angle
            self.vectorAngle.rotate_ip(-self.angle)
            self.vectorAngle = self.vectorAngle + circleCenter
            self.rotatedImage = image
            setTrainPosition(self, self.vectorAngle[0], self.vectorAngle[1])
            return self.rotatedImage

        else:
            return 0, 0

    def setCurrent(self, ID):
        setCurrentTrack(self, ID)

    def setNext(self, ID):
        setNextTrack(self, ID)

    def getNextTrack(self):
        return self.nextTrack

    def getCurrentTrack(self):
        return self.currentTrack

    def getCurrentPosition(self):
        return self.xTrain, self.yTrain

    def displaceTrain(self, x, y):
        self.xTrain += x
        self.yTrain += y

    def reverseTrain(self, currentX, currentY, trackType, screen, compass, image, angle, circleCenter, junctionDirection):
        # Checks if the current track is a straight piece.
        if trackType == "LongStraight" or trackType == "Station" or trackType == "ShortStraight" or (trackType == "JunctionRight" and junctionDirection == 0) or (trackType == "JunctionLeft" and junctionDirection == 0):
            # This is used to move the train by 0.3 units diagonally.
            trueDiagonal = math.sqrt(2 * (0.15 * 0.15))
            # This just moves the train along a coordinate by 0.3 units in a straight line.
            if compass == "E":
                # Move the train west (reverse of east)
                setTrainPosition(self, currentX - 0.3, currentY)
                self.rotatedImage = pygame.transform.rotate(self.image, 180)
                return self.rotatedImage
            if compass == "N":
                # Move the train south (reverse of north)
                setTrainPosition(self, currentX, currentY + 0.3)
                self.rotatedImage = pygame.transform.rotate(self.image, -90)
                return self.rotatedImage
            if compass == "S":
                # Move the train north (reverse of south)
                setTrainPosition(self, currentX, currentY - 0.3)
                self.rotatedImage = pygame.transform.rotate(self.image, 90)
                return self.rotatedImage
            if compass == "W":
                # Move the train east (reverse of west)
                setTrainPosition(self, currentX + 0.3, currentY)
                self.rotatedImage = pygame.transform.rotate(self.image, 180)
                return self.rotatedImage
            if compass == "NE":
                # Move the train southwest (reverse of northeast)
                setTrainPosition(self, currentX - trueDiagonal,
                                 currentY + trueDiagonal)
                self.rotatedImage = pygame.transform.rotate(self.image, 135)
                return self.rotatedImage
            if compass == "NW":
                # Move the train southeast (reverse of northwest)
                setTrainPosition(self, currentX + trueDiagonal,
                                 currentY + trueDiagonal)
                self.rotatedImage = pygame.transform.rotate(self.image, 45)
                return self.rotatedImage
            if compass == "SE":
                # Move the train northwest (reverse of southeast)
                setTrainPosition(self, currentX - trueDiagonal,
                                 currentY - trueDiagonal)
                self.rotatedImage = pygame.transform.rotate(self.image, 315)
                return self.rotatedImage
            if compass == "SW":
                # Move the train northeast (reverse of southwest)
                setTrainPosition(self, currentX + trueDiagonal,
                                 currentY - trueDiagonal)
                self.rotatedImage = pygame.transform.rotate(self.image, 225)
                return self.rotatedImage

        elif trackType == "LongRight" or trackType == "LongLeft" or (trackType == "JunctionRight" and junctionDirection == 1) or (trackType == "JunctionLeft" and junctionDirection == 1):
            # For curved movement, it uses a vector to get the coordinates around a curve.
            # This creates an invisible circle with the same radius as the curve itself.
            self.vectorAngle = pygame.math.Vector2(0, 150)
            self.angle = angle
            # This rotates the train object, usually by 1 or 2 degrees.
            # Rotate in the opposite direction
            self.vectorAngle.rotate_ip(self.angle)
            # This moves the vector to the center of the circle of the track piece.
            self.vectorAngle = self.vectorAngle + circleCenter
            # This brings the image of the train to a new image.
            self.rotatedImage = image
            # The train's position is set to the new coordinates.
            setTrainPosition(self, self.vectorAngle[0], self.vectorAngle[1])
            return self.rotatedImage
        elif trackType == "ShortRight" or trackType == "ShortLeft":
            self.vectorAngle = pygame.math.Vector2(0, 75)
            self.angle = angle
            # Rotate in the opposite direction
            self.vectorAngle.rotate_ip(self.angle)
            self.vectorAngle = self.vectorAngle + circleCenter
            self.rotatedImage = image
            setTrainPosition(self, self.vectorAngle[0], self.vectorAngle[1])
            return self.rotatedImage
