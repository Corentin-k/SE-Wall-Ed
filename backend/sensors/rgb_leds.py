import RPi.GPIO as GPIO
import time

left_R = 19
left_G = 13
left_B = 0

right_R = 1
right_G = 5
right_B = 6

def switchSetpup() :
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    GPIO.setup(left_R, GPIO.OUT)  
    GPIO.setup(right_R, GPIO.OUT)  
    GPIO.setup(left_G, GPIO.OUT)  
    GPIO.setup(right_G, GPIO.OUT) 
    GPIO.setup(left_B, GPIO.OUT)  
    GPIO.setup(right_B, GPIO.OUT) 

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
        switch(1, left_R)
        switch(1, right_R)
        switch(0, left_G)
        switch(0, right_G)
        switch(0, left_B)
        switch(0, right_B)
        time.sleep(1)
        switch(0, left_R)
        switch(0, right_R)

        
main()