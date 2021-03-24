# MicroPython TinyPICO LOL RGB Shield

A MicroPython library for the TinyPICO LOL RGB Shield, by @tinyledmatrix

## Demo

![demo](docs/demo.gif)

```python
from lolrgb import *
display = LOLRGB()

display.write('TinyPICO LOL RGB Shield', RAINBOW)
```

## Examples

```python
from lolrgb import *
display = LOLRGB()

# persist settings so you dont need to add them to each write() call
display.set_color(RED)
display.set_delay_ms(SHORT_PAUSE)
display.set_boundary(CHAR_BOUNDARY)

# strings inheriting settings
display.write('Hello World')
display.write('This is really cool', RED, SHORT_PAUSE)

# providing a colour but not replacing settings
display.write('Red', RED)
display.write('Green', GREEN)
display.write('Blue', BLUE)

display.set_color(GREEN)
display.write('Green')

# you can provide colours using a color tuple (r,g,b)
display.write('Bright Red', (255,0,0), SHORT_PAUSE)
display.write('Bright White', (255,255,255), SHORT_PAUSE)
# congratulations, you are now blind for the next few minutes

# you can write at different speeds
display.write('Slow', RED, LONG_PAUSE)
display.write('Fast', RED, MEDIUM_PAUSE)
display.write('Faster', RED, SHORT_PAUSE)
display.write('Fastest', RED, NO_PAUSE)

# you can write in cycling colours by providing a list of color tuples
# eg. [(r,g,b), (r,g,b), (r,g,b)]
# colour cycles at word boundaries (spaces)
display.write('Red Blue Red Blue', [RED,BLUE], SHORT_PAUSE, WORD_BOUNDARY)
display.write('Red Green Blue', RGB, SHORT_PAUSE, WORD_BOUNDARY)
display.write('R G B R G B', RGB, SHORT_PAUSE, WORD_BOUNDARY)
display.write('Rainbow Coloured Words', RAINBOW, MEDIUM_PAUSE, WORD_BOUNDARY)

# colour cycles at character boundaries
display.write('RGB', RGB, SHORT_PAUSE, CHAR_BOUNDARY)
display.write('Rainbow Coloured Letters', RAINBOW, MEDIUM_PAUSE, CHAR_BOUNDARY)

# you can write bytes
display.write(b'Red')
display.write(bytearray(b'Red'))

# you can write ints
display.write(1234, RAINBOW, MEDIUM, CHAR_BOUNDARY)

# you can write floats
display.write(12.34, RAINBOW, MEDIUM, CHAR_BOUNDARY)
display.write(1/3, RAINBOW, MEDIUM, CHAR_BOUNDARY)

# all supported ascii chars (32-127)
display.write(''.join(chr(i) for i in range(32,128)), RED, FAST)

# unsupported chars
display.write(chr(31))   # < 32 == hollow rect
display.write(chr(128))  # > 127 == filled rect
```

## Links

* [micropython.org](http://micropython.org)
* [Buy a LOL RGB Shield](https://unexpectedmaker.com/shop/tinypico-shield-lolrgb)
* [Buy a TinyPICO](https://unexpectedmaker.com/shop/tinypico-usbc)
* [Buy a TinyPICO Side by Side](https://unexpectedmaker.com/shop/tinypico-mzffe-zatnr-zehhx)
* [TinyPICO Getting Started](https://www.tinypico.com/gettingstarted)
* [Arduino version](https://github.com/tinypico/tinypico-arduino)

## License

Licensed under the [MIT License](http://opensource.org/licenses/MIT).

Copyright (c) 2021 Mike Causer
