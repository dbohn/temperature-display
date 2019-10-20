from PIL import Image,ImageDraw,ImageFont
from datetime import datetime
import threading
from eink import EinkDisplay

class Screen(object):
    def __init__(self, sensors):
        self.epd = EinkDisplay(port=0, device=0)
        self.width = self.epd.width
        self.height = self.epd.height
        self.numButtons = 4
        self.statusBarHeight = 24
        self.statusBarPadding = 3
        self.image = None
        self.draw = None
        self.sensors = sensors
        self.renderLock = threading.RLock()

        self.fonts = {
            "measurement": ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 32),
            "description": ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 10),
            "toolbar": ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', self.statusBarHeight - 2 * self.statusBarPadding)
        }

    def button(self, text, position):
        cellWidth = self.width / self.numButtons
        buttonX = position * cellWidth
        buttonY = self.height - self.statusBarHeight
        cellHeight = self.statusBarHeight
        textWidth, textHeight = self.draw.textsize(text, self.fonts['toolbar'])
        offset = buttonX + (cellWidth - textWidth) / 2
        self.draw.text((offset, buttonY + ((cellHeight - textHeight) / 2)), text, font = self.fonts['toolbar'], fill = 0)
        if position > 0:
            self.draw.line((buttonX, 240, buttonX, 264), fill = 0)

    def measurement(self, temperature, trend, name, position):
        initialY = position * 50
        self.draw.text((10, initialY), temperature, font = self.fonts['measurement'], fill = 0)
        trendSymbol = '\u2192' # ->
        if trend is None:
            trendSymbol = '-'
        elif trend >= 1:
            trendSymbol = '\u2197' # ↗
        elif trend <= -1:
            trendSymbol = '\u2198' # ↘
        self.draw.text((10, initialY + 36), trendSymbol, font = self.fonts['description'], fill = 0)
        self.draw.text((10 + 15, initialY + 36), name, font = self.fonts['description'], fill = 0)
        self.draw.line((0,initialY + 50 ,176, initialY + 50), fill = 0)

    def renderToolbar(self):
        self.draw.line((0, self.height - self.statusBarHeight, self.width, self.height - self.statusBarHeight), fill = 0)
        self.button("\u27F3", 0)
        self.button("\u2190", 1)
        self.button("\u2192", 2)
        self.button("\u2699", 3)

    def renderTimestamp(self):
        now = datetime.today()
        timestamp = "{}.{}.{} {}:{}".format(now.day, now.month, now.year, now.hour, now.minute)
        textWidth, textHeight = self.draw.textsize(timestamp, self.fonts['description'])
        xOffset = (self.width - textWidth) / 2
        yPos = self.height - self.statusBarHeight - textHeight - 3
        self.draw.text((xOffset, yPos), timestamp, font = self.fonts['description'], fill = 0)

    def render(self):
        self.image = Image.new('1', (self.width, self.height), 255)
        self.draw = ImageDraw.Draw(self.image)

        for i, measurement in enumerate(self.sensors, start = 0):
            self.measurement(measurement.measurementValue(), measurement.trendValue(), measurement.name, i)

        self.renderToolbar()

        self.renderTimestamp()

        return self.image

    def encodeBuffer(self, image):
        buf = [0xFF] * ((self.width//8) * self.height)
        image_monocolor = image
        imwidth, imheight = image_monocolor.size
        pixels = image_monocolor.load()
        if(imwidth == self.width and imheight == self.height):
            for y in range(imheight):
                for x in range(imwidth):
                    # Set the bits for the column of pixels at the current position.
                    if pixels[x, y] == 0:
                        buf[(x + y * self.width) // 8] &= ~(0x80 >> (x % 8))
        elif(imwidth == self.height and imheight == self.width):
            for y in range(imheight):
                for x in range(imwidth):
                    newx = y
                    newy = self.height - x - 1
                    if pixels[x, y] == 0:
                        buf[(newx + newy*self.width) // 8] &= ~(0x80 >> (y % 8))
        return buf

    def update(self):
        self.renderLock.acquire()
        try:
            img = self.render()
            self.epd.display(self.encodeBuffer(self.render()))
        finally:
            self.renderLock.release()
        #self.epd.sleep()

    def shutdown(self):
        print("Shutting down")
        self.epd.sleep()