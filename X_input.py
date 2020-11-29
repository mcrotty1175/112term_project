# Modified from https://github.com/r4dian/Xbox-Controller-for-Python/blob/master/xinput.py
"""
A module for getting input from Microsoft XBox 360 controllers via the XInput library on Windows.

Adapted from Jason R. Coombs' code here:
http://pydoc.net/Python/jaraco.input/1.0.1/jaraco.input.win32.xinput/
under the MIT licence terms

Upgraded to Python 3
Modified to add deadzones, reduce noise, and support vibration
Only req is Pyglet 1.2alpha1 or higher:
pip install --upgrade http://pyglet.googlecode.com/archive/tip.zip 
"""

import ctypes
import sys
import time
import math
from operator import itemgetter, attrgetter
from itertools import count, starmap
from pyglet import event

# structs according to
# http://msdn.microsoft.com/en-gb/library/windows/desktop/ee417001%28v=vs.85%29.aspx


class XINPUT_GAMEPAD(ctypes.Structure):
    _fields_ = [
        ('buttons', ctypes.c_ushort),  # wButtons
        ('left_trigger', ctypes.c_ubyte),  # bLeftTrigger
        ('right_trigger', ctypes.c_ubyte),  # bLeftTrigger
        ('l_thumb_x', ctypes.c_short),  # sThumbLX
        ('l_thumb_y', ctypes.c_short),  # sThumbLY
        ('r_thumb_x', ctypes.c_short),  # sThumbRx
        ('r_thumb_y', ctypes.c_short),  # sThumbRy
    ]


class XINPUT_STATE(ctypes.Structure):
    _fields_ = [
        ('packet_number', ctypes.c_ulong),  # dwPacketNumber
        ('gamepad', XINPUT_GAMEPAD),  # Gamepad
    ]


class XINPUT_VIBRATION(ctypes.Structure):
    _fields_ = [("wLeftMotorSpeed", ctypes.c_ushort),
                ("wRightMotorSpeed", ctypes.c_ushort)]

class XINPUT_BATTERY_INFORMATION(ctypes.Structure):
    _fields_ = [("BatteryType", ctypes.c_ubyte),
                ("BatteryLevel", ctypes.c_ubyte)]

xinput = ctypes.windll.xinput1_4


def struct_dict(struct):
    """
    take a ctypes.Structure and return its field/value pairs
    as a dict.

    >>> 'buttons' in struct_dict(XINPUT_GAMEPAD)
    True
    >>> struct_dict(XINPUT_GAMEPAD)['buttons'].__class__.__name__
    'CField'
    """
    get_pair = lambda field_type: (
        field_type[0], getattr(struct, field_type[0]))
    return dict(list(map(get_pair, struct._fields_)))


def get_bit_values(number, size=32):
    """
    Get bit values as a list for a given number

    >>> get_bit_values(1) == [0]*31 + [1]
    True

    >>> get_bit_values(0xDEADBEEF)
    [1L, 1L, 0L, 1L, 1L, 1L, 1L, 0L, 1L, 0L, 1L, 0L, 1L, 1L, 0L, 1L, 1L, 0L, 1L, 1L, 1L, 1L, 1L, 0L, 1L, 1L, 1L, 0L, 1L, 1L, 1L, 1L]

    You may override the default word size of 32-bits to match your actual
    application.
    >>> get_bit_values(0x3, 2)
    [1L, 1L]

    >>> get_bit_values(0x3, 4)
    [0L, 0L, 1L, 1L]
    """
    res = list(gen_bit_values(number))
    res.reverse()
    # 0-pad the most significant bit
    res = [0] * (size - len(res)) + res
    return res


def gen_bit_values(number):
    """
    Return a zero or one for each bit of a numeric value up to the most
    significant 1 bit, beginning with the least significant bit.
    """
    number = int(number)
    while number:
        yield number & 0x1
        number >>= 1

ERROR_DEVICE_NOT_CONNECTED = 1167
ERROR_SUCCESS = 0


