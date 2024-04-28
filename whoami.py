#!/usr/bin/python3
""" DIYHA whoami
"""

# The MIT License (MIT)
#
# Copyright (c) 2024 parttimehacker@gmail.com
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

import logging.config
import time

from pkg_classes.configmodel import ConfigModel
from pkg_classes.statusmodel import StatusModel
from pkg_classes.ssd1306hal import SSD1306HAL

# Start logging and enable imported classes to log appropriately.

LOGGING_FILE = '/usr/local/whoami/logging.ini'
logging.config.fileConfig(fname=LOGGING_FILE, disable_existing_loggers=False)
LOGGER = logging.getLogger(__name__)
LOGGER.info('Application started: whoami')

# get the command line arguments

CONFIG = ConfigModel(LOGGING_FILE)
STATUS = StatusModel(LOGGING_FILE)
DISPLAY = SSD1306HAL(LOGGING_FILE)

INFO_INDEX = 0
MAX_INFO = 4

def update_information(index):
    STATUS.compute_averages()
    line0 = STATUS.host + " " + STATUS.ip_address

    match index:
        case 0:
            line1 = STATUS.osVersion
        case 1:
            line1 = STATUS.rpVersion
        case 2:
            line1 = STATUS.dict["cpu_usage"]
        case 3:
            line1 = STATUS.dict["cpu_temperature"]
        case _:
            line1 = STATUS.dict["disk_space"]

    DISPLAY.display_text(0, line0,fill="#128")
    DISPLAY.display_text(1, line1)
    DISPLAY.update_display()

if __name__ == '__main__':

    STATUS.collect_data()
    index = 0
    update_information(index)

    while True:
        time.sleep(1.0)
        STATUS.collect_data()
        if STATUS.computations > 0:
            index += 1
            if index > MAX_INFO:
                index = 0
            update_information(index)



