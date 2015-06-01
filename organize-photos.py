#!/usr/bin/python
import sys
import os, shutil
import subprocess
import os.path
import argparse
from datetime import datetime
from PIL import Image
import time

######################## Variables #########################
# Where to put the new files
destDir = '/home/apr/Dropbox/Photos/'
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
    #print "36867"
    cDate = exif[36867]

  # Otherwise use [306 Modify Date] (for older cameras ?)
  elif 306 in exif.keys():
    #print "306"
    cDate = exif[306]

  return datetime.strptime(cDate, "%Y:%m:%d %H:%M:%S")

###################### Main program ########################

print (time.strftime("%d/%m/%Y %H:%M:%S"))

# Define the arguments we want (and optional arguments)
parser = argparse.ArgumentParser()
parser.add_argument("pathString", help="Path to Process")
parser.add_argument("-m", "--move", help="Move the files (default = copy)", action="store_true")
parser.add_argument("-d", "--dest", help="Set an alternative destination directory (full path)", action="store")
args = parser.parse_args()

if args.move:
    print "Will MOVE files"

if args.dest:
  destDir = args.dest

print "Will copy files to %s" % (destDir)
print "Will process: ", args.pathString
sourceDir = args.pathString

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
          original = fullpath
          extension = os.path.splitext(original)[1]
          suffix = 'a'

          try:
            pDate = photoDate(original)
            yr = pDate.year
            mo = pDate.month
            
            # Show the progress as we move to a new month or year
            if not lastYear == yr or not lastMonth == mo:
              sys.stdout.write('\nProcessing %04d-%02d...' % (yr, mo))
              lastMonth = mo
              lastYear = yr
            else:
              sys.stdout.write('.')
              
            # Get the new destination filename and create directory
            newname = pDate.strftime(fmt)
            thisDestDir = destDir + '/%04d/%02d' % (yr, mo)
            if not os.path.exists(thisDestDir):
              os.makedirs(thisDestDir)

            duplicate = thisDestDir + '/%s%s' % (newname, extension)

            # Fix identical timestamps with a suffix
            while os.path.exists(duplicate):
              newname = pDate.strftime(fmt) + suffix
              duplicate = destDir + '/%04d/%02d/%s%s' % (yr, mo, newname, extension)
              suffix = chr(ord(suffix) + 1)
              
            # Copy or Move the files
            if args.move:
              shutil.move(original, duplicate)
            else:
              shutil.copy2(original, duplicate)

          except Exception:
            if args.move:
              shutil.move(original, duplicate)
              problems.append(photo)
            else:
              shutil.copy2(original, duplicate)
              problems.append(photo)
          except:
            sys.exit("Execution stopped.")
                  
# Report the problem files, if any.
if len(problems) > 0:
  print "\nProblem files:"
  print "\n".join(problems)
  print "These can be found in: %s" % errorDir
