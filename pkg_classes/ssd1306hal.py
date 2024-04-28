#!/usr/bin/python3
""" Display 2 lines of status information """

# The MIT License (MIT)
#
# Copyright (c) 2019 parttimehacker@gmail.com
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import board
from PIL import Image, ImageDraw, ImageFont
import busio
import adafruit_ssd1306
import logging
import logging.config


class SSD1306HAL:
    """ Manage an st7789 LCD display with a hardware abstraction layer. """

    def __init__(self, logging_file):
        ''' initialize hardware and data elements '''
        logging.config.fileConfig(fname=logging_file, disable_existing_loggers=False)
        # Get the logger specified in the file
        self.logger = logging.getLogger(__name__)
        self.set_data_structures()
        self.init_ssd1306_display()

    def set_data_structures(self, ):
        self.row_text = ["", ""]
        self.row_Y_cord = [0, 16]
        self.font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
        self.row_font = [self.font, self.font]
        self.row_fill = [ "255", "255"]

    def init_ssd1306_display(self, ):
        # Create the I2C interface.
        i2c1 = busio.I2C(board.SCL, board.SDA)
        self.disp = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c1)

        # Clear display.
        self.disp.fill(0)
        self.disp.show()

        self.image = Image.new("1", (self.disp.width, self.disp.height))
        self.draw = ImageDraw.Draw(self.image)
        self.draw.rectangle((0, 0, self.disp.width, self.disp.height), outline=0, fill=0)
        self.font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
        self.clear_display()

    def clear_display(self):
        self.disp.fill(0)
        self.disp.show()

    def display_text(self, row=0, text="", font="Default", fill="#255"):
        if row >= 0 and row <= 1:
            self.row_text[row] = text
            if font == "Default":
                self.row_font[row] = self.font
            else:
                self.row_font[row] = font
            self.row_fill[row] = fill

    def update_display(self):
        self.draw.rectangle((0, 0, self.disp.width, self.disp.height), outline=0, fill=0)
        self.draw.text((0, -1), self.row_text[0], font=self.row_font[0], fill=self.row_fill[0])
        self.draw.text((0, 16), self.row_text[1], font=self.row_font[1], fill=self.row_fill[1])
        self.disp.image(self.image)
        self.disp.show()
