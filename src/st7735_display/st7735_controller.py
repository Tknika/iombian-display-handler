#!/usr/bin/env python3

import logging

import digitalio
import board
import math
from PIL import Image, ImageDraw, ImageFont
import adafruit_rgb_display.st7735 as st7735

logger = logging.getLogger(__name__)


class ST7735Controller(object):

    cs_pin = digitalio.DigitalInOut(board.CE0)
    dc_pin = digitalio.DigitalInOut(board.D25)
    reset_pin = digitalio.DigitalInOut(board.D24)
    BAUDRATE = 24000000

    def __init__(self, rotation=270, max_font_size=11):
        self.rotation = rotation
        self.diplay = None
        self.display_width = None
        self.display_height = None
        self.font_cache = {}
        self.max_font_size = max_font_size

    def initialize(self):
        spi = board.SPI()

        self.display = st7735.ST7735R(spi, rotation=self.rotation, cs=ST7735Controller.cs_pin,
                                dc=ST7735Controller.dc_pin, rst=ST7735Controller.reset_pin,
                                baudrate=ST7735Controller.BAUDRATE)
        
        if self.display.rotation % 180 == 90:
            self.display_height = self.display.width
            self.display_width = self.display.height
        else:
            self.display_height = self.display.height
            self.display_width = self.display.width
   
    def shutdown(self, message=None):
        image = Image.new("RGB", (self.display_width, self.display_height))

        draw = ImageDraw.Draw(image)
        draw.rectangle((0, 0, self.display_width, self.display_height), fill=(0, 0, 0))
        self.display.image(image)

    def render_lines(self, lines):
        image = Image.new("RGB", (self.display_width, self.display_height))

        draw = ImageDraw.Draw(image)
        draw.rectangle((0, 0, self.display_width, self.display_height), fill=(255, 255, 255))
        self.display.image(image)
        
        num_lines = len(lines)
        size = math.floor(self.display_height / num_lines)
        font_size = size if size < self.max_font_size else self.max_font_size
        font = self.__get_font(font_size)
        height_step = size
        height_pos = 0

        for line in lines:
            draw.text((0, height_pos), line, font=font, fill=(0, 0, 0))
            height_pos += height_step

        self.display.image(image)

    def render_config(self, device_name, link, font_size=15):
        CONFIG_TITLE = "Unconfigured device"

        image = Image.new("RGB", (self.display_width, self.display_height))

        draw = ImageDraw.Draw(image)
        draw.rectangle((0, 0, self.display_width, self.display_height), fill=(255, 255, 255))

        font = self.__get_font(font_size)
     
        config_title_text_x, config_title_text_y = font.getsize(CONFIG_TITLE)
        device_name_text_x, device_name_text_y = font.getsize(device_name)

        device_name_pos_x = self.display_width//2 - device_name_text_x//2
        device_name_pos_y = config_title_text_y+1

        draw.text((0, 0), CONFIG_TITLE, font=font, fill=(0, 0, 0))
        draw.text((device_name_pos_x, device_name_pos_y), device_name, font=font, fill=(0, 0, 0))

        self.display.image(image)

        import qrcode
        img = qrcode.make(link, box_size=3, border=1).convert("RGB")

        y_start = self.display_width//2 - img.width//2
        self.display.image(img, y=y_start)

    def __get_font(self, font_size):
        cache = self.font_cache.get(font_size, None)
        if cache:
            return cache
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size)
        self.font_cache[font_size] = font
        return font