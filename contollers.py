# Based on the Inputs module
# Something Something Educational Purposes
# Please don't sue me

# Copyright (c) 2016, 2018: Zeth
# All rights reserved.
#
# BSD Licence
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#
#     * Neither the name of the copyright holder nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import os
import sys
import io
import glob
import struct
import platform
import math
import time
import codecs
from warnings import warn
from itertools import count
from operator import itemgetter
from multiprocessing import Process, Pipe
import ctypes

__version__ = "mcrottyTP"

WIN = True if platform.system() == 'Windows' else False
MAC = True if platform.system() == 'Darwin' else False
NIX = True if platform.system() == 'Linux' else False

if WIN:
    # pylint: disable=wrong-import-position
    import ctypes.wintypes
    DWORD = ctypes.wintypes.DWORD
    HANDLE = ctypes.wintypes.HANDLE
    WPARAM = ctypes.wintypes.WPARAM
    LPARAM = ctypes.wintypes.WPARAM
    MSG = ctypes.wintypes.MSG
else:
    DWORD = ctypes.c_ulong
    HANDLE = ctypes.c_void_p
    WPARAM = ctypes.c_ulonglong
    LPARAM = ctypes.c_ulonglong
    MSG = ctypes.Structure

if NIX:
    from fcntl import ioctl

OLD = sys.version_info < (3, 4)

PERMISSIONS_ERROR_TEXT = (
    '''The user (that this program is being run as) does 
    not have permission to access the input events, 
    check groups and permissions, for example, on 
    Debian, the user needs to be in the input group.''')

# Standard event format for most devices.
# long, long, unsigned short, unsigned short, int
EVENT_FORMAT = str('llHHi')

EVENT_SIZE = struct.calcsize(EVENT_FORMAT)


def chunks(raw):
    """Yield successive EVENT_SIZE sized chunks from raw."""
    for i in range(0, len(raw), EVENT_SIZE):
        yield struct.unpack(EVENT_FORMAT, raw[i:i+EVENT_SIZE])


if OLD:
    def iter_unpack(raw):
        """Yield successive EVENT_SIZE chunks from message."""
        return chunks(raw)
else:
    def iter_unpack(raw):
        """Yield successive EVENT_SIZE chunks from message."""
        return struct.iter_unpack(EVENT_FORMAT, raw)


def convert_timeval(seconds_since_epoch):
    """Convert time into C style timeval."""
    frac, whole = math.modf(seconds_since_epoch)
    microseconds = math.floor(frac * 1000000)
    seconds = math.floor(whole)
    return seconds, microseconds

XINPUT_MAPPING = (
    (1, 0x11),
    (2, 0x11),
    (3, 0x10),
    (4, 0x10),
    (5, 0x13a),
    (6, 0x13b),
    (7, 0x13d),
    (8, 0x13e),
    (9, 0x136),
    (10, 0x137),
    (13, 0x130),
    (14, 0x131),
    (15, 0x134),
    (16, 0x133),
    (17, 0x11),
    ('l_thumb_x', 0x00),
    ('l_thumb_y', 0x01),
    ('left_trigger', 0x02),
    ('r_thumb_x', 0x03),
    ('r_thumb_y', 0x04),
    ('right_trigger', 0x05),
)

XINPUT_DLL_NAMES = (
    "XInput1_4.dll",
    "XInput9_1_0.dll",
    "XInput1_3.dll",
    "XInput1_2.dll",
    "XInput1_1.dll"
)

XINPUT_ERROR_DEVICE_NOT_CONNECTED = 1167
XINPUT_ERROR_SUCCESS = 0

DEVICE_PROPERTIES = (
    (0x00, "INPUT_PROP_POINTER"),  # needs a pointer
    (0x01, "INPUT_PROP_DIRECT"),  # direct input devices
    (0x02, "INPUT_PROP_BUTTONPAD"),  # has button(s) under pad
    (0x03, "INPUT_PROP_SEMI_MT"),  # touch rectangle only
    (0x04, "INPUT_PROP_TOPBUTTONPAD"),  # softbuttons at top of pad
    (0x05, "INPUT_PROP_POINTING_STICK"),  # is a pointing stick
    (0x06, "INPUT_PROP_ACCELEROMETER"),  # has accelerometer
    (0x1f, "INPUT_PROP_MAX"),
    (0x1f + 1, "INPUT_PROP_CNT"))


SYNCHRONIZATION_EVENTS = (
    (0, "SYN_REPORT"),
    (1, "SYN_CONFIG"),
    (2, "SYN_MT_REPORT"),
    (3, "SYN_DROPPED"),
    (0xf, "SYN_MAX"),
    (0xf+1, "SYN_CNT"))


