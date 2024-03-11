import RPi.GPIO as GPIO

class raspi_io():
    global led
    global switch
    global IO
    led = 40
    switch = 18
    IO = GPIO

    def __init__()->None:
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(led, GPIO.OUT)
        GPIO.setup(switch, GPIO.IN)

    def cleanup():
        IO.cleanup()

    def flash_on():
        GPIO.output(led, GPIO.HIGH)
        
    def flash_off():    
        GPIO.output(led, GPIO.LOW)
        print('Switch status = ', GPIO.input(switch))


def __init__(self):
    raspi_io = raspi_io()