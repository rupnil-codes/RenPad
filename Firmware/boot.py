import time
import board
import busio
import usb_hid
import storage
import supervisor
import displayio
import adafruit_ssd1306

from kmk.kmk_keyboard import KMKKeyboard
from kmk.keys import KC
from kmk.scanners import DiodeOrientation
from kmk.extensions.rgb import RGB
from kmk.extensions.display import Display, TextEntry

usb_hid.enable((
    usb_hid.Device.KEYBOARD,
    usb_hid.Device.CONSUMER_CONTROL,
))

storage.remount("/", readonly=False)

supervisor.set_usb_identification(
    manufacturer="Rz3neri",
    product="RenPad"
)

keyboard = KMKKeyboard()

keyboard.col_pins = (board.GP26, board.GP27, board.GP28, board.GP29)
keyboard.row_pins = (board.GP6, board.GP7)
keyboard.diode_orientation = DiodeOrientation.ROW2COL

rgb = RGB(
    pixel_pin=board.GP3,
    num_pixels=5,
    hue_default=170,
    sat_default=255,
    val_default=80,
)
keyboard.extensions.append(rgb)

displayio.release_displays()
i2c = busio.I2C(board.GP1, board.GP0)
oled = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c, addr=0x3C)

last_key = ""
last_key_time = 0
DISPLAY_TIME = 3

def key_text():
    if time.monotonic() - last_key_time < DISPLAY_TIME:
        return last_key
    return ""

display = Display(
    display=oled,
    entries=[
        TextEntry(text="RenPad", x=0, y=0),
        TextEntry(text=key_text, x=0, y=16),
    ],
)
keyboard.extensions.append(display)

keyboard.keymap = [[
    KC.LGUI(KC.V),
    KC.LALT(KC.TAB),
    KC.LGUI(KC.TAB),
    KC.LGUI(KC.E),

    KC.LCTL(KC.LSHIFT(KC.ESC)),
    KC.LGUI(KC.LCTL(KC.D)),
    KC.LGUI(KC.LCTL(KC.LEFT)),
    KC.LGUI(KC.LCTL(KC.RIGHT)),
]]

key_names = {
    keyboard.keymap[0][0]: "Clipboard",
    keyboard.keymap[0][1]: "Switch App",
    keyboard.keymap[0][2]: "Task View",
    keyboard.keymap[0][3]: "Explorer",
    keyboard.keymap[0][4]: "TaskMgr",
    keyboard.keymap[0][5]: "New Desk",
    keyboard.keymap[0][6]: "Desk Left",
    keyboard.keymap[0][7]: "Desk Right",
}

@keyboard.before_hid_send
def show_pressed_key(keyboard):
    global last_key, last_key_time
    if keyboard.keys_pressed:
        key = list(keyboard.keys_pressed)[0]
        if key in key_names:
            last_key = key_names[key]
        else:
            last_key = "Key"
        last_key_time = time.monotonic()

@keyboard.after_hid_send
def react_to_keys(keyboard):
    if keyboard.keys_pressed:
        rgb.increase_hue()

keyboard.go()
