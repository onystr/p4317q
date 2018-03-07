#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from enum import Enum, unique
import serial
import argparse

# Constant
endian = 'big'


# Base Class of Exception
class P4317qError(Exception):
    pass


# Header Error
class HeaderError(P4317qError):
    pass


# Checksum Error
class ChecksumError(P4317qError):
    pass


# Unsupported Command
class UnsupportedCommand(P4317qError):
    pass


# Parameter Over Range
class ParameterOverRange(P4317qError):
    pass


# Extra Parameter (one byte)
class ExtraParameter(P4317qError):
    pass


# Format Error (too short)
class FormatError(P4317qError):
    pass


# Length Error
class LengthError(P4317qError):
    pass


# Result Code Error
class ResultCodeError(P4317qError):
    pass


# Command Error
class CommandError(P4317qError):
    pass


# Header
@unique
class Header(Enum):
    Command = bytes([0x37, 0x51])
    Reply = bytes([0x6f, 0x37])


# R/W
@unique
class ReadWrite(Enum):
    Read = bytes([0xeb])
    Write = bytes([0xea])


# Command
@unique
class Command(Enum):
    # MONITOR MANAGEMENT
    AssertTag = bytes([0x00])
    MonitorName = bytes([0x01])
    MonitorSerialNumber = bytes([0x02])
    BacklightHours = bytes([0x04])
    # POWER MANAGEMENT
    PowerState = bytes([0x20])
    PowerLED = bytes([0x21])
    PowerUSB = bytes([0x22])
    ResetPower = bytes([0x2f])
    # IMAGE ADJUSTMENT
    Brightness = bytes([0x30])
    Contrast = bytes([0x31])
    AspectRatio = bytes([0x33])
    Sharpness = bytes([0x34])
    # COLOR MANAGEMENT
    InputColorFormat = bytes([0x46])
    ColorPresetCaps = bytes([0x47])
    ColorPreset = bytes([0x48])
    CustomColor = bytes([0x49])
    ResetColor = bytes([0x4f])
    # VIDEO INPUT MANAGEMENT
    AutoSelect = bytes([0x60])
    VideoInputCaps = bytes([0x61])
    VideoInput = bytes([0x62])
    # PIP/PBP MANAGEMENT
    PxPMode = bytes([0x70])
    PxPSubInput = bytes([0x71])
    PxPLocation = bytes([0x72])
    # OSD MANAGEMENT
    OSDTransparency = bytes([0x80])
    OSDLanguage = bytes([0x81])
    OSDTimer = bytes([0x83])
    OSDButtonLock = bytes([0x84])
    ResetOSD = bytes([0x8f])
    # SYSTEM MANAGEMENT
    VersionFirmware = bytes([0xa0])
    DDCCI = bytes([0xa2])
    LCDConditioning = bytes([0xa3])
    FactoryReset = bytes([0xaf])


# Data Length
class DataLength(object):
    # POWER MANAGEMENT
    PowerState = 1
    PowerLED = 1
    PowerUSB = 1
    # IMAGE ADJUSTMENT
    Brightness = 1
    Contrast = 1
    AspectRatio = 1
    Sharpness = 1
    # COLOR MANAGEMENT
    InputColorFormat = 1
    ColorPreset = 4
    CustomColor = 7
    # VIDEO INPUT MANAGEMENT
    AutoSelect = 1
    VideoInput = 4
    # PIP/PBP MANAGEMENT
    PxPMode = 1
    PxPSubInput = 4
    PxPLocation = 1
    # OSD MANAGEMENT
    OSDTransparency = 1
    OSDLanguage = 1
    OSDTimer = 1
    OSDButtonLock = 1
    # SYSTEM MANAGEMENT
    DDCCI = 1
    LCDConditioning = 1


# State
@unique
class State(Enum):
    Off = bytes([0x00])
    On = bytes([0x01])


# Aspect Ratio
@unique
class AspectRatio(Enum):
    AR_16_9 = bytes([0x00])
    AR_4_3 = bytes([0x02])
    AR_5_4 = bytes([0x04])


