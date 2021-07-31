import os
from blinkpy.blinkpy import Blink
from blinkpy.auth import Auth
from blinkpy.helpers.util import json_load
from pprint import pprint,pformat
#import camera

Credsfile = "/home/eolson/creds/blinkcreds_eolson"
Download_root = '/mnt/z'
Since = "05/01/2021"

class Mycamera:
    def __init__(self, camera):
        self.camera = camera

    def attributes(self):
        return self.camera.attributes

    def obj(self):
        print(dir(self.camera))

def initialize_cams(creds):
    blink = Blink()
    auth = Auth(json_load(creds))
    blink.auth = auth
    blink.start()
    blink.refresh()
    return blink

def cameras(blink):
    mylist = []

    for name, camera in blink.cameras.items():
        item = Mycamera(camera)
        mylist.append(item.camera.attributes)

    return mylist


def download_videos(blink, camera, since, download_dir):
    debugflag = False
    blink.download_videos(download_dir, since=since,  camera=camera, debug=debugflag)

def modify_videos(download_dir, display_dir):
    pass

def main():
    blink = initialize_cams(Credsfile)
    cam_list = cameras(blink)
    pprint(cam_list)
    for struct in cam_list:
        camera = struct['name']
        print('download videos for ' + camera)
        old_dld = "{}/{}".format(Download_root, camera)
        download_dir = "{}/{}/{}".format(Download_root, "download", camera)
        os.makedirs(old_dld, exist_ok = True)
        os.makedirs(download_dir, exist_ok = True)

        download_videos(blink, camera, Since, download_dir)
        download_videos(blink, camera, Since, old_dld)

main()

