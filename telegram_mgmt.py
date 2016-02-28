#!/opt/bitnami/python/bin/python
# -*- coding: utf-8 -*-
#
# Simple Bot to reply to Telegram messages
# This program is dedicated to the public domain under the CC0 license.

"""
This Bot uses the Updater class to handle the bot.

First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

from telegram import Updater
import logging
import json, sys

import os
SCRIPTPATH = os.path.dirname(os.path.realpath(__file__))
BOTSCONFIGDIR = SCRIPTPATH + "/.bots/"


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

# Enable logging
logging.basicConfig(filename=LOGFILE,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
    bot.sendMessage(update.message.chat_id, text='Hi Hari!')

from subprocess import call, check_output, STDOUT

def ssrs(bot, update):
    kw = map(lambda x: x.strip().lower(), update.message.text.strip().split())
    CTLMANAGER = SCRIPTPATH + "/ctl_manager.sh"
    CMD = kw[0][1:]
    BOTHANDLE = kw[1]
    if BOTHANDLE != 'manager':
        outp = check_output([CTLMANAGER, CMD, BOTHANDLE], stderr=STDOUT) 
        bot.sendMessage(update.message.chat_id, text=outp)


def updatefile(bdir, typ, value):
    gitlocal = bdir + '/src' 
    filemapper = {'botkey':'.botkey', 'gitpath':'.gitpath', 'runscript':'.runscript'}
    valuemapper = {'botkey':value, 'gitpath':value, 'runscript':gitlocal + "/" + value}

    f = open(bdir + '/' + filemapper[typ], "w+")
    f.write(valuemapper[typ])
    f.close()

def listbots(bot, update):
    outp = check_output(
                ['/bin/ls', BOTSCONFIGDIR ],
                 stderr=STDOUT) 
    bot.sendMessage(update.message.chat_id, text=outp)
    return

def updatebot(bot, update):
    kw = map(lambda x: x.strip(), update.message.text.strip().split())
    try:
            CMD = kw[0][1:].lower()
            BOTHANDLE = kw[1].lower()
            TYP = kw[2].lower()
            if TYP not in ['botkey', 'gitpath', 'runscript']:
                raise ValueError
            VALUE = kw[3]
    except:
            outp = "Usage: /updatebot <bothandle> <BOTKEY|GITPATH|RUNSCRIPT> <newvalue>"
            bot.sendMessage(update.message.chat_id, text=outp)
            return

    bdir = BOTSCONFIGDIR + BOTHANDLE
    updatefile(bdir, TYP, VALUE)


def rmbot(bot, update):
    kw = map(lambda x: x.strip(), update.message.text.strip().split())
    try:
            CMD = kw[0][1:].lower()
            channel = kw[1].lower()
            BOTHANDLE = kw[2].lower()
    except:
            outp = "Usage: /rmbot TELEGRAM <bothandle>"
            bot.sendMessage(update.message.chat_id, text=outp)
            return

    bdir = BOTSCONFIGDIR + BOTHANDLE

    try:
        outp = check_output(
                ['/bin/rm', '-rf', bdir ],
                 stderr=STDOUT) 
        outp = "Removed!"
    except:
        outp = "Exception!"
    bot.sendMessage(update.message.chat_id, text=outp)




def newbot(bot, update):
    kw = map(lambda x: x.strip(), update.message.text.strip().split())
    try:
            CMD = kw[0][1:].lower()
            CHANNEL = kw[1].lower()
            BOTHANDLE = kw[2].lower()
            BOTKEY = kw[3]
            GITPATH = kw[4]
            SCRIPT_TO_RUN = kw[5]
    except:
            outp = "Usage: /newbot telegram <bothandle> <botkey> <gitpath> <script_to_run>"
            bot.sendMessage(update.message.chat_id, text=outp)
            return

    if CHANNEL not in ['telegram']:
        outp = "Channel %s not supported" % CHANNEL
        bot.sendMessage(update.message.chat_id, text=outp)
        return

    if CHANNEL in ['telegram']:
        bdir = BOTSCONFIGDIR + BOTHANDLE
        if CMD == 'newbot' and os.path.isdir(bdir):
            outp = "Error! Bot already exists"
            bot.sendMessage(update.message.chat_id, text=outp)
            return
        gitlocal = bdir + '/src' 

        try:
            outp = "Exception!"
            outp = check_output(
                ['/usr/bin/git', 'clone', GITPATH, gitlocal ],
                 stderr=STDOUT) 

            outp = check_output(
                ['chmod', '755', gitlocal + "/" + SCRIPT_TO_RUN],
                 stderr=STDOUT) 
        except:
            bot.sendMessage(update.message.chat_id, text=outp)
            return


        for (f, c) in [ ('botkey', BOTKEY),
                        ('runscript', SCRIPT_TO_RUN),
                        ('gitpath', GITPATH) ]:
            updatefile(bdir, f, c)

        outp = "Bot %s registered!" % BOTHANDLE
        bot.sendMessage(update.message.chat_id, text=outp)
        return

def help(bot, update):
    bot.sendMessage(update.message.chat_id, text='Help!')

def echo(bot, update):
    bot.sendMessage(update.message.chat_id, text=update.message.text)

def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))


def main():
    # Create the EventHandler and pass it your bot's token.
    updater = Updater(BOTKEY)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    for cmd in ['up', 'down', 'refresh', 'status']:
        dp.addTelegramCommandHandler(cmd, ssrs)

    for cmd in ['newbot', 'forcenewbot'] :
        dp.addTelegramCommandHandler(cmd, newbot)

    for cmd in [1] :
        dp.addTelegramCommandHandler('updatebot', updatebot)
        dp.addTelegramCommandHandler('rmbot', rmbot)
        dp.addTelegramCommandHandler('listbots', listbots)

    dp.addTelegramCommandHandler("start", help)
    dp.addTelegramCommandHandler("help", help)

    # on noncommand i.e message - echo the message on Telegram
    dp.addTelegramMessageHandler(echo)

    # log all errors
    dp.addErrorHandler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until the you presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()