# Color Format
@unique
class ColorFormat(Enum):
    RGB = bytes([0x00])
    YPbPr = bytes([0x01])


# Color Preset
@unique
class ColorPreset(Enum):
    Standard = bytes([0x01, 0x00, 0x00, 0x00])
    Paper = bytes([0x10, 0x00, 0x00, 0x00])
    CustomColor = bytes([0x80, 0x00, 0x00, 0x00])
    Warm = bytes([0x00, 0x01, 0x00, 0x00])
    Cool = bytes([0x00, 0x02, 0x00, 0x00])


# Video Input
@unique
class VideoInput(Enum):
    HDMI1 = bytes([0x01, 0x00, 0x00, 0x00])
    HDMI2 = bytes([0x02, 0x00, 0x00, 0x00])
    DP1 = bytes([0x08, 0x00, 0x00, 0x00])
    DP2 = bytes([0x10, 0x00, 0x00, 0x00])
    VGA1 = bytes([0x40, 0x00, 0x00, 0x00])


# PxP Mode
@unique
class PxPMode(Enum):
    Off = bytes([0x00])
    PIPSmall = bytes([0x01])
    PIPLarge = bytes([0x02])
    PBP2Windows = bytes([0x05])
    PBP3WindowsMode1 = bytes([0x06])
    PBP3WindowsMode2 = bytes([0x07])
    PBP4Windows = bytes([0x08])


# PxP Location
@unique
class PxPLocation(Enum):
    TopRight = bytes([0x00])
    TopLeft = bytes([0x01])
    BottomRight = bytes([0x02])
    BottomLeft = bytes([0x03])


# Window
@unique
class Window(Enum):
    Window1 = bytes([0x00])
    Window2 = bytes([0x01])
    Window3 = bytes([0x02])
    Window4 = bytes([0x03])


# RGB
class RGB(object):
    __Red = None
    __Green = None
    __Blue = None

    def __init__(self, red=None, green=None, blue=None, rgb=None):
        if red is not None:
            if red in range(0, 100):
                self.__Red = red
            else:
                raise ValueError
        if green is not None:
            if green in range(0, 100):
                self.__Green = green
            else:
                raise ValueError
        if blue is not None:
            if blue in range(0, 100):
                self.__Blue = blue
            else:
                raise ValueError
        if rgb is not None:
            v = int.from_bytes(rgb[0:1], endian)
            if v in range(0, 100):
                self.__Red = v
            else:
                raise ValueError
            v = int.from_bytes(rgb[1:2], endian)
            if v in range(0, 100):
                self.__Green = v
            else:
                raise ValueError
            v = int.from_bytes(rgb[2:3], endian)
            if v in range(0, 100):
                self.__Blue = v
            else:
                raise ValueError

    @property
    def red(self):
        return self.__Red

    @red.setter
    def red(self, v):
        if v in range(0, 100):
            self.__Red = v
        else:
            raise ValueError

    @property
    def green(self):
        return self.__Green

    @green.setter
    def green(self, v):
        if v in range(0, 100):
            self.__Green = v
        else:
            raise ValueError

    @property
    def blue(self):
        return self.__Blue

    @blue.setter
    def blue(self, v):
        if v in range(0, 100):
            self.__Blue = v
        else:
            raise ValueError

    def to_bytes(self):
        return bytes([self.__Red, self.__Green, self.__Blue])

    def __str__(self):
        return "Red:{} Green:{} Blue:{}".format(self.__Red, self.__Green, self.__Blue)


# Language
class Language(Enum):
    English = bytes([0x00])
    Spanish = bytes([0x01])
    French = bytes([0x02])
    German = bytes([0x03])
    Portuguese = bytes([0x04])
    Russian = bytes([0x05])
    Chinese = bytes([0x06])
    Japanese = bytes([0x07])


# Result Code
class ResultCode(Enum):
    Success = bytes([0x00])
    Timeout = bytes([0x01])
    ParametersError = bytes([0x02])
    NotConnected = bytes([0x03])
    OtherFailure = bytes([0x04])


