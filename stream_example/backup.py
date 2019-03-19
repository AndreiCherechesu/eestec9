import cv2, sys
import numpy as np
import time
import socketio
import json
import random
from threading import Thread, Lock
from utils import printTimeDiff, initTimeDiff
from client import startListening, curFrame, frameFragments
import comenzi

def nothing(x):
    pass

class Player:
    def __init__(self, id, color):
        self.id = id
        if (self.id == 1):
            self.direction = "right"
        else:
            self.direction = "left"
        self.center = (0,0)
        self.last_known_center = (0,0)
        self.color = color
        self.fill = 2

    def setContour(self, contour):
        self.contour = contour

    def changeDirection(self):
        if (self.direction == "right"):
            self.direction = "left"
        else:
            self.direction = "right"
    
    def setCenter(self, center):
        self.center = center

    def drawCircle(self, img):
        cv2.circle(img, self.center, 10, self.color, self.fill)

cv2.namedWindow("Trackbars")
 
cv2.createTrackbar("L - H", "Trackbars", 0, 179, nothing)
cv2.createTrackbar("L - S", "Trackbars", 0, 255, nothing)
cv2.createTrackbar("L - V", "Trackbars", 0, 255, nothing)
cv2.createTrackbar("U - H", "Trackbars", 179, 179, nothing)
cv2.createTrackbar("U - S", "Trackbars", 255, 255, nothing)
cv2.createTrackbar("U - V", "Trackbars", 255, 255, nothing)

counter_tp = 0
counter_jmp = 0
counter_checked = 0
start_time = 0
elapsed_time = 0
lock = True

p1 = Player(1, (0, 0, 255))
p2 = Player(2, (255, 0, 0))
resp = comenzi.sendCommand(comenzi.url_status, comenzi.status)
player = resp['player']
if (player == "p1"):
    myplayer = p1
else:
    myplayer = p2

myplayer.fill = -1
isFirsttime = True
mytp = False
recently_tp = False


