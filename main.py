from pyjoycon import ButtonEventJoyCon, get_L_id, get_R_id
import pygame
from pynput.mouse import Button, Controller
from pynput import keyboard
from screeninfo import get_monitors

joycon_id = get_L_id()
joycon = ButtonEventJoyCon(*joycon_id)

t = int(1000/120)

center_x = 2148 # 1338, 1416
center_y = 1840 # 1132, 1110
deadzone = 250

def apply_deadzone(val, center, deadzone):
    if abs(val - center) < deadzone:
        return center
    return val

def bind_to_range(n, lower, upper):
    if n < lower:
        return lower
    if n > upper:
        return upper
    return n

mouse = Controller()
kb = keyboard.Controller()

scroll_mode = False

state = 0
left_x = 0
right_x = 0
up_y = 0
down_y = 0

x_maximum = 0
y_maximum = 0

'''while state < 5:
    pygame.time.wait(t)
    for event_type, status in joycon.events():
        if event_type == 'zl' and status:
            if state == 0:
                center_x = joycon.get_stick_left_horizontal()
                center_y = joycon.get_stick_left_vertical()
            elif state == 1:
                up_y = joycon.get_stick_left_vertical()
            elif state == 2:
                right_x = joycon.get_stick_left_horizontal()
            elif state == 3:
                down_y = joycon.get_stick_left_vertical()
            else:
                left_x = joycon.get_stick_left_horizontal()
            state += 1
            
x_maximum = min(abs(center_x - left_x), abs(center_x - right_x))
y_maximum = min(abs(center_y - down_y), abs(center_y - up_y))
'''

center_x = 1905
center_y = 2298
x_maximum = 1151
y_maximum = 1042

range_min = 10000
range_max = -10000

sample_frames = 100

g_at_rest_x = 0
g_at_rest_y = 0
g_at_rest_z = 0

monitor = get_monitors()[0]
monitor_width = monitor.width
monitor_height = monitor.height

for frame in range(sample_frames):
    gx = joycon.get_gyro_x()
    g_at_rest_x += gx
    range_min = min(range_min, gx)
    range_max = max(range_max, gx)
    g_at_rest_y += joycon.get_gyro_y()
    g_at_rest_z += joycon.get_gyro_z()
    pygame.time.wait(t)

g_at_rest_x = int(g_at_rest_x/sample_frames)
g_at_rest_y = int(g_at_rest_y/sample_frames)
g_at_rest_z = int(g_at_rest_z/sample_frames)

# gyro_deadzone = range_max - range_min
default_gyro_deadzone = 40
button_press_gyro_deadzone = 100
gyro_deadzone = default_gyro_deadzone
# print(gyro_deadzone)

button_press_timeout_timer = -1

print(f'center_x = {center_x}\ncenter_y = {center_y}\nx_maximum = {x_maximum}\ny_maximum = {y_maximum}')

while 1:
    time = pygame.time.get_ticks()
    if time > button_press_timeout_timer:
        gyro_deadzone = default_gyro_deadzone
    
    # x - wrist turning
    # y - wrist left/right
    # z - wrist up/down
    gyro_cursor_x = joycon.get_gyro_z() - g_at_rest_z
    gyro_cursor_x = apply_deadzone(gyro_cursor_x, 0, gyro_deadzone)

    gyro_cursor_y = joycon.get_gyro_y() - g_at_rest_y
    gyro_cursor_y = apply_deadzone(gyro_cursor_y, 0, gyro_deadzone)
    # print(z, gy)
    gyro_cursor_x = -gyro_cursor_x / 1000
    gyro_cursor_y = gyro_cursor_y / 1000
    x, y = mouse.position
    x += gyro_cursor_x * 50
    y += gyro_cursor_y * 50
    x = bind_to_range(x, 0, monitor_width - 1)
    y = bind_to_range(y, 0, monitor_height - 1)
    # print(gyro_cursor_x, gyro_cursor_y)

    mouse.position = x, y

    pygame.time.wait(t)

    for event_type, status in joycon.events():
        button_press_timeout_timer = time + 200
        gyro_deadzone = button_press_gyro_deadzone
        if event_type == 'zl':
            if status:
                mouse.press(Button.left)
            else:
                mouse.release(Button.left)
        if event_type == 'l':
            if status:
                mouse.press(Button.right)
            else:
                mouse.release(Button.right)
        if event_type == 'down' and status:
            with kb.pressed(keyboard.Key.cmd):
                kb.press(keyboard.Key.tab)
                kb.release(keyboard.Key.tab)
        if event_type == 'up':
            with kb.pressed(keyboard.Key.ctrl_l):
                kb.press(keyboard.Key.left)
                kb.release(keyboard.Key.left)
        print(event_type, status)
    
    stick_x = joycon.get_stick_left_horizontal()
    stick_y = joycon.get_stick_left_vertical()

    stick_x = apply_deadzone(stick_x, center_x, deadzone)
    stick_y = apply_deadzone(stick_y, center_y, deadzone)

    stick_x = stick_x - center_x
    stick_x = stick_x / x_maximum
    stick_y = center_y - stick_y
    stick_y = stick_y / y_maximum
    
    stick_x = bind_to_range(stick_x, -1, 1)
    stick_y = bind_to_range(stick_y, -1, 1)

    if stick_y > 0.6:
        kb.press(keyboard.Key.down)
        kb.release(keyboard.Key.down)
    elif stick_y < -0.6:
        kb.press(keyboard.Key.up)
        kb.release(keyboard.Key.up)

    if stick_x > 0.6:
        kb.press(keyboard.Key.right)
        kb.release(keyboard.Key.right)
    elif stick_x < -0.6:
        kb.press(keyboard.Key.left)
        kb.release(keyboard.Key.left)

    if scroll_mode and (stick_x or stick_y):
        mouse.scroll(stick_x, stick_y)
    else:
        scale = 30
        if stick_x * stick_x + stick_y * stick_y < 0.64:
            scale = 8
            
        x, y = mouse.position
        x += scale * stick_x
        y += scale * stick_y
        #mouse.position = (x, y)