#smooth_remotecontrol 
#Run this code to give commands via gamepad

import time
from adafruit_pca9685 import PCA9685
from board import SCL, SDA
import busio
import threading
from evdev import InputDevice, categorize, ecodes


i2c = busio.I2C(SCL, SDA)
pca = PCA9685(i2c)
pca.frequency = 50

# servo channels
CHANNEL_TORSO = 0
CHANNEL_LEFT_ARM = 3
CHANNEL_RIGHT_ARM = 4

# Servo positions
FORWARD_POS = -150
NEUTRAL_POS = -5
BACKWARD_POS = 100
LEFT_ARM_NEUTRAL_POS = -32
RIGHT_ARM_NEUTRAL_POS = -200
LEFT_ARM_LIFT_POS = 128 
RIGHT_ARM_LIFT_POS = -360 

LEFT_ARM_PUSH_POS = 30  
RIGHT_ARM_PUSH_POS = -105 
TURN_STEP_LEFT_ARM = 188  
TURN_STEP_RIGHT_ARM = 80  

def angle_to_pulse(angle):
    min_pulse = 1000
    max_pulse = 2000
    pulse_width = min_pulse + (max_pulse - min_pulse) * ((angle + 180) / 360)
    return int(pulse_width * 65535 / 20000)
    
def set_servo_angle(channel, angle):
    pulse = angle_to_pulse(angle)
    pca.channels[channel].duty_cycle = pulse


def set_servo_angle_smooth(channel, start_angle, end_angle, steps=20):
    step_delay = 0.03
    step_size = (end_angle - start_angle) / steps
    for step in range(steps):
        current_angle = start_angle + step * step_size
        pulse = angle_to_pulse(current_angle)
        pca.channels[channel].duty_cycle = pulse
        time.sleep(step_delay)
    pca.channels[channel].duty_cycle = angle_to_pulse(end_angle)

def threaded_move(channel, start_angle, end_angle, steps=20):
    threading.Thread(target=set_servo_angle_smooth, args=(channel, start_angle, end_angle, steps)).start()

# Movement Functions
def move_forward():
    print("[TARS] Moving forward...")
    threaded_move(CHANNEL_TORSO, NEUTRAL_POS, FORWARD_POS)
    time.sleep(1)

    #if torso smooth swing doesnt work try fast swing so that TARS lands on its torso after swing
    #using set_servo_angle instead of threaded_move 

    #threaded_move(CHANNEL_LEFT_ARM, LEFT_ARM_NEUTRAL_POS, LEFT_ARM_LIFT_POS)
    #threaded_move(CHANNEL_RIGHT_ARM, RIGHT_ARM_NEUTRAL_POS, RIGHT_ARM_LIFT_POS)
    #time.sleep(1)
    #threaded_move(CHANNEL_TORSO, FORWARD_POS, BACKWARD_POS)
    #time.sleep(1) 

    set_servo_angle(CHANNEL_LEFT_ARM, LEFT_ARM_LIFT_POS)
    set_servo_angle(CHANNEL_RIGHT_ARM, RIGHT_ARM_LIFT_POS)
    time.sleep(1)   
    set_servo_angle(CHANNEL_TORSO , BACKWARD_POS)
    time.sleep(0.8)

    threaded_move(CHANNEL_LEFT_ARM, LEFT_ARM_LIFT_POS, LEFT_ARM_NEUTRAL_POS)
    threaded_move(CHANNEL_RIGHT_ARM, RIGHT_ARM_LIFT_POS, RIGHT_ARM_NEUTRAL_POS)
    time.sleep(0.2)
    threaded_move(CHANNEL_TORSO, BACKWARD_POS, NEUTRAL_POS)
    time.sleep(0.8)

def turn_left():
    print("[TARS] Turning left...")
    threaded_move(CHANNEL_TORSO, NEUTRAL_POS, 150)
    time.sleep(0.2)
    left_target = LEFT_ARM_NEUTRAL_POS + TURN_STEP_LEFT_ARM
    right_target = RIGHT_ARM_NEUTRAL_POS + TURN_STEP_RIGHT_ARM
    threaded_move(CHANNEL_LEFT_ARM, LEFT_ARM_NEUTRAL_POS, left_target)
    threaded_move(CHANNEL_RIGHT_ARM, RIGHT_ARM_NEUTRAL_POS, right_target)
    time.sleep(0.5)
    threaded_move(CHANNEL_TORSO, FORWARD_POS, NEUTRAL_POS)
    threaded_move(CHANNEL_LEFT_ARM, left_target, LEFT_ARM_NEUTRAL_POS)
    threaded_move(CHANNEL_RIGHT_ARM, right_target, RIGHT_ARM_NEUTRAL_POS)
    time.sleep(0.8)

def turn_right():
    print("[TARS] Turning right...")
    threaded_move(CHANNEL_TORSO, NEUTRAL_POS, 150)
    time.sleep(0.2)
    left_target = LEFT_ARM_NEUTRAL_POS - TURN_STEP_LEFT_ARM
    right_target = RIGHT_ARM_NEUTRAL_POS - TURN_STEP_RIGHT_ARM
    threaded_move(CHANNEL_LEFT_ARM, LEFT_ARM_NEUTRAL_POS, left_target)
    threaded_move(CHANNEL_RIGHT_ARM, RIGHT_ARM_NEUTRAL_POS, right_target)
    time.sleep(0.5)
    threaded_move(CHANNEL_TORSO, FORWARD_POS, NEUTRAL_POS)
    threaded_move(CHANNEL_LEFT_ARM, left_target, LEFT_ARM_NEUTRAL_POS)
    threaded_move(CHANNEL_RIGHT_ARM, right_target, RIGHT_ARM_NEUTRAL_POS)
    time.sleep(0.8)

def neutral():
    print("[TARS] Returning to neutral...")
    threaded_move(CHANNEL_TORSO, FORWARD_POS, BACKWARD_POS)
    time.sleep(1)
    threaded_move(CHANNEL_TORSO, NEUTRAL_POS, NEUTRAL_POS)
    threaded_move(CHANNEL_LEFT_ARM, LEFT_ARM_NEUTRAL_POS, LEFT_ARM_NEUTRAL_POS)
    threaded_move(CHANNEL_RIGHT_ARM, RIGHT_ARM_NEUTRAL_POS, RIGHT_ARM_NEUTRAL_POS)

# Gamepad Control Integration

def setup_gamepad(device_path="/dev/input/event6"):
    try:
        gamepad = InputDevice(device_path)
        print(f"[TARS] Gamepad detected: {gamepad.name}")
        return gamepad
    except FileNotFoundError:
        print(f"[ERROR] No gamepad found at {device_path}")
        exit(1)

def gamepad_control_loop(gamepad):
    print("[TARS] Listening for gamepad input...")
    for event in gamepad.read_loop():
        if event.type == ecodes.EV_KEY and event.value == 1: 
            if event.code == ecodes.BTN_NORTH:     # Y
                move_forward()
            elif event.code == ecodes.BTN_WEST:    # X
                turn_left()
            elif event.code == ecodes.BTN_EAST:    # B
                turn_right()
            elif event.code == ecodes.BTN_SOUTH:   # A
                neutral()

if __name__ == "__main__":
    neutral() 
    gamepad = setup_gamepad()
    gamepad_control_loop(gamepad)
