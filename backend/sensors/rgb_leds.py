import RPi.GPIO as GPIO
import time


def switchSetpup() :
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    GPIO.setup(9, GPIO.OUT)  
    GPIO.setup(25, GPIO.OUT)  
    GPIO.setup(11, GPIO.OUT)  

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
        switch(1, 9)
        switch(1, 25)
        switch(1, 11)
        time.sleep(1)
        switch(0, 9)
        switch(0, 25)
        switch(0, 11)
        time.sleep(1)

main()