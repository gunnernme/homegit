import os
import sys
from blinkpy.blinkpy import Blink
from blinkpy.auth import Auth
from blinkpy.helpers.util import json_load
from pprint import pprint,pformat
from datetime import datetime
import re
import dateutil.parser
import pytz
import tzlocal
import pathlib
import time
import logging
from logging import info,debug
from shutil import copyfile
#import camera

Credsfile = "/home/eolson/creds/blinkcreds_eolson"
Download_root = '/mnt/z'
Since = "05/01/2021"

#
#
#

class Netblink:
    def initialize_cams(self, creds):
        blink = Blink()
        try: 
          auth = Auth(json_load(creds))
          blink.auth = auth
          blink.start()
          blink.refresh()
        except:
          pass
        return blink

    def we_are_logging(self):
      return self.verbose is None or not re.match(r'(f|0).*', self.verbose.lower())

    def setup_log_file(self):
      log = os.environ.get('LOGFILE', None)
      if not log:
        self.logfile = "{}.log".format(os.path.basename(sys.argv[0]))
        logging.basicConfig(filename=self.logfile, level=logging.INFO)
      else:
        if re.match(r'stderr',log.lower()):
          logging.basicConfig(level=logging.INFO)

    def __init__(self, credsfile):
      self.blink = None
      self.verbose = None
      self.logfile = None
      self.credsfile = credsfile
      os.nice(5)

      self.verbose = os.environ.get('VERBOSE', None)
      #
      # it's going to do logging unless explicitly told not to
      if self.we_are_logging():
        self.setup_log_file()

      info('Started')
      self.blink = self.initialize_cams(self.credsfile)

    def cameras(self):
        mylist = []

        for name, camera in self.blink.cameras.items():
            item = Mycamera(camera)
            mylist.append(item.camera.attributes)

        return mylist

    def download_videos(self, camera, since, download_dir):
        debugflag = False
        try:
          os.mkdir(download_dir)
        except FileExistsError:
          pass
        self.blink.download_videos(download_dir, since=since,  camera=camera, debug=debugflag)

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
        self.month_day_string = self.localfiletime.strftime("%m-%d")

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

    def month_day(self):
      return self.month_day_string

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
      newdir = display_dir + '/' + x.year_month() + '/' + x.month_day()
      new = newdir + '/' + x.localfilename()
      debug("orig={} new={}".format(orig, new))
      if not os.path.isdir(newdir):
        info("{} is not a dir".format(newdir))
        if os.path.exists(newdir):
          info("{} does exist".format(newdir))
          os.unlink(newdir)
        try:
          info("{} mkdir".format(newdir))
          os.mkdir(newdir)
        except FileExistsError:
          pass
      lft = x.localfiletime.timestamp()
      checkfile = newdir + "/" + x.localfilename()
      if not os.path.isfile(checkfile):
        info("Copy {} to {}".format(orig, new))
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
    instance = Netblink(Credsfile)
    cam_list = instance.cameras()

    for struct in cam_list:
        camera = struct['name']
        #print('download videos for ' + camera)
        old_dld = "{}/{}".format(Download_root, camera)
        test_dld = "{}/{}/{}".format(Download_root, 'test', camera)
        download_dir = "{}/{}/{}".format(Download_root, "download", camera)
        os.makedirs(old_dld, exist_ok = True)
        os.makedirs(download_dir, exist_ok = True)

        info('before download for {}'.format(camera))
        instance.download_videos(camera, Since, download_dir)
        info('after  download')
        #download_videos(blink, camera, Since, old_dld)

        modify_videos(download_dir, old_dld)

    info('Finished')

main()

