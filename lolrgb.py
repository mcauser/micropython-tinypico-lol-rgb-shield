"""
MicroPython TinyPICO LOL RGB Shield
https://github.com/mcauser/micropython-tinypico-lolrgb

MIT License
Copyright (c) 2021 Mike Causer

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from micropython import const
from time import sleep_ms
from neopixel import NeoPixel
from machine import Pin

__version__ = '0.0.3'

# very dim colours as these pixels are BRIGHT!
RED = (1,0,0)
YELLOW = (1,1,0)
GREEN = (0,1,0)
CYAN = (0,1,1)
BLUE = (0,0,1)
MAGENTA = (1,0,1)
BLACK = (0,0,0)

RGB = [RED,GREEN,BLUE]
RAINBOW = [RED,YELLOW,GREEN,CYAN,BLUE,MAGENTA]

# rgb matrix size 14 x 5
WIDTH = const(14)
HEIGHT = const(5)
DATA_PIN = const(14)

# some delay helpers
NO_PAUSE = const(0)
SHORT_PAUSE = const(20)
MEDIUM_PAUSE = const(50)
LONG_PAUSE = const(100)

CHAR_BOUNDARY = const(0)  # each letter is a different colour
WORD_BOUNDARY = const(1)  # each word is a different colour

# tomthumb ascii 32-127
_TOMTHUMB = (
    # 32-47
    b"\x0A\xD7\x12\x32\x80\x00"
    b"\x0A\xFC\x6A\x49\x20\x01"
    b"\x08\x56\x90\x4B\xF1\xC2"
    b"\x00\x7D\x28\x49\x24\x14"
    b"\x08\x54\x58\x32\x88\x10"
    # 48-63
    b"\xEB\xFB\xFF\xFC\x02\x27"
    b"\xA8\x9B\x21\xB5\x25\xD1"
    b"\xAB\xBF\xF9\xFC\x08\x0A"
    b"\xAA\x12\x69\xA5\x25\xD0"
    b"\xEB\xF3\xF9\xFC\x42\x22"
    # 64-80
    b"\x4B\x3D\xFB\xBC\xD9\x6A"
    b"\xB6\xCB\x24\xA8\xD9\xFD"
    b"\xFF\x4B\xFF\xE8\xE9\xFD"
    b"\x96\xCB\x25\xAA\xD9\x7D"
    b"\x77\x3D\xE3\xBD\x5F\x6A"
    # 81-95
    b"\xCB\x3F\x6D\xB7\xF1\xD0"
    b"\xB6\xC5\x6D\xB4\xC8\x68"
    b"\xD7\xA5\x6F\x49\x44\x40"
    b"\x9F\x15\x57\xAA\x42\x40"
    b"\x8E\xE4\xD5\xAB\xF1\xC7"
    # 96-112
    b"\x82\x02\x08\x88\x8C\x00"
    b"\x42\x02\xD3\x80\x44\x00"
    b"\x0F\x37\x7F\xC8\xD5\xF2"
    b"\x16\xCB\x91\xA8\xE5\xED"
    b"\x1F\x36\xD6\xAB\x5F\x6A"
    # 113-127
    b"\x00\x04\x00\x00\x35\x9F"
    b"\x4A\x3E\x00\x17\xA4\xB7"
    b"\xB7\xE5\x6D\xAD\xC0\x47"
    b"\xCE\x35\x7F\x47\x24\x87"
    b"\x86\x64\xD7\xBB\xB5\x87"
)
# 96 glyphs packed into 180 bytes

# 16 font chars per row, packed into 6 bytes (16*3 == 6*8)
# font is 5px tall, so each page consists of 5 sets of 6 bytes
_FONT_CHARS_PER_ROW = const(16)
_BYTES_PER_ROW = const(6)

_CHAR_WIDTH = const(3)   # font uses 5x3 characters
_SPACE_WIDTH = const(1)  # number of pixel columns between each letter
_CHAR_AND_SPACE = const(_CHAR_WIDTH + _SPACE_WIDTH)

_SPACE_CHAR = const(32)
_ZERO_CHAR = const(48)
_DEL_CHAR = const(127)

class LOLRGB:
    def __init__(self):
        self._pin = Pin(DATA_PIN, Pin.OUT)
        self._np = NeoPixel(self._pin, WIDTH * HEIGHT)
        self._delay_ms = MEDIUM_PAUSE
        self._color = RED
        self._boundary = CHAR_BOUNDARY

    def set_delay_ms(self, delay_ms, persist=True):
        # number of ms between each column of pixels drawn to the display
        delay_ms = int(delay_ms)
        if delay_ms < 0:
            raise ValueError('Please provide a delay >= 0')
        if persist:
            self._delay_ms = delay_ms
        else:
            return delay_ms

    def set_color(self, color, persist=True):
        # tuple (r,g,b) = one colour
        # list of tuples = cycle through colours
        color = self._colorify(color)
        if persist:
            self._color = color
        else:
            return color

    def set_boundary(self, boundary, persist=True):
        # when to move onto the next colour when cycling through colours
        if not CHAR_BOUNDARY <= boundary <= WORD_BOUNDARY:
            raise ValueError('Please provide a boundary (0-1)')
        if persist:
            self._boundary = boundary
        else:
            return boundary

    def write(self, string, color=None, delay_ms=None, boundary=None):
        try:
            self._write(string, color, delay_ms, boundary)
        except KeyboardInterrupt:
            self._np.fill(BLACK)
            self._np.write()

    def _colorify(self, color, top=True):
        # ensures its a valid single colour tuple or a list of colour tuples
        if top and isinstance(color, list):
            for c in color:
                self._colorify(c, False)
            if len(color) == 1:
                return color[0]
        elif not isinstance(color, tuple) or len(color) != 3:
            raise ValueError('Invalid color. Must be a tuple (r,g,b) or list of tuples [(r,g,b),(r,g,b)]')
        return color

    def _stringify(self, string):
        # ensures the string is printable
        if isinstance(string, str):
            return string
        if isinstance(string, (int, float)):
            return str(string)
        if isinstance(string, (bytearray, bytes)):
            return string.decode("utf-8")
        raise TypeError('Could not interpret string')

    def _write(self, string, color=None, delay_ms=None, boundary=None):
        string = self._stringify(string)

        #if len(string) == 0:
        # raise ValueError('Please provide a non-empty string')

        if color is None:
            color = self._color
        else:
            color = self.set_color(color, False)
        num_colors = 1 if isinstance(color, tuple) else len(color)

        if delay_ms is None:
            delay_ms = self._delay_ms
        else:
            delay_ms = self.set_delay_ms(delay_ms, False)

        if boundary is None:
            boundary = self._boundary
        else:
            boundary = self.set_boundary(boundary, False)

        # number of columns to be drawn
        str_len_with_space = len(string) * _CHAR_AND_SPACE

        # number of frames to draw, starting with the string offscreen right
        # and ending offscreen left
        frames = WIDTH + str_len_with_space

        # for colour cycling
        num_spaces = 0

        for frame in range(frames):
            self._np.fill(BLACK)

            # which column of pixels is currently being drawn
            # starts offscreen on the right and moves left on each frame
            cursor = WIDTH - frame

            # loop over each column that needs to be drawn
            column_from = max(cursor, 0)
            column_to = min(WIDTH, cursor + str_len_with_space)

            for column in range(column_from, column_to):
                # column number relative to the string
                str_column = column - cursor

                # which char of the string is being drawn
                char_index = str_column // _CHAR_AND_SPACE

                # column of font character including space (1-4)
                column_in_char = str_column % _CHAR_AND_SPACE

                # if multiple colours, detect word boundaries
                if num_colors > 1:
                    num_spaces = string.count(' ', 0, char_index)

                # 0=48, A=65, a=97
                ascii_code = ord(string[char_index])

                # font only supports chars 32-127, anything more or less gets a
                # hollow rect (zero) or a filled rect (del)
                if ascii_code < _SPACE_CHAR:
                    ascii_code = _ZERO_CHAR  # hollow rect
                elif ascii_code > _DEL_CHAR:
                    ascii_code = _DEL_CHAR  # filled rect

                # ascii_code 32 (space), nothing to draw, skip ahead to the next char
                if ascii_code == _SPACE_CHAR:
                    continue

                # only output font columns, skip spaces
                if column_in_char < _CHAR_WIDTH:
                    # which char offset in the font
                    font_position = ascii_code - _SPACE_CHAR

                    # offset of the column in the font
                    font_col = (font_position * _CHAR_WIDTH) + column_in_char

                    # the page in the font that contains this char column
                    # note: some chars span multiple bytes in the font
                    # so its calculated at a column level
                    font_page = font_position // _FONT_CHARS_PER_ROW

                    # which byte in the font contains this char column
                    font_index = (font_col // 8) + (font_page * 4 * _BYTES_PER_ROW)

                    # how many bits to shift the byte to get this char column
                    shift = 7 - (font_col % 8)

                    # determine the colour for this column
                    if num_colors == 1:
                        char_color = color
                    elif boundary == CHAR_BOUNDARY:
                        char_color = color[(char_index - num_spaces) % num_colors]
                    elif boundary == WORD_BOUNDARY:
                        char_color = color[num_spaces % num_colors]

                    # write column of pixel data
                    for h in range(HEIGHT):
                        self._np[column + WIDTH * h] = char_color if _TOMTHUMB[font_index + _BYTES_PER_ROW * h] >> shift & 1 else BLACK

            # draw the pixels
            self._np.write()

            # pause between each frame
            if delay_ms > 0:
                sleep_ms(delay_ms)