# Up Down
class UpDown(Enum):
    Up = 1
    Next = 1
    Inc = 1
    Down = -1
    Previous = -1
    Dec = -1


class P4317Q(object):
    """
    DELL P4317Q
    """

    def __init__(self, s):
        """

        :param s: Serial Port Device Name of str type
        """
        self.__serial = s

    @staticmethod
    def __calc_check_sum(v):
        """
        Calculate Checksum
        :param v: Command of bytes type
        :return: Checksum of bytes type
        """
        s = 0
        for i in v:
            s ^= i
        return s.to_bytes(1, endian)

    def __build_cmd(self, rw, cmd, data=bytes()):
        """
        Build Command
        :param rw: Read or Write of ReadWrite type (not bytes type)
        :param cmd: Command of Command type (not bytes type)
        :param data: data of bytes type if needed
        :return: Command of bytearray type
        """
        c = bytearray()

        # Add Header
        c.extend(Header.Command.value)

        # Add Length
        c.extend((len(rw.value) + len(cmd.value) + len(data)).to_bytes(1, endian))

        # Add Read/Write
        c.extend(rw.value)

        # Add Command
        c.extend(cmd.value)

        # Add Data
        c.extend(data)

        # Add CheckSum
        c.extend(self.__calc_check_sum(c))

        return c

    def __parse_reply(self, cmd, reply):
        """
        Parse Reply
        :param cmd: Command of Command type
        :param reply: Reply of bytes type
        :return: Data of bytes type if exist
        """
        # Check header
        if reply[0:2] != Header.Reply.value:
            raise HeaderError

        # Check Length
        ln = int.from_bytes(reply[2:3], endian)
        if ln != len(reply)-4:
            raise LengthError

        # Check Reply
        if reply[3:4] != bytes([0x02]):
            raise FormatError

        # Check Result Code
        if reply[4:5] != ResultCode.Success.value:
            raise ResultCodeError(int.from_bytes(reply[4:5], endian))

        # Check Command
        if reply[5:6] != cmd.value:
            raise CommandError

        # Check Checksum
        if reply[ln+3:ln+4] != self.__calc_check_sum(reply[0:ln+3]):
            raise ChecksumError

        # Return Data if exist(Length if greater than 4)
        return None if ln < 4 else reply[6:ln+3]

    def query(self, rw, cmd, data=bytes()):
        """
        Query Command
        :param rw: Read or Write of ReadWrite type
        :param cmd: Command of Command type
        :param data: Data of bytes type
        :return: Data of bytes type if exist
        """
        with serial.Serial(port=self.__serial, timeout=0.1) as s:
            s.reset_output_buffer()
            s.reset_input_buffer()
            s.write(self.__build_cmd(rw=rw, cmd=cmd, data=bytes(data)))
            s.flush()
            return self.__parse_reply(cmd=cmd, reply=s.read(64))

    def set_value(self, n, v=None, ud=None):
        """
        Set Value
        :param n: Member Name of str type
        :param v: Value to Set of Specific type
        :param ud: Up or Down of UpDown type
        :return: Value after change
        """
        if v is not None:
            exec('self.{}={}'.format(n, v))
            new = v
        elif ud is not None:
            old = eval('self.{}'.format(n))
            type = old.__class__.__name__
            if type == 'int':
                new = old + ud.value
                try:
                    exec('self.{}={}'.format(n, new))
                except ValueError:
                    new = old
            else:
                try:
                    new = eval('{}(list({})[list({}).index(old)+ud.value])'.format(type, type, type))
                except IndexError:
                    new = eval('{}[0] if 0 <= ud.value else {}[-1]'.format(type, type))
                exec('self.{}={}'.format(n, new))
        else:
            raise ValueError
        return new

    def get_value(self, n):
        """
        Get Value
        :param n: Member Name of str type
        :return: Value of Specific type
        """
        return eval('self.{}'.format(n))

    # MONITOR MANAGEMENT

    @property
    def assert_tag(self):
        """
        Get Assert Tag
        :return: Assert Tag of string type
        """
        return str(self.query(ReadWrite.Read, Command.AssertTag))

    @property
    def monitor_name(self):
        """
        Get Monitor Name
        :return: Monitor Name of string type
        """
        return self.query(ReadWrite.Read, Command.MonitorName).decode()

    @property
    def monitor_serial_number(self):
        """
        Get Monitor Serial Number
        :return: Monitor Serial Number of bytes type
        """
        return self.query(ReadWrite.Read, Command.MonitorSerialNumber)

    @property
    def backlight_hours(self):
        """
        Get Backlight Hours
        :return: Backlight Hours of int type
        """
        return int.from_bytes(self.query(ReadWrite.Read, Command.BacklightHours), endian)

    # POWER MANAGEMENT

    @property
    def power_state(self):
        """
        Get Power State
        :return: Power State of State type
        """
        return State(self.query(ReadWrite.Read, Command.PowerState))

    @power_state.setter
    def power_state(self, v):
        """
        Set Power State
        :param v: Power State of State type
        :return: None
        """
        self.query(ReadWrite.Write, Command.PowerState, v.value)

    @property
    def power_led(self):
        """
        Get Power LED
        :return: Power LED of State type
        """
        return State(self.query(ReadWrite.Read, Command.PowerLED))

    @power_led.setter
    def power_led(self, v):
        """
        Set Power LED
        :param v: Power LED of State type
        :return: None
        """
        self.query(ReadWrite.Write, Command.PowerLED, v.value)

    @property
    def power_usb(self):
        """
        Get Power USB
        :return: Power USB of State Type
        """
        return State(self.query(ReadWrite.Read, Command.PowerUSB))

    @power_usb.setter
    def power_usb(self, v):
        """
        Set Power USB
        :param v: Power USB of State Type
        :return: None
        """
        self.query(ReadWrite.Write, Command.PowerUSB, v.value)

    def reset_power(self):
        """
        Reset Power
        :return: None
        """
        self.query(ReadWrite.Write, Command.ResetPower)

    # IMAGE ADJUSTMENT

    @property
    def brightness(self):
        """
        Get Brightness
        :return: Brightness of int type
        """
        return int.from_bytes(self.query(ReadWrite.Read, Command.Brightness), endian)

    @brightness.setter
    def brightness(self, v):
        """
        Set Brightness
        :param v: Brightness of int type
        :return: None
        """
        if v not in range(0, 100):
            raise ValueError
        self.query(ReadWrite.Write, Command.Brightness, v.to_bytes(DataLength.Brightness, endian))

    @property
    def contrast(self):
        """
        Get Contrast
        :return: Contrast of int type
        """
        return int.from_bytes(self.query(ReadWrite.Read, Command.Contrast), endian)

    @contrast.setter
    def contrast(self, v):
        """
        Set Contrast
        :param v: Contrast of int type
        :return: None
        """
        if v not in range(0, 100):
            raise ValueError
        self.query(ReadWrite.Write, Command.Contrast, v.to_bytes(DataLength.Contrast, endian))

    @property
    def aspect_ratio(self):
        """
        Get Aspect Ratio
        :return: Aspect Ratio of AspectRatio type
        """
        return AspectRatio(self.query(ReadWrite.Read, Command.AspectRatio))

    @aspect_ratio.setter
    def aspect_ratio(self, v):
        """
        Set Aspect Ratio
       :param v: Aspect Ratio of AspectRatio type
        :return: None
        """
        self.query(ReadWrite.Write, Command.AspectRatio, v.value)

    @property
    def sharpness(self):
        """
        Get Sharpness
        :return: Sharpness of int type
        """
        return int.from_bytes(self.query(ReadWrite.Read, Command.Sharpness), endian)

    @sharpness.setter
    def sharpness(self, v):
        """
        Set Sharpness
        :param v: Sharpness of int type
        :return: None
        """
        self.query(ReadWrite.Write, Command.Sharpness, v.to_bytes(DataLength.Sharpness, endian))

    # COLOR MANAGEMENT

    @property
    def input_color_format(self):
        """
        Get Input Color Format
        :return: Color Format of ColorFormat type
        """
        return ColorFormat(self.query(ReadWrite.Read, Command.InputColorFormat))

    @input_color_format.setter
    def input_color_format(self, v):
        """
        Set Input Color Format
        :param v: Color Format of ColorFormat type
        :return: None
        """
        self.query(ReadWrite.Write, Command.InputColorFormat, v.value)

    @property
    def color_preset_caps(self):
        """
        Get Color Preset Capabilities
        :return: ???
        """
        return self.query(ReadWrite.Read, Command.ColorPresetCaps)

    @property
    def color_preset(self):
        """
        Get Color Preset
        :return: Color Preset of ColorPreset type
        """
        return ColorPreset(self.query(ReadWrite.Read, Command.ColorPreset))

    @color_preset.setter
    def color_preset(self, v):
        """
        Set Color Preset
        :param v: Color Preset of ColorPreset type
        :return: None
        """
        self.query(ReadWrite.Write, Command.ColorPreset, v.value)

    @property
    def custom_color(self):
        """
        Get Custom Color
        :return: Custom Color of RGB type
        """
        return RGB(rgb=self.query(ReadWrite.Read, Command.CustomColor))

    @custom_color.setter
    def custom_color(self, v):
        """
        Set Custom Color
        :param v: list of Custom Color
        :return: None
        """
        self.query(ReadWrite.Write, Command.CustomColor, v.to_bytes())

    def reset_color(self):
        """
        Reset Color
        :return: None
        """
        self.query(ReadWrite.Write, Command.ResetColor)

    # VIDEO INPUT MANAGEMENT

    @property
    def auto_select(self):
        """
        Get Auto Select
        :return: Auto Select of State type
        """
        return State(self.query(ReadWrite.Read, Command.AutoSelect))

    @auto_select.setter
    def auto_select(self, v):
        """
        Set Auto Select
        :param v: Auto Select of State type
        :return: None
        """
        self.query(ReadWrite.Write, Command.AutoSelect, v.value)

    @property
    def video_input_caps(self):
        """
        Get Video Input Capabilities
        :return: ???
        """
        return self.query(ReadWrite.Read, Command.VideoInputCaps)

    @property
    def video_input(self):
        """
        Get Video Input
        :return: Video Input of VideoInput type
        """
        return VideoInput(self.query(ReadWrite.Read, Command.VideoInput))

    @video_input.setter
    def video_input(self, v):
        """
        Set Video Input
        :param v: Video Input of VideoInput type
        :return: None
        """
        self.query(ReadWrite.Write, Command.VideoInput, v.value)

    # PIP/PBP MANAGEMENT

    @property
    def pxp_mode(self):
        """
        Get PxP Mode
        :return: PxP Mode of PxPMode type
        """
        return State(self.query(ReadWrite.Read, Command.PxPMode))

    @pxp_mode.setter
    def pxp_mode(self, v):
        """
        Set PxP Mode
        :param v: PxP Mode of PxPMode type
        :return: None
        """
        self.query(ReadWrite.Write, Command.PxPMode, v.value)

    def get_pxp_sub_input(self, win):
        """
        Get PxP Sub Input
        :param win: Window of Window type to Get
        :return: PxP Sub Input of VideoInput type
        """
        return VideoInput(self.query(ReadWrite.Read, Command.PxPSubInput, win.value))

    @property
    def pxp_sub_input_win1(self):
        """
        Get PxP Sub Input of Window 1
        :return: PxP Sub Input of VideoInput type
        """
        return self.get_pxp_sub_input(win=Window.Window1)

    @property
    def pxp_sub_input_win2(self):
        """
        Get PxP Sub Input of Window 2
        :return: PxP Sub Input of VideoInput type
        """
        return self.get_pxp_sub_input(win=Window.Window2)

    @property
    def pxp_sub_input_win3(self):
        """
        Get PxP Sub Input of Window 1
        :return: PxP Sub Input of VideoInput type
        """
        return self.get_pxp_sub_input(win=Window.Window3)

    @property
    def pxp_sub_input_win4(self):
        """
        Get PxP Sub Input of Window 4
        :return: PxP Sub Input of VideoInput type
        """
        return self.get_pxp_sub_input(win=Window.Window4)

    def set_pxp_sub_input(self, win, v):
        """
        Set PxP Sub Input
        :param win: Window of Window type to Set
        :param v: PxP Sub Input of VideoInput type
        :return: None
        """
        self.query(ReadWrite.Write, Command.PxPSubInput, bytearray().join(win.value).join(v.value))

    @pxp_sub_input_win1.setter
    def pxp_sub_input_win1(self, v):
        """
        Set PxP Sub Input of Window 1
        :param v: PxP Sub Input of VideoInput type
        :return: None
        """
        self.set_pxp_sub_input(win=Window.Window1, v=v)

    @pxp_sub_input_win2.setter
    def pxp_sub_input_win2(self, v):
        """
        Set PxP Sub Input of Window 2
        :param v: PxP Sub Input of VideoInput type
        :return: None
        """
        self.set_pxp_sub_input(win=Window.Window2, v=v)

    @pxp_sub_input_win3.setter
    def pxp_sub_input_win3(self, v):
        """
        Set PxP Sub Input of Window 3
        :param v: PxP Sub Input of VideoInput type
        :return: None
        """
        self.set_pxp_sub_input(win=Window.Window3, v=v)

    @pxp_sub_input_win4.setter
    def pxp_sub_input_win4(self, v):
        """
        Set PxP Sub Input of Window 4
        :param v: PxP Sub Input of VideoInput type
        :return: None
        """
        self.set_pxp_sub_input(win=Window.Window4, v=v)

    @property
    def pxp_location(self):
        """
        Get PxP Location
        :return: PxP Location of PxPLocation type
        """
        return PxPLocation(self.query(ReadWrite.Read, Command.PxPLocation))

    @pxp_location.setter
    def pxp_location(self, v):
        """
        Set PxP Location
        :param v: PxP Location of PxPLocation type
        :return: None
        """
        self.query(ReadWrite.Write, Command.PxPLocation, v.value)

    # OSD MANAGEMENT

    @property
    def osd_transparency(self):
        """
        Get OSD Transparency
        :return: OSD Transparency of int type
        """
        return int.from_bytes(self.query(ReadWrite.Read, Command.OSDTransparency), endian)

    @osd_transparency.setter
    def osd_transparency(self, v):
        """
        Set OSD Transparency
        :param v: OSD Transparency of int type
        :return: None
        """
        if v not in range(0, 100):
            raise ValueError
        self.query(ReadWrite.Write, Command.OSDTransparency, v.to_bytes(DataLength.OSDTransparency, endian))

    @property
    def osd_language(self):
        """
        Get OSD Language
        :return: OSD Language of Language type
        """
        return Language(self.query(ReadWrite.Read, Command.OSDLanguage))

    @osd_language.setter
    def osd_language(self, v):
        """
        Set OSD Language
        :param v: LSD Language of Language type
        :return: None
        """
        self.query(ReadWrite.Write, Command.OSDLanguage, v.value)

    @property
    def osd_timer(self):
        """
        Get OSD Timer
        :return: OSD Time of int type
        """
        return int.from_bytes(self.query(ReadWrite.Read, Command.OSDTimer), endian)

    @osd_timer.setter
    def osd_timer(self, v):
        """
        Set OSD Timer
        :param v: OSD Timer of int type
        :return: None
        """
        if v not in range(5, 60):
            raise ValueError
        self.query(ReadWrite.Write, Command.OSDTimer, v.to_bytes(DataLength.OSDTimer, endian))

    @property
    def osd_button_lock(self):
        """
        Get OSD Button Lock
        :return: OSD Button Lock of State type
        """
        return State(self.query(ReadWrite.Read, Command.OSDButtonLock))

    @osd_button_lock.setter
    def osd_button_lock(self, v):
        """
        Set OSD Button Lock
        :param v: OSD Button Lock of State type
        :return: None
        """
        self.query(ReadWrite.Write, Command.OSDButtonLock, v.value)

    def reset_osd(self):
        """
        Reset OSD
        :return: None
        """
        self.query(ReadWrite.Write, Command.ResetOSD)

    # SYSTEM MANAGEMENT

    @property
    def version_firmware(self):
        """
        Get Version Firmware
        :return: Version Firmware of string type
        """
        return str(self.query(ReadWrite.Read, Command.VersionFirmware))

    @property
    def ddcci(self):
        """
        Get DDCCI
        :return: DDCCI of State type
        """
        return State(self.query(ReadWrite.Read, Command.DDCCI))

    @ddcci.setter
    def ddcci(self, v):
        """
        Set DDCCI
        :param v: DDCCI of State type
        :return: None
        """
        self.query(ReadWrite.Write, Command.DDCCI, v.value)

    @property
    def lcd_conditioning(self):
        """
        Get LCD Conditioning
        :return: LCD Conditioning of State type
        """
        return State(self.query(ReadWrite.Read, Command.LCDConditioning))

    @lcd_conditioning.setter
    def lcd_conditioning(self, v):
        """
        Set LCD Conditioning
        :param v: LCD Conditioning of State type
        :return: None
        """
        self.query(ReadWrite.Write, Command.LCDConditioning, v.value)

    def factory_reset(self):
        """
        Factory Reset
        :return: None
        """
        self.query(ReadWrite.Write, Command.FactoryReset)


