# viewMotion-OLED
Uses a OLED to track motion events for the day along with other system statistics.


OLED Screen: Diymall 0.96" Inch Yellow Blue I2c IIC Serial Oled LCD LED Module 12864 128X64 for Arduino Display 51 Msp420 Stim32 SCR

https://www.amazon.com/gp/product/B00O2LLT30/ref=oh_aui_search_detailpage?ie=UTF8&psc=1

Installed the Adafruit SSD1306 and GPIO drivers to run it.


https://github.com/adafruit/Adafruit_SSD1306

https://github.com/adafruit/Adafruit_Python_GPIO

Screen is used to detach a terminal so it can run.

apt-get screen



TODO:

* Run as a daemon instead


# Usage

Usage: viewMotion-OLED.py [options] file

Options:

  -h, --help            show this help message and exit

  -p, --print           Print Debug Information

  -v VELOCITY, --velocity=VELOCITY

                        This is the speed (in px) the animation moves (default: -1 = 128 moves/cycle)

  -c CYCLE, --cycle=CYCLE

                        This is the number of animation cycles before the graphics flip (to prevent burn-in)

  -s SPEED, --speed=SPEED

                        Speed in Seconds that each cycle stalls for (default: 1)