WINCODES = (
    (0x01, 0x110),  # Left mouse button
    (0x02, 0x111),  # Right mouse button
    (0x03, 0),  # Control-break processing
    (0x04, 0x112),  # Middle mouse button (three-button mouse)
    (0x05, 0x113),  # X1 mouse button
    (0x06, 0x114),  # X2 mouse button
    (0x07, 0),  # Undefined
    (0x08, 14),  # BACKSPACE key
    (0x09, 15),  # TAB key
    (0x0A, 0),  # Reserved
    (0x0B, 0),  # Reserved
    (0x0C, 0x163),  # CLEAR key
    (0x0D, 28),  # ENTER key
    (0x0E, 0),  # Undefined
    (0x0F, 0),  # Undefined
    (0x10, 42),  # SHIFT key
    (0x11, 29),  # CTRL key
    (0x12, 56),  # ALT key
    (0x13, 119),  # PAUSE key
    (0x14, 58),  # CAPS LOCK key
    (0x15, 90),  # IME Kana mode
    (0x15, 91),  # IME Hanguel mode (maintained for compatibility; use
                 # VK_HANGUL)
    (0x15, 91),  # IME Hangul mode
    (0x16, 0),  # Undefined
    (0x17, 92),  # IME Junja mode - These all need to be fixed
    (0x18, 93),  # IME final mode - By someone who
    (0x19, 94),  # IME Hanja mode - Knows how
    (0x19, 95),  # IME Kanji mode - Japanese Keyboards work
    (0x1A, 0),  # Undefined
    (0x1B, 1),  # ESC key
    (0x1C, 0),  # IME convert
    (0x1D, 0),  # IME nonconvert
    (0x1E, 0),  # IME accept
    (0x1F, 0),  # IME mode change request
    (0x20, 57),  # SPACEBAR
    (0x21, 104),  # PAGE UP key
    (0x22, 109),  # PAGE DOWN key
    (0x23, 107),  # END key
    (0x24, 102),  # HOME key
    (0x25, 105),  # LEFT ARROW key
    (0x26, 103),  # UP ARROW key
    (0x27, 106),  # RIGHT ARROW key
    (0x28, 108),  # DOWN ARROW key
    (0x29, 0x161),  # SELECT key
    (0x2A, 210),  # PRINT key
    (0x2B, 28),  # EXECUTE key
    (0x2C, 99),  # PRINT SCREEN key
    (0x2D, 110),  # INS key
    (0x2E, 111),  # DEL key
    (0x2F, 138),  # HELP key
    (0x30, 11),  # 0 key
    (0x31, 2),  # 1 key
    (0x32, 3),  # 2 key
    (0x33, 4),  # 3 key
    (0x34, 5),  # 4 key
    (0x35, 6),  # 5 key
    (0x36, 7),  # 6 key
    (0x37, 8),  # 7 key
    (0x38, 9),  # 8 key
    (0x39, 10),  # 9 key
    #  (0x3A-40, 0),  # Undefined
    (0x41, 30),  # A key
    (0x42, 48),  # B key
    (0x43, 46),  # C key
    (0x44, 32),  # D key
    (0x45, 18),  # E key
    (0x46, 33),  # F key
    (0x47, 34),  # G key
    (0x48, 35),  # H key
    (0x49, 23),  # I key
    (0x4A, 36),  # J key
    (0x4B, 37),  # K key
    (0x4C, 38),  # L key
    (0x4D, 50),  # M key
    (0x4E, 49),  # N key
    (0x4F, 24),  # O key
    (0x50, 25),  # P key
    (0x51, 16),  # Q key
    (0x52, 19),  # R key
    (0x53, 31),  # S key
    (0x54, 20),  # T key
    (0x55, 22),  # U key
    (0x56, 47),  # V key
    (0x57, 17),  # W key
    (0x58, 45),  # X key
    (0x59, 21),  # Y key
    (0x5A, 44),  # Z key
    (0x5B, 125),  # Left Windows key (Natural keyboard)
    (0x5C, 126),  # Right Windows key (Natural keyboard)
    (0x5D, 139),  # Applications key (Natural keyboard)
    (0x5E, 0),  # Reserved
    (0x5F, 142),  # Computer Sleep key
    (0x60, 82),  # Numeric keypad 0 key
    (0x61, 79),  # Numeric keypad 1 key
    (0x62, 80),  # Numeric keypad 2 key
    (0x63, 81),  # Numeric keypad 3 key
    (0x64, 75),  # Numeric keypad 4 key
    (0x65, 76),  # Numeric keypad 5 key
    (0x66, 77),  # Numeric keypad 6 key
    (0x67, 71),  # Numeric keypad 7 key
    (0x68, 72),  # Numeric keypad 8 key
    (0x69, 73),  # Numeric keypad 9 key
    (0x6A, 55),  # Multiply key
    (0x6B, 78),  # Add key
    (0x6C, 96),  # Separator key
    (0x6D, 74),  # Subtract key
    (0x6E, 83),  # Decimal key
    (0x6F, 98),  # Divide key
    (0x70, 59),  # F1 key
    (0x71, 60),  # F2 key
    (0x72, 61),  # F3 key
    (0x73, 62),  # F4 key
    (0x74, 63),  # F5 key
    (0x75, 64),  # F6 key
    (0x76, 65),  # F7 key
    (0x77, 66),  # F8 key
    (0x78, 67),  # F9 key
    (0x79, 68),  # F10 key
    (0x7A, 87),  # F11 key
    (0x7B, 88),  # F12 key
    (0x7C, 183),  # F13 key
    (0x7D, 184),  # F14 key
    (0x7E, 185),  # F15 key
    (0x7F, 186),  # F16 key
    (0x80, 187),  # F17 key
    (0x81, 188),  # F18 key
    (0x82, 189),  # F19 key
    (0x83, 190),  # F20 key
    (0x84, 191),  # F21 key
    (0x85, 192),  # F22 key
    (0x86, 192),  # F23 key
    (0x87, 194),  # F24 key
    #  (0x88-8F, 0),  # Unassigned
    (0x90, 69),  # NUM LOCK key
    (0x91, 70),  # SCROLL LOCK key
    #  (0x92-96, 0),  # OEM specific
    #  (0x97-9F, 0),  # Unassigned
    (0xA0, 42),  # Left SHIFT key
    (0xA1, 54),  # Right SHIFT key
    (0xA2, 29),  # Left CONTROL key
    (0xA3, 97),  # Right CONTROL key
    (0xA4, 125),  # Left MENU key
    (0xA5, 126),  # Right MENU key
    (0xA6, 158),  # Browser Back key
    (0xA7, 159),  # Browser Forward key
    (0xA8, 173),  # Browser Refresh key
    (0xA9, 128),  # Browser Stop key
    (0xAA, 217),  # Browser Search key
    (0xAB, 0x16c),  # Browser Favorites key
    (0xAC, 150),  # Browser Start and Home key
    (0xAD, 113),  # Volume Mute key
    (0xAE, 114),  # Volume Down key
    (0xAF, 115),  # Volume Up key
    (0xB0, 163),  # Next Track key
    (0xB1, 165),  # Previous Track key
    (0xB2, 166),  # Stop Media key
    (0xB3, 164),  # Play/Pause Media key
    (0xB4, 155),  # Start Mail key
    (0xB5, 0x161),  # Select Media key
    (0xB6, 148),  # Start Application 1 key
    (0xB7, 149),  # Start Application 2 key
    #  (0xB8-B9, 0),  # Reserved
    (0xBA, 39),  # Used for miscellaneous characters; it can vary by keyboard.
    (0xBB, 13),  # For any country/region, the '+' key
    (0xBC, 51),  # For any country/region, the ',' key
    (0xBD, 12),  # For any country/region, the '-' key
    (0xBE, 52),  # For any country/region, the '.' key
    (0xBF, 53),  # Slash
    (0xC0, 40),  # Apostrophe
    #  (0xC1-D7, 0),  # Reserved
    #  (0xD8-DA, 0),  # Unassigned
    (0xDB, 26),  # [
    (0xDC, 86),  # \
    (0xDD, 27),  # ]
    (0xDE, 43),  # '
    (0xDF, 119),  # VK_OFF - What's that?
    (0xE0, 0),  # Reserved
    (0xE1, 0),  # OEM Specific
    (0xE2, 43),  # Either the angle bracket key or the backslash key
                 # on the RT 102-key keyboard (0xE3-E4, 0), # OEM
                 # specific
    (0xE5, 0),  # IME PROCESS key
    (0xE6, 0),  # OEM specific
    (0xE7, 0),  # Used to pass Unicode characters as if they were
                # keystrokes. The VK_PACKET key is the low word of a
                # 32-bit Virtual Key value used for non-keyboard input
                # methods. For more information, see Remark in
                # KEYBDINPUT, SendInput, WM_KEYDOWN, and WM_KEYUP
    (0xE8, 0),  # Unassigned
    #  (0xE9-F5, 0),  # OEM specific
    (0xF6, 0),  # Attn key
    (0xF7, 0),  # CrSel key
    (0xF8, 0),  # ExSel key
    (0xF9, 222),  # Erase EOF key
    (0xFA, 207),  # Play key
    (0xFB, 0x174),  # Zoom key
    (0xFC, 0),  # Reserved
    (0xFD, 0x19b),  # PA1 key
    (0xFE, 0x163),   # Clear key
    (0xFF, 185)
)

