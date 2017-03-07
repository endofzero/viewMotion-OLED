#!/usr/bin/env python
# Version 1.1
from __future__ import division
import math
import time
import psutil
import rrdtool
import numpy as np
import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306
import optparse
import MySQLdb
import os
import datetime
import gc
import ConfigParser

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from subprocess import PIPE, Popen
from array import array
from datetime import timedelta

db_settings = ConfigParser.ConfigParser()


usage = "usage: %prog [options] file"
parser = optparse.OptionParser(usage=usage, description=__doc__)

today = datetime.date.today()

usage = "usage: %prog [options] file"
parser = optparse.OptionParser(usage=usage, description=__doc__)

parser.add_option('-p', '--print', action="store_true",
                   help='Print Debug Information', default=False, dest='debug')
parser.add_option('-v', '--velocity', action="store",
                   help='This is the speed (in px) the animation moves (default: -1 = 128 moves/cycle) ', dest='velocity', default=-1)
parser.add_option('-c', '--cycle', action="store",
                   help='This is the number of animation cycles before the graphics flip (to prevent burn-in)', dest='cycle', default=2)
parser.add_option('-s', '--speed', action="store",
                   help='Speed in Seconds that each cycle stalls for (default: 1)', dest='speed', default=1)
parser.add_option('-d', '--dbconfig', action="store",
                   help='Location of the ini file storing the credentials to connect to the MySQL database (default: db_config.ini)', dest='dbconfig', default='db_config.ini')

options, args = parser.parse_args()

today = datetime.date.today()

DEBUG = False

if options.debug == True:
    DEBUG = True
else:
    DEBUG = False

if DEBUG:
    print 'Options: ' + str(options)
    print 'Args: ' + str(args)

db_settings.read(options.dbconfig)

db_host = db_settings.get('Database','Host')
db_username = db_settings.get('Database','Username')
db_password = db_settings.get('Database','Password')
db_database = db_settings.get('Database','Database')

if DEBUG:
    print 'DB_HOST: ' + str(db_host)
    print 'DB_Username: ' + str(db_username)
    print 'DB_Password: ' + str(db_password)
    print 'DB_Database: ' + str(db_database)

def get_cpu_temperature():
        process = Popen (['vcgencmd', 'measure_temp'], stdout=PIPE)
        output, _error = process.communicate()
        return float(output[output.index('=') + 1:output.rindex("'")])

def render_uptime(draw,event_flip):
    # Calculate Uptime
    with open('/proc/uptime', 'r') as f:
        uptime_seconds = float(f.readline().split()[0])
        uptime_raw = timedelta(seconds = uptime_seconds)
#        print "uptime_raw " + str(uptime_raw)
#        print "uptime_raw.days " + str(uptime_raw.days)
    if (uptime_raw.days == 1):
#        print str(uptime_raw).replace(" day, ", ":")
        out = str(uptime_raw).replace(" day, ", ":")
#        print 'out ' + str(out)
    elif (uptime_raw.days > 1):
#        print str(uptime_raw).replace(" days, ", ":")
        out = str(uptime_raw).replace(" days, ", ":")
#        print 'out ' + str(out)
    else:
        out = "0:" + str(uptime_raw)
    outAr = out.split(':')
#    print 'outAr ' + str(outAr)
    outAr = ["%02d" % (int(float(x))) for x in outAr]
    out   = ":".join(outAr)
    uptime_string = str(out)

    if event_flip:
    # Draw Uptime
        draw.text((0, -2), str(uptime_string), font=font, fill=255)
    else:
        draw.text((0, 7), str(uptime_string), font=font, fill=255)
    return;

def render_time(draw,event_flip):
    # Draw Time.
    if event_flip:
        draw.text((width-48, -2), time.strftime("%H:%M:%S"), font=font, fill=1)
    else:
        draw.text((width-48, 7), time.strftime("%H:%M:%S"), font=font, fill=1)
    return;

def render_temperature(draw,event_flip):
    # Get CPU Temperature
    cpu_temperature = get_cpu_temperature()
    cpu_average = os.getloadavg()

    # Draw Temperature
    if event_flip:
        draw.text((0, 6), str(round(cpu_temperature,1)) + 'c ' + str(round(cpu_average[0],2)) + ' ' + str(round(cpu_average[1],2)) + ' ' + str(round(cpu_average[2],2)), font=font, fill=1)
    else:
        draw.text((0, -2), str(round(cpu_temperature,1)) + 'c ' + str(round(cpu_average[0],2)) + ' ' + str(round(cpu_average[1],2)) + ' ' + str(round(cpu_average[2],2)), font=font, fill=1)
    return;



