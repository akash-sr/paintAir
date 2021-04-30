# import libraries
import cv2
import numpy as np
import time
import os
import handTrackingModule as htm

# set path for menu bar frames
menuPath= "menu-bar"

# get file names of menu bar frames in a list
frameList = os.listdir(menuPath)
# declare an empty frames array to store the frames
frames = []

# populate the frames list
for imPath in frameList:
    image = cv2.imread(f'{menuPath}/{imPath}')
    frames.append(image)
# # check if all the frames have been added
# print(len(frames))
# set the initial frame
menubar = frames[3]

# start web-cam and set video stream dimensions
cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

detector = htm.handDetector(detectionCon=0.85)

# set brush size
brushThickness = 15
# set eraser size
eraserThickness = 50

# set drawing start points
xp, yp = 0, 0

# set color codes
red = (28, 22, 225)
blue = (244, 166, 31)
green = (40, 219, 94)
black = (0, 0, 0)
# set initial color
drawColor = black

# initialize canvas
canvas = np.zeros((720, 1280, 3), np.uint8)

while True:
    # import web-cam feed
    success, img = cap.read()
    # flip the image as the web-cam mirrors the feed
    img = cv2.flip(img, 1)

    # find hand landmarks
    img = detector.findHands(img)
    # get hand landmarks in a list
    lmList = detector.findPosition(img,draw=False)
    # check if it is working
    if len(lmList) != 0:
        # # print landmark co-ordinates
        # print(lmList)

        # tip of index finger
        xi, yi = lmList[8][1:]  # 8-> index finger, [1:]->last all cols except 1st
        # tip of middle finger
        xm, ym = lmList[12][1:]  # 12->middle finger

        # check which fingers are up
        fingers = detector.fingersUp()

        # if first three fingers are up -> selection mode
        if fingers[1] and fingers[2]:
            cv2.rectangle(img, (xi, yi-25), (xm, ym+25), drawColor, cv2.FILLED )
            print("Selection Mode")
            xp, yp = 0, 0
            if xi > 1100:
                # red color
                if 60 < yi < 175:
                    drawColor = red
                    menubar = frames[0] 
                # blue color
                elif 195 < yi < 300:
                    drawColor = blue
                    menubar = frames[1]
                # green color
                elif 350 < yi < 455:
                    drawColor = green
                    menubar = frames[2]
                # eraser
                elif 500 < yi < 720:
                    drawColor = black
                    menubar = frames[3]

        elif fingers[1] and fingers[2]==False:
            cv2.circle(img, (xi, yi), 15, drawColor, cv2.FILLED)
            print("Drawing Mode")

            # if it's an eraser, change thickness
            if drawColor == black:
                brushSize = eraserThickness
                ink = 0
            else:
                brushSize = brushThickness
                
            # initialize xp and yp for the first drawing frame
            if xp==0 and yp==0:
                xp, yp = xi, yi

            cv2.line(img, (xp, yp), (xi, yi), drawColor, brushSize)
            cv2.line(canvas, (xp, yp), (xi, yi), drawColor, brushSize)
            xp, yp = xi, yi
    # # combine canvas with web-cam feed
    # # convert canvas to gray scale
    imgGray = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)
    # # invert the coloring of the gray scale canvas
    _, imgInv = cv2.threshold(imgGray, 50, 255, cv2.THRESH_BINARY_INV)
    # # convert it back to BGR inorder to make the dimensions right
    imgInv = cv2.cvtColor(imgInv, cv2.COLOR_GRAY2BGR)
    # # Bit wise AND of this with Image.
    # # Basically, all the places where something was drawn becomes black in the web-cam feed
    img = cv2.bitwise_and(img, imgInv)
    # # Bit wise OR of this with the original canvas.
    # # The blacked out regions are re-filled with the corresponding drawing on the canvas
    img = cv2.bitwise_or(img, canvas)

    # setting the menubar frame
    img[0:720, 1130:1280] = menubar

    # display the updated web-cam feed
    cv2.imshow("Image", img)
    # cv2.imshow("Canvas", canvas)

    cv2.waitKey(1)