MAC_EVENT_CODES = (
    # NSLeftMouseDown Quartz.kCGEventLeftMouseDown
    (1, ("Key", 0x110, 1, 589825)),
    # NSLeftMouseUp Quartz.kCGEventLeftMouseUp
    (2, ("Key", 0x110, 0, 589825)),
    # NSRightMouseDown Quartz.kCGEventRightMouseDown
    (3, ("Key", 0x111, 1, 589826)),
    # NSRightMouseUp Quartz.kCGEventRightMouseUp
    (4, ("Key", 0x111, 0, 589826)),
    (5, (None, 0, 0, 0)),    # NSMouseMoved Quartz.kCGEventMouseMoved
    (6, (None, 0, 0, 0)),  # NSLeftMouseDragged Quartz.kCGEventLeftMouseDragged
    # NSRightMouseDragged Quartz.kCGEventRightMouseDragged
    (7, (None, 0, 0, 0)),
    (8, (None, 0, 0, 0)),    # NSMouseEntered
    (9, (None, 0, 0, 0)),    # NSMouseExited
    (10, (None, 0, 0, 0)),   # NSKeyDown
    (11, (None, 0, 0, 0)),   # NSKeyUp
    (12, (None, 0, 0, 0)),   # NSFlagsChanged
    (13, (None, 0, 0, 0)),   # NSAppKitDefined
    (14, (None, 0, 0, 0)),   # NSSystemDefined
    (15, (None, 0, 0, 0)),   # NSApplicationDefined
    (16, (None, 0, 0, 0)),   # NSPeriodic
    (17, (None, 0, 0, 0)),   # NSCursorUpdate
    (22, (None, 0, 0, 0)),   # NSScrollWheel Quartz.kCGEventScrollWheel
    (23, (None, 0, 0, 0)),   # NSTabletPoint Quartz.kCGEventTabletPointer
    (24, (None, 0, 0, 0)),   # NSTabletProximity Quartz.kCGEventTabletProximity
    (25, (None, 0, 0, 0)),   # NSOtherMouseDown Quartz.kCGEventOtherMouseDown
    (25.2, ("Key", 0x112, 1, 589827)),   # BTN_MIDDLE
    (25.3, ("Key", 0x113, 1, 589828)),   # BTN_SIDE
    (25.4, ("Key", 0x114, 1, 589829)),   # BTN_EXTRA
    (26, (None, 0, 0, 0)),   # NSOtherMouseUp Quartz.kCGEventOtherMouseUp
    (26.2, ("Key", 0x112, 0, 589827)),   # BTN_MIDDLE
    (26.3, ("Key", 0x113, 0, 589828)),   # BTN_SIDE
    (26.4, ("Key", 0x114, 0, 589829)),   # BTN_EXTRA
    (27, (None, 0, 0, 0)),   # NSOtherMouseDragged
    (29, (None, 0, 0, 0)),   # NSEventTypeGesture
    (30, (None, 0, 0, 0)),   # NSEventTypeMagnify
    (31, (None, 0, 0, 0)),   # NSEventTypeSwipe
    (18, (None, 0, 0, 0)),   # NSEventTypeRotate
    (19, (None, 0, 0, 0)),   # NSEventTypeBeginGesture
    (20, (None, 0, 0, 0)),   # NSEventTypeEndGesture
    (27, (None, 0, 0, 0)),   # Quartz.kCGEventOtherMouseDragged
    (32, (None, 0, 0, 0)),   # NSEventTypeSmartMagnify
    (33, (None, 0, 0, 0)),   # NSEventTypeQuickLook
    (34, (None, 0, 0, 0)),   # NSEventTypePressure
)

