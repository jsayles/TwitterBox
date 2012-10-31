#!/usr/bin/python

import settings
import RPi.GPIO as GPIO
import tweetstream
import time

def main():
  # Initialise display
  GPIO.setmode(GPIO.BCM)       # Use BCM GPIO numbers
  GPIO.setup(LCD_E, GPIO.OUT)  # E
  GPIO.setup(LCD_RS, GPIO.OUT) # RS
  GPIO.setup(LCD_D4, GPIO.OUT) # DB4
  GPIO.setup(LCD_D5, GPIO.OUT) # DB5
  GPIO.setup(LCD_D6, GPIO.OUT) # DB6
  GPIO.setup(LCD_D7, GPIO.OUT) # DB7
  lcd_init()

  # Setup the alert light
  GPIO.setup(LIGHT_PIN, GPIO.OUT) 
  GPIO.output(LIGHT_PIN, GPIO.LOW)

  # A little feedback 
  for w in TWITTER_TRACK:
    print "Watching twitter for " + w
    write_lcd("Watching for", w)

  while True:
    try:
      stream = tweetstream.FilterStream(TWITTER_USER, TWITTER_PASS, track=TWITTER_TRACK)
      for tweet in stream:
        author = tweet['user']['screen_name']
        text = tweet['text']
        print "@" + author + ": " + text
        write_lcd("New Tweet!", "@" + author)
        GPIO.output(LIGHT_PIN, GPIO.HIGH)
        time.sleep(10)
        GPIO.output(LIGHT_PIN, GPIO.LOW)
        write_lcd("Watching Twitter", "...")
    except tweetstream.ConnectionError, e:
      print "Disconnected from twitter. Reason:", e.reason

def write_lcd(line1, line2):
  lcd_byte(LCD_LINE_1, LCD_CMD)
  lcd_string(line1)
  lcd_byte(LCD_LINE_2, LCD_CMD)
  lcd_string(line2)

def lcd_init():
  # Initialise display
  lcd_byte(0x33,LCD_CMD)
  lcd_byte(0x32,LCD_CMD)
  lcd_byte(0x28,LCD_CMD)
  lcd_byte(0x0C,LCD_CMD)  
  lcd_byte(0x06,LCD_CMD)
  lcd_byte(0x01,LCD_CMD)  

def lcd_string(message):
  # Send string to display

  message = message.ljust(LCD_WIDTH," ")  

  for i in range(LCD_WIDTH):
    lcd_byte(ord(message[i]),LCD_CHR)

def lcd_byte(bits, mode):
  # Send byte to data pins
  # bits = data
  # mode = True  for character
  #        False for command

  GPIO.output(LCD_RS, mode) # RS

  # High bits
  GPIO.output(LCD_D4, False)
  GPIO.output(LCD_D5, False)
  GPIO.output(LCD_D6, False)
  GPIO.output(LCD_D7, False)
  if bits&0x10==0x10:
    GPIO.output(LCD_D4, True)
  if bits&0x20==0x20:
    GPIO.output(LCD_D5, True)
  if bits&0x40==0x40:
    GPIO.output(LCD_D6, True)
  if bits&0x80==0x80:
    GPIO.output(LCD_D7, True)

  # Toggle 'Enable' pin
  time.sleep(E_DELAY)    
  GPIO.output(LCD_E, True)  
  time.sleep(E_PULSE)
  GPIO.output(LCD_E, False)  
  time.sleep(E_DELAY)      

  # Low bits
  GPIO.output(LCD_D4, False)
  GPIO.output(LCD_D5, False)
  GPIO.output(LCD_D6, False)
  GPIO.output(LCD_D7, False)
  if bits&0x01==0x01:
    GPIO.output(LCD_D4, True)
  if bits&0x02==0x02:
    GPIO.output(LCD_D5, True)
  if bits&0x04==0x04:
    GPIO.output(LCD_D6, True)
  if bits&0x08==0x08:
    GPIO.output(LCD_D7, True)

  # Toggle 'Enable' pin
  time.sleep(E_DELAY)    
  GPIO.output(LCD_E, True)  
  time.sleep(E_PULSE)
  GPIO.output(LCD_E, False)  
  time.sleep(E_DELAY)   

if __name__ == '__main__':
  main()
