import os
from blinkpy.blinkpy import Blink
from blinkpy.auth import Auth
from blinkpy.helpers.util import json_load
from pprint import pprint,pformat
from datetime import datetime
import dateutil.parser
import pytz
import tzlocal
import pathlib
import time
from shutil import copyfile
#import camera

Credsfile = "/home/eolson/creds/blinkcreds_eolson"
Download_root = '/mnt/z'
Since = "05/01/2021"

#
#
#

class Mycamera:
    def __init__(self, camera):
        self.camera = camera

    def attributes(self):
        return self.camera.attributes

    def obj(self):
        print(dir(self.camera))

class vidfile:
    def __init__(self, f):
        self.filename = f
        self.dirname = ''
        if self.filename.find('/') != -1:
          lastslash = self.filename.rindex('/')
          self.dirname = self.filename[0:lastslash]
          self.filename = self.filename[lastslash+1:]
        dashloc = self.filename.index('-')
        dotloc  = self.filename.rindex('.')

        self.camname = self.filename[0:dashloc]
        datepart = self.filename[dashloc+1:dotloc]
        self.ext = self.filename[dotloc+1:]
        d1 = datepart.rindex('-')
        minoff = datepart[d1+1:]
        datepart = datepart[0:d1]
        d1 = datepart.rindex('-')
        hroff = datepart[d1+1:]
        datepart = datepart[0:d1]
        self.utcoffset = hroff + minoff
        datepart = datepart + '+' + self.utcoffset
        filestring = self.camname + '-' + datepart + self.ext
        self.filetime = datetime.strptime(datepart, "%Y-%m-%dt%H-%M-%S%z")
        local_timezone = tzlocal.get_localzone()
        self.localfiletime = self.filetime.replace(tzinfo=pytz.utc).astimezone(local_timezone)
        local_offset = self.localfiletime.strftime("%z")
        localdate_string =  self.localfiletime.strftime("%Y-%m-%dt%H-%M-%S")
        self.localtime_filename = self.camname + '-' + localdate_string + \
          local_offset[0] + local_offset[1:3] + '-' + local_offset[3:5] + \
          '.' + self.ext
        self.year_month_string = self.localfiletime.strftime("%Y-%m")

    def camname(self):
      return self.camname

    def filetime(self):
      return self.filetime

    def localfiletime(self):
      return self.localfiletime

    def origfilename(self):
      return self.filename

    def utcoffset(self):
      return self.utcoffset

    def ext(self):
      return self.ext

    def dirname(self):
      return self.dirname

    def localfilename(self):
      return self.localtime_filename

    def __str__(self):
      mystr = self.filename + ':' + \
        self.local_filetime() +  ':' + \
        self.dirname + ':' 

      return mystr

    def year_month(self):
      return self.year_month_string


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
    try:
      os.mkdir(download_dir)
    except FileExistsError:
      pass
    blink.download_videos(download_dir, since=since,  camera=camera, debug=debugflag)

def modify_videos(download_dir, display_dir):
    filename = '/mnt/z/window/window-2021-06-09t11-21-14-00-00.mp4'
    flist = []
    thing = vidfile(filename)
    #print(thing)
    #return 

    for p in pathlib.Path(download_dir).iterdir():
      if p.is_file():
        flist.append(vidfile(str(p)))

    for x in flist:
      orig = download_dir + '/' + x.origfilename()
      newdir = display_dir + '/' + x.year_month()
      new = newdir + '/' + x.localfilename()
      try:
        os.mkdir(newdir)
      except FileExistsError:
        pass
      lft = x.localfiletime.timestamp()
      if not os.path.isfile(display_dir + "/" + new):
        copyfile(orig, new)
        os.utime(new, (lft, lft))

def camdump(cam):
    mycam = {}
    mycam['battery_status'] = cam['battery']
    mycam['battery_voltage'] = cam['battery_voltage']
    mycam['temperature'] = cam['temperature']
    mycam['name'] = cam['name']
    return mycam

def main():
    blink = initialize_cams(Credsfile)
    os.nice(5)
    cam_list = cameras(blink)
    #for x in cam_list:
        #pprint(camdump(x))
    for struct in cam_list:
        camera = struct['name']
        #print('download videos for ' + camera)
        old_dld = "{}/{}".format(Download_root, camera)
        test_dld = "{}/{}/{}".format(Download_root, 'test', camera)
        download_dir = "{}/{}/{}".format(Download_root, "download", camera)
        os.makedirs(old_dld, exist_ok = True)
        os.makedirs(download_dir, exist_ok = True)

        download_videos(blink, camera, Since, download_dir)
        #download_videos(blink, camera, Since, old_dld)

        modify_videos(download_dir, old_dld)

main()