def get_func(args):
    print(P4317Q(s=args.device).get_value(args.type[0]))


def set_func(args):
    P4317Q(s=args.device).set_value(args.type[0], v=args.value)


def up_func(args):
    P4317Q(s=args.device).set_value(args.type[0], ud=UpDown.Up)


def down_func(args):
    P4317Q(s=args.device).set_value(args.type[0], ud=UpDown.Down)


def search_func(args):
    class FakeCommand(object):
        def __init__(self, v):
            self.value = v

    p4317q = P4317Q(s=args.device)
    for c in range(0, 0xff):
        try:
            print('{} : {}'.format(hex(c), p4317q.query(rw=ReadWrite.Read, cmd=FakeCommand(bytes([c])))))
        except P4317qError:
            pass


def main():
    """
    Main Function
    :return: None
    """
    # Setup Parser
    parser = argparse.ArgumentParser(description='DELL P4317Q Monitor Controller.',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--device', dest='device', default='/dev/ttyS0', help='serial device name.')
    parser.add_argument('--version', action='version', version='%(prog)s 1.0.0')
    subparsers = parser.add_subparsers()
    parser_get = subparsers.add_parser('get', description='get value.')
    parser_get.add_argument('--type', nargs=1, metavar='TYPE', dest='type', help='setting type.', required=True)
    parser_get.set_defaults(func=get_func)
    parser_set = subparsers.add_parser('set', description='set value.',)
    parser_set.add_argument('--type', nargs=1, metavar='TYPE', dest='type', help='setting type.', required=True)
    parser_set.add_argument('--value', nargs=1, metavar='VALUE', dest='value', help='setting value.', required=True)
    parser_set.set_defaults(func=set_func)
    parser_up = subparsers.add_parser('up', description='up value.')
    parser_up.add_argument('--type', nargs=1, metavar='TYPE', dest='type', help='setting type.', required=True)
    parser_up.set_defaults(func=up_func)
    parser_down = subparsers.add_parser('down', description='down value.')
    parser_down.add_argument('--type', nargs=1, metavar='TYPE', dest='type', help='setting type.', required=True)
    parser_down.set_defaults(func=down_func)
    parser_search = subparsers.add_parser('search')
    parser_search.set_defaults(func=search_func)
    args = parser.parse_args()

    # Execute Command
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