def render_motion_stats(draw, event_number, event_time, event_score,event_flip):
    if event_flip:
        draw.text((0, 16), '   Event #', font=font, fill=1)
        draw.text((0, 24), str(event_number), font=font, fill=1)
        draw.text((0, 32), '  Evt Time', font=font, fill=1)
        draw.text((0, 40), str(event_time), font=font, fill=1)
        draw.text((0, 48), '     Score', font=font, fill=1)
        draw.text((0, 54), str(event_score), font=font, fill=1)
    else:
        draw.text((65, 16), '   Event #', font=font, fill=1)
        draw.text((65, 24), str(event_number), font=font, fill=1)
        draw.text((65, 32), '  Evt Time', font=font, fill=1)
        draw.text((65, 40), str(event_time), font=font, fill=1)
        draw.text((65, 48), '     Score', font=font, fill=1)
        draw.text((65, 54), str(event_score), font=font, fill=1)
    return;

def render_motion_box(draw,event_flip):
    #render the preview area
    #DIM: 63x47 - 63,16:127:63
    if event_flip:
        # Upper Left
        draw.rectangle((63, 16 , 63, 18), outline=255, fill=0)
        draw.rectangle((63, 16 , 65, 16), outline=255, fill=0)
        # Upper Right
        draw.rectangle((126, 16 , 126, 18), outline=255, fill=0)
        draw.rectangle((126, 16 , 125, 16), outline=255, fill=0)
        # Lower Right
        draw.rectangle((126, 63 , 125, 63), outline=255, fill=0)
        draw.rectangle((126, 61 , 126, 63), outline=255, fill=0)
        # Lower Left
        draw.rectangle((63, 63 , 63, 61), outline=255, fill=0)
        draw.rectangle((63, 63 , 65, 63), outline=255, fill=0)
    else:
        # Upper Left
        draw.rectangle((0, 16 , 0, 18), outline=255, fill=0)
        draw.rectangle((0, 16 , 2, 16), outline=255, fill=0)
        # Upper Right
        draw.rectangle((63, 16 , 63, 18), outline=255, fill=0)
        draw.rectangle((63, 16 , 62, 16), outline=255, fill=0)
        # Lower Right
        draw.rectangle((63, 63 , 62, 63), outline=255, fill=0)
        draw.rectangle((63, 61 , 63, 63), outline=255, fill=0)
        # Lower Left
        draw.rectangle((0, 63 , 0, 61), outline=255, fill=0)
        draw.rectangle((0, 63 , 2, 63), outline=255, fill=0)
    return;

def render_motion_event(draw,target_size_width,target_size_height,target_center_x,target_center_y,event_flip):

    if event_flip:
        window_offset_x = 63
        window_offset_y = 16
    else:
        window_offset_x = 0
        window_offset_y = 16
#    target_size_width = 7
#    target_size_height = 2
#    target_center_x = 39
#    target_center_y = 16
    target_size_width = np.floor((target_size_width/640)*63)
    target_size_height = np.floor((target_size_height/480)*47)
    target_center_x = np.floor((target_center_x/640)*63)
    target_center_y = np.floor((target_center_y/480)*47)

    calc_start_x = np.floor(window_offset_x+target_center_x)-(target_size_width/2)
    calc_start_y = np.floor(window_offset_y+target_center_y)-(target_size_height/2)

    calc_end_x = int(calc_start_x + target_size_width)
    calc_end_y = int(calc_start_y + target_size_height)

    if DEBUG:
        print 'C StartX ' + str(calc_start_x)
        print 'C StartY ' + str(calc_start_y)
        print 'C EndX ' + str(calc_end_x)
        print 'C EndY ' + str(calc_end_y)

    draw.rectangle((calc_start_x, calc_start_y , calc_end_x, calc_end_y), outline=255, fill=0)
    return;


def pull_event_list():
    gc.collect()

    db = MySQLdb.connect(host=db_host, # your host, usually localhost
                     user=db_username, # your username
                     passwd=db_password, # your password
                     db=db_database) # name of the data base


    cur = db.cursor()
    # Get new date
    today = datetime.date.today()
    # Query for motion data
    cur.execute("SELECT * FROM security WHERE EXTRACT(DAY FROM time_stamp)="+today.strftime('%d')+" AND EXTRACT(MONTH FROM time_stamp)="+today.strftime('%m')+" AND EXTRACT(YEAR FROM time_stamp)="+today.strftime('%Y')+" AND file_type = 1 ORDER BY time_stamp ASC")
    # Store the output
    sql_data = cur.fetchall()

    # Parse the output
    if DEBUG:
        print "SQL Query: " + str("SELECT * FROM security WHERE EXTRACT(DAY FROM time_stamp)="+today.strftime('%d')+" AND EXTRACT(MONTH FROM time_stamp)="+today.strftime('%m')+" AND EXTRACT(YEAR FROM time_stamp)="+today.strftime('%Y')+" AND file_type = 1 ORDER BY time_stamp ASC")
        print("Daily Events: " + str(len(sql_data)))
        print("SQL Data: " + str(sql_data))

        if len(sql_data) == 0:
            print "Zero Events"
        else:
            for row in sql_data :
                print row[1], str(row[2]).split('/'), row[5], row[7], row[8], row[9], row[10], str(row[11]).split(' ')
                filename = row[2].split('/')[8]
                print filename.split('-')
    return sql_data;

