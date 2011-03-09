import subprocess
from threading import *
import wx
import time
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
  def __init__(self, notify_window, comVoiceInput):
    """ Initialize the worker thread immediately """
    Thread.__init__(self)
    self._notify_window = notify_window
    self.vInput = comVoiceInput
    self.start()

  def run(self):
    """ Look at what the voice input has printed to stdout.
        If any command token has been posted, call the state machine on the input and post the corresponding event
    """
    while(True):
      time.sleep(1)
      new_input = open(self.vInput, "r").readlines() if os.path.exists(self.vInput) else None
      if new_input:
        #TODO post actually relevant events
        print new_input
        map(lambda command: wx.PostEvent(self._notify_window, VoiceInputEvent(command)), new_input)
    