MAC_KEYS = (
    (0x00, 30),  # kVK_ANSI_A
    (0x01, 31),  # kVK_ANSI_S    (0x02, 32),  # kVK_ANSI_D
    (0x03, 33),  # kVK_ANSI_F
    (0x04, 35),  # kVK_ANSI_H
    (0x05, 34),  # kVK_ANSI_G
    (0x06, 44),  # kVK_ANSI_Z
    (0x07, 45),  # kVK_ANSI_X
    (0x08, 46),  # kVK_ANSI_C
    (0x09, 47),  # kVK_ANSI_V
    (0x0B, 48),  # kVK_ANSI_B
    (0x0C, 16),  # kVK_ANSI_Q
    (0x0D, 17),  # kVK_ANSI_W
    (0x0E, 18),  # kVK_ANSI_E
    (0x0F, 33),  # kVK_ANSI_R
    (0x10, 21),  # kVK_ANSI_Y
    (0x11, 20),  # kVK_ANSI_T
    (0x12, 2),  # kVK_ANSI_1
    (0x13, 3),  # kVK_ANSI_2
    (0x14, 4),  # kVK_ANSI_3
    (0x15, 5),  # kVK_ANSI_4
    (0x16, 7),  # kVK_ANSI_6
    (0x17, 6),  # kVK_ANSI_5
    (0x18, 13),  # kVK_ANSI_Equal
    (0x19, 10),  # kVK_ANSI_9
    (0x1A, 8),  # kVK_ANSI_7
    (0x1B, 12),  # kVK_ANSI_Minus
    (0x1C, 9),  # kVK_ANSI_8
    (0x1D, 11),  # kVK_ANSI_0
    (0x1E, 27),  # kVK_ANSI_RightBracket
    (0x1F, 24),  # kVK_ANSI_O
    (0x20, 22),  # kVK_ANSI_U
    (0x21, 26),  # kVK_ANSI_LeftBracket
    (0x22, 23),  # kVK_ANSI_I
    (0x23, 25),  # kVK_ANSI_P
    (0x25, 38),  # kVK_ANSI_L
    (0x26, 36),  # kVK_ANSI_J
    (0x27, 40),  # kVK_ANSI_Quote
    (0x28, 37),  # kVK_ANSI_K
    (0x29, 39),  # kVK_ANSI_Semicolon
    (0x2A, 43),  # kVK_ANSI_Backslash
    (0x2B, 51),  # kVK_ANSI_Comma
    (0x2C, 53),  # kVK_ANSI_Slash
    (0x2D, 49),  # kVK_ANSI_N
    (0x2E, 50),  # kVK_ANSI_M
    (0x2F, 52),  # kVK_ANSI_Period
    (0x32, 41),  # kVK_ANSI_Grave
    (0x41, 83),  # kVK_ANSI_KeypadDecimal
    (0x43, 55),  # kVK_ANSI_KeypadMultiply
    (0x45, 78),  # kVK_ANSI_KeypadPlus
    (0x47, 69),  # kVK_ANSI_KeypadClear
    (0x4B, 98),  # kVK_ANSI_KeypadDivide
    (0x4C, 96),  # kVK_ANSI_KeypadEnter
    (0x4E, 74),  # kVK_ANSI_KeypadMinus
    (0x51, 117),  # kVK_ANSI_KeypadEquals
    (0x52, 82),  # kVK_ANSI_Keypad0
    (0x53, 79),  # kVK_ANSI_Keypad1
    (0x54, 80),  # kVK_ANSI_Keypad2
    (0x55, 81),  # kVK_ANSI_Keypad3
    (0x56, 75),  # kVK_ANSI_Keypad4
    (0x57, 76),  # kVK_ANSI_Keypad5
    (0x58, 77),  # kVK_ANSI_Keypad6
    (0x59, 71),  # kVK_ANSI_Keypad7
    (0x5B, 72),  # kVK_ANSI_Keypad8
    (0x5C, 73),  # kVK_ANSI_Keypad9
    (0x24, 28),  # kVK_Return
    (0x30, 15),  # kVK_Tab
    (0x31, 57),  # kVK_Space
    (0x33, 111),  # kVK_Delete
    (0x35, 1),  # kVK_Escape
    (0x37, 125),  # kVK_Command
    (0x38, 42),  # kVK_Shift
    (0x39, 58),  # kVK_CapsLock
    (0x3A, 56),  # kVK_Option
    (0x3B, 29),  # kVK_Control
    (0x3C, 54),  # kVK_RightShift
    (0x3D, 100),  # kVK_RightOption
    (0x3E, 126),  # kVK_RightControl
    (0x36, 126),  # Right Meta
    (0x3F, 0x1d0),  # kVK_Function
    (0x40, 187),  # kVK_F17
    (0x48, 115),  # kVK_VolumeUp
    (0x49, 114),  # kVK_VolumeDown
    (0x4A, 113),  # kVK_Mute
    (0x4F, 188),  # kVK_F18
    (0x50, 189),  # kVK_F19
    (0x5A, 190),  # kVK_F20
    (0x60, 63),  # kVK_F5
    (0x61, 64),  # kVK_F6
    (0x62, 65),  # kVK_F7
    (0x63, 61),  # kVK_F3
    (0x64, 66),  # kVK_F8
    (0x65, 67),  # kVK_F9
    (0x67, 87),  # kVK_F11
    (0x69, 183),  # kVK_F13
    (0x6A, 186),  # kVK_F16
    (0x6B, 184),  # kVK_F14
    (0x6D, 68),  # kVK_F10
    (0x6F, 88),  # kVK_F12
    (0x71, 185),  # kVK_F15
    (0x72, 138),  # kVK_Help
    (0x73, 102),  # kVK_Home
    (0x74, 104),  # kVK_PageUp
    (0x75, 111),  # kVK_ForwardDelete
    (0x76, 62),  # kVK_F4
    (0x77, 107),  # kVK_End
    (0x78, 60),  # kVK_F2
    (0x79, 109),  # kVK_PageDown
    (0x7A, 59),  # kVK_F1
    (0x7B, 105),  # kVK_LeftArrow
    (0x7C, 106),  # kVK_RightArrow
    (0x7D, 108),  # kVK_DownArrow
    (0x7E, 103),  # kVK_UpArrow
    (0x0A, 170),  # kVK_ISO_Section
    (0x5D, 124),  # kVK_JIS_Yen
    (0x5E, 92),  # kVK_JIS_Underscore
    (0x5F, 95),  # kVK_JIS_KeypadComma
    (0x66, 94),  # kVK_JIS_Eisu
    (0x68, 90)   # kVK_JIS_Kana
)


EVENT_MAP = (
    ('types', EVENT_TYPES),
    ('type_codes', ((value, key) for key, value in EVENT_TYPES)),
    ('xpad', XINPUT_MAPPING),
    ('Sync', SYNCHRONIZATION_EVENTS))


# Now comes all the structs we need to parse the infomation coming
# from Windows.

class XinputGamepad(ctypes.Structure):
    """Describes the current state of the Xbox 360 Controller.

    For full details see Microsoft's documentation:

    https://msdn.microsoft.com/en-us/library/windows/desktop/
    microsoft.directx_sdk.reference.xinput_gamepad%28v=vs.85%29.aspx

    """
    # pylint: disable=too-few-public-methods
    _fields_ = [
        ('buttons', ctypes.c_ushort),  # wButtons
        ('left_trigger', ctypes.c_ubyte),  # bLeftTrigger
        ('right_trigger', ctypes.c_ubyte),  # bLeftTrigger
        ('l_thumb_x', ctypes.c_short),  # sThumbLX
        ('l_thumb_y', ctypes.c_short),  # sThumbLY
        ('r_thumb_x', ctypes.c_short),  # sThumbRx
        ('r_thumb_y', ctypes.c_short),  # sThumbRy
    ]


class XinputState(ctypes.Structure):
    """Represents the state of a controller.

    For full details see Microsoft's documentation:

    https://msdn.microsoft.com/en-us/library/windows/desktop/
    microsoft.directx_sdk.reference.xinput_state%28v=vs.85%29.aspx

    """
    # pylint: disable=too-few-public-methods
    _fields_ = [
        ('packet_number', ctypes.c_ulong),  # dwPacketNumber
        ('gamepad', XinputGamepad),  # Gamepad
    ]


class XinputVibration(ctypes.Structure):
    """Specifies motor speed levels for the vibration function of a
    controller.

    For full details see Microsoft's documentation:

    https://msdn.microsoft.com/en-us/library/windows/desktop/
    microsoft.directx_sdk.reference.xinput_vibration%28v=vs.85%29.aspx

    """
    # pylint: disable=too-few-public-methods
    _fields_ = [("wLeftMotorSpeed", ctypes.c_ushort),
                ("wRightMotorSpeed", ctypes.c_ushort)]