class XInputJoystick(event.EventDispatcher):
    """
    XInputJoystick

    A stateful wrapper, using pyglet event model, that binds to one
    XInput device and dispatches events when states change.

    Example:
    controller_one = XInputJoystick(0)
    """
    max_devices = 2

    def __init__(self, device_number, normalize_axes=True):
        values = vars()
        del values['self']
        self.__dict__.update(values)

        super(XInputJoystick, self).__init__()

        self._last_state = self.get_state()
        self.received_packets = 0
        self.missed_packets = 0


        # Set the method that will be called to normalize
        #  the values for analog axis.
        choices = [self.translate_identity, self.translate_using_data_size]
        self.translate = choices[normalize_axes]

    def translate_using_data_size(self, value, data_size):
        # normalizes analog data to [0,1] for unsigned data
        #  and [-0.5,0.5] for signed data
        data_bits = 8 * data_size
        return float(value) / (2 ** data_bits - 1)

    def translate_identity(self, value, data_size=None):
        return value

    def get_state(self):
        "Get the state of the controller represented by this object"
        state = XINPUT_STATE()
        res = xinput.XInputGetState(self.device_number, ctypes.byref(state))
        if res == ERROR_SUCCESS:
            return state
        if res != ERROR_DEVICE_NOT_CONNECTED:
            raise Exception(
                "Unknown error %d attempting to get state of device %d" % (res, self.device_number))
        # else return None (device is not connected)

    def is_connected(self):
        return self._last_state is not None

    @staticmethod
    def enumerate_devices():
        "Returns the devices that are connected"
        devices = list(
            map(XInputJoystick, list(range(XInputJoystick.max_devices))))
        return [d for d in devices if d.is_connected()]

    def set_vibration(self, left_motor, right_motor):
        "Control the speed of both motors seperately"
        # Set up function argument types and return type
        XInputSetState = xinput.XInputSetState
        XInputSetState.argtypes = [ctypes.c_uint, ctypes.POINTER(XINPUT_VIBRATION)]
        XInputSetState.restype = ctypes.c_uint

        vibration = XINPUT_VIBRATION(
            int(left_motor * 65535), int(right_motor * 65535))
        XInputSetState(self.device_number, ctypes.byref(vibration))

    def dispatch_events(self):
        "The main event loop for a joystick"
        change = None
        state = self.get_state()
        if not state:
            raise Exception(
                "Joystick %d is not connected" % self.device_number)
        if state.packet_number != self._last_state.packet_number:
            # state has changed, handle the change
            self.update_packet_count(state)
            change = self.handle_changed_state(state)
        self._last_state = state
        return change

    def update_packet_count(self, state):
        "Keep track of received and missed packets for performance tuning"
        self.received_packets += 1
        missed_packets = state.packet_number - \
            self._last_state.packet_number - 1
        if missed_packets:
            self.dispatch_event('on_missed_packet', missed_packets)
        self.missed_packets += missed_packets

    def handle_changed_state(self, state):
        "Dispatch various events as a result of the state changing"
        self.dispatch_event('on_state_changed', state)
        analogInput = self.dispatch_axis_events(state)
        digitalInput = self.dispatch_button_events(state)
        return digitalInput, analogInput

    def dispatch_axis_events(self, state):
        # axis fields are everything but the buttons
        axis_fields = dict(XINPUT_GAMEPAD._fields_)
        axis_fields.pop('buttons')
        for axis, type in list(axis_fields.items()):
            old_val = getattr(self._last_state.gamepad, axis)
            new_val = getattr(state.gamepad, axis)
            data_size = ctypes.sizeof(type)
            old_val = self.translate(old_val, data_size)
            new_val = self.translate(new_val, data_size)

            # an attempt to add deadzones and dampen noise
            # done by feel rather than following
            # http://msdn.microsoft.com/en-gb/library/windows/desktop/ee417001%28v=vs.85%29.aspx#dead_zone
            # ags, 2014-07-01
            if ( old_val != new_val and
                (abs(new_val) > 0.0800000000000000) and
                (abs(old_val - new_val) > 0.0000000050000000) or
                (axis == 'right_trigger' or axis == 'left_trigger') and 
                new_val == 0 and abs(old_val - new_val) > 0.00000000500000000):
                self.dispatch_event('on_axis', axis, new_val)
                return (axis, new_val)
            elif abs(new_val) >= 0.40:
                self.dispatch_event('on_axis', axis, new_val)
                return (axis, new_val)

    def dispatch_button_events(self, state):
        changed = state.gamepad.buttons ^ self._last_state.gamepad.buttons
        changed = get_bit_values(changed, 16)
        buttons_state = get_bit_values(state.gamepad.buttons, 16)
        changed.reverse()
        buttons_state.reverse()
        button_numbers = count(1)
        changed_buttons = list(
            filter(itemgetter(0), list(zip(changed, button_numbers, buttons_state))))
        tuple(starmap(self.dispatch_button_event, changed_buttons))
        if changed_buttons != []:
            return changed_buttons[0]
        

    def dispatch_button_event(self, changed, number, pressed):
        self.dispatch_event('on_button', number, pressed)
        if pressed == 1:
            return number


    # stub methods for event handlers
    def on_state_changed(self, state):
        pass

    def on_axis(self, axis, value):
        pass

    def on_button(self, button, pressed):
        pass

    def on_missed_packet(self, number):
        pass

