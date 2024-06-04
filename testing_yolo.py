import time
import cv2
import numpy as np
from motor_servo import Servo
import ultrasonic
import pygame
motor_servo = Servo()

net = cv2.dnn.readNetFromDarknet("yolov4-tiny-custom.cfg","yolov4-tiny-custom_best.weights")

classes = ['topi','kacamata_hitam','helm','masker','manusia']

cap = cv2.VideoCapture(0)
#img = cv2.imread("bangun (1)")
prev_frame_time = 0
new_frame_time = 0

while 1:
    _, img = cap.read()

    img = cv2.resize(img, (480, 480))

    hight, width, _ = img.shape
    blob = cv2.dnn.blobFromImage(img, 1 / 255, (416, 416), (0, 0, 0), swapRB=True, crop=False)
    net.setInput(blob)
    output_layers_name = net.getUnconnectedOutLayersNames()
    layerOutputs = net.forward(output_layers_name)

    boxes = []
    confidences = []
    class_ids = []

    for output in layerOutputs:
        for detection in output:
            score = detection[5:]
            class_id = np.argmax(score)
            confidence = score[class_id]
            if confidence > 0.5:
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * hight)
                w = int(detection[2] * width)
                h = int(detection[3] * hight)

                x = int(center_x - w / 2)
                y = int(center_y - h / 2)

                boxes.append([x, y, w, h])
                confidences.append((float(confidence)))
                class_ids.append(class_id)

                #width= int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                #height= int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                
    indexes = cv2.dnn.NMSBoxes(boxes, confidences, .8, .4)
    font = cv2.FONT_HERSHEY_PLAIN
    colors = np.random.uniform(0, 255, size=(len(boxes), 3))

    new_frame_time = time.time()
    fps = 1 / (new_frame_time - prev_frame_time)
    prev_frame_time = new_frame_time
    fps = round(fps, 2)
    fps = str(fps)

    if len(indexes) > 0:
        for i in indexes.flatten():
            x, y, w, h = boxes[i]
            label = str(classes[class_ids[i]])
            if label == 'manusia': 
                print("terdeteksi manusia")
                motor_servo.open()
                time.sleep(10)
                motor_servo.close()
                ultrasonic.measure_distance()
                motor_servo.open()
                motor_servo.close()
            
            elif label == 'topi':
                tplaying = time.time()
                print("topi terdeteksi")
                playMusic('topiaudio.mp3')
                while(time.time()- tplaying <3):
                    time.sleep(0.1)
                    topi = True
                    
            elif label == 'kacamata_hitam':
                tplaying = time.time()
                print("kacamata hitam terdeteksi")
                playMusic('kacamatahitamaudio.mp3')
                while(time.time()- tplaying <3):
                    time.sleep(0.1)
                    topi = True
            
            elif label == 'helm':
                tplaying = time.time()
                print("helm terdeteksi")
                playMusic('helmaudio.mp3')
                while(time.time()- tplaying <3):
                    time.sleep(0.1)
                    topi = True
                    
            elif label == 'masker':
                tplaying = time.time()
                print("masker terdeteksi")
                playMusic('maskeraudio.mp3')
                while(time.time()- tplaying <3):
                    time.sleep(0.1)
                    topi = True
                    
            confidence = str(round(confidences[i], 2))
            color = colors[i]
            cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)
            cv2.putText(img, label + " " + confidence, (x, y + 100), font, 2, color, 2)
            
    cv2.putText(img, "{} fps".format(fps), (1,25), font, 1, (0,255,255), 2)
    cv2.imshow('img', img)
    if cv2.waitKey(1) == ord('q'):
        break

#cap.release()
cv2.destroyAllWindows()