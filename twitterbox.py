#!/usr/bin/python

from settings import *
import RPi.GPIO as GPIO
import logging
import Queue
import threading
import tweepy
import time
import os

########################################################################
class CustomStreamListener(tweepy.StreamListener):
	#----------------------------------------------------------------------
	def __init__(self, queue, logger):
		tweepy.StreamListener.__init__(self)
		self.queue = queue
		self.logger = logger
		self.logger.debug("Twitter listener created")

	#----------------------------------------------------------------------
	def on_status(self, status):
		self.queue.put("@" + status.user.screen_name + ": " + status.text)

	#----------------------------------------------------------------------
	def on_error(self, status_code):
		if status_code == 420:
			self.logger.error("Hit the rate limit for twitter... sleeping for a minute")
			time.sleep(60)
		else:
			self.logger.error("Encountered error with status code: " + str(status_code))
		return True # Don't kill the stream

	#----------------------------------------------------------------------
	def on_timeout(self):
		self.logger.error("Timeout...")
		return True # Don't kill the stream

########################################################################
class Watcher(threading.Thread):
	#----------------------------------------------------------------------
	def __init__(self, queue, logger):
		threading.Thread.__init__(self)
		self.queue = queue
		self.logger = logger
		self.logger.debug("Twitter watcher created")
		self.auth = None
		self.api = None

	#----------------------------------------------------------------------
	def authenticate(self):
		self.logger.info("Authenticating to twitter")
		try:
			self.auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
			self.auth.set_access_token(access_key, access_secret)
			self.api = tweepy.API(self.auth)
		except Exception as e:
			self.logger.error("Could not authenticate: " + str(e))

	#----------------------------------------------------------------------
	def run(self):
		if not self.auth or not self.api:
			self.authenticate()
			
		try:
			listener = CustomStreamListener(self.queue, self.logger)
			stream = tweepy.streaming.Stream(self.auth, listener)
			self.logger.info("Starting twitter stream")
			stream.filter(track=track)
			self.logger.error("Twitter stream closed")
		except Exception as e:
			self.logger.error("Disconnected from twitter: " + str(e))

	#----------------------------------------------------------------------
	def getUserData(self):

		if not self.auth or not self.api:
			self.authenticate()

		try:
			user = self.api.get_user(screen_name)
			user_data = {"Screen Name:": screen_name,
				"Followers:": str(user.followers_count)}
			return user_data
		except Exception as e:
			self.logger.error("Could not get data for " + screen_name + ": " + str(e))


########################################################################
class Printer(threading.Thread):
	#----------------------------------------------------------------------
	def __init__(self, queue, logger):
		threading.Thread.__init__(self)
		self.queue = queue
		self.logger = logger
		self.logger.debug("Twitter printer created")

	#----------------------------------------------------------------------
	def run(self):
		while True:
			try:
				msg = self.queue.get()
				self.logger.info(msg)
				write_lcd("New Tweet!", msg)
				self.logger.debug("Light on...")
				GPIO.output(LIGHT_PIN, GPIO.HIGH)
				time.sleep(LIGHT_DELAY)
				self.logger.debug("Light off")
				GPIO.output(LIGHT_PIN, GPIO.LOW)
				write_lcd("Watching Twitter", "...")
				self.queue.task_done()
			except Exception as e:
				self.logger.error("Exception in printer: " + str(e))

########################################################################
def main():
	# Setup Logging
	logger = logging.getLogger('twitterbox')
	hdlr = logging.FileHandler(LOG)
	formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
	hdlr.setFormatter(formatter)
	logger.addHandler(hdlr) 
	if DEBUG:
		logger.setLevel(logging.DEBUG)
	else:
		logger.setLevel(logging.INFO)
	logger.info("Starting up...")

	# A little feedback 
	for w in track:
		logger.info("Watching twitter for " + w)

	# Not interested
	GPIO.setwarnings(False)

	# Initialise display
	GPIO.setmode(GPIO.BCM)	     # Use BCM GPIO numbers
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

	write_lcd("Watching Twitter", "...")

	queue = Queue.Queue()
	watcher = None
	printer = None
	loops = 0
	while True:
		loops = loops + 1
		logger.debug("Main Loop " + str(loops))

		# Make sure our twitter thread is alive and happy
		if not watcher or not watcher.is_alive():
			logger.info("Starting watcher thread")
        		watcher = Watcher(queue, logger)
        		watcher.setDaemon(True)
        		watcher.start()

		# Make sure our printing thread is alive and happy
		if not printer or not printer.is_alive():
			logger.info("Starting printer thread")
        		printer = Printer(queue, logger)
        		printer.setDaemon(True)
        		printer.start()

		# Throw some user data into the queue
		user_data = watcher.getUserData()
		for k,v in user_data.iteritems():
			logger.debug(k + " " + v)
			write_lcd(k, v)
			time.sleep(4)
	
		time.sleep(10)

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
	# mode = True	 for character
	#				 False for command

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