list(map(XInputJoystick.register_event_type, [
    'on_state_changed',
    'on_axis',
    'on_button',
    'on_missed_packet',
]))

def sampleJoystick(inputIndex):
    """
    Grab a specific gamepad, logging changes to the screen.
    L & R analogue triggers set the vibration motor speed.
    """
    joysticks = XInputJoystick.enumerate_devices()
    device_numbers = list(map(attrgetter('device_number'), joysticks))

    print('found %d devices: %s' % (len(joysticks), device_numbers))

    if not joysticks:
        sys.exit(0)

    j = joysticks[inputIndex]
    print('using %d' % j.device_number)

    buttonMap = {
            1: "Up",
            2: "Down",
            3: "Left",
            4: "Right",
            5: None,
            6: None,
            7: None,
            8: None,
            9: "L_Bumper",
            10: "R_Bumper",
            11: None,
            12: None,
            13: "A",
            14: "B",
            15: "X",
            16: "Y",
            None:None
        }

    @j.event
    def on_button(button, pressed):
        if pressed == 1:
            # print(buttonMap[button])
            return button
        else:
            pass

    left_speed = 0
    right_speed = 0

    @j.event
    def on_axis(axis, value):
        left_speed = 0
        right_speed = 0

        '''
        # Makes controller vibrate when pushing triggers
        if axis == "left_trigger":
            left_speed = value
        elif axis == "right_trigger":
            right_speed = value
        j.set_vibration(left_speed, right_speed)
        '''
        return (axis, value)

    while True:
        yield j.dispatch_events()


if __name__ == "__main__":
    player1 = sampleJoystick(0)
    # player2 = sampleJoystick(1)
    buttonMap = {
            1: "Up",
            2: "Down",
            3: "Left",
            4: "Right",
            5: "Menu",
            6: "View",
            7: "L_Stick",
            8: "R_Stick",
            9: "L_Bumper",
            10: "R_Bumper",
            11: None,
            12: None,
            13: "A",
            14: "B",
            15: "X",
            16: "Y",
            None:None
        }
    while True:
        p1 = next(player1)
        if p1 != None:
            # print(p1)
            if p1[0] != None and p1[0][2]:
                print("Player 1:", buttonMap[p1[0][1]])
            if p1[1] != None:
                print("Player 1:", p1[1])
        # p2 = next(player2)
        # if p2 != None:
        #     for elem in p2:
        #         if elem != None:
        #             print("Player 2:", buttonMap[elem])
