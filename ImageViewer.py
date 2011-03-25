import os
import subprocess
import wx
import re
import csv
from voice import VoiceInput, VoiceInputEvent, EVT_ID

MAIN_WINDOW_DEFAULT_SIZE = (300,200)

class activePanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.box_x = 0
        self.box_y = 0
        self.box_dx = 0
        self.box_dy = 0
        self.show_box = False
        self.parent_frame = parent
        
    def refreshBox(self):
        dc = wx.MemoryDC() # the canvas we actually draw on
        if self.show_box and self.parent_frame.bitmap:
           current_bitmap = wx.BitmapFromImage(self.parent_frame.image)
           dc.SelectObject(current_bitmap)
           dc.SetPen(wx.Pen('#4c4c4c', 1, wx.SOLID))
           dc.SetBrush(wx.Brush(wx.Colour(0,0,0), wx.TRANSPARENT))
           dc.DrawRectangle(self.box_x, self.box_y, self.box_dx, self.box_dy)
           dc.SelectObject(wx.NullBitmap)
           self.parent_frame.static_bitmap = wx.StaticBitmap(self, -1, current_bitmap)
           print self.box_x, self.box_y, self.box_dx, self.box_dy

    def setRectAttributes(self, x, y, dx, dy):
        self.box_x = x
        self.box_y = y
        self.box_dx = dx
        self.box_dy = dy

