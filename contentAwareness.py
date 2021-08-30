from sys import argv
from PIL import Image
from IPython.display import display
import numpy as np

def main():
    fileName = None

    fileName = argv[1]
    print("Attempting to open file: " + fileName)

    mainImage = Image.open(fileName)
    mainP = mainImage.load()
    width = mainImage.size[0]
    height = mainImage.size[1]

    # calculate vertical and horizontal energy
    energyV = np.zeros((width,height-1))
    verticalImage = Image.new('RGB', (width, height-1))
    verticalP = verticalImage.load()
    for i in range(width):    
        for j in range(height-1):  
            thisP = mainP[i,j]
            thatP = mainP[i,j+1]
            thisBright = thisP[0] + thisP[1] + thisP[2]
            thatBright = thatP[0] + thatP[1] + thatP[2]
            energyV[i,j] = thatBright - thisBright
            endBright = (int)((thatBright - thisBright)/765*127+127)
            verticalP[i,j] = (endBright, endBright, endBright)

    energyH = np.zeros((width-1,height))
    horizontalImage = Image.new('RGB', (width-1, height))
    horizontalP = horizontalImage.load()
    for i in range(width-1):    
        for j in range(height):  
            thisP = mainP[i,j]
            thatP = mainP[i+1,j]
            thisBright = thisP[0] + thisP[1] + thisP[2]
            thatBright = thatP[0] + thatP[1] + thatP[2]
            energyH[i,j] = thatBright - thisBright
            endBright = (int)((thatBright - thisBright)/765*127+127)
            horizontalP[i,j] = (endBright, endBright, endBright)

    # average the vertical and horizontal energy into one energy 
    energyArray = np.zeros((width-1,height-1))
    energyImage = Image.new('RGB', (width-1, height-1))
    energyP = energyImage.load()
    for i in range(width-1):    
        for j in range(height-1):  
            totalEnergy = horizontalP[i,j][0] + verticalP[i,j][0]
            averageE = (int)(totalEnergy/2)
            energyArray[i,j] = energyH[i,j] + energyV[i,j]
            energyP[i,j] = (averageE,averageE,averageE)

    # set all values in the energy array to absolute, we only care about magnitude
    for subArray in energyArray:
        for i in range(len(subArray)):
            subArray[i] = abs(subArray[i])

    # show images for debug/fun
    verticalImage.save("v" + fileName)
    horizontalImage.save("h" + fileName)
    energyImage.save("e" + fileName)

    # array for traversing through the image to find the minimum energy seam
    # currently only finds vertical seams
    minArray = np.zeros((width-1,height-1))
    for y in range(height-1):
        for x in range(width-1):
            m = energyArray[x][y]
            if y != 0:
                smallestUp = minArray[x][y-1]
                if x > 0 and minArray[x-1][y-1] < smallestUp:
                    smallestUp = minArray[x-1][y-1]
                if x < width-2 and minArray[x+1][y-1] < smallestUp:
                    smallestUp = minArray[x+1][y-1]
                m += smallestUp
            minArray[x][y] = m        
    
    minPath = np.zeros((height-1))
    minLoc = 0
    m = minArray[0][height-2]
    for x in range(1,width-1):
        if minArray[x][height-2] < m:
            minLoc = x
            m = minArray[x][height-2]
    minPath[height-2] = minLoc

    for y in range(height-2, -1, -1):
        minAnchor = minLoc
        m = minArray[minAnchor][y]
        if minAnchor > 0 and minArray[minAnchor-1][y] < m:
            minLoc = minAnchor - 1
            m = minArray[minAnchor-1][y]
        if minAnchor < width-2 and minArray[minAnchor+1][y] < m:
            minLoc = minAnchor + 1
            m = minArray[minAnchor+1][y]
        minPath[y] = minLoc

    # add red seam to energy image for fun and display
    for y in range(height-1):
        energyP[minPath[y],y] = (255,0,0)

    energyImage.save("es" + fileName)

    # construct new image with seam removed
    newImage = Image.new('RGB', (width-1, height))
    newP = newImage.load()
    removedX = 0
    for y in range(height):
        removeOffset = 0
        if y != height-1:
            removedX = minPath[y]
        for x in range(width-1):
            if x == removedX:
                removed = 1
            newP[x,y] = mainP[x+removeOffset,y]

    newImage.save("out" + fileName)


    pass

if __name__ == "__main__":
    main()