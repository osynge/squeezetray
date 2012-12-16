import wx
import  cStringIO   
import logging

smile16_png = \
'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x10\x00\x00\x00\x10\x08\x06\
\x00\x00\x00\x1f\xf3\xffa\x00\x00\x00\x04sBIT\x08\x08\x08\x08|\x08d\x88\x00\
\x00\x02\xa3IDATx\x9ce\x93\xdfkSg\x18\xc7?\xe7WL\x1b\xa2\x07!U\xa9\x89\xe9j\
\x90H\x87\x0cA\x86"\xb2\xf6B\xa1\xe0\x8d\xca\x19.\x88XJ\xa0\xb7R\xbc\x14\xbc\
\xb2\xfb\x03z\x93u\x17\xbb\xdb\x8dcHA\x85\xe4\xa6\xec\x80\x11d\xa3\x9548WMW\
\x10\xd9\xc4\xa2\x89\xc99=\xfdz\xd1D\x83\xbe\xf0\xde\xbc\xcf\xfb\xe1\xf9\xf2\
\xfd>\x0f\xae\xeb\xd2\x7f\xcb\xe5\xb2\n\x85\xcb\xcaf\x0f\xc8\xb6\r9\x8e\xa9\
\\.\xadbqZ\xbe\xef\xeb\xf3\xff&}\xc7\xf3.\xe9\xea\xd5\xf3\x8c\x8d\xfd\xc3\
\xdd\xbb\'i\xb5~\xa0\xd9\xfc\x9e;w\x8e12r\x1f\xcf;\x85\xe7]T?c\xb8\xae\x0b\
\xc0\x89\x13\xdf(\x93\xf9\x9f\xf9\xf9\xf38N\x004\x81w@\x04t\x80g\x84a\x8d\
\x99\x99\x80F\xe3$\xd5\xea\xb2\x01\xec(\xf0\xbcK\xcad\xa0T\xba\x8d\xe3\xe4\
\x81D\x17\xec5k\x03-\x1c\xc7\xa0T\xdaE&\xb3\x84\xe7]\xd8)\xfa\xbe\xaftz\xaf\
\x82\xa0&\xe9\xb9\xa4\x07\x9a\x9d\x9d\x15 \xa9 \xa9 @\xa9TJ\xd2\xa0\xa4\x01\
\x05\x01J\x1fD\xbe\xef\xcb(\x16\xa752\xb2\xc5\x8d\x1b7\x01\x0bx\x82a\x9c\x03\
@*\x00\x9b\xe4\xf3OY]]E\x1a\x04E\xb0e0\xf7c\xc4Z\xa3\x80Y\xa9\xdccrr\x18\xd8\
\x00\x9e\x01\x7f\xf6Y\xd4\x016X__\xef{\xdb\x86\xce \x93\x13I*\x95E\x0c\xc71\
\xd5l^\xc7q\x92@\x9b\xa9\xa9\x97,,\x04\x1f\x8d\x83\xf5\xae\xa1]8\x8a`s\x88\
\xb0m\x918\xd4\xe8\xc5\x18t\x1d\x7f\xcb\xc2B\x08l\x02\xcb@\xbd\x0f\x16h\x8b\
\xaf\x0e\xc6!\x1c\x800\x0e\x80\x99\xcd\x0eS\xaf\xff\x0b\xbc\x02\xea\xe4\xf3\
\x8f\x80\x87\xdd\xce\xfa\x04\x13Bd\xb2\xf6\xf2-\xb4\x92\xd4W\r\xb2\x87R\xd8\
\xe3\xe3gY\\\xfc\x85\xb1\xb1\x18 j5H$D\xb3\xd7\x98m`\x0b"\x83\xe3G\x93\xe8\
\xf90\xb4v\xb3\xf8\xe05\xe3g&z1\x1a\n\x82\x81nL;Q)\x1eW,\x16\x93m[J\xc4m\x1d\
\x1b\xdd+m\x1c\x91j\xa7\x15<\xfeN\xe9\xfd1\xf9Ke\x19\xae\xeb\xe2y\x17\x14E?S\
*\xd9}\x92\x05\xe66\xc4,&\x8e\x0eQ\xfe-\x05\xed$\x84\xbb\x98\xbeY\xc3J~\xcb\
\xaf\xbfW\x8c\xbeQ\xfeZ\x99\xcc\x12\xf3\xf3\xe08=\xf5&\xbc\xdf\x03o\xf6C;I\
\xd8\x8c1s\xebo\x1a\xff\x1d\xa0\xfa\xd7\xda\xa7Q\x06\xa8V\x97\r\xcb\x9abt\
\x14\xe6\xe6`e\x05\xc2\x8eE\xd81Yy\xfa\x8e\xb9\x9f^0z\xee!\xd6\xee\xd3\x1fa\
\x00>_O\xdf\xf7U,^S.\xb7O\x8e\x8d\x1c\x1b\xe5\x0e\x0f\xa98}E\xfe\x1fK_\xac\
\xf3\x07\xc0b=\xfa\xc1x\xb5\x84\x00\x00\x00\x00IEND\xaeB`\x82'   
   

   
def makeBitmap(data):   
    stream = cStringIO.StringIO(data)   
    return wx.BitmapFromImage(wx.ImageFromStream(stream))   
   
class MyArtProvider(wx.ArtProvider):   
    def __init__(self):
        self.log = logging.getLogger("MyArtProvider")
        wx.ArtProvider.__init__(self)   
        self.defaultIconMappingActionName = { 
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
            }
        self.defaultIconMappingSize = { 
            16 : set(["media_playback_start_16x16.png",
                "media_playback_pause_16x16.png",
                "media_playback_stop_16x16",
                "media_record_16x16.png",
                "media_seek_backward_16x16.png",
                "media_seek_forward_16x16.png",
                "media_skip_backward_16x16.png",
                "media_skip_forward_16x16.png",
                "media_eject_16x16.png"]),
            32 : set(["media_playback_start_32x32.png",
                "media_playback_pause_32x32.png",
                "media_playback_stop_32x32",
                "media_record_32x32.png",
                "media_seek_backward_32x32.png",
                "media_seek_forward_32x32.png",
                "media_skip_backward_32x32.png",
                "media_skip_forward_32x32.png",
                "media_eject_32x32.png"]),
            }
        self.log.error("MyArtProvider: ")   
    def CreateBitmap(self, artid, client, size):   
        # You can do anything here you want, such as using the same   
        # image for any size, any client, etc., or using specific   
        # images for specific sizes, whatever...   
   
        # See end of file for the image data   
        self.log.warn("MyArtProvider: providing %s:%s at %s\n" %(artid, client, size))   
        bmp = wx.NullBitmap   
        # use this one for all 48x48 images   
        if size.width == 48:   
            bmp = makeBitmap(smile16_png)   
   
        # but be more specific for these   
        bmp = makeBitmap(smile16_png)   
         
   
        if bmp.Ok():   
            self.log.info("MyArtProvider: providing %s:%s at %s\n" %(artid, client, size))   
        return bmp   
   
