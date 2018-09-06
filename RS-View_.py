import sys
from ij import WindowManager as WM, IJ
from ij.io import OpenDialog
import csv
from ij.gui import Roi, Overlay, GenericDialog
import time

""" 
This plugIn was written to support researchers working with
RapidSTORM. It will take the raw image sequence and the localization
table (txt format; columns = x, y, Frame, Intensity) and marks the
found localization as an overlay in square form.
Note: only tif is supported at the moment, because sif files(Andor)
can't be opened correctly.
Author: Patrick Zessin
Version: 2.0 (2013-07-22)
"""



#This code will delete the first code line in the rapidstorm localization table
#It is a 1 : 1 copy from this page 
#http://www.mfasold.net/blog/2010/02/python-recipe-read-csvtsv-textfiles-and-ignore-comment-lines/

class CommentedFile:
    def __init__(self, f, commentstring="#"):
        self.f = f
        self.commentstring = commentstring
    def next(self):
        line = self.f.next()
        while line.startswith(self.commentstring):
            line = self.f.next()
        return line
    def __iter__(self):
        return self

#This function will set the roi according to the given localization
def set_roi(x, y, t, I):
    global overlay
    global width
    global form

    if form == "Square":
        roi = Roi(x,y,width,width)
    else:
        roi = OvalRoi(x,y,width,width)
        
    roi.setPosition(t)
    roi.setName(str(I))
    roi.setNonScalable(True)
    overlay.add(roi)


# Here starts the main function

# Present a dialog to ask for pixel size, fit window and RAW data fileformat
dialog = GenericDialog("Localization settings used in rapidSTORM")
dialog.addMessage("Raw data settings")
dialog.addNumericField("Pixel size [nm]", 160, 0)
dialog.addNumericField("Column with X values", 0, 0)
dialog.addNumericField("Column with Y values", 1, 0)
dialog.addNumericField("Column with t values", 2, 0)
dialog.addNumericField("Start loading localizations at frame", 0, 0)
dialog.addMessage("Presentation settings")
dialog.addNumericField("Width/Height of overlay [px]", 5, 0)
dialog.addChoice("Form", ["Square", "Oval"], "Square")

dialog.showDialog()

pixel = dialog.getNextNumber()
xColumn = int(dialog.getNextNumber())
yColumn = int(dialog.getNextNumber())
tColumn = int(dialog.getNextNumber())
startFrame = int(dialog.getNextNumber())
width = dialog.getNextNumber()
form = dialog.getNextChoice()

# open the file find dialog
od = OpenDialog("Choose your raw data image sequence", "", "*.tif")


filename = od.getFileName()
directory = od.getDirectory() 

#end plugin when no file is picked
if filename is None:
  sys.exit("No valid file picked")

IJ.showStatus("Loading image sequence")

#import of the image file
filepath = directory + filename

IJ.run("TIFF Virtual Stack...", "open=[" + filepath + "]")


#get the open image

imp = IJ.getImage()
nFrames = imp.getNFrames()
nSlices = imp.getNSlices()
overlay = Overlay()
overlay.clear()

if nFrames == 0 and nSlice == 0:
    sys.exit("Image contains no frames")
elif nFrames == 1:
    maxFrames = nSlices
else:
    maxFrames = nFrames

# Get the localization Table
# open the file find dialog
od = OpenDialog("Choose your localization file (Malk format: y,x,t,I)", "", "*.txt")  
csv_name = od.getFileName()
csv_directory = od.getDirectory()
 

#end plugin when no file is picked
if csv_name is None:
   sys.exit("No valid file picked")

# load the text file as a dictionary
IJ.showStatus("Loading localization list")
csv_path = csv_directory + csv_name

csv_list = csv.reader(CommentedFile(open(csv_path, 'rb')), delimiter=' ', quoting=csv.QUOTE_NONNUMERIC)

zeit = time.time()

t0 = 1

for line in csv_list:
  
    if line[tColumn] >= startFrame and line[tColumn] <= startFrame + maxFrames:
        x = (line[xColumn]/pixel)-(width/2)
        y = (line[yColumn]/pixel)-(width/2)
        t = int(line[tColumn])- startFrame +1            #rapidSTORM starts counting with 0, imageJ with 1
        I = int(line[3])

        set_roi(x,y,t,I)

        #show ROIs at the image in realtime and update progress 
        if t0 - t != 0:
            imp.setOverlay(overlay)
            imp.show()
            IJ.showProgress(t, maxFrames)
            imp.setOverlay(overlay)
            imp.show()

        t0 = t
    
imp.setOverlay(overlay)
imp.show()
IJ.showProgress(1)

#print "%.3f" % (time.time()-zeit)
#dialog = GenericDialog("Message")
#dialog.addMessage("All  finished")
#dialog.showDialog()
