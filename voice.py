import subprocess
from threading import *
import wx
import time
import re
import os

#TODO: Define custom events for specific commands
EVT_ID = wx.NewId()
class VoiceInputEvent(wx.PyEvent):
  """ Simple Custom Event to let the GUI know about voice events
  """
  def __init__(self, command):
    wx.PyEvent.__init__(self)
    self.SetEventType(EVT_ID)
    self.command = command

class VoiceInput(Thread):
  """ Worker Thread that listens to the output of the voice recognition system
      Posts event information to the GUI.
  """

  tokens = [ "open",
             "close", ##
             "next",
             "back", 
             "zoom", ##
             "up", ##
             "down",
             "contrast",
             "blur",
             "sharp",
          ]
  
  def __init__(self, notify_window, comVoiceInput):
    """ Initialize the worker thread immediately """
    Thread.__init__(self)
    self._notify_window = notify_window
    self.voiceProc = subprocess.Popen(
        ["./lib/bin/Release/pocketsphinx_continuous",
         "-hmm", "./lib/model/hmm/en_US/hub4wsj_sc_8k",
         "-lm", "./lib/model/lm/en_US/hub4.5000.DMP",
         "-dict", "./lib/model/lm/en_US/cmu07a.dic",
         ],
        stdout=subprocess.PIPE)
    self.start()

  def match_input(self, input_string):
    if input_string and re.match("^[0-9]+:", input_string):
      return input_string
    elif re.match("READY", input_string):
      print "READY FOR VOICE INPUT"
    else:
      return None

  def run(self):
    """ Look at what the voice input has printed to stdout.
        If any command token has been posted, call the state machine on the input and post the corresponding event
    """
    while(True):
      time.sleep(1)
      new_input = self.voiceProc.stdout.readline() if not self.voiceProc.stdout.closed else None
      if new_input:
        new_input = self.match_input(new_input)
        if new_input:
          #print new_input
          wx.PostEvent(self._notify_window, VoiceInputEvent(new_input))
      else:
        print "No input"
        return
    
