import  wx
from cStringIO import StringIO
import cairosvg


import logging
import os



def getProgramFolder():
    moduleFile = __file__
    moduleDir = os.path.split(os.path.abspath(moduleFile))[0]
    programFolder = os.path.abspath(moduleDir)

    return programFolder
def joindirs(directory,item):
    return "%s/%s" % (directory,item)

class directoryArray():
    def __init__(self):
        self.log = logging.getLogger("directoryArray")
        self.path = []
        self.foundpaths = []
    def checkPathsExist(self):
        self.foundpaths = []
        for directory in self.path:
            if os.path.isdir(directory):
                self.foundpaths.append(directory)
        if len (self.foundpaths) == 0:
            self.log.warning("Icon paths not found")
        return self.foundpaths 
             
    def ScanPaths(self,item):
        if len (self.foundpaths) == 0:
            
            self.log.warning("No valid icon paths found")
            
        
        for directory in self.foundpaths:
            fullpath = joindirs(directory,item)
            if os.path.isfile(fullpath):
                #self.log.debug("Found")
                return fullpath
        return None



class MyArtProvider(wx.ArtProvider):
    def __init__(self):
        wx.ArtProvider.__init__(self)

    def CreateBitmap(self, artid, client, size):
        print artid
        width, height = size.Get()
        fp = open("icons/button.svg")
        svgxml = fp.read()
        svgpng = cairosvg.svg2png(svgxml)
        svgimg = wx.ImageFromStream(StringIO(svgpng),wx.BITMAP_TYPE_PNG)
        svgimg = svgimg.Scale(width, height, wx.IMAGE_QUALITY_HIGH)
        svgbmp = wx.BitmapFromImage(svgimg)
        return svgbmp
