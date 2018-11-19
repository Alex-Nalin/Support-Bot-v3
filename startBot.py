import time

import botbuilder
import modules.botlog as botlog
import modules.command.commandhub as hub
import modules.symphony.datafeed as datafeed
import modules.plugins.commandloader as cmdloader
import modules.symphony.messaging as messaging
import os
import codecs
import json


#Grab the config.json main parameters
_configPathdDefault = os.path.abspath('config.json')

with codecs.open(_configPathdDefault, 'r', 'utf-8-sig') as json_file:
        _configDef = json.load(json_file)

loopCount = 0

def Main():
    global loopCount

    botlog.LogSymphonyInfo('Starting Symphony Zendesk Bot session...')
    botSession = botbuilder.SymSession()

    # Bot Loop Begins here
    loopControl = botSession.StartBot()
    loopCount = 0

    # Pre-load the command definitions
    cmdloader.LoadAllCommands()

    #messaging.SendSymphonyMessage(_configDef['BotStreamForPing'], "Starting Bot session")

    while loopControl:

        messages = datafeed.PollDataFeed(botSession.DataFeedId)

        if messages is not None:

            if len(messages) == 0:
                # botlog.LogConsoleInfo('204 - No Content')
                # messaging.SendSymphonyMessage(_configDef['BotStreamForPing'], "Just a ping to keep the bot alive")
                pass

            for msg in messages:
                if msg.IsValid and msg.Sender.IsValidSender:
                    hub.ProcessCommand(msg)

        else:
            botlog.LogSymphonyInfo('Error detected reading datafeed. Invalidating session...')
            #messaging.SendSymphonyMessage(_configDef['BotStreamForPing'], "Error detected reading datafeed. Invalidating session...")
            botSession.InvalidateSession()
            loopControl = False

            loopControl = botSession.StartBot()


while loopCount < 10:
    try:
        Main()
    except SystemExit:
        loopCount = 99
        pass
    except Exception as ex:
        botlog.LogSystemError('Error: ' + str(ex))
        botlog.LogSymphonyError('Unhandled error, probably network difficulties at the Agent. Retrying in 5s.')
        #messaging.SendSymphonyMessage(_configDef['BotStreamForPing'],"There seems to be some network difficulties at the Agent. Please try again in 5s.")

        time.sleep(5)
        loopCount += 1