#!/opt/bitnami/python/bin/python
# -*- coding: utf-8 -*-
#
# Simple Bot to reply to Telegram messages
# This program is dedicated to the public domain under the CC0 license.


import os, sys, logging
SCRIPTPATH = os.path.dirname(os.path.realpath(__file__))

BOTKEY = ""

if not BOTKEY:
    try:
        BOTHANDLE = sys.argv[1]
        f = open('%s/.botkey' % BOTHANDLE)
        BOTKEY = f.readline().strip()
        f.close()
    except:
        pass

if not BOTKEY:
    try:
        BOTHANDLE = SCRIPTPATH
        f = open(SCRIPTPATH + '/.BOTKEY')
        BOTKEY = f.readline().strip()
        f.close()
    except:
        print "BOTKEY not provided"
        sys.exit()

LOGFILE = "/tmp/telegram_logs/%s" % os.path.basename(BOTHANDLE)
os.makedirs("/tmp/telegram_logs", 0755)

# Enable logging
logging.basicConfig(filename=LOGFILE,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO)

logger = logging.getLogger(__name__)

