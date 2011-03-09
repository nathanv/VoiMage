import subprocess
import wx
import time
from ImageViewer import *

if __name__ == '__main__':
  # make an App object, set stdout to console for debugging
  app = App(redirect=False)
  voiceProc = subprocess.Popen(["./voice", "open.raw"])
  app.MainLoop()
  voiceProc.terminate()

