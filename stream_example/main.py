import cv2, sys
import numpy as np
import tensorflow

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



class DetectorAPI:
    def __init__(self, path_to_ckpt):
        self.path_to_ckpt = path_to_ckpt

        self.detection_graph = tf.Graph()
        with self.detection_graph.as_default():
            od_graph_def = tf.GraphDef()
            with tf.gfile.GFile(self.path_to_ckpt, 'rb') as fid:
                serialized_graph = fid.read()
                od_graph_def.ParseFromString(serialized_graph)
                tf.import_graph_def(od_graph_def, name='')

        self.default_graph = self.detection_graph.as_default()
        self.sess = tf.Session(graph=self.detection_graph)

        # Definite input and output Tensors for detection_graph
        self.image_tensor = self.detection_graph.get_tensor_by_name('image_tensor:0')
        # Each box represents a part of the image where a particular object was detected.
        self.detection_boxes = self.detection_graph.get_tensor_by_name('detection_boxes:0')
        # Each score represent how level of confidence for each of the objects.
        # Score is shown on the result image, together with the class label.
        self.detection_scores = self.detection_graph.get_tensor_by_name('detection_scores:0')
        self.detection_classes = self.detection_graph.get_tensor_by_name('detection_classes:0')
        self.num_detections = self.detection_graph.get_tensor_by_name('num_detections:0')

    def processFrame(self, image):
        # Expand dimensions since the trained_model expects images to have shape: [1, None, None, 3]
        image_np_expanded = np.expand_dims(image, axis=0)
        # Actual detection.
        start_time = time.time()
        (boxes, scores, classes, num) = self.sess.run(
            [self.detection_boxes, self.detection_scores, self.detection_classes, self.num_detections],
            feed_dict={self.image_tensor: image_np_expanded})
        end_time = time.time()

        print("Elapsed Time:", end_time-start_time)

        im_height, im_width,_ = image.shape
        boxes_list = [None for i in range(boxes.shape[1])]
        for i in range(boxes.shape[1]):
            boxes_list[i] = (int(boxes[0,i,0] * im_height),
                        int(boxes[0,i,1]*im_width),
                        int(boxes[0,i,2] * im_height),
                        int(boxes[0,i,3]*im_width))

        return boxes_list, scores[0].tolist(), [int(x) for x in classes[0].tolist()], int(num[0])

    def close(self):
        self.sess.close()
        self.default_graph.close()


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


#incercare Tensorflow
model_path = '/home/skanda/facultate/eestec/eestec9/stream_example/faster_rcnn_inception_v2_coco_2018_01_28/frozen_inference_graph.pb'
odapi = DetectorAPI(path_to_ckpt=model_path)
threshold = 0.7

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
    
    boxes, scores, classes, num = odapi.processFrame(frame)
    for i in range(len(boxes)):
            # Class 1 represents human
            if classes[i] == 1 and scores[i] > threshold:
                box = boxes[i]
                cv2.rectangle(frame,(box[1],box[0]),(box[3],box[2]),(255,0,0),2)

    cv2.imshow("preview", frame)
    cv2.waitKey(1)
    


    # contours, hier = cv2.findContours(result_gray, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # for cnt in contours:
    #         (x,y,w,h) = cv2.boundingRect(cnt)
    #         # if w > 30 and h > 50:
    #         cv2.rectangle(frame, (x,y), (x+w,y+h), (255, 0, 0), 2)
            
    # cv2.imshow('client1', frame)
    # cv2.waitKey(1)

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