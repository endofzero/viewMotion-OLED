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
* Dynamic Image sizes for motion capture (currently just 640x480)

# Usage

Usage: viewMotion-OLED.py [options] file

Options:

  -h, --help            
                        Show this help message and exit

  -p, --print           
                        Print Debug Information

  -v VELOCITY, --velocity=VELOCITY

                        This is the speed (in px) the animation moves (default: -1 = 128 moves/cycle)

  -c CYCLE, --cycle=CYCLE

                        This is the number of animation cycles before the graphics flip (to prevent burn-in)

  -s SPEED, --speed=SPEED

                        Speed in Seconds that each cycle stalls for (default: 1)

  -d FILE, --dbconfig=FILE
                        
                        Location of the Database config file for the MySQL credentials (default: db_config.ini)


# Information

Motion SQL query

			sql_query insert into security(camera, event_number, filename, frame, file_type, changed_pixels, noise_level, motion_width, motion_height, motion_x, motion_y, time_stamp, event_time_stamp) values('%t', '%v', '%f', '%q', '%n', '%D', '%N', '%i', '%J', '%K', '%L', '%Y-%m-%d %T', '%C')


Based on a 640 x 480 image
