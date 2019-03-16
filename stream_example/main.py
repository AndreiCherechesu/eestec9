import cv2, sys
import numpy as np

from utils import printTimeDiff, initTimeDiff
from client import startListening, curFrame, frameFragments

def nothing(x):
    pass

cv2.namedWindow("Trackbars")
 
cv2.createTrackbar("L - H", "Trackbars", 0, 179, nothing)
cv2.createTrackbar("L - S", "Trackbars", 0, 255, nothing)
cv2.createTrackbar("L - V", "Trackbars", 0, 255, nothing)
cv2.createTrackbar("U - H", "Trackbars", 179, 179, nothing)
cv2.createTrackbar("U - S", "Trackbars", 255, 255, nothing)
cv2.createTrackbar("U - V", "Trackbars", 255, 255, nothing)

def detect_subzero(frame_subzero, frame, lower_subzero, upper_subzero):
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
    
    for cnt in contours:
        if 300<cv2.contourArea(cnt)<5000:
            (x,y,w,h) = cv2.boundingRect(cnt)
            if w > 10 and h > 30:
                cv2.rectangle(aux_gray, (x,y), (x+w,y+h), (255, 0, 0), 2)
                cv2.rectangle(frame, (x,y), (x+w,y+h), (255, 0, 0), 2)
        
        # (x,y,w,h) = cv2.boundingRect(cnt)
        # if w > 5 and h > 5:
        #     cv2.rectangle(aux_gray, (x,y), (x+w,y+h), (0, 0, 255), 2)
        #     cv2.rectangle(frame, (x,y), (x+w,y+h), (0, 0, 255), 2)

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
    dilation = cv2.dilate(res_gray, kernel, iterations=7)
    erodate = cv2.erode(dilation, kernel, iterations=5)

    contours, hier = cv2.findContours(erodate, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    aux_gray = res_gray
    
    for cnt in contours:
        if 300<cv2.contourArea(cnt)<5000:
            (x,y,w,h) = cv2.boundingRect(cnt)
            if w > 10 and h > 30:
                cv2.rectangle(aux_gray, (x,y), (x+w,y+h), (0, 0, 255), 2)
                cv2.rectangle(frame, (x,y), (x+w,y+h), (0, 0, 255), 2)
        
        # (x,y,w,h) = cv2.boundingRect(cnt)
        # if w > 5 and h > 5:
        #     cv2.rectangle(aux_gray, (x,y), (x+w,y+h), (0, 0, 255), 2)
        #     cv2.rectangle(frame, (x,y), (x+w,y+h), (0, 0, 255), 2)

    
    cv2.imshow('scorpion', aux_gray)
    cv2.waitKey(1)
    cv2.imshow('scorpion_dilatat', erodate)
    cv2.waitKey(1)

def example(frame):
    l_h = cv2.getTrackbarPos("L - H", "Trackbars")
    l_s = cv2.getTrackbarPos("L - S", "Trackbars")
    l_v = cv2.getTrackbarPos("L - V", "Trackbars")
    u_h = cv2.getTrackbarPos("U - H", "Trackbars")
    u_s = cv2.getTrackbarPos("U - S", "Trackbars")
    u_v = cv2.getTrackbarPos("U - V", "Trackbars")

    lower_subzero = np.array([0, 71, 70])
    upper_subzero = np.array([71, 255, 255])

    #TODO: do something with your frame
    frame = frame[0:500, 0:800]
    frame_subzero = frame.copy()
    frame_scorpion = frame.copy()

    detect_subzero(frame_subzero, frame, lower_subzero, upper_subzero)
    
    lower_scorpion = np.array([l_h, l_s, l_v])
    upper_scorpion = np.array([u_h, u_s, u_v])

    # lower_scorpion = np.array([88, 114, 87])
    # upper_scorpion = np.array([116, 167, 182])

    # lower_scorpion = np.array([229, 30, 39])
    # upper_scorpion = np.array([238, 40, 55])

    detect_scorpion(frame_scorpion, frame, lower_scorpion, upper_scorpion)
    # # convert to corect color scheme
    

    # contours, hier = cv2.findContours(result_gray, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # for cnt in contours:
    #         (x,y,w,h) = cv2.boundingRect(cnt)
    #         # if w > 30 and h > 50:
    #         cv2.rectangle(frame, (x,y), (x+w,y+h), (255, 0, 0), 2)
            
    cv2.imshow('client1', frame)
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
#         cv2.rectangle(frame, (x,y), (x+w,y+h),(0,255,0),2)