# Twitter settings
consumer_key="your consumer key"
consumer_secret="your consumer secret"
access_key = "your acces key"
access_secret = "your access secret"
track=["what", "you want", "to", "track"]

# Log file
LOG="twitterbox.log"

# Where did you plug in the light?
LIGHT_PIN = 4

# Define GPIO to LCD mapping
LCD_RS = 7
LCD_E  = 8
LCD_D4 = 25
LCD_D5 = 24
LCD_D6 = 23
LCD_D7 = 18

# Define some device constants
LCD_WIDTH = 16    # Maximum characters per line
LCD_CHR = True
LCD_CMD = False

LCD_LINE_1 = 0x80 # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0 # LCD RAM address for the 2nd line

# Timing constants
E_PULSE = 0.00005
E_DELAY = 0.00005

# Now get the local settings
from local_settings import *