class Frame(wx.Frame):

    def __init__(self, parent, id, title):
        style=wx.DEFAULT_FRAME_STYLE ^ (wx.RESIZE_BORDER)
        wx.Frame.__init__(self, parent, id, title=title, size=MAIN_WINDOW_DEFAULT_SIZE, style=style)
        self.Centre()
        self.panel = activePanel(self)
        self.panel.SetBackgroundColour('White')
        self.current_file = None
        self.orig_cfile = None

        self.CreateMenuBar()

        # create StatusBar;give it 2 columns
        self.statusBar = self.CreateStatusBar()
        self.statusBar.SetFieldsCount(2)
        self.statusBar.SetStatusText('No image specified', 1)

        self.bitmap = None
        self.static_bitmap = None
        self.box_state = False
        # Worker thread that listens for voice input
        self.worker = VoiceInput(self, "voice.in")
        self.workerId = EVT_ID
        self.Connect(-1, -1, self.workerId, self.handleVoice)
        
        self.Bind(wx.EVT_KEY_DOWN, self.onKeyPress)
        self.Show()
        self.SetFocus()

    def onKeyPress(self, event):
        print "got : %s" % event
        self.current_file = 'foo'
        self.drawBox('box.txt')

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
        if self.box_state:
            if re.search("left", command):
                print "Received left move"
                self.moveBox(-40, 0)
            elif re.search("right", command):
                print "Received right move"
                self.moveBox(40, 0)
            elif re.search("up", command):
                print "Received up move"
                self.moveBox(0, -40)
            elif re.search("down", command):
                print "Received down move"
                self.moveBox(0, 40)
            elif re.search("bigger", command) or \
                 re.search("baker", command):
                print "Received bigger resize command"
                self.resizeBox(1.1) # need to tweak scale factors
            elif re.search("smaller", command):
                print "Received smaller resize command"
                self.resizeBox(0.9)
            elif re.search("and", command):
                print "Received end of box state"
                self.box_state = False
                open("box.txt", "w").write("%s,%s,%s,%s" %
                                               (self.panel.box_x,
                                               self.panel.box_y,
                                               self.panel.box_dx,
                                               self.panel.box_dy))
            else:
                print "Uncategorized %s" % command
            return
        
        if re.search("open", command): # handle "open" command
            self.OnOpen(event)
            print "Opened %s" % self.current_file
        elif re.search("contrast", command) or \
             re.search("on cross", command) or \
             re.search("andrea", command) or \
             re.search("on trial", command): # handle "contrast" command
            print "Received contrast command" # make sure the old bitmap doesn't crowd the new one
            try:
                subprocess.check_call(['matlab', '-nosplash', '-nodesktop', '-nojvm', '-r', "binarize('%s', 'regular'); exit;" % self.current_file])
                self.current_file = 'contrast.png'
                self.reloadImage('contrast.png')
            except subprocess.CalledProcessError:
                print "Contrast command failed"
        elif re.search("soon", command): # handle "zoom" command, Not working, mostly matlab problems
            print "Received zoom command"
            try:
                subprocess.check_call(['matlab', '-nosplash', '-nodesktop', '-nojvm', '-r', "zoom('%s', ''); exit;" % self.current_file])
                self.current_file = 'zoom.png'
                self.reloadImage('zoom.png')
            except subprocess.CalledProcessError:
                print "Zoom command failed"
        elif re.search("box", command) or \
             re.search("bob", command) or \
             re.search("all this", command) or \
             re.search("bill", command) or \
             re.search("talk", command) or \
             re.search("mike", command) or \
             re.search("office", command):
            print "Received cluster command"
            try:
                subprocess.check_call(['matlab', '-nosplash', '-nodesktop', '-nojvm', '-r', "box('%s', '');" % self.current_file])
                self.drawBox('box.txt')
                self.box_state = True
            except subprocess.CalledProcessError:
                print "Cluster command failed"
        elif re.search("edge", command): #voice mapping stinks, matlab crashes
            print "Received edge command"
            try:
                subprocess.check_call(['matlab', '-nosplash', '-nodesktop', '-nojvm', '-r', "edge('%s');" % self.current_file])
                self.current_file = 'edge.png'
                self.reloadImage('edge.png')
            except subprocess.CalledProcessError:
                print "Edge command failed"
        elif re.search("close", command): # handle 'back' command
            print "Received close command"
            self.OnExit(event)
        else:
            print "Uncategorized: %s" %command

    def moveBox(self, dx, dy):
        (width, height) = self.panel.GetSizeTuple()
        if self.panel.box_x + dx >= 0 and (self.panel.box_x + dx + self.panel.box_dx) < width:
            self.panel.box_x += dx
        elif self.panel.box_x + dx < 0:
            self.panel.box_x = 0
        else:
            self.panel.box_x = width - self.panel.box_x - self.panel.box_dx - 1;

        if self.panel.box_y + dy >= 0 and (self.panel.box_y + dy + self.panel.box_dy) < height:
            self.panel.box_y += dy
        elif self.panel.box_y + dy < 0:
            self.panel.box_y = 0
        else:
            self.panel.box_y = width - self.panel.box_y - self.panel.box_dy - 1;
        self.panel.refreshBox()
        self.panel.Update()
        self.Update()
        self.Refresh()

    def resizeBox(self, scale):
        (width, height) = self.panel.GetSizeTuple()
        if (self.panel.box_x + scale*self.panel.box_dx + self.panel.box_dx) < width:
            self.panel.box_dx *= scale
        if (self.panel.box_y + self.panel.box_dy + self.panel.box_dy) < height:
            self.panel.box_dy *= scale
        
        self.panel.refreshBox()
        self.panel.Update()
        self.Update()
        self.Refresh()

    def drawBox(self, filename):
        csv_handle = csv.reader(open(filename, "rb"))
        box_info = []
        for data in csv_handle:
          box_info = data
        self.panel.setRectAttributes(int(box_info[0]), int(box_info[1]), int(box_info[2]), int(box_info[3]))
        self.panel.show_box = True
        self.panel.Update()
        self.Update()
        self.panel.refreshBox()
        self.Refresh()

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
        self.bitmap = wx.BitmapFromImage(self.image)
        self.static_bitmap = wx.StaticBitmap(self.panel, -1, self.bitmap)
        # Resize application's window to image size
        self.SetClientSize(self.static_bitmap.GetSize())
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
