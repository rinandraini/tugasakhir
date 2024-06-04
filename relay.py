import RPi.GPIO as GPIO
import time

# Atur mode pin GPIO
GPIO.setmode(GPIO.BCM)

# Tentukan nomor pin yang akan digunakan
relay_pin = 18

# Atur pin sebagai output
GPIO.setup(relay_pin, GPIO.OUT)

try:
    while True:
        # Hidupkan relay (set pin ke HIGH)
        GPIO.output(relay_pin, GPIO.HIGH)
        print("Relay ON")
        time.sleep(1)  # Tunggu 1 detik
        
        # Matikan relay (set pin ke LOW)
        GPIO.output(relay_pin, GPIO.LOW)
        print("Relay OFF")
        time.sleep(1)  # Tunggu 1 detik

except KeyboardInterrupt:
    # Tangani interrupt dari keyboard (Ctrl+C)
    print("Program dihentikan secara manual")

finally:
    # Bersihkan pin GPIO
    GPIO.cleanup()
