#!/usr/bin/env python3

 # =============================================================================
 #     Program:  BMF Monitor
 # Description:  Checks remote file URLs and fetches them if they have changed
 #
 #      Author:  Ben Yanke <ben@benyanke.com>
 #        repo:  github:borenstein/bmf-monitor
 #
 # =============================================================================

import os
import time
import datetime
from email.utils import parseaddr

class Filefetcher:

  # Bucket for data and hash storage
  data_bucket = None

  # URLs to check
  urls = []

  # Alerting email
  alert_email = None

  # Set this to true by using env var DEBUG
  debug = None

  # Hard coded confg options
  bucket_path_hashes = "hashes/sha256"
  bucket_path_data = "data"

  # Constructor
  def __init__(self):

    # Parses the env vars into the config vars
    self.loadConfig()
    self.loadKnownHashes()
    self.checkUrls()

    self.logInfo("Exiting successfully")

  ########################
  # Logging Methods
  ########################

  # Generic method to handle all log levels
  def logWrite(self,level,msg):
    # Don't print debug out of debug mode
    if level is not 'debug' or self.debug:
        print("[" + self.logTime() + "] [" + level.upper() + "] " + str(msg))

  # lturn a string with the timestamp for consistent logging purposes
  def logTime(self):
      return datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')

  # Function to write an debug log
  # This method used in the main program
  def logDebug(self, msg):
    self.logWrite('debug', msg)

  # Function to write an info log
  # This method used in the main program
  def logInfo(self, msg):
    self.logWrite('info ', msg)

  # Function to write a fatal log and exit w/ code 1
  # This method used in the main program to
  def logFatal(self, msg):
    self.logWrite('fatal', msg)
    exit(1)


  ########################
  # Main Methods
  ########################

  # Accepts an email address as param, exits program if not valid email
  def validateEmailOrExit(self, email):
      success = '@' in parseaddr(email)[1]

      if success:
          self.logDebug("Email '" + email + "' was verified as a valid email")
      else:
          self.logFatal("Email '" + email + "' was not a valid email")


  # Loads and verifies the configuration from environment variables
  def loadConfig(self):

    # Check for debug mode
    if "DEBUG" in os.environ and (os.environ['DEBUG'].lower() in ['1', 'true', 'yes', 'on']):
        self.debug = True
        self.logDebug("Debug mode enabled")

    self.logInfo("Loading configuration")

    # Check if DATA_BUCKET is set
    # If not, fail hard. Can not run with a default
    if "DATA_BUCKET" in os.environ:
        data_bucket = os.environ['DATA_BUCKET']
        self.logDebug("data_bucket set to '" + data_bucket + "' with environment variable 'DATA_BUCKET'")
    else:
        self.logFatal("Environment variable 'DATA_BUCKET' is not set")

    # Check if ALERT_EMAIL is set
    # If not, fail to empty. Can still run without an alerting email
    if "ALERT_EMAIL" in os.environ:
        alert_email = os.environ['ALERT_EMAIL']
        self.logDebug("alert_email set to '" + alert_email + "' with environment variable 'ALERT_EMAIL'")
        self.validateEmailOrExit(alert_email)
    else:
        self.logDebug("Environment variable 'ALERT_EMAIL' is not set. Defaulting to blank.")

    # Parse in URLs
    # Read in as many as exist, but fail hard if the first is not found. Can not run with a default
    # Will read in environment variables URL_1, URL_2, URL_3, ..., URL_n into list 'self.urls'
    #
    # Hard fails if at least URL_1 not set

    i = 1
    while True:
        varname = "URL_" + str(i)
        if varname in os.environ:
            self.urls.append({
                "url": os.environ[varname],
                "stored_sha256": '', # to be filled later
                "current_sha256": '', # to be filled later
            })
            self.logDebug("Environment variable '" + varname + "' set to " + os.environ[varname])
        else:
            # Hard fail if on the first loop
            if(i == 1):
                self.logFatal("URL_1 was not found - can not continue without at least one URL")
            # Otherwise, simply exit the loop, since we've parsed all the entries
            else:
                self.logInfo("Parsed " + str(len(self.urls)) + " URLs into the configuration")
                break
        i += 1

    self.logDebug(self.urls)
    self.logDebug("Confguration successfully loaded")


  # Checks all the URLs
  def loadKnownHashes(self):
    self.logDebug("Loading previously known hashes from s3")

  # Checks all the URLs
  def checkUrls(self):
     self.logDebug("Checking URLs against previously known hashes")



# This function called by Lambda directly
def lambda_handler(event, context):

    # This is all that's needed, everything is in the constructor
    ff = Filefetcher()

    # Delete the object so it starts fresh on every run
    del ff

    return {
        'statusCode': 200,
        'body': ''
    }

# This function called by CLI users
lambda_handler(None,None)
