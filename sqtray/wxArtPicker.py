import wx
import logging
import os
import wxIcons

   
class MyArtProvider(wx.ArtProvider):   
    def __init__(self):
        self.log = logging.getLogger("MyArtProvider")
        wx.ArtProvider.__init__(self)   
        self.defaultIconMappingActionName = { 
            'ART_APPLICATION_STATUS_DISCONECTED' : set(["media_playback_start_16x16.png"]),
            'ART_PLAYER_PLAY' : set(["media_playback_start_16x16.png",
                "media_playback_start_22x22.png",
                "media_playback_start_24x24.png",
                "media_playback_start_32x32.png",
                "media_playback_start_48x48.png",
                "media_playback_start_72x72.png",
                "media_playback_start_128x128.png"]),
            'ART_PLAYER_PAUSE' : set(["media_playback_pause_16x16.png",
                "media_playback_pause_22x22.png",
                "media_playback_pause_24x24.png",
                "media_playback_pause_32x32.png",
                "media_playback_pause_48x48.png",
                "media_playback_pause_72x72.png",
                "media_playback_pause_128x128.png"]),
            'ART_PLAYER_SEEK_FORWARD' : set(["media_seek_forward_16x16.png",
                "media_seek_forward_22x22.png",
                "media_seek_forward_24x24.png",
                "media_seek_forward_32x32.png",
                "media_seek_forward_48x48.png",
                "media_seek_forward_72x72.png",
                "media_seek_forward_128x128.png"]),
            'ART_PLAYER_SEEK_BACKWARD' : set(["media_skip_backward_16x16.png",
                "media_skip_backward_22x22.png",
                "media_skip_backward_24x24.png",
                "media_skip_backward_32x32.png",
                "media_skip_backward_48x48.png",
                "media_skip_backward_72x72.png",
                "media_skip_backward_128x128.png"]),
            
            }
        self.defaultIconMappingSize = { 
            (16, 16) : set(["media_playback_start_16x16.png",
                "media_playback_pause_16x16.png",
                "media_playback_stop_16x16",
                "media_record_16x16.png",
                "media_seek_backward_16x16.png",
                "media_seek_forward_16x16.png",
                "media_skip_backward_16x16.png",
                "media_skip_forward_16x16.png",
                "media_eject_16x16.png"]),
            (24, 24) : set(["media_playback_start_24x24.png",
                "media_playback_pause_24x24.png",
                "media_playback_stop_24x24",
                "media_record_24x24.png",
                "media_seek_backward_24x24.png",
                "media_seek_forward_24x24.png",
                "media_skip_backward_24x24.png",
                "media_skip_forward_24x24.png",
                "media_eject_24x24.png"]),
            (32, 32) : set(["media_playback_start_32x32.png",
                "media_playback_pause_32x32.png",
                "media_playback_stop_32x32",
                "media_record_32x32.png",
                "media_seek_backward_32x32.png",
                "media_seek_forward_32x32.png",
                "media_skip_backward_32x32.png",
                "media_skip_forward_32x32.png",
                "media_eject_32x32.png"]),
            }
        
    def CreateBitmap(self, artid, client, size):   
        # You can do anything here you want, such as using the same   
        # image for any size, any client, etc., or using specific   
        # images for specific sizes, whatever...   
   
        # See end of file for the image data   
        self.log.debug("MyArtProvider: providing %s:%s at %s" %(artid, client, size))   
        bmp = wx.NullBitmap   
        # use this one for all 48x48 images
        NamesSize = set()
        NamesArtId = set()
        if artid in self.defaultIconMappingActionName.keys():
            NamesArtId = self.defaultIconMappingActionName[artid]
            if "ART_APPLICATION_STATUS_DISCONECTED" == artid:
                self.log.info("ART_APPLICATION_STATUS_DISCONECTED")   
                return wxIcons.trayDefault.GetBitmap()
                

        NamesSize = set()
        IconSize = size.Get()
        if IconSize in self.defaultIconMappingSize.keys():
            NamesSize = self.defaultIconMappingSize[IconSize]
        Found = NamesSize.intersection(NamesArtId)
        numberFound = len(Found)
        for item in Found:
            self.log.debug("found one")
            filePath = "icons/%s" % item
            if os.path.isfile(filePath):
                self.log.debug("exists one")
                fp = open(filePath)
                bmp = wx.BitmapFromImage(wx.ImageFromStream(fp))
                fp.close()
                break
   
        # but be more specific for these   
         
         
   
        if bmp.Ok():   
            self.log.info("MyArtProvider: providing %s:%s at %s" %(artid, client, size))   
        return bmp   
   
