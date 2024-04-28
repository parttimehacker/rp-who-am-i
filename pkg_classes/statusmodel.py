#!/usr/bin/python3
""" DIYHA MQTT CPU and OS monitor """

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

import socket
import subprocess
from threading import Thread
from time import sleep
import psutil
from gpiozero import CPUTemperature
import logging
import logging.config
import RPi.GPIO as GPIO
from pkg_classes.ssd1306hal import SSD1306HAL


class StatusModel:
    """ Collect CPU and OS metrics. """

    def __init__(self, logging_file):
        ''' Setup MQTT topics and initialize data elements '''
        logging.config.fileConfig(fname=logging_file, disable_existing_loggers=False)
        # Get the logger specified in the file
        self.logger = logging.getLogger(__name__)
        # static or boot time data
        self.host = socket.gethostname()
        self.get_os_version()
        self.get_rp_version()
        self.get_ip_address()\
        # computations
        self.cpu_accumulator = 0.0
        self.celsius_accumulator = 0.0
        self.disk_free_accumulator = 0.0
        self.computations = 0.0
        # string computed average of measurements
        self.dict = {"cpu_usage": "", "cpu_temperature": "", "disk_space": ""}

    def get_server_name(self, ):
        ''' return local host name'''
        return self.host

    def collect_data(self, ):
        ''' collect one sample of data '''
        self.cpu_accumulator += psutil.cpu_percent(interval=1)
        cpu = CPUTemperature()
        self.celsius_accumulator += cpu.temperature
        disk = psutil.disk_usage('/')
        # Divide from Bytes -> KB -> MB -> GB
        self.disk_free_accumulator = round(disk.free / 1024.0 / 1024.0 / 1024.0, 1)
        self.computations += 1.0

    def compute_averages(self, ):
        ''' compute display data '''
        if self.computations > 0:
            cpu = self.cpu_accumulator / self.computations
            celsius = self.celsius_accumulator / self.computations
            free = self.disk_free_accumulator

            self.dict["cpu_usage"] = "CPU  " + "{0:.1f}".format(cpu) + "%"
            self.dict["cpu_temperature"] = "TEMP " + "{0:.1f}".format(celsius) +"%"
            self.dict["disk_space"] = "FREE: " + "{0:.1f}".format(free) + "GB"

            self.cpu_accumulator = 0.0
            self.celsius_accumulator = 0.0
            self.disk_free_accumulator = 0.0
            self.computations = 0.0

    def get_os_version(self, ):
        ''' get the current os version and make available to observers '''
        cmd = subprocess.Popen('cat /etc/os-release', shell=True, stdout=subprocess.PIPE)
        for line in cmd.stdout:
            if b'=' in line:
                key, value = line.split(b'=')
                if b'VERSION' == key:
                    data, chaff = value.split(b'\n')
                    strData = str(data, 'utf-8')
                    self.osVersion = strData.replace('"', '')
                    self.logger.info( self.osVersion )

    def get_rp_version(self, ):
        ''' get the current pi version and make available to observers '''
        cmd = subprocess.Popen('cat /proc/device-tree/model', shell=True, stdout=subprocess.PIPE)
        for line in cmd.stdout:
            key, value = line.split(b' Pi ')
            data, chaff = value.split(b'\x00')
            self.rpVersion = str(data, 'utf-8')
            self.logger.info( self.rpVersion )

    def get_ip_address(self, ):
        ''' get the current ip address and make available to observers '''
        self.host = socket.gethostname()
        ip = subprocess.check_output(["hostname", "-I"])
        # print(ip)
        ips = ip.decode("utf-8")
        # print(ips)
        ipss = ips.split(" ", 1)
        self.ip_address = ipss[0]
        self.logger.info( self.host )
        self.logger.info( self.ip_address )

