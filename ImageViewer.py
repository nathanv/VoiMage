import os
import subprocess
import wx
import re
import csv
from voice import VoiceInput, VoiceInputEvent, EVT_ID

MAIN_WINDOW_DEFAULT_SIZE = (300,200)

class Frame(wx.Frame):

    def __init__(self, parent, id, title):
        style=wx.DEFAULT_FRAME_STYLE ^ (wx.RESIZE_BORDER)
        wx.Frame.__init__(self, parent, id, title=title, size=MAIN_WINDOW_DEFAULT_SIZE, style=style)
        self.Center()
        self.panel = wx.Panel(self)
        self.panel.SetBackgroundColour('White')
        self.current_file = None
        self.orig_cfile = None

        self.CreateMenuBar()

        # create StatusBar;give it 2 columns
        self.statusBar = self.CreateStatusBar()
        self.statusBar.SetFieldsCount(2)
        self.statusBar.SetStatusText('No image specified', 1)

        self.bitmap = None
        # Worker thread that listens for voice input
        self.worker = VoiceInput(self, "voice.in")
        self.workerId = EVT_ID
        self.Connect(-1, -1, self.workerId, self.handleVoice)

    def CreateMenuBar(self):
        "Create menu bar with Open, Exit"
        menuBar = wx.MenuBar()
        # Tell Frame about MenuBar
        self.SetMenuBar(menuBar)
        menuFile = wx.Menu()
        menuBar.Append(menuFile, '&File')
        fileOpenMenuItem = menuFile.Append(-1, '&Open Image', 'Open a picture')
        #print "fileOpenMenuItem.GetId()", fileOpenMenuItem.GetId()
        self.Bind(wx.EVT_MENU, self.OnOpen, fileOpenMenuItem)
        # create a menu item for Exit and bind to OnExit function
        exitMenuItem = menuFile.Append(-1, 'E&xit', 'Exit the viewer')
        self.Bind(wx.EVT_MENU, self.OnExit, exitMenuItem)

    def handleVoice(self, event):
        """ Handle voice events, delegating to other event handlers as appropriate """
        command = event.command
        if re.search("open", command): # handle "open" command
            self.OnOpen(event)
            print "Opened %s" % self.current_file
        elif re.search("contrast", command): # handle "contrast" command
            print "Recieved contrast command"
            try:
                subprocess.check_call(['matlab', '-nosplash', '-nodesktop', '-nojvm', '-r', "contrast(0, 1.0, '%s'); exit;" % self.current_file])
                self.current_file = 'tmp.jpg'
                self.reloadImage('tmp.jpg')
            except subprocess.CalledProcessError:
                print "Contrast command failed"
        elif re.search("soon", command): # handle "blur" command
            print "Recieved zoom command"
            try:
                subprocess.check_call(['matlab', '-nosplash', '-nodesktop', '-nojvm', '-r', "zoom('%s', 1.5, 0, 0); exit;" % self.current_file])
            except subprocess.CalledProcessError:
                print "Zoom command failed"
        elif re.search("sharp", command): # handle "blur" command
            print "Recieved sharpen command"
        elif re.search("next", command): # handle 'next' command
            print "Recieved next command"
        elif re.search("back", command): # handle 'back' command
            print "Recieved back command"
        elif re.search("down", command): # handle 'back' command
            print "Recieved down command"
        elif re.search("left", command): # handle 'back' command
            print "Recieved left command"
        elif re.search("right", command): # handle 'back' command
            print "Recieved right command"
        elif re.search("box", command):
            print "Recieved cluster command"
            try:
                subprocess.check_call(['matlab', '-nosplash', '-nodesktop', '-nojvm', '-r', "main_cluster('%s');" % self.current_file])
                boxfile = csv.reader(open('box.txt','rb'))
                box = []
                for data in boxfile:
                    box.append(data[0])
                    box.append(data[1])
                    box.append(data[2])
                    box.append(data[3])
                x1 = box.append(data[0])
                y1 = box.append(data[1])
                dx = box.append(data[2])
                dy = box.append(data[3])
                self.Bind(wx.EVT_PAINT, self.OnPaint)
                self.DrawRectangle(self, e, x1, y1, dx, dy)
                self.Show()
            except subprocess.CalledProcessError:
                print "Cluster command failed"
        elif re.search("close", command): # handle 'back' command
            print "Recieved close command"
            self.OnExit(event)
        else:
            print "Uncategorized: %s" %command

    def OnPaint(self, e, x1, y1, fx, dy):
        dc = wx.ClientDC(self)
        dc.SetPen(wx.Pen('#4c4c4c', 1, wx.TRANSPARENT))
    
    def OnOpen(self, event):
        "Open image file, set title if successful"
        # Create file-open dialog in current directory
        filters = 'Image files (*.tiff;*.png;*.jpg)|*.tiff;*.png;*.jpg'
        dlg = wx.FileDialog(self, message="Open an Image...", defaultDir=os.getcwd(),
                            defaultFile="", wildcard=filters, style=wx.OPEN)
        # Call dialog
        if dlg.ShowModal() == wx.ID_OK:
            # Since user has selected file, get path, set window's title to path
            filename = dlg.GetPath()
            self.SetTitle(filename)
            wx.BeginBusyCursor()
            # load image from filename
            self.current_file = filename
            self.orig_cfile = filename
            self.image = wx.Image(filename, wx.BITMAP_TYPE_ANY, -1) # auto-detect file type
            # set StatusBar to show image's size
            self.statusBar.SetStatusText('Size = %s' % (str(self.image.GetSize())) , 1)
            # display image inside panel
            self.ShowBitmap()
            wx.EndBusyCursor()

        dlg.Destroy() # Garbage Collect Dialog

    def reloadImage(self, filename):
        self.image = wx.Image(filename, wx.BITMAP_TYPE_ANY, -1)
        self.statusBar.SetStatusText('Size = %s' % (str(self.image.GetSize())) , 1)
        self.ShowBitmap()

    def ShowBitmap(self):
        # Convert image Bitmap to draw
        self.bitmap = wx.StaticBitmap(self.panel, -1, wx.BitmapFromImage(self.image))
        # Resize application's window to image size
        self.SetClientSize(self.bitmap.GetSize())
        self.Center() # open in centre of screen

    def OnExit(self, event):
        self.Destroy()


class App(wx.App):

    def OnInit(self):
        self.frame = Frame(parent=None, id=-1, title='Image Viewer')
        self.frame.Show()
        self.SetTopWindow(self.frame)
        return True

if __name__ == "__main__":
    # make an App object, set stdout to console for debugging
    app = App(redirect=False)

    app.MainLoop()
