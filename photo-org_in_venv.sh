#!/bin/bash

source /home/apr/repos/photoManagement/env/bin/activate

python /home/apr/repos/photoManagement/organize-photos.py /home/apr/Pictures/Auto-Upload/ $1 > /home/apr/repos/photoManagement/cron.log

deactivate