if sys.version_info.major == 2:
    # pylint: disable=redefined-builtin
    class PermissionError(IOError):
        """Raised when trying to run an operation without the adequate access
        rights - for example filesystem permissions. Corresponds to errno
        EACCES and EPERM."""


class UnpluggedError(RuntimeError):
    """The device requested is not plugged in."""
    pass


class NoDevicePath(RuntimeError):
    """No evdev device path was given."""
    pass


class UnknownEventType(IndexError):
    """We don't know what this event is."""
    pass


class UnknownEventCode(IndexError):
    """We don't know what this event is."""
    pass


class InputEvent(object):  # pylint: disable=useless-object-inheritance
    """A user event."""
    # pylint: disable=too-few-public-methods
    def __init__(self,
                 device,
                 event_info):
        self.device = device
        self.timestamp = event_info["timestamp"]
        self.code = event_info["code"]
        self.state = event_info["state"]
        self.ev_type = event_info["ev_type"]


class InputDevice(object):  # pylint: disable=useless-object-inheritance
    """A user input device."""
    # pylint: disable=too-many-instance-attributes
    def __init__(self, manager,
                 device_path=None,
                 char_path_override=None,
                 read_size=1):
        self.read_size = read_size
        self.manager = manager
        self.__pipe = None
        self._listener = None
        self.leds = None
        if device_path:
            self._device_path = device_path
        else:
            self._set_device_path()
        # We should by now have a device_path

        try:
            if not self._device_path:
                raise NoDevicePath
        except AttributeError:
            raise NoDevicePath

        self.protocol, _, self.device_type = self._get_path_infomation()
        if char_path_override:
            self._character_device_path = char_path_override
        else:
            self._character_device_path = os.path.realpath(self._device_path)

        self._character_file = None

        self._evdev = False
        self._set_evdev_state()

        self.name = "Unknown Device"
        self._set_name()

    def _set_device_path(self):
        """Set the device path, overridden on the MAC and Windows."""
        pass

    def _set_evdev_state(self):
        """Set whether the device is a real evdev device."""
        if NIX:
            self._evdev = True

    def _set_name(self):
        if NIX:
            with open("/sys/class/input/%s/device/name" %
                      self.get_char_name()) as name_file:
                self.name = name_file.read().strip()
            self.leds = []

    def _get_path_infomation(self):
        """Get useful infomation from the device path."""
        long_identifier = self._device_path.split('/')[4]
        protocol, remainder = long_identifier.split('-', 1)
        identifier, _, device_type = remainder.rsplit('-', 2)
        return (protocol, identifier, device_type)

    def get_char_name(self):
        """Get short version of char device name."""
        return self._character_device_path.split('/')[-1]

    def get_char_device_path(self):
        """Get the char device path."""
        return self._character_device_path

    def __str__(self):
        try:
            return self.name
        except AttributeError:
            return "Unknown Device"

    def __repr__(self):
        return '%s.%s("%s")' % (
            self.__module__,
            self.__class__.__name__,
            self._device_path)

    @property
    def _character_device(self):
        if not self._character_file:
            if WIN:
                self._character_file = io.BytesIO()
                return self._character_file
            try:
                self._character_file = io.open(
                    self._character_device_path, 'rb')
            except PermissionError:
                # Python 3
                raise PermissionError(PERMISSIONS_ERROR_TEXT)
            except IOError as err:
                # Python 2
                if err.errno == 13:
                    raise PermissionError(PERMISSIONS_ERROR_TEXT)
                else:
                    raise

        return self._character_file

    def __iter__(self):
        while True:
            event = self._do_iter()
            if event:
                yield event

    def _get_data(self, read_size):
        """Get data from the character device."""
        return self._character_device.read(read_size)

    @staticmethod
    def _get_target_function():
        """Get the correct target function. This is only used by Windows
        subclasses."""
        return False

    def _get_total_read_size(self):
        """How much event data to process at once."""
        if self.read_size:
            read_size = EVENT_SIZE * self.read_size
        else:
            read_size = EVENT_SIZE
        return read_size

    def _do_iter(self):
        read_size = self._get_total_read_size()
        data = self._get_data(read_size)
        if not data:
            return None
        evdev_objects = iter_unpack(data)
        events = [self._make_event(*event) for event in evdev_objects]
        return events

    # pylint: disable=too-many-arguments
    def _make_event(self, tv_sec, tv_usec, ev_type, code, value):
        """Create a friendly Python object from an evdev style event."""
        event_type = self.manager.get_event_type(ev_type)
        eventinfo = {
            "ev_type": event_type,
            "state": value,
            "timestamp": tv_sec + (tv_usec / 1000000),
            "code": self.manager.get_event_string(event_type, code)
        }

        return InputEvent(self, eventinfo)

    def read(self):
        """Read the next input event."""
        return next(iter(self))

    @property
    def _pipe(self):
        """On Windows we use a pipe to emulate a Linux style character
        buffer."""
        if self._evdev:
            return None

        if not self.__pipe:
            target_function = self._get_target_function()
            if not target_function:
                return None

            self.__pipe, child_conn = Pipe(duplex=False)
            self._listener = Process(target=target_function,
                                     args=(child_conn,), daemon=True)
            self._listener.start()
        return self.__pipe

    def __del__(self):
        if 'WIN' in globals() or 'MAC' in globals():
            if WIN or MAC:
                if self.__pipe:
                    self._listener.terminate()

def delay_and_stop(duration, dll, device_number):
    """Stop vibration aka force feedback aka rumble on
    Windows after duration miliseconds."""
    xinput = getattr(ctypes.windll, dll)
    time.sleep(duration/1000)
    xinput_set_state = xinput.XInputSetState
    xinput_set_state.argtypes = [
        ctypes.c_uint, ctypes.POINTER(XinputVibration)]
    xinput_set_state.restype = ctypes.c_uint
    vibration = XinputVibration(0, 0)
    xinput_set_state(device_number, ctypes.byref(vibration))


