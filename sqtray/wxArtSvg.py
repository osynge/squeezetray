import wx
from cStringIO import StringIO
import cairosvg


import logging
import os

log = logging.getLogger(__name__)

art_map = {'ART_APPLICATION_STATUS_DISCONECTED': 'application_disconected.svg',
           'ART_APPLICATION_STATUS_CONNECTED': 'application_connected.svg',
           'ART_PLAYER_PLAY': 'play.svg',
           'ART_PLAYER_STOP': 'stop.svg',
           'ART_PLAYER_PAUSE': 'pause.svg',
           'ART_PLAYER_SEEK_FORWARD': 'forward.svg',
           'ART_PLAYER_SEEK_BACKWARD': 'backward.svg'}


def getProgramFolder():
    moduleFile = __file__
    moduleDir = os.path.split(os.path.abspath(moduleFile))[0]
    programFolder = os.path.abspath(moduleDir)
    return programFolder


def joindirs(directory, item):
    return "%s/%s" % (directory, item)


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
        if len(self.foundpaths) == 0:
            self.log.warning("Icon paths not found")
        return self.foundpaths

    def ScanPaths(self, item):
        if len(self.foundpaths) == 0:
            self.log.warning("No valid icon paths found")
        for directory in self.foundpaths:
            fullpath = joindirs(directory, item)
            if os.path.isfile(fullpath):
                return fullpath
        return None


class MyArtProvider(wx.ArtProvider):
    def __init__(self, directorys):
        wx.ArtProvider.__init__(self)
        self.da = directorys

    def CreateBitmap(self, artid, client, size):
        art_fsvg = art_map.get(artid)
        if art_fsvg is None:
            log.error("Could not find SVG file name for artid:" + artid)
            return wx.NullBitmap
        art_path = self.da.ScanPaths(art_fsvg)
        if art_path is None:
            log.error("Could not find SVG file:" + art_fsvg)
            return wx.NullBitmap
        width, height = size.Get()
        fp = open(art_path)
        svgxml = fp.read()
        svgpng = cairosvg.svg2png(svgxml)
        svgimg = wx.ImageFromStream(StringIO(svgpng), wx.BITMAP_TYPE_PNG)
        svgimg = svgimg.Scale(width, height, wx.IMAGE_QUALITY_HIGH)
        svgbmp = wx.BitmapFromImage(svgimg)
        return svgbmp
