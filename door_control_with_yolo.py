import time
import cv2
import numpy as np
from motor_servo import Servo
import ultrasonic
import pygame
import RPi.GPIO as GPIO

# Inisialisasi motor servo
motor_servo = Servo()

# Inisialisasi jaringan YOLO
net = cv2.dnn.readNetFromDarknet("yolov4-tiny-custom.cfg", "yolov4-tiny-custom_best.weights")

# Kelas objek
classes = ['topi', 'kacamata_hitam', 'helm', 'masker', 'manusia']

# Inisialisasi webcam
cap = cv2.VideoCapture(0)

# Inisialisasi pygame untuk audio
pygame.mixer.init()

# Inisialisasi GPIO untuk solenoid lock
SOLENOID_PIN = 25
GPIO.setmode(GPIO.BCM)
GPIO.setup(SOLENOID_PIN, GPIO.OUT)

def solenoid_lock(state):
    if state:
        GPIO.output(SOLENOID_PIN, GPIO.HIGH)
    else:
        GPIO.output(SOLENOID_PIN, GPIO.LOW)

prev_frame_time = 0
new_frame_time = 0

while True:
    ret, img = cap.read()
    if not ret:
        break

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
                confidences.append(float(confidence))
                class_ids.append(class_id)

    indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.8, 0.4)
    font = cv2.FONT_HERSHEY_PLAIN
    colors = np.random.uniform(0, 255, size=(len(boxes), 3))

    new_frame_time = time.time()
    fps = 1 / (new_frame_time - prev_frame_time)
    prev_frame_time = new_frame_time
    fps = round(fps, 2)
    fps = str(fps)

    violation_detected = False

    if len(indexes) > 0:
        for i in indexes.flatten():
            x, y, w, h = boxes[i]
            label = str(classes[class_ids[i]])

            if label == 'manusia':
                distance = ultrasonic.measure_distance()
                if distance <= 5 and not violation_detected:
                    print("Manusia terdeteksi dalam jarak 5 cm")
                    solenoid_lock(True)  # Buka solenoid lock
                    motor_servo.open()
                    time.sleep(10)
                    motor_servo.close()
                    solenoid_lock(False)  # Tutup solenoid lock
            elif label in ['topi', 'kacamata_hitam', 'helm', 'masker']:
                print(f"{label} terdeteksi")
                pygame.mixer.music.load(f"{label}audio.mp3")
                pygame.mixer.music.play()
                violation_detected = True

            confidence = str(round(confidences[i], 2))
            color = colors[i]
            cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)
            cv2.putText(img, label + " " + confidence, (x, y + 100), font, 2, color, 2)

    cv2.putText(img, "{} fps".format(fps), (1, 25), font, 1, (0, 255, 255), 2)
    cv2.imshow('img', img)
    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
pygame.quit()
GPIO.cleanup()