class GamePad(InputDevice):
    """A gamepad or other joystick-like device."""
    def __init__(self, manager, device_path,
                 char_path_override=None):
        super(GamePad, self).__init__(manager,
                                      device_path,
                                      char_path_override)
        self._write_file = None
        self.__device_number = None
        if WIN:
            if "Microsoft_Corporation_Controller" in self._device_path:
                self.name = "Microsoft X-Box 360 pad"
                identifier = self._get_path_infomation()[1]
                self.__device_number = int(identifier.split('_')[-1])
                self.__received_packets = 0
                self.__missed_packets = 0
                self.__last_state = self.__read_device()
        if NIX:
            self._number_xpad()

    def _number_xpad(self):
        """Get the number of the joystick."""
        js_path = self._device_path.replace('-event', '')
        js_chardev = os.path.realpath(js_path)
        try:
            number_text = js_chardev.split('js')[1]
        except IndexError:
            return
        try:
            number = int(number_text)
        except ValueError:
            return
        self.__device_number = number

    def get_number(self):
        """Return the joystick number of the gamepad."""
        return self.__device_number

    def __iter__(self):
        while True:
            if WIN:
                self.__check_state()
            event = self._do_iter()
            if event:
                yield event

    def __check_state(self):
        """On Windows, check the state and fill the event character device."""
        state = self.__read_device()
        if not state:
            raise UnpluggedError(
                "Gamepad %d is not connected" % self.__device_number)
        if state.packet_number != self.__last_state.packet_number:
            # state has changed, handle the change
            self.__handle_changed_state(state)
            self.__last_state = state

    @staticmethod
    def __get_timeval():
        """Get the time and make it into C style timeval."""
        return convert_timeval(time.time())

    def create_event_object(self,
                            event_type,
                            code,
                            value,
                            timeval=None):
        """Create an evdev style object."""
        if not timeval:
            timeval = self.__get_timeval()
        try:
            event_code = self.manager.codes['type_codes'][event_type]
        except KeyError:
            raise UnknownEventType(
                "We don't know what kind of event a %s is." % event_type)
        event = struct.pack(EVENT_FORMAT,
                            timeval[0],
                            timeval[1],
                            event_code,
                            code,
                            value)
        return event

    def __write_to_character_device(self, event_list, timeval=None):
        """Emulate the Linux character device on other platforms such as
        Windows."""
        # Remember the position of the stream
        pos = self._character_device.tell()
        # Go to the end of the stream
        self._character_device.seek(0, 2)
        # Write the new data to the end
        for event in event_list:
            self._character_device.write(event)
        # Add a sync marker
        sync = self.create_event_object("Sync", 0, 0, timeval)
        self._character_device.write(sync)
        # Put the stream back to its original position
        self._character_device.seek(pos)

    def __handle_changed_state(self, state):
        """
        we need to pack a struct with the following five numbers:
        tv_sec, tv_usec, ev_type, code, value

        then write it using __write_to_character_device

        seconds, mircroseconds, ev_type, code, value
        time we just use now
        ev_type we look up
        code we look up
        value is 0 or 1 for the buttons
        axis value is maybe the same as Linux? Hope so!
        """
        timeval = self.__get_timeval()
        events = self.__get_button_events(state, timeval)
        events.extend(self.__get_axis_events(state, timeval))
        if events:
            self.__write_to_character_device(events, timeval)

    def __map_button(self, button):
        """Get the linux xpad code from the Windows xinput code."""
        _, start_code, start_value = button
        value = start_value
        ev_type = "Key"
        code = self.manager.codes['xpad'][start_code]
        if 1 <= start_code <= 4:
            ev_type = "Absolute"
        if start_code == 1 and start_value == 1:
            value = -1
        elif start_code == 3 and start_value == 1:
            value = -1
        return code, value, ev_type

    def __map_axis(self, axis):
        """Get the linux xpad code from the Windows xinput code."""
        start_code, start_value = axis
        value = start_value
        code = self.manager.codes['xpad'][start_code]
        return code, value

    def __get_button_events(self, state, timeval=None):
        """Get the button events from xinput."""
        changed_buttons = self.__detect_button_events(state)
        events = self.__emulate_buttons(changed_buttons, timeval)
        return events

    def __get_axis_events(self, state, timeval=None):
        """Get the stick events from xinput."""
        axis_changes = self.__detect_axis_events(state)
        events = self.__emulate_axis(axis_changes, timeval)
        return events

    def __emulate_axis(self, axis_changes, timeval=None):
        """Make the axis events use the Linux style format."""
        events = []
        for axis in axis_changes:
            code, value = self.__map_axis(axis)
            event = self.create_event_object(
                "Absolute",
                code,
                value,
                timeval=timeval)
            events.append(event)
        return events

    def __emulate_buttons(self, changed_buttons, timeval=None):
        """Make the button events use the Linux style format."""
        events = []
        for button in changed_buttons:
            code, value, ev_type = self.__map_button(button)
            event = self.create_event_object(
                ev_type,
                code,
                value,
                timeval=timeval)
            events.append(event)
        return events

    @staticmethod
    def __gen_bit_values(number):
        """
        Return a zero or one for each bit of a numeric value up to the most
        significant 1 bit, beginning with the least significant bit.
        """
        number = int(number)
        while number:
            yield number & 0x1
            number >>= 1

    def __get_bit_values(self, number, size=32):
        """Get bit values as a list for a given number

        >>> get_bit_values(1) == [0]*31 + [1]
        True

        >>> get_bit_values(0xDEADBEEF)
        [1L, 1L, 0L, 1L, 1L, 1L, 1L,
        0L, 1L, 0L, 1L, 0L, 1L, 1L, 0L, 1L, 1L, 0L, 1L, 1L, 1L, 1L,
        1L, 0L, 1L, 1L, 1L, 0L, 1L, 1L, 1L, 1L]

        You may override the default word size of 32-bits to match your actual
        application.
        >>> get_bit_values(0x3, 2)
        [1L, 1L]

        >>> get_bit_values(0x3, 4)
        [0L, 0L, 1L, 1L]

        """
        res = list(self.__gen_bit_values(number))
        res.reverse()
        # 0-pad the most significant bit
        res = [0] * (size - len(res)) + res
        return res

    def __detect_button_events(self, state):
        changed = state.gamepad.buttons ^ self.__last_state.gamepad.buttons
        changed = self.__get_bit_values(changed, 16)
        buttons_state = self.__get_bit_values(state.gamepad.buttons, 16)
        changed.reverse()
        buttons_state.reverse()
        button_numbers = count(1)
        changed_buttons = list(
            filter(itemgetter(0),
                   list(zip(changed, button_numbers, buttons_state))))
        # returns for example [(1,15,1)] type, code, value?
        return changed_buttons

    def __detect_axis_events(self, state):
        # axis fields are everything but the buttons
        # pylint: disable=protected-access
        # Attribute name _fields_ is special name set by ctypes
        axis_fields = dict(XinputGamepad._fields_)
        axis_fields.pop('buttons')
        changed_axes = []

        # Ax_type might be useful when we support high-level deadzone
        # methods.
        # pylint: disable=unused-variable
        for axis, ax_type in list(axis_fields.items()):
            old_val = getattr(self.__last_state.gamepad, axis)
            new_val = getattr(state.gamepad, axis)
            if old_val != new_val:
                changed_axes.append((axis, new_val))
        return changed_axes

    def __read_device(self):
        """Read the state of the gamepad."""
        state = XinputState()
        res = self.manager.xinput.XInputGetState(
            self.__device_number, ctypes.byref(state))
        if res == XINPUT_ERROR_SUCCESS:
            return state
        if res != XINPUT_ERROR_DEVICE_NOT_CONNECTED:
            raise RuntimeError(
                "Unknown error %d attempting to get state of device %d" % (
                    res, self.__device_number))
        # else (device is not connected)
        return None

    @property
    def _write_device(self):
        if not self._write_file:
            if not NIX:
                return None
            try:
                self._write_file = io.open(
                    self._character_device_path, 'wb')
            except PermissionError:
                # Python 3
                raise PermissionError(PERMISSIONS_ERROR_TEXT)
            except IOError as err:
                # Python 2
                if err.errno == 13:
                    raise PermissionError(PERMISSIONS_ERROR_TEXT)
                else:
                    raise

        return self._write_file

    def _start_vibration_win(self, left_motor, right_motor):
        """Start the vibration, which will run until stopped."""
        xinput_set_state = self.manager.xinput.XInputSetState
        xinput_set_state.argtypes = [
            ctypes.c_uint, ctypes.POINTER(XinputVibration)]
        xinput_set_state.restype = ctypes.c_uint
        vibration = XinputVibration(
            int(left_motor * 65535), int(right_motor * 65535))
        xinput_set_state(self.__device_number, ctypes.byref(vibration))

    def _stop_vibration_win(self):
        """Stop the vibration."""
        xinput_set_state = self.manager.xinput.XInputSetState
        xinput_set_state.argtypes = [
            ctypes.c_uint, ctypes.POINTER(XinputVibration)]
        xinput_set_state.restype = ctypes.c_uint
        stop_vibration = ctypes.byref(XinputVibration(0, 0))
        xinput_set_state(self.__device_number, stop_vibration)

    def _set_vibration_win(self, left_motor, right_motor, duration):
        """Control the motors on Windows."""
        self._start_vibration_win(left_motor, right_motor)
        stop_process = Process(target=delay_and_stop,
                               args=(duration,
                                     self.manager.xinput_dll,
                                     self.__device_number))
        stop_process.start()

    def __get_vibration_code(self, left_motor, right_motor, duration):
        """This is some crazy voodoo, if you can simplify it, please do."""
        inner_event = struct.pack(
            '2h6x2h2x2H28x',
            0x50,
            -1,
            duration,
            0,
            int(left_motor * 65535),
            int(right_motor * 65535))
        buf_conts = ioctl(self._write_device, 1076905344, inner_event)
        return int(codecs.encode(buf_conts[1:3], 'hex'), 16)

    def _set_vibration_nix(self, left_motor, right_motor, duration):
        """Control the motors on Linux.
        Duration is in miliseconds."""
        code = self.__get_vibration_code(left_motor, right_motor, duration)
        secs, msecs = convert_timeval(time.time())
        outer_event = struct.pack(EVENT_FORMAT, secs, msecs, 0x15, code, 1)
        self._write_device.write(outer_event)
        self._write_device.flush()

    def set_vibration(self, left_motor, right_motor, duration):
        """Control the speed of both motors seperately or together.
        left_motor and right_motor arguments require a number between
        0 (off) and 1 (full).
        duration is miliseconds, e.g. 1000 for a second."""
        if WIN:
            self._set_vibration_win(left_motor, right_motor, duration)
        elif NIX:
            self._set_vibration_nix(left_motor, right_motor, duration)
        else:
            raise NotImplementedError

