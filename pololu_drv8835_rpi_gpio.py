try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print("Error importing RPi.GPIO!  This is probably because you need superuser privileges.  You can achieve this by using 'sudo' to run your script")

# To keep source compatibility with Pololu's library using wiringPi we keep the range as -480 to 480
# Motor speeds for this library are specified as numbers
# between -MAX_SPEED and MAX_SPEED, inclusive.
_max_speed = 480
# RPi.GPIO currently doesn't support hardware PWM so we use a relatively low frequency
_frequency = 3000
MAX_SPEED = _max_speed

# Default GPIO pin assignments
MOTOR1_PWM_PIN = 12
MOTOR1_DIR_PIN = 5
MOTOR2_PWM_PIN = 13
MOTOR2_DIR_PIN = 6

# Global RPi.GPIO PWMs
m1_pwm = None
m2_pwm = None

def io_init():
    """GPIO initializer - global as done once regardless of number of instances of Motor/Motors classes"""
    global m1_pwm, m2_pwm
    if not m1_pwm == None:
        return

    GPIO.setmode(GPIO.BCM)
    GPIO.setup([MOTOR1_PWM_PIN, MOTOR1_DIR_PIN, MOTOR2_PWM_PIN, MOTOR2_DIR_PIN], GPIO.OUT)
    m1_pwm=GPIO.PWM(MOTOR1_PWM_PIN, _frequency)
    m2_pwm=GPIO.PWM(MOTOR2_PWM_PIN, _frequency)
    m1_pwm.start(0)
    m2_pwm.start(0)

def cleanup():
    """Global cleanup"""
    global motors
    m1_pwm.stop()
    m2_pwm.stop()
    GPIO.cleanup()

class Motor(object):
    MAX_SPEED = _max_speed

    def __init__(self, pwm_pin, dir_pin, pwm):
        io_init()
        self.pwm_pin = pwm_pin
        self.dir_pin = dir_pin
        self.pwm = pwm

    def setSpeed(self, speed):
        if speed < -MAX_SPEED:
            speed = -MAX_SPEED
        elif speed > MAX_SPEED:
            speed = MAX_SPEED

        speed_percent = speed * 100.0 / MAX_SPEED
        self.setSpeedPercent(speed_percent)

    def setSpeedPercent(self, speed):
        dir_value = GPIO.LOW
        if speed < 0:
            speed = -speed
            dir_value = GPIO.HIGH
        if speed > 100:
            speed = 100
        self.pwm.ChangeDutyCycle(speed)
        GPIO.output(self.dir_pin, dir_value)
 
class Motors(object):
    MAX_SPEED = _max_speed

    def __init__(self):
        io_init()
        global m1_pwm, m2_pwm
        self.motor1 = Motor(pwm_pin=MOTOR1_PWM_PIN, dir_pin=MOTOR1_DIR_PIN, pwm=m1_pwm)
        self.motor2 = Motor(pwm_pin=MOTOR2_PWM_PIN, dir_pin=MOTOR2_DIR_PIN, pwm=m2_pwm)

    def setSpeeds(self, m1_speed, m2_speed):
        self.motor1.setSpeed(m1_speed)
        self.motor2.setSpeed(m2_speed)

    def setSpeedsPercent(self, m1_speed, m2_speed):
        self.motor1.setSpeedPercent(m1_speed)
        self.motor2.setSpeedPercent(m2_speed)

motors = Motors()