data_packet = pull_event_list()

if DEBUG:
    print 'Data Packet: ' + str(data_packet)

# Raspberry Pi pin configuration:
RST = 24
# Note the following are only used with SPI:
DC = 23
SPI_PORT = 0
SPI_DEVICE = 0

WAIT_MS = float(options.speed)
BOUNCE_UP = False

disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST, i2c_address=0x3c)

# Initialize library.
disp.begin()

# Get display width and height.
width = disp.width
height = disp.height

# Clear display.
disp.clear()
disp.display()

# Create image buffer.
# Make sure to create image with mode '1' for 1-bit color.
image = Image.new('1', (width, height))

# Load default font.
font = ImageFont.load_default()
# Create drawing object.
draw = ImageDraw.Draw(image)

# Set animation properties
velocity = options.velocity
startpos = width

# Animate text moving in sine wave.
print('Press Ctrl-C to quit.')
pos = startpos
ypos = -4
ball_size = 2

event_count= 0
event_count_max=len(data_packet)

event_cycle = 1
event_flip = True

#Start of Cycle
while True:


    # Clear image buffer by drawing a black filled box.
    draw.rectangle((0,0,width,height), outline=0, fill=0)
    if DEBUG:
        print data_packet[event_count]
    # Animation top section with dot
    # Move the ball down
    if pos <= 75:
        if ypos < 8:
            BOUNCE_UP = False
        if ypos > 12:
            BOUNCE_UP = True
        if ypos == 8:
            BOUNCE_UP = False
    else:
        if ypos > 4:
            BOUNCE_UP = True
        if ypos == 0:
            BOUNCE_UP = False
    if BOUNCE_UP == True:
        ypos += -1
    else:
        ypos += 1

    render_uptime(draw,event_flip)
    render_time(draw,event_flip)
    render_temperature(draw,event_flip)
    # Draw the ball
    draw.ellipse((pos, ypos, pos+ball_size, ypos+ball_size), outline=1, fill=0)

    # Draw Target area - 4:3 aspect ratio 63 x 47 px
    render_motion_box(draw,event_flip)
    try:
        render_motion_stats(draw,str(event_count+1) + '/' + str(len(data_packet)),str(data_packet[event_count][12].strftime('%H:%M:%S')),str(data_packet[event_count][5]),event_flip)
    except:
	if DEBUG:
	    print("Render_motion_stats Errored")
        render_motion_stats(draw,'0/0','0:00:00:00','0',event_flip)
    try:
        render_motion_event(draw,(data_packet[event_count][7]),(data_packet[event_count][8]),(data_packet[event_count][9]),(data_packet[event_count][10]),event_flip)
    except:
	if DEBUG:
	    print("Render_motion_event Errored")
        render_motion_event(draw,1,1,1,1,event_flip)

    # Move position for next frame.
    pos += int(velocity)
    if DEBUG:
        print 'Event Count: ' + str(event_count)
        print 'Event Count Max: ' + str(event_count_max)
        print 'Event Cycle: ' + str(event_cycle)
        print 'Event_Flip: ' + str(event_flip)
    # Once the ball reaches the end, a full cycle is considered to be done. after N cycles the graphics will flip
    # to the opposite sides to try and prevent screen burn-in over long use of an OLED
    if pos < 0:
        pos = startpos
        # Move the Cycle Forward one, reset when it reaches two
        if event_cycle > int(options.cycle)-1:
            event_count_max = 0
            # Update the datapacket
#    	    print 'PreClear Data Packet Len: ' + str(len(data_packet))
	    data_packet = []
#    	    print 'Clear? Data Packet: ' + str(data_packet)
#    	    print 'AfterClear Data Packet Len: ' + str(len(data_packet))
            data_packet = pull_event_list()
#    	    print 'AfterLoad Data Packet: ' + str(data_packet)
	    event_count_max = len(data_packet)
#    	    print 'AfterLoad Event Count Max: ' + str(event_count_max)
	    # Start the counter back to zero
	    event_count = 0
            # Flip to the other side
            if event_flip == False:
                event_flip = True
            else:
                event_flip = False
            event_cycle = 1
        else:
            event_cycle += 1
        #reset the collection
	if DEBUG:
    	    print 'Data Packet: ' + str(data_packet)
    	    print 'Event Count: ' + str(event_count)
    	    print 'Event Count Max: ' + str(event_count_max)
    if ypos < 0:
        ypos = 0
    if event_count >= event_count_max-1:
        event_count = 0
    else:
        event_count += 1
    disp.image(image)
    disp.display()
    # Pause briefly before drawing next frame.
    time.sleep(WAIT_MS)