class OtherDevice(InputDevice):
    """A device of which its is type is either undetectable or has not
    been implemented yet.
    """
    pass

class RawInputDeviceList(ctypes.Structure):
    """
    Contains information about a raw input device.

    For full details see Microsoft's documentation:

    http://msdn.microsoft.com/en-us/library/windows/desktop/
    ms645568(v=vs.85).aspx
    """
    # pylint: disable=too-few-public-methods
    _fields_ = [
        ("hDevice", HANDLE),
        ("dwType", DWORD)
    ]

class DeviceManager(object):  # pylint: disable=useless-object-inheritance
    """Provides access to all connected and detectible user input
    devices."""
    # pylint: disable=too-many-instance-attributes

    def __init__(self):
        self.codes = {key: dict(value) for key, value in EVENT_MAP}
        self._raw = []
        self.keyboards = []
        self.mice = []
        self.gamepads = []
        self.other_devices = []
        self.all_devices = []
        self.leds = []
        self.microbits = []
        self.xinput = None
        self.xinput_dll = None
        if WIN:
            self._raw_device_counts = {
                'mice': 0,
                'keyboards': 0,
                'otherhid': 0,
                'unknown': 0
            }
        self._post_init()

    def _post_init(self):
        """Call the find devices method for the relevant platform."""
        if WIN:
            self._find_devices_win()
        elif MAC:
            self._find_devices_mac()
        else:
            self._find_devices()
        self._update_all_devices()
        if NIX:
            self._find_leds()

    def _update_all_devices(self):
        """Update the all_devices list."""
        self.all_devices = []
        self.all_devices.extend(self.keyboards)
        self.all_devices.extend(self.mice)
        self.all_devices.extend(self.gamepads)
        self.all_devices.extend(self.other_devices)

    def _parse_device_path(self, device_path, char_path_override=None):
        """Parse each device and add to the approriate list."""

        # 1. Make sure that we can parse the device path.
        try:
            device_type = device_path.rsplit('-', 1)[1]
        except IndexError:
            warn("The following device path was skipped as it could "
                 "not be parsed: %s" % device_path, RuntimeWarning)
            return

        # 2. Make sure each device is only added once.
        realpath = os.path.realpath(device_path)
        if realpath in self._raw:
            return
        self._raw.append(realpath)

        # 3. All seems good, append the device to the relevant list.
        if device_type == 'kbd':
            self.keyboards.append(Keyboard(self, device_path,
                                           char_path_override))
        elif device_type == 'mouse':
            self.mice.append(Mouse(self, device_path,
                                   char_path_override))
        elif device_type == 'joystick':
            self.gamepads.append(GamePad(self,
                                         device_path,
                                         char_path_override))
        else:
            self.other_devices.append(OtherDevice(self,
                                                  device_path,
                                                  char_path_override))

    def _find_xinput(self):
        """Find most recent xinput library."""
        for dll in XINPUT_DLL_NAMES:
            try:
                self.xinput = getattr(ctypes.windll, dll)
            except OSError:
                pass
            else:
                # We found an xinput driver
                self.xinput_dll = dll
                break
        else:
            # We didn't find an xinput library
            warn(
                "No xinput driver dll found, gamepads not supported.",
                RuntimeWarning)

    def _find_devices_win(self):
        """Find devices on Windows."""
        self._find_xinput()
        self._detect_gamepads()
        self._count_devices()
        if self._raw_device_counts['keyboards'] > 0:
            self.keyboards.append(Keyboard(
                self,
                "/dev/input/by-id/usb-A_Nice_Keyboard-event-kbd"))

        if self._raw_device_counts['mice'] > 0:
            self.mice.append(Mouse(
                self,
                "/dev/input/by-id/usb-A_Nice_Mouse_called_Arthur-event-mouse"))

    def _find_devices_mac(self):
        """Find devices on Mac."""
        self.keyboards.append(Keyboard(self))
        self.mice.append(MightyMouse(self))
        self.mice.append(Mouse(self))

    def _detect_gamepads(self):
        """Find gamepads."""
        state = XinputState()
        # Windows allows up to 4 gamepads.
        for device_number in range(4):
            res = self.xinput.XInputGetState(
                device_number, ctypes.byref(state))
            if res == XINPUT_ERROR_SUCCESS:
                # We found a gamepad
                device_path = (
                    "/dev/input/by_id/" +
                    "usb-Microsoft_Corporation_Controller_%s-event-joystick"
                    % device_number)
                self.gamepads.append(GamePad(self, device_path))
                continue
            if res != XINPUT_ERROR_DEVICE_NOT_CONNECTED:
                raise RuntimeError(
                    "Unknown error %d attempting to get state of device %d"
                    % (res, device_number))

    def _count_devices(self):
        """See what Windows' GetRawInputDeviceList wants to tell us.

        For now, we are just seeing if there is at least one keyboard
        and/or mouse attached.

        GetRawInputDeviceList could be used to help distinguish between
        different keyboards and mice on the system in the way Linux
        can. However, Roma uno die non est condita.

        """
        number_of_devices = ctypes.c_uint()

        if ctypes.windll.user32.GetRawInputDeviceList(
                ctypes.POINTER(ctypes.c_int)(),
                ctypes.byref(number_of_devices),
                ctypes.sizeof(RawInputDeviceList)) == -1:
            warn("Call to GetRawInputDeviceList was unsuccessful."
                 "We have no idea if a mouse or keyboard is attached.",
                 RuntimeWarning)
            return

        devices_found = (RawInputDeviceList * number_of_devices.value)()

        if ctypes.windll.user32.GetRawInputDeviceList(
                devices_found,
                ctypes.byref(number_of_devices),
                ctypes.sizeof(RawInputDeviceList)) == -1:
            warn("Call to GetRawInputDeviceList was unsuccessful."
                 "We have no idea if a mouse or keyboard is attached.",
                 RuntimeWarning)
            return

        for device in devices_found:
            if device.dwType == 0:
                self._raw_device_counts['mice'] += 1
            elif device.dwType == 1:
                self._raw_device_counts['keyboards'] += 1
            elif device.dwType == 2:
                self._raw_device_counts['otherhid'] += 1
            else:
                self._raw_device_counts['unknown'] += 1

    def _find_devices(self):
        """Find available devices."""
        self._find_by('id')
        self._find_by('path')
        self._find_special()

    def _find_by(self, key):
        """Find devices."""
        by_path = glob.glob('/dev/input/by-{key}/*-event-*'.format(key=key))
        for device_path in by_path:
            self._parse_device_path(device_path)

    def _find_leds(self):
        """Find LED devices, Linux-only so far."""
        for path in glob.glob('/sys/class/leds/*'):
            self._parse_led_path(path)

    def _parse_led_path(self, path):
        name = path.rsplit('/', 1)[1]
        if name.startswith('xpad'):
            self.leds.append(GamepadLED(self, path, name))
        elif name.startswith('input'):
            self.leds.append(SystemLED(self, path, name))
        else:
            self.leds.append(LED(self, path, name))

    def _get_char_names(self):
        """Get a list of already found devices."""
        return [device.get_char_name() for
                device in self.all_devices]

    def _find_special(self):
        """Look for special devices."""
        charnames = self._get_char_names()
        for eventdir in glob.glob('/sys/class/input/event*'):
            char_name = os.path.split(eventdir)[1]
            if char_name in charnames:
                continue
            name_file = os.path.join(eventdir, 'device', 'name')
            with open(name_file) as name_file:
                device_name = name_file.read().strip()
                if device_name in self.codes['specials']:
                    self._parse_device_path(
                        self.codes['specials'][device_name],
                        os.path.join('/dev/input', char_name))

    def __iter__(self):
        return iter(self.all_devices)

    def __getitem__(self, index):
        try:
            return self.all_devices[index]
        except IndexError:
            raise IndexError("list index out of range")

    def get_event_type(self, raw_type):
        """Convert the code to a useful string name."""
        try:
            return self.codes['types'][raw_type]
        except KeyError:
            raise UnknownEventType("We don't know this event type")

    def get_event_string(self, evtype, code):
        """Get the string name of the event."""
        if WIN and evtype == 'Key':
            # If we can map the code to a common one then do it
            try:
                code = self.codes['wincodes'][code]
            except KeyError:
                pass
        try:
            return self.codes[evtype][code]
        except KeyError:
            raise UnknownEventCode("We don't know this event.", evtype, code)

    def get_typecode(self, name):
        """Returns type code for `name`."""
        return self.codes['type_codes'][name]

    def detect_microbit(self):
        """Detect a microbit."""
        try:
            gpad = MicroBitPad(self)
        except ModuleNotFoundError:
            warn(
                "The microbit library could not be found in the pythonpath. \n"
                "For more information, please visit \n"
                "https://inputs.readthedocs.io/en/latest/user/microbit.html",
                RuntimeWarning)
        else:
            self.microbits.append(gpad)
            self.gamepads.append(gpad)

devices = DeviceManager()  # pylint: disable=invalid-name

def get_gamepad(i):
    """Get a single action from a gamepad."""
    try:
        gamepad = devices.gamepads[i]
    except IndexError:
        raise UnpluggedError("No gamepad found.")
    return gamepad.read()