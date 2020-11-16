import RPi.GPIO as GPIO
import time
import os
import atexit


TRIG = 4
ECHO = 18
LIGHT_PORT = 17

GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG,GPIO.OUT)
GPIO.setup(ECHO,GPIO.IN)
GPIO.setup(LIGHT_PORT, GPIO.OUT)

NOISE_FILE = "noise.m4a"
SALAM_FILE = "salam.m4a"

DISTANCE_THRESHOLD = 30

atexit.register(GPIO.cleanup)

def play(filename):
    os.system("ffplay -nodisp -autoexit " + filename + " >/dev/null 2>&1")


def light_on():
    GPIO.output(LIGHT_PORT, GPIO.HIGH)


def light_off():
    GPIO.output(LIGHT_PORT, GPIO.LOW)


def get_distance():
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)
    while GPIO.input(ECHO) == False:
        start = time.time()
    while GPIO.input(ECHO) == True:
        end = time.time()
    sig_time = end-start
    distance = sig_time / 0.000058
    return distance


def calc_average_distance():
    sum = 0
    num_tests = 10
    for x in range(num_tests):
        sum = sum + get_distance()
        time.sleep(0.0001)
    average = sum / num_tests
    print("Average distance is " + str(average) + "cm")
    return average


average_distance = calc_average_distance()


def is_open():
    sum = 0
    for x in range(3):
        time.sleep(0.0001)
        sum += get_distance()
    distance = sum / 3
    difference = abs(average_distance - distance)
    open = difference > DISTANCE_THRESHOLD
    return open

num_consecutive_positives = 0

while True:
    if num_consecutive_positives > 3:
        average_distance = calc_average_distance()
        num_consecutive_positives = 0

    periodic_check = is_open()
    if(periodic_check):
        should_continue = True
        for x in range(3):
            time.sleep(0.001)
            if not is_open():
                should_continue = False
                break
        if should_continue:
            light_on()
            play(SALAM_FILE)
            num_consecutive_positives = num_consecutive_positives + 1
            time.sleep(30)
            light_off()
        else:
            num_consecutive_positives = 0
    else:
        num_consecutive_positives = 0
    time.sleep(3)
