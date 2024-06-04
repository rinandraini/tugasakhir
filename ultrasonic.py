import RPi.GPIO as GPIO
import time

# Constants
TRIG_PIN = 23   # Raspberry Pi GPIO pin connected to TRIG pin of ultrasonic sensor
ECHO_PIN = 24   # Raspberry Pi GPIO pin connected to ECHO pin of ultrasonic sensor
DISTANCE_THRESHOLD = 5 # in centimeters

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG_PIN, GPIO.OUT)
GPIO.setup(ECHO_PIN, GPIO.IN)

def measure_distance():
    # Generate 10-microsecond pulse to TRIG pin
    GPIO.output(TRIG_PIN, GPIO.HIGH)
    time.sleep(0.00001)
    GPIO.output(TRIG_PIN, GPIO.LOW)

    # Measure duration of pulse from ECHO pin
    pulse_start = time.time()
    pulse_end = pulse_start

    while GPIO.input(ECHO_PIN) == 0 and time.time() - pulse_start < 0.1:
        pulse_start = time.time()

    while GPIO.input(ECHO_PIN) == 1 and time.time() - pulse_end < 0.1:
        pulse_end = time.time()

    duration = pulse_end - pulse_start

    # Calculate the distance
    distance_cm = duration * 34300 / 2
    
    print(f"Distance: {distance_cm:.2f} cm")

    return distance_cm

#try:
#    while True:
        # Measure distance
#        distance_cm = measure_distance()

        # Print the value
#        print(f"Distance: {distance_cm:.2f} cm")

#        time.sleep(0.5)

#except KeyboardInterrupt:
#    GPIO.cleanup()