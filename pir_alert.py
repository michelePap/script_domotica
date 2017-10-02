import RPi.GPIO as GPIO
import time
import os
sensor = 7

GPIO.setmode(GPIO.BCM)
GPIO.setup(sensor, GPIO.IN, GPIO.PUD_DOWN)

previous_state = False
current_state = False

while True:
    time.sleep(0.1)
    previous_state = current_state
    current_state = GPIO.input(sensor)
    if current_state != previous_state:
        new_state = "HIGH" if current_state else "LOW"
	if new_state == "HIGH":
		os.system ("fswebcam -r 640x480 /home/pi/tg/alert.jpg")
        break;
