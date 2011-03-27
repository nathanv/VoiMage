import os
import shutil
import subprocess
import wx
import re
import csv
from voice import VoiceInput, VoiceInputEvent, EVT_ID

MAIN_WINDOW_DEFAULT_SIZE = (600,480)

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
           self.parent_frame.clearPanel()
           self.parent_frame.static_bitmap = wx.StaticBitmap(self, -1, current_bitmap)
           print self.box_x, self.box_y, self.box_dx, self.box_dy

    def overlayBitmap(self, boxBitmap):
        dc = wx.MemoryDC()
        current_bitmap = wx.BitmapFromImage(self.parent_frame.image)
        dc.SelectObject(current_bitmap)
        dc.DrawBitmap(boxBitmap, self.box_x, self.box_y)
        dc.SelectObject(wx.NullBitmap)
        self.parent_frame.clearPanel()
        self.parent_frame.static_bitmap = wx.StaticBitmap(self, -1, current_bitmap)
        current_bitmap.SaveFile("overlay.jpg", wx.BITMAP_TYPE_JPEG)
        self.parent_frame.current_file = "overlay.jpg"
        print "overlaid image"

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
        self.panel.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.Bind(wx.EVT_CHAR_HOOK, self.OnKeyDown)
        self.current_file = None
        self.orig_cfile = None

        self.CreateMenuBar()

        # create StatusBar;give it 2 columns
        self.statusBar = self.CreateStatusBar()
        self.statusBar.SetFieldsCount(2)
        self.statusBar.SetStatusText('No image specified', 1)

        self.bitmap = None
        self.static_bitmap = None
        self.box_bitmap = None
        self.box_state = False
        self.box_on_screen = False
        # Worker thread that listens for voice input
        self.worker = VoiceInput(self, "voice.in")
        self.workerId = EVT_ID
        self.Connect(-1, -1, self.workerId, self.handleVoice)
        self.Show()
        self.SetFocus()
        self.errors = 0
        self.pos = 0
        self.canUndo = False
        self.expected_commands = ['open', 'box', 'contrast', 'edge']
        dirList=os.listdir('%s\images' % os.getcwd())
        self.images_list = []
        for fname in dirList:
            print fname
            self.images_list.append('%s\images\%s' % (os.getcwd(),fname))
        print self.images_list
        self.image_position=0
        self.panel.SetFocus()
        
    def OnKeyDown(self, event):
        print "got : %s" % event
        keycode = event.GetKeyCode()
        print keycode
        if self.box_state:
            self.statusBar.SetStatusText('Position box (end to exit)' , 1)
            if keycode == 65:
                print "Received 'a'; left move"
                self.moveBox(-40, 0)
            elif keycode == 68:
                print "Received 'd'; right move"
                self.moveBox(40, 0)
            elif keycode == 87:
                print "Received 'w'; up move"
                self.moveBox(0, -40)
            elif keycode == 83:
                print "Received 's'; down move"
                self.moveBox(0, 40)
            elif keycode == 388 or keycode == 43:
                print "Received '+'; bigger resize command"
                self.resizeBox(1.1) # need to tweak scale factors
            elif keycode == 390 or keycode == 45:
                print "Received '-'; smaller resize command"
                self.resizeBox(0.9)
            elif  keycode == 85 and self.canUndo: # 'u' key
                print "Received 'u'/Undo command"
                self.current_file = "tmp.jpg"
                self.reloadImage("tmp.jpg")
                self.box_state = False
                self.box_on_screen = False
            elif keycode == 312: #end key
                self.statusBar.SetStatusText('Say/Enter a command' , 1)
                print "Received 'End'; end of box state"
                self.box_state = False
                open("box.txt", "w").write("%s,%s,%s,%s" %
                                               (self.panel.box_x,
                                               self.panel.box_y,
                                               self.panel.box_dx,
                                               self.panel.box_dy))
            else:
                print "Uncategorized %s" % keycode
            event.Skip()
            return
        self.statusBar.SetStatusText('Say/Enter a command' , 1)
        if  keycode == wx.WXK_RIGHT:
            print "Received k; move to the right"
            if self.bitmap == None:
                self.image_position = 0    
            elif self.image_position + 1 >= len(self.images_list):
                self.image_position = 0
            else:
                self.image_position += 1                           
            print self.image_position
            self.current_file = self.images_list[self.image_position]
            self.orig_cfile = self.current_file
            self.createUndoBackup()
            print self.current_file
            self.reloadImage(self.current_file)
            event.Skip()
        elif keycode == wx.WXK_LEFT:
            print "Received j; move to the left"
            if self.bitmap == None:
                self.image_position = 0    
            elif self.image_position - 1 < 0:
                self.image_position = len(self.images_list)-1
            else:
                self.image_position -= 1                           
            print self.image_position
            self.current_file = self.images_list[self.image_position]
            self.orig_cfile = self.current_file
            self.createUndoBackup()
            print self.current_file
            self.reloadImage(self.current_file)
            event.Skip()
        elif keycode == 79: # handle "open" command
            self.OnOpen(event)
            print "'o'; Opened %s" % self.current_file
            self.createUndoBackup()
        elif keycode == 67: # handle "contrast" command
            self.doContrastCommand()
            print "'c'"
        elif keycode == 90: # handle "zoom" command, Not working, mostly matlab problems
            self.doZoomCommand()
            print "'z'"
        elif keycode == 66:
            self.statusBar.SetStatusText('Position Box(end to exit)' , 1)
            self.doBoxCommand()
            print "'b'"
        elif keycode == 69: #voice mapping stinks, matlab crashes
            self.doEdgeCommand()
            print "'e'"
        elif keycode == 27: # handle 'esc/close' command
            print "Received 'Esc'; close command"
            self.OnExit(event)
        elif keycode == 85 and self.canUndo: # 'u' key
            print "Received 'u'/Undo command"
            self.current_file = "tmp.jpg"
            self.reloadImage("tmp.jpg")
            self.box_state = False
            self.box_on_screen = False
        else:
            print "Uncategorized: %s" % keycode
        event.Skip()

    def createUndoBackup(self):
        if self.current_file and self.current_file != 'tmp.jpg':
            shutil.copyfile(self.current_file, 'tmp.jpg')
            self.canUndo = True

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
            self.statusBar.SetStatusText('Positioning area of interest' , 1)
            if re.search("left", command) or \
               re.search(re.escape("let"), command) or \
               re.search(re.escape("last"), command) or \
               re.search(re.escape("nafta"), command) or \
               re.search(re.escape("that is that"), command):
                print "Received left move"
                self.moveBox(-40, 0)
            elif re.search("right", command):
                print "Received right move"
                self.moveBox(40, 0)
            elif re.search("up", command) or \
                 re.search(re.escape("i think"), command) or \
                 re.search(re.escape("how could"), command) or \
                 re.search(re.escape("out of"), command) or \
                 re.search(re.escape("ah"), command) or \
                 re.search(re.escape("topic"), command) or \
                 re.search(re.escape("profit"), command) or \
                 re.search(re.escape("a death"), command) or \
                 re.search(re.escape("stop"), command) or \
                 re.search(re.escape("pop"), command) or \
                 re.search(re.escape("cop"), command) or \
                 re.search(re.escape("what can"), command) or \
                 re.search(re.escape("but"), command):
                print "Received up move"
                self.moveBox(0, -40)
            elif re.search("down", command):
                print "Received down move"
                self.moveBox(0, 40)
            elif re.search("bigger", command) or \
                 re.search(re.escape("they're"), command) or \
                 re.search(re.escape("they are"), command) or \
                 re.search("baker", command):
                print "Received bigger resize command"
                self.resizeBox(1.1) # need to tweak scale factors
            elif re.search("smaller", command) or \
                 re.search(re.escape("the caller"), command):
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
        self.statusBar.SetStatusText('Say/Enter a command' , 1)
        if re.search("open", command): # handle "open" command
            self.OnOpen(event)
            print "Opened %s" % self.current_file
            # save the current image to 'tmp.jpg' so we can go undo
            if self.current_file and self.current_file != 'tmp.jpg':
                shutil.copyfile(self.current_file, 'tmp.jpg')
                self.canUndo = True
        elif re.search("contrast", command) or \
             re.search("on cross", command) or \
             re.search("andrea", command) or \
             re.search("on trial", command): # handle "contrast" command
            self.doContrastCommand()
        elif re.search("soon", command) or \
             re.search("zone", command) or \
             re.search("room", command) or \
             re.search("film", command): # handle "zoom" command, Not working, mostly matlab problems
            self.doZoomCommand()
        elif (re.search("undo", command) or \
             re.search(re.escape("and do"), command) or \
             re.search(re.escape("and they"), command) or \
             re.search(re.escape("i'm guilty"), command) or \
             re.search(re.escape("i do"), command) or \
             re.search(re.escape("and it"), command) or \
             re.search(re.escape("and they were"), command)) and self.canUndo: # handle "undo" command.
            self.current_file = "tmp.jpg"
            self.reloadImage("tmp.jpg")
            self.box_state = False
            self.box_on_screen = False
        elif re.search("box", command) or \
             re.search("bob", command) or \
             re.search("all this", command) or \
             re.search("all that", command) or \
             re.search("bill", command) or \
             re.search("talk", command) or \
             re.search("mike", command) or \
             re.search("well", command) or \
             re.search("both", command) or \
             re.search("office", command):
            self.statusBar.SetStatusText('Position Box(end to exit)' , 1)
            self.doBoxCommand()
        elif re.search("edge", command) or \
             re.search("good", command) or \
             re.search(re.escape("they didn't"), command) or \
             re.search(re.escape("i didn't"), command) or \
             re.search(re.escape("that's in"), command) or \
             re.search(re.escape("ed kids"), command) or \
             re.search(re.escape("that jim"), command) or \
             re.search(re.escape("heads up"), command) or \
             re.search(re.escape("that kid"), command) or \
             re.search(re.escape("that just"), command) or \
             re.search(re.escape("head count"), command) or \
             re.search(re.escape("it's the"), command) or \
             re.search(re.escape("did you"), command) or \
             re.search(re.escape("had you"), command) or \
             re.search(re.escape("and to have"), command) or \
             re.search(re.escape("that changed"), command) or \
             re.search(re.escape("and just"), command) or \
             re.search(re.escape("that's up"), command) or \
             re.search(re.escape("but just"), command) or \
             re.search(re.escape("stay tuned"), command) or \
             re.search(re.escape("a tragic death"), command) or \
             re.search(re.escape("add to it"), command) or \
             re.search(re.escape("as to it"), command) or \
             re.search(re.escape("ed king"), command) or \
             re.search(re.escape("a few"), command) or \
             re.search(re.escape("at times"), command) or \
             re.search("agent", command) or \
             re.search("heads", command) or \
             re.search("and", command) or \
             re.search("exit", command) or \
             re.search("magic", command) or \
             re.search("aging", command) or \
             re.search(re.escape("ed ("), command) or \
             re.search("page", command) or \
             re.search("tensions", command) or \
             re.search("thank you", command) or \
             re.search("jeff", command): #voice mapping stinks, matlab crashes
            self.doEdgeCommand()
        elif re.search("close", command): # handle 'back' command
            print "Received close command"
            self.OnExit(event)
        else:
            print "Uncategorized: %s" % command
            self.errors += 1
            if self.errors > 1:
                self.doNextCommand(event)

    def overlayResult(self, boxfile):
        boxImage = wx.Image(boxfile, wx.BITMAP_TYPE_ANY, -1)
        boxBitmap = wx.BitmapFromImage(boxImage)
        self.panel.overlayBitmap(boxBitmap)
        self.Update()
        self.panel.Refresh()
        self.Refresh()
        

    def doNextCommand(self, event):
        next_command = self.expected_commands[self.pos]
        self.pos = (self.pos + 1) % 4
        if next_command == 'open':
            self.OnOpen(event)
        elif next_command == 'box':
            self.doBoxCommand()
        elif next_command == 'contrast':
            self.doContrastCommand()
        elif next_command == 'zoom':
            self.doZoomCommand()
        elif next_command == 'edge':
            self.doEdgeCommand()
        else:
            print "Error, unknown command: %s" % next_command

    def doContrastCommand(self):
        print "Received contrast command" # make sure the old bitmap doesn't crowd the new one
        self.errors = 0
        self.pos = (self.pos + 1) % 4
        try:
            if self.box_on_screen == True:
                print "self.box_on_screen == %s" % self.box_on_screen
                subprocess.check_call(['matlab', '-nosplash', '-nodesktop', '-nojvm', '-wait', '-noFigureWindows', '-minimize', '-r', "binarizeBox('%s', 'regular', %s, %s, %s, %s); exit;" % (self.orig_cfile, self.panel.box_x, self.panel.box_y, self.panel.box_dx, self.panel.box_dy)])
                print "binarizeBox('%s', 'regular', %s, %s, %s, %s); exit;" % (self.current_file, self.panel.box_x, self.panel.box_y, self.panel.box_dx, self.panel.box_dy)
                self.overlayResult('binarizebox.png')
                #self.box_on_screen = False
            else:
                print "self.box_on_screen == %s" % self.box_on_screen
                subprocess.check_call(['matlab', '-nosplash', '-nodesktop', '-nojvm', '-wait', '-noFigureWindows',  '-minimize', '-r', "binarize('%s', 'regular'); exit;" % self.orig_cfile])
                self.current_file = 'contrast.png'
                self.reloadImage(self.current_file)
        except subprocess.CalledProcessError:
            print "Contrast command failed"

    def doZoomCommand(self):
        print "Received zoom command"
        self.errors = 0
        self.pos = (self.pos + 1) % 4
        try:
            subprocess.check_call(['matlab', '-nosplash', '-nodesktop', '-nojvm',  '-wait', '-noFigureWindows', '-minimize', '-r', "zoom('%s', ''); exit;" % self.current_file])
            self.current_file = 'zoom.png'
            self.reloadImage('zoom.png')
        except subprocess.CalledProcessError:
            print "Zoom command failed"

    def doBoxCommand(self):
        print "Received cluster command"
        self.errors = 0
        self.pos = (self.pos + 1) % 4
        try:
            subprocess.check_call(['matlab', '-nosplash', '-nodesktop', '-nojvm',  '-wait', '-noFigureWindows', '-minimize', '-r', "box('%s', ''); exit;" % self.current_file])
            self.drawBox('box.txt')
            self.box_state = True
            self.box_on_screen = True
        except subprocess.CalledProcessError:
            print "Cluster command failed"

    def doEdgeCommand(self):
        print "Received edge command"
        self.errors = 0
        self.pos = (self.pos + 1) % 4
        try:
            if self.box_on_screen == True:
                print "self.box_on_screen == %s" % self.box_on_screen
                subprocess.check_call(['matlab', '-nosplash', '-nodesktop', '-nojvm','-wait', '-noFigureWindows', '-minimize', '-r', "outlineBox('%s', %s, %s, %s, %s); exit;" % (self.orig_cfile, self.panel.box_x, self.panel.box_y, self.panel.box_dx, self.panel.box_dy)])
                self.overlayResult('edgebox.png')
            else:
                print "self.box_on_screen == %s" % self.box_on_screen
                subprocess.check_call(['matlab', '-nosplash', '-nodesktop', '-nojvm', '-wait', '-noFigureWindows', '-minimize', '-r', "outline('%s'); exit;" % self.orig_cfile])
                self.current_file = 'edge.png'
            self.reloadImage(self.current_file)
        except subprocess.CalledProcessError:
            print "Edge command failed"

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
        self.panel.box_dx = abs(self.panel.box_dx)
        self.panel.box_dy = abs(self.panel.box_dy)
        self.panel.refreshBox()
        self.panel.Update()
        self.Update()
        self.Refresh()

    def resizeBox(self, scale):
        (width, height) = self.panel.GetSizeTuple()
        if (self.panel.box_x + scale*self.panel.box_dx) < width:
            self.panel.box_dx *= scale
        if (self.panel.box_y + scale*self.panel.box_dy) < height:
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
        self.errors = 0
        self.pos = (self.pos + 1) % 4
        filters = 'Image files (*.tiff;*.png;*.jpg)|*.tiff;*.png;*.jpg'
        dlg = wx.FileDialog(self, message="Open an Image...", defaultDir='%s\images' % os.getcwd(),
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

    def clearPanel(self):
        if self.static_bitmap:
            self.static_bitmap.Destroy()

    def ShowBitmap(self):
        # Convert image Bitmap to draw
        self.bitmap = wx.BitmapFromImage(self.image)
        self.clearPanel()
        self.static_bitmap = wx.StaticBitmap(self.panel, -1, self.bitmap)
        # Resize application's window to image size
        self.SetClientSize(self.static_bitmap.GetSize())
        self.Center() # open in centre of screen
        self.Refresh()

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