def detect_subzero(frame_subzero, frame, lower_subzero, upper_subzero, ):
    frame_rgb = cv2.cvtColor(frame_subzero, cv2.COLOR_BGR2RGB)
    
    # # clean image
    frame_blur = cv2.GaussianBlur(frame_rgb, (3,3), 0)

    # # convert to hsv
    frame_hsv = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2HSV)

    mask = cv2.inRange(frame_hsv, lower_subzero, upper_subzero)
 
    frame_hsv = cv2.bitwise_and(frame_hsv, frame_hsv, mask=mask)
    
    # # manipulate colors
    cv2.threshold(frame_hsv, 127, 255, cv2.THRESH_BINARY, frame_hsv)

    res_gray = cv2.cvtColor(frame_hsv, cv2.COLOR_BGR2GRAY)

    ret, gray = cv2.threshold(res_gray, 127, 255, 0)
    
    gray2 = res_gray.copy()
    mask = np.zeros(res_gray.shape, np.uint8)

    kernel = np.ones((3,3),np.uint8)
    dilation = cv2.dilate(res_gray, kernel, iterations=5)
    erodate = cv2.erode(dilation, kernel, iterations=5)

    contours, hier = cv2.findContours(erodate, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    aux_gray = res_gray
    global isFirsttime
    global myplayer
    global p1
    global p2

    rectlist = []
    for cnt in contours:
        if 300<cv2.contourArea(cnt)<5000:
            # cv2.drawContours(aux_gray, color=(255,0,0))
            # cv2.drawContours(frame, color=(255,0,0))
            (x,y,w,h) = cv2.boundingRect(cnt)
            if w > 10 and h > 30:
                cv2.rectangle(aux_gray, (x,y), (x+w,y+h), (255, 0, 0), 2)
                cv2.rectangle(frame, (x,y), (x+w,y+h), (255, 0, 0), 2)
                rectlist.append((x + w/2, y + h/2))
        # (x,y,w,h) = cv2.boundingRect(cnt)
        # if w > 5 and h > 5:
        #     cv2.rectangle(aux_gray, (x,y), (x+w,y+h), (0, 0, 255), 2)
        #     cv2.rectangle(frame, (x,y), (x+w,y+h), (0, 0, 255), 2)

    if isFirsttime == True:
        if len(rectlist) == 1:
            isFirsttime = False
            first = rectlist[0]

            if (myplayer is p1):
                p2.center = first
            else:
                p1.center = first

    cv2.imshow('subzero', aux_gray)
    cv2.waitKey(1)
    cv2.imshow('subzero_dilatat', erodate)
    cv2.waitKey(1)

def detect_scorpion(frame_scorpion, frame, lower_scorpion, upper_scorpion):
    frame_rgb = cv2.cvtColor(frame_scorpion, cv2.COLOR_BGR2RGB)
    
    # # clean image
    frame_blur = cv2.GaussianBlur(frame_rgb, (3,3), 0)

    # # convert to hsv
    frame_hsv = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2HSV)

    mask = cv2.inRange(frame_hsv, lower_scorpion, upper_scorpion)
 
    frame_hsv = cv2.bitwise_and(frame_hsv, frame_hsv, mask=mask)
    
    # # manipulate colors
    cv2.threshold(frame_hsv, 127, 255, cv2.THRESH_BINARY, frame_hsv)

    res_gray = cv2.cvtColor(frame_hsv, cv2.COLOR_BGR2GRAY)

    ret, gray = cv2.threshold(res_gray, 127, 255, 0)
    
    gray2 = res_gray.copy()
    mask = np.zeros(res_gray.shape, np.uint8)

    kernel = np.ones((5,5),np.uint8)
    # closing = cv2.morphologyEx(res_gray, cv2.MORPH_CLOSE, kernel)
    # closing = cv2.morphologyEx(closing, cv2.MORPH_CLOSE, kernel)
    dilation = cv2.dilate(res_gray, kernel, iterations=2)
    erodate = cv2.erode(dilation, kernel, iterations=2)

    contours, hier = cv2.findContours(erodate, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    aux_gray = res_gray
    
    global isFirsttime
    rectlist = []
    last_mean = (0,0,0)
    for cnt in contours:
        if 200<cv2.contourArea(cnt)<5000:
            # cv2.drawContours(aux_gray, [cnt], 0, (255,0,0), 3)
            # cv2.drawContours(frame, [cnt], 0, (255,0,0), -1)
            (x,y,w,h) = cv2.boundingRect(cnt)
            
            if w > 20 and h > 20:
                cv2.rectangle(aux_gray, (x,y), (x+w,y+h), (0, 0, 255), 2)
                cv2.rectangle(frame, (x,y), (x+w,y+h), (0, 0, 255), 2)
                rectlist.append((x + w/2, y + h/2))
               
    if isFirsttime == True:
        if len(rectlist) == 2:
            isFirsttime = False
            first = rectlist[0]
            second = rectlist[1]

            if (first[1] < second[1]):
                p1.center = first
                p1.last_known_center = first
                p2.center = second
                p2.last_known_center = second
            else:
                p1.center = second
                p1.last_known_center = second
                p2. center = first
                p2.last_known_center = first
    
    if len(rectlist) == 2:
        isFirsttime = False
        first = rectlist[0]
        second = rectlist[1]

        if (first[0] < second[0]):
            if (recently_tp == False and abs(p1.center[0] - first[0]) <= 50):
                p1.center = first
                p1.last_known_center = first
                p2.center = second      
                p2.last_known_center = second
        else:
            if (recently_tp == False and (abs(p1.center[0] - first[0]) <= 50)):
                p1.center = second
                p1.last_known_center = second
                p2. center = first
                p2.last_known_center = first

    
    cv2.imshow('scorpion', aux_gray)
    cv2.waitKey(1)
    cv2.imshow('scorpion_dilatat', erodate)
    cv2.waitKey(1)


def detect_jump(frame_scorpion, frame, lower_scorpion, upper_scorpion):
    frame_rgb = cv2.cvtColor(frame_scorpion, cv2.COLOR_BGR2RGB)
    
    # # clean image
    frame_blur = cv2.GaussianBlur(frame_rgb, (3,3), 0)

    # # convert to hsv
    frame_hsv = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2HSV)

    mask = cv2.inRange(frame_hsv, lower_scorpion, upper_scorpion)
 
    frame_hsv = cv2.bitwise_and(frame_hsv, frame_hsv, mask=mask)
    
    # # manipulate colors
    cv2.threshold(frame_hsv, 127, 255, cv2.THRESH_BINARY, frame_hsv)

    res_gray = cv2.cvtColor(frame_hsv, cv2.COLOR_BGR2GRAY)

    ret, gray = cv2.threshold(res_gray, 127, 255, 0)
    
    gray2 = res_gray.copy()
    mask = np.zeros(res_gray.shape, np.uint8)

    kernel = np.ones((5,5),np.uint8)
    # closing = cv2.morphologyEx(res_gray, cv2.MORPH_CLOSE, kernel)
    # closing = cv2.morphologyEx(closing, cv2.MORPH_CLOSE, kernel)
    dilation = cv2.dilate(res_gray, kernel, iterations=2)
    erodate = cv2.erode(dilation, kernel, iterations=2)

    contours, hier = cv2.findContours(erodate, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    aux_gray = res_gray
    

    last_mean = (0,0,0)
    for cnt in contours:
        if 100<cv2.contourArea(cnt)<5000:
            # cv2.drawContours(aux_gray, [cnt], 0, (255,0,0), 3)
            # cv2.drawContours(frame, [cnt], 0, (255,0,0), -1)
            (x,y,w,h) = cv2.boundingRect(cnt)
            if w > 20 and h > 20:
                 if y < 60:
                    cv2.rectangle(aux_gray, (x,y), (x+w,y+h), (0, 0, 255), -1)
                    cv2.rectangle(frame, (x,y), (x+w,y+2), (255, 0, 230), -1)
                    return True
    
    return False

def detect_teleport(frame_teleport, frame, lower_teleport, upper_teleport):
    frame_rgb = cv2.cvtColor(frame_teleport, cv2.COLOR_BGR2RGB)
    
    # # clean image
    frame_blur = cv2.GaussianBlur(frame_rgb, (3,3), 0)

    # # convert to hsv
    frame_hsv = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2HSV)

    mask = cv2.inRange(frame_hsv, lower_teleport, upper_teleport)
 
    frame_hsv = cv2.bitwise_and(frame_hsv, frame_hsv, mask=mask)
    
    # # manipulate colors
    cv2.threshold(frame_hsv, 127, 255, cv2.THRESH_BINARY, frame_hsv)

    res_gray = cv2.cvtColor(frame_hsv, cv2.COLOR_BGR2GRAY)

    ret, gray = cv2.threshold(res_gray, 127, 255, 0)
    
    gray2 = res_gray.copy()
    mask = np.zeros(res_gray.shape, np.uint8)

    kernel = np.ones((5,5),np.uint8)
    # closing = cv2.morphologyEx(res_gray, cv2.MORPH_CLOSE, kernel)
    # closing = cv2.morphologyEx(closing, cv2.MORPH_CLOSE, kernel)
    dilation = cv2.dilate(res_gray, kernel, iterations=4)
    erodate = cv2.erode(dilation, kernel, iterations=4)

    contours, hier = cv2.findContours(erodate, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    aux_gray = res_gray
    
    last_mean = (0,0,0)
    detected_tp = False
    for cnt in contours:
        if 300<cv2.contourArea(cnt)<5000:
            # cv2.drawContours(aux_gray, [cnt], 0, (255,0,0), 3)
            # cv2.drawContours(frame, [cnt], 0, (255,0,0), -1)
            (x,y,w,h) = cv2.boundingRect(cnt)
            if w > 30 and h > 30:
                cv2.rectangle(aux_gray, (x,y), (x+w,y+h), (0, 255, 0), -1)
                cv2.rectangle(frame, (x,y), (x+w,y+h), (0, 255, 0), -1)
                print("detected_tp teleport")
                detected_tp = True
                break

    global p1
    global p2
    global mytp
    global myplayer
    if (detected_tp == True and mytp == False):
        if (myplayer is p1):
            myplayer.fill = 2
            myplayer = p2
            myplayer.fill = -1
        else:
            myplayer.fill = 2
            myplayer = p1
            myplayer.fill = -1
        
    cv2.imshow('teleport', aux_gray)
    cv2.waitKey(1)
    cv2.imshow('teleport_dilatat', erodate)
    cv2.waitKey(1)

    return detected_tp

def counterAttack():
    global p1
    global myplayer

    comenzi.teleport_left()
    comenzi.teleport_right()
    comenzi.low_kick()  

    comboAttack()

def tucombo_right():
    comenzi.spear_right()
    comenzi.teleport_right()
    comenzi.upsword_left()
    comenzi.upsword_right()
    comenzi.low_kick()
    lock = True

def tucombo_left():
    comenzi.spear_left()
    comenzi.teleport_left()
    comenzi.upsword_right()
    comenzi.upsword_left()
    comenzi.low_kick()
    lock = True

def doom_right():
    global lock
    comenzi.upsword_right()
    comenzi.upsword_left()
    comenzi.uppercut()
    lock = True

def doom_left():
    comenzi.upsword_left()
    comenzi.upsword_right()
    comenzi.uppercut()
    lock = True

def too_distant():
    global myplayer
    global lock
    
    if (abs(p1.center[0] - p2.center[0]) > 40 and \
        abs(p1.center[0] - p2.center[0]) < 70):
        if (myplayer.direction == "left"):
            comenzi.spear_left()
        else:
            comenzi.spear_right()

    elif (abs(p1.center[0] - p2.center[0]) > 70):
        counterAttack()
    else:
        comboAttack()
        
        return
        
    lock = True

def comboAttack():
    global myplayer
    if (myplayer.direction == "left"):
        for i in range(1,2):
            comenzi.takedown_left()

        doom_left()
        doom_left()
        comenzi.bpunch()
        comenzi.spear_left()
        doom_left()
        for i in range(1,3):
            comenzi.teleport_left()
            doom_right()
            comenzi.bpunch()
            comenzi.teleport_right()
            doom_left()
        comenzi.forward2_left()
        for i in range(1,3):
            comenzi.takedown_left()
    else:
        comenzi.forward2_right()
        doom_right()
        comenzi.spear_right()
        doom_right()
        for i in range(1,3):
            comenzi.teleport_right()
            comenzi.teleport_left()
        comenzi.teleport_right()
        comenzi.forward2_left()
        for i in range(1,2):
            doom_left()

funclist = [comboAttack, doom_left, doom_right, tucombo_left, tucombo_right, counterAttack]

def example(frame):
    l_h = cv2.getTrackbarPos("L - H", "Trackbars")
    l_s = cv2.getTrackbarPos("L - S", "Trackbars")
    l_v = cv2.getTrackbarPos("L - V", "Trackbars")
    u_h = cv2.getTrackbarPos("U - H", "Trackbars")
    u_s = cv2.getTrackbarPos("U - S", "Trackbars")
    u_v = cv2.getTrackbarPos("U - V", "Trackbars")

    global counter_tp
    global counter_jmp
    global counter_checked
    global p1
    global p2
    global threadlist
    global lock
    global funclist

    if (counter_tp > 0):
        counter_tp -= 1
    
    if (counter_jmp > 0):
        counter_jmp -= 1

    lower_subzero = np.array([0, 71, 70])
    upper_subzero = np.array([71, 255, 255])

    #TODO: do something with your frame
    frame = frame[0:500, 0:800]
    frame_subzero = frame.copy()
    frame_scorpion = frame.copy()

    detect_subzero(frame_subzero, frame, lower_subzero, upper_subzero)

    lower_scorpion = np.array([88, 114, 87])
    upper_scorpion = np.array([116, 167, 182])

    lower_teleport = np.array([104, 149, 129])
    upper_teleport = np.array([149, 196, 165])

    detect_scorpion(frame_scorpion, frame, lower_scorpion, upper_scorpion)
    
    detected_tp = False
    if (counter_tp <= 0):
        recently_tp = False
        detected_tp = detect_teleport(frame_scorpion, frame, lower_teleport, upper_teleport)
    if (detected_tp == True):
        counter_tp = 4
        recently_tp = True
        p1.changeDirection()
        p2.changeDirection()
        if (lock == True):
            lock = False
            t = Thread(target=counterAttack)
            t.start()

    # Every 10 frames check if my player is correct
 
    t2 = Thread(target=too_distant)
    t2.start()

    detected_jmp = False
    if (counter_jmp <= 0):
        detected_jmp = detect_jump(frame_scorpion, frame, lower_scorpion, upper_scorpion)
    if (detected_jmp == True):
        # Thread(target=doom_right).start()
        # Thread(target=doom_left).start()
        pass

    compressionRatio = 0.4
    upscaled = cv2.resize(frame, (0,0), fx=1/compressionRatio, fy=1/compressionRatio)
    p1.drawCircle(frame)
    p2.drawCircle(frame)
    cv2.imshow('upscaled', upscaled)
    cv2.waitKey(1)
    #render frame to our scree


UDP_IP = "0.0.0.0"
UDP_PORT = 5005
if (len(sys.argv) > 1):
    UDP_PORT = int(sys.argv[1])
startListening(UDP_IP, UDP_PORT, example)


# hog = cv2.HOGDescriptor()
#     hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
#     gray_frame = cv2.cvtColor(frame_hsv, cv2.COLOR_RGB2GRAY)

#     rects, weights = hog.detectMultiScale(gray_frame)
        
#     # Measure elapsed time for detections
#     for i, (x, y, w, h) in enumerate(rects):
#         if weights[i] < 0.7:
#             continue
#         cv2.rectangle(frame, (scorpionx,y), (x+w,y+h),(0,255,0),2)

