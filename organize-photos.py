#!/usr/bin/python
import sys
import os, shutil
import subprocess
import os.path
from datetime import datetime
from PIL import Image

######################## Variables #########################
# Where to put the new files
#destDir = os.environ['HOME'] + '/Dropbox/Photos'
#destDir = '/data/Photos'
destDir = '/data/p3'
errorDir = destDir + '/Unsorted/'

# The format for the new file names.
fmt = "%Y-%m-%d_%H-%M-%S"

# File extensions to process
extensionsToProcess = ('.jpg', '.JPG')

######################## Functions #########################

def photoDate(f):
  "Return the date/time on which the given photo was taken."
  
  # Get the exif data
  exif =  Image.open(original)._getexif()

  # First we will try to use [36867 Date/Time Original]
  if 36867 in exif.keys():
    print "36867"
    cDate = exif[36867]

  # Otherwise use [306 Modify Date] (for older cameras ?)
  elif 306 in exif.keys():
    print "306"
    cDate = exif[306]

  return datetime.strptime(cDate, "%Y:%m:%d %H:%M:%S")

###################### Main program ########################

# Check that we have supplied a path to process
if len(sys.argv) != 2:
  print "Usage: python %s /path/to/process" % sys.argv[0]
  sys.exit()

print "Will process: ", sys.argv[1]
sourceDir = sys.argv[1]

# List of problem files
problems = []

# Prepare to output as processing occurs
lastMonth = 0
lastYear = 0

# Create the destination folder if necessary
if not os.path.exists(destDir):
  os.makedirs(destDir)
if not os.path.exists(errorDir):
  os.makedirs(errorDir)

# Copy photos into year and month subfolders. Name the copies according to
# their timestamps. If more than one photo has the same timestamp, add
# suffixes 'a', 'b', etc. to the names. 
for root, dirs, photos in os.walk(sourceDir):
    for photo in photos:
        if photo.endswith(extensionsToProcess):

          # We need to get the full path to the sub directory
          fullpath = os.path.join(root, photo)

#          print "Processing %s..." % fullpath

          original = fullpath
          suffix = 'a'
          try:
            pDate = photoDate(original)
            yr = pDate.year
            mo = pDate.month
            
            if not lastYear == yr or not lastMonth == mo:
              sys.stdout.write('\nProcessing %04d-%02d...' % (yr, mo))
              lastMonth = mo
              lastYear = yr
            else:
              sys.stdout.write('.')
              
            newname = pDate.strftime(fmt)
            thisDestDir = destDir + '/%04d/%02d' % (yr, mo)
            if not os.path.exists(thisDestDir):
              os.makedirs(thisDestDir)
              
            duplicate = thisDestDir + '/%s.jpg' % (newname)
            while os.path.exists(duplicate):
              newname = pDate.strftime(fmt) + suffix
              duplicate = destDir + '/%04d/%02d/%s.jpg' % (yr, mo, newname)
              suffix = chr(ord(suffix) + 1)
            shutil.copy2(original, duplicate)
          except Exception:
            shutil.copy2(original, errorDir + photo)
            problems.append(photo)
          except:
            sys.exit("Execution stopped.")
                  
# Report the problem files, if any.
if len(problems) > 0:
  print "\nProblem files:"
  print "\n".join(problems)
  print "These can be found in: %s" % errorDir
