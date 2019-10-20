# Procedures to interact with the display were adapted from the demo script provided by waveshare for their
# eink displays! See https://github.com/waveshare/e-Paper

from gpiozero import SPIDevice
import time

# Display resolution
EPD_WIDTH       = 176
EPD_HEIGHT      = 264

RST_PIN         = 17
DC_PIN          = 25
CS_PIN          = 8
BUSY_PIN        = 24

PANEL_SETTING                               = 0x00
POWER_SETTING                               = 0x01
POWER_OFF                                   = 0x02
POWER_OFF_SEQUENCE_SETTING                  = 0x03
POWER_ON                                    = 0x04
POWER_ON_MEASURE                            = 0x05
BOOSTER_SOFT_START                          = 0x06
DEEP_SLEEP                                  = 0x07
DATA_START_TRANSMISSION_1                   = 0x10
DATA_STOP                                   = 0x11
DISPLAY_REFRESH                             = 0x12
DATA_START_TRANSMISSION_2                   = 0x13
PARTIAL_DATA_START_TRANSMISSION_1           = 0x14
PARTIAL_DATA_START_TRANSMISSION_2           = 0x15
PARTIAL_DISPLAY_REFRESH                     = 0x16
LUT_FOR_VCOM                                = 0x20
LUT_WHITE_TO_WHITE                          = 0x21
LUT_BLACK_TO_WHITE                          = 0x22
LUT_WHITE_TO_BLACK                          = 0x23
LUT_BLACK_TO_BLACK                          = 0x24
PLL_CONTROL                                 = 0x30
TEMPERATURE_SENSOR_COMMAND                  = 0x40
TEMPERATURE_SENSOR_CALIBRATION              = 0x41
TEMPERATURE_SENSOR_WRITE                    = 0x42
TEMPERATURE_SENSOR_READ                     = 0x43
VCOM_AND_DATA_INTERVAL_SETTING              = 0x50
LOW_POWER_DETECTION                         = 0x51
TCON_SETTING                                = 0x60
TCON_RESOLUTION                             = 0x61
SOURCE_AND_GATE_START_SETTING               = 0x62
GET_STATUS                                  = 0x71
AUTO_MEASURE_VCOM                           = 0x80
VCOM_VALUE                                  = 0x81
VCM_DC_SETTING_REGISTER                     = 0x82
PROGRAM_MODE                                = 0xA0
ACTIVE_PROGRAM                              = 0xA1
READ_OTP_DATA                               = 0xA2

