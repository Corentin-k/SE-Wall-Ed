import RPi.GPIO as GPIO
import time


def switchSetpup() :
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    GPIO.setup(5, GPIO.OUT)  
    GPIO.setup(6, GPIO.OUT)  
    GPIO.setup(13, GPIO.OUT)  

def switch(status, gpio):
    if status == 1:
        GPIO.output(gpio, GPIO.HIGH)
    elif status == 0:
        GPIO.output(gpio, GPIO.LOW)
    else:
        pass



def main():
    switchSetpup()
    run = True
    while run :
        switch(1, 5)
        switch(1, 6)
        switch(1, 13)
        time.sleep(1)
        switch(0, 5)
        switch(0, 6)
        switch(0, 13)
        time.sleep(1)

main()