class EinkDisplay(SPIDevice):
    def __init__(self, **spi_args):
        super().__init__(**spi_args)
        self._initHost()
        self._init()
        self.width = EPD_WIDTH
        self.height = EPD_HEIGHT

    def _initHost(self):
        self._spi._set_clock_mode(0b00)
        self._spi._interface.max_speed_hz = 2000000
        self.pin_factory.reserve_pins(self, RST_PIN, DC_PIN, BUSY_PIN)
        self._reset = self.pin_factory.pin(RST_PIN)
        self._reset.function = 'output'
        self._dc = self.pin_factory.pin(DC_PIN)
        self._dc.function = 'output'
        self._busy = self.pin_factory.pin(BUSY_PIN)
        self._busy.function = 'input'

    def _init(self):
        self.reset()
        self.sendCommand(POWER_SETTING)
        self.sendData(0x03)                  # VDS_EN, VDG_EN
        self.sendData(0x00)                  # VCOM_HV, VGHL_LV[1], VGHL_LV[0]
        self.sendData(0x2b)                  # VDH
        self.sendData(0x2b)                  # VDL
        self.sendData(0x09)                  # VDHR
        self.sendCommand(BOOSTER_SOFT_START)
        self.sendData(0x07)
        self.sendData(0x07)
        self.sendData(0x17)
        # Power optimization
        self.sendCommand(0xF8)
        self.sendData(0x60)
        self.sendData(0xA5)
        # Power optimization
        self.sendCommand(0xF8)
        self.sendData(0x89)
        self.sendData(0xA5)
        # Power optimization
        self.sendCommand(0xF8)
        self.sendData(0x90)
        self.sendData(0x00)
        # Power optimization
        self.sendCommand(0xF8)
        self.sendData(0x93)
        self.sendData(0x2A)
        # Power optimization
        self.sendCommand(0xF8)
        self.sendData(0xA0)
        self.sendData(0xA5)
        # Power optimization
        self.sendCommand(0xF8)
        self.sendData(0xA1)
        self.sendData(0x00)
        # Power optimization
        self.sendCommand(0xF8)
        self.sendData(0x73)
        self.sendData(0x41)
        self.sendCommand(PARTIAL_DISPLAY_REFRESH)
        self.sendData(0x00)
        self.sendCommand(POWER_ON)
        self.waitUntilIdle()

        self.sendCommand(PANEL_SETTING)
        self.sendData(0xAF)        # KW-BF   KWR-AF    BWROTP 0f
        self.sendCommand(PLL_CONTROL)
        self.sendData(0x3A)        # 3A 100HZ   29 150Hz 39 200HZ    31 171HZ
        self.sendCommand(VCM_DC_SETTING_REGISTER)
        self.sendData(0x12)

        self.setLut()

    lut_vcom_dc = [
        0x00, 0x00,
        0x00, 0x08, 0x00, 0x00, 0x00, 0x02,
        0x60, 0x28, 0x28, 0x00, 0x00, 0x01,
        0x00, 0x14, 0x00, 0x00, 0x00, 0x01,
        0x00, 0x12, 0x12, 0x00, 0x00, 0x01,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00
    ]
    lut_ww = [
        0x40, 0x08, 0x00, 0x00, 0x00, 0x02,
        0x90, 0x28, 0x28, 0x00, 0x00, 0x01,
        0x40, 0x14, 0x00, 0x00, 0x00, 0x01,
        0xA0, 0x12, 0x12, 0x00, 0x00, 0x01,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    ]
    lut_bw = [
        0x40, 0x08, 0x00, 0x00, 0x00, 0x02,
        0x90, 0x28, 0x28, 0x00, 0x00, 0x01,
        0x40, 0x14, 0x00, 0x00, 0x00, 0x01,
        0xA0, 0x12, 0x12, 0x00, 0x00, 0x01,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    ]
    lut_bb = [
        0x80, 0x08, 0x00, 0x00, 0x00, 0x02,
        0x90, 0x28, 0x28, 0x00, 0x00, 0x01,
        0x80, 0x14, 0x00, 0x00, 0x00, 0x01,
        0x50, 0x12, 0x12, 0x00, 0x00, 0x01,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    ]
    lut_wb = [
        0x80, 0x08, 0x00, 0x00, 0x00, 0x02,
        0x90, 0x28, 0x28, 0x00, 0x00, 0x01,
        0x80, 0x14, 0x00, 0x00, 0x00, 0x01,
        0x50, 0x12, 0x12, 0x00, 0x00, 0x01,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    ]

    def setLut(self):
        self.sendCommand(LUT_FOR_VCOM)               # vcom
        for count in range(0, 44):
            self.sendData(self.lut_vcom_dc[count])
        self.sendCommand(LUT_WHITE_TO_WHITE)         # ww --
        for count in range(0, 42):
            self.sendData(self.lut_ww[count])
        self.sendCommand(LUT_BLACK_TO_WHITE)         # bw r
        for count in range(0, 42):
            self.sendData(self.lut_bw[count])
        self.sendCommand(LUT_WHITE_TO_BLACK)         # wb w
        for count in range(0, 42):
            self.sendData(self.lut_bb[count])
        self.sendCommand(LUT_BLACK_TO_BLACK)         # bb b
        for count in range(0, 42):
            self.sendData(self.lut_wb[count])

    def sendCommand(self, command):
        self._dc.state = False
        self._spi.write([command])

    def sendData(self, data):
        self._dc.state = True
        self._spi.write([data])

    def reset(self):
        self._reset.state = True
        self.delayMs(200)
        self._reset.state = False
        self.delayMs(200)
        self._reset.state = True
        self.delayMs(200)
        pass

    def delayMs(self, duration):
        time.sleep(duration / 1000.0)

    def waitUntilIdle(self):
        while (self._busy.state == 0):
            self.sendCommand(0x71)
        self.delayMs(100)

    def clear(self, color=0xFF):
        self.sendCommand(DATA_START_TRANSMISSION_1)
        for i in range(0, self.width * self.height // 8):
            self.sendData(0xFF)
        self.sendCommand(DATA_START_TRANSMISSION_2)
        for i in range(0, self.width * self.height // 8):
            self.sendData(color)
        self.sendCommand(DISPLAY_REFRESH)
        self.waitUntilIdle()

    def display(self, image):
        self.sendCommand(DATA_START_TRANSMISSION_1)
        for i in range(0, self.width * self.height // 8):
            self.sendData(0xFF)
        self.sendCommand(DATA_START_TRANSMISSION_2)
        for i in range(0, self.width * self.height // 8):
            self.sendData(image[i])
        self.sendCommand(DISPLAY_REFRESH)
        self.waitUntilIdle()

    def sleep(self):
        self.sendCommand(0X50)
        self.sendData(0xf7)
        self.sendCommand(0X02)
        self.sendCommand(0X07)
        self.sendData(0xA5)