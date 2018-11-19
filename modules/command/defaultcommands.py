import requests
import os
import codecs
import json
import modules.botlog as botlog
import modules.botconfig as botconfig
import modules.crypto as crypto
import modules.symphony.messaging as messaging
import http.client
from Data.dictionary import AcronymsDictionary
from googleapiclient.discovery import build
from Data.access import AccessFile
import ast
import modules.symphony.callout as callout
import modules.symphony.messagereader as symreader
import modules.utility_date_time as utdt

#Grab the config.json Symphony parameters
_configPath = os.path.abspath('modules/command/default.json')
with codecs.open(_configPath, 'r', 'utf-8-sig') as json_file:
    _config = json.load(json_file)

_configPathdDefault = os.path.abspath('config.json')
with codecs.open(_configPathdDefault, 'r', 'utf-8-sig') as json_file:
        _configDef = json.load(json_file)

_configPathZendesk = os.path.abspath('modules/plugins/Zendesk/config.json')
with codecs.open(_configPathZendesk, 'r', 'utf-8-sig') as json_file:
    _configZen = json.load(json_file)

_configPathSymp = os.path.abspath('modules/plugins/Symp/config.json')
with codecs.open(_configPathSymp, 'r', 'utf-8-sig') as json_file:
    _configSym = json.load(json_file)


def SendSymphonyEcho(messageDetail):
    msg = messageDetail.Command.MessageText
    messaging.SendSymphonyMessage(messageDetail.StreamId, msg)

def SendSymphonyEchoV2(messageDetail):
    msg = messageDetail.Command.MessageText.strip()
    messaging.SendSymphonyMessageV2(messageDetail.StreamId, msg)

def LogSymphonyMessageDebug(messageDetail):
    botlog.LogSymphonyInfo('Message for Debugging: ' + repr(messageDetail.MessageRaw))
    messageDetail.ReplyToChat('Thank you for helping improve my code!')


def GetGoogleTranslation(messageDetail):
    botlog.LogSymphonyInfo("Bot Call - Google translate")
    transText = messageDetail.Command.MessageText

    if transText:

        botlog.LogSymphonyInfo('Attempting to translate: ' + transText)

        payload = {"client": "gtx", "sl": "auto", "tl": "en", "dt": "t", "q": transText}
        transEP = "https://translate.googleapis.com/translate_a/single"

        response = requests.get(transEP, params=payload).json()
        translation = response[0][0][0]
        lang = response[2]
        msg = 'I think you said: ' + translation + ' (' + lang + ')'
    else:
        msg = 'Please include a word or sentence to be translated.'

    messaging.SendSymphonyMessage(messageDetail.StreamId, msg)


# https://www.alphavantage.co/documentation/
def GetAlphaVantageStockQuote(messageDetail):
    botlog.LogSymphonyInfo("Bot call - Alpha Vantage Stock Quote")
    quoteText = messageDetail.Command.MessageText

    try:
        avAPIKey = botconfig.GetCommandSetting('alphavantage')['apikey']

        quoteSymbol = quoteText.split()[0]

        payload = {"function": "TIME_SERIES_DAILY", "apikey": avAPIKey, "symbol": quoteSymbol}
        avEP = 'https://www.alphavantage.co/query'
        response = requests.get(avEP, params=payload).json()

        tsDate = sorted(list(response['Time Series (Daily)'].keys()), reverse=True)[0]
        tsOpen = response['Time Series (Daily)'][tsDate]['1. open']
        tsClose = response['Time Series (Daily)'][tsDate]['4. close']

        msg = 'Quote for: ' + quoteText + '<br/>Date: ' + tsDate + '<br/>Open: ' + tsOpen
        msg += '<br/>Close: ' + tsClose + ''

        messaging.SendSymphonyMessage(messageDetail.StreamId, msg)

    except Exception as ex:
        errorStr = "Symphony REST Exception (system): {}".format(ex)
        botlog.LogSystemError(errorStr)
        msg = "Sorry, I could not return a quote."
        messaging.SendSymphonyMessage(messageDetail.StreamId, msg)


#Original
def GetGiphyImageOld(messageDetail):
    try:
        giphyAPIKey = botconfig.GetCommandSetting('giphy')['apikey']

        giphyText = messageDetail.Command.MessageText

        paramList = giphyText.split()

        isRandom = len(paramList) == 0 or paramList[0] == 'random'

        if isRandom:
            ep = "http://api.giphy.com/v1/gifs/random"
            payload = {"apikey": giphyAPIKey}
        else:
            ep = "http://api.giphy.com/v1/gifs/translate"
            payload = {"apikey": giphyAPIKey, "s": giphyText}

        response = requests.get(ep, params=payload).json()

        if isRandom:
            msg = "<a href='" + response['data']['image_original_url'] + "'/>"
        else:
            msg = "<a href='" + response['data']['images']['original']['url'] + "'/>"

        messaging.SendSymphonyMessage(messageDetail.StreamId, msg)

    except Exception as ex:
        errorStr = "Symphony REST Exception (system): {}".format(ex)
        botlog.LogSystemError(errorStr)
        msg = "Sorry, I could not return a GIF right now."
        messaging.SendSymphonyMessage(messageDetail.StreamId, msg)

#Fixed with Card
def GetGiphyImage(messageDetail):
    botlog.LogSymphonyInfo("Bot Call - Giphy")
    try:
        giphyAPIKey = botconfig.GetCommandSetting('giphy')['apikey']

        giphyText = messageDetail.Command.MessageText

        paramList = giphyText.split()

        isRandom = len(paramList) == 0 or paramList[0] == 'random'

        if isRandom:
            ep = "http://api.giphy.com/v1/gifs/random"
            payload = {"apikey": giphyAPIKey}
        else:
            ep = "http://api.giphy.com/v1/gifs/translate"
            payload = {"apikey": giphyAPIKey, "s": giphyText}

        response = requests.get(ep, params=payload).json()

        if isRandom:
            #msg = "<img src='" + response['data']['image_original_url'] + "'/>"
            gifimagelink = (response['data']['image_original_url'])
            msg = "<card iconSrc=\"https://thumb.ibb.co/csXBgU/Symphony2018_App_Icon_Mobile.png\" accent=\"tempo-bg-color--blue\"><header>(Click to view the GIF)</header><body><img src=\"" + gifimagelink + "\"/><br/><a href=\"" + gifimagelink + "\"/></body></card>"

        else:
            gifimagelink = (response['data']['images']['original']['url'])
            #print(*paramList)

            #joins all the elements of the array
            header = ' '.join(paramList)

            msg = "<card iconSrc=\"https://thumb.ibb.co/csXBgU/Symphony2018_App_Icon_Mobile.png\" accent=\"tempo-bg-color--blue\"><header> You searched Giphy for: \"<b>"+ header +"</b>\" (click to view GIF)</header><body><img src=\"" + gifimagelink + "\"/><br/><a href=\"" + gifimagelink + "\"/></body></card>"

        messaging.SendSymphonyMessageV2(messageDetail.StreamId, msg)

    except Exception as ex:
        errorStr = "Symphony REST Exception (system): {}".format(ex)
        botlog.LogSystemError(errorStr)
        msg = "Sorry, I could not return a GIF right now."
        messaging.SendSymphonyMessage(messageDetail.StreamId, msg)

def SymphonyZendeskBotHelp(messageDetail):
    botlog.LogSymphonyInfo("###############")
    botlog.LogSymphonyInfo("Bot Call - Help")
    botlog.LogSymphonyInfo("###############")

    try:

        # message = (messageDetail.Command.MessageText)
        # message_split = message.split()
        # more = 0

        # _configPathZendesk = os.path.abspath('modules/plugins/Zendesk/config.json')
        #_configPathSymphony = os.path.abspath('modules/plugins/Symp/config.json')
        _moreconfigPath = os.path.abspath('modules/command/default.json')

        # with codecs.open(_configPathZendesk, 'r', 'utf-8-sig') as json_file:
        #     _configZen = json.load(json_file)

        with codecs.open(_configPathSymp, 'r', 'utf-8-sig') as json_file:
            _configSym = json.load(json_file)

        with codecs.open(_moreconfigPath, 'r', 'utf-8-sig') as json_file:
            _moreconfig = json.load(json_file)

        header = "<b class =\"tempo-text-color--blue\">Symphony Zendesk Bot Help</b> For more information, please consult <b>Symphony Team</b><br/>"
        # ---------

        table_body = "<table style='border-collapse:collapse;border:2px solid black;table-layout:auto;max-width:100%;box-shadow: 5px 5px'><thead><tr style='background-color:#4D94FF;color:#ffffff;font-size:1rem' class=\"tempo-text-color--white tempo-bg-color--black\">" \
                     "<td style='border:1px solid blue;border-bottom: double blue;text-align:center;max-width:15%'>COMMAND</td>" \
                     "<td style='border:1px solid blue;border-bottom: double blue;text-align:center;max-width:15%'>PARAMETER</td>" \
                     "<td style='border:1px solid blue;border-bottom: double blue;text-align:center;max-width:20%'>SAMPLE</td>" \
                     "<td style='border:1px solid blue;border-bottom: double blue;text-align:center;max-width:25%'>DESCRIPTION</td>" \
                     "<td style='border:1px solid blue;border-bottom: double blue;text-align:center;max-width:12.5%'>CATEGORY</td>"\
                     "<td style='border:1px solid blue;border-bottom: double blue;text-align:center;max-width:12.5%'>PERMISSION</td>" \
                     "</tr></thead><tbody>"

        # Seems we need to set this to a colour the first time to work
        perm_bg_color = "green"
        for index in range(len(_configZen["commands"])):

            caterory = _configZen["commands"][index]["category"]

            if caterory == "Zendesk":
                caterory_bg_color = "cyan"
            if caterory == "Zendesk/General":
                caterory_bg_color = "purple"
            if caterory == "General Bot command":
                caterory_bg_color = "blue"
            if caterory == "Miscellaneous Bot command":
                caterory_bg_color = "yellow"

            permission = _configZen["commands"][index]["permission"]

            if permission == "Bot Admin":
                perm_bg_color = "red"
            if permission == "Zendesk Agent":
                perm_bg_color = "orange"
            if permission == "All":
                perm_bg_color = "green"
            if permission == "Zendesk Agent/Zendesk End-user":
                perm_bg_color = "yellow"

            table_body += "<tr>" \
                          "<td style='border:1px solid black;text-align:left'>" + _configZen["commands"][index]["helptext"] + "</td>" \
                          "<td style='border:1px solid black;text-align:left'>" + _configZen["commands"][index]["param"] + "</td>" \
                          "<td style='border:1px solid black;text-align:left'>" + _configZen["commands"][index]["example"] + "</td>" \
                          "<td style='border:1px solid black;text-align:left'>" + _configZen["commands"][index]["description"] + "</td>" \
                          "<td class=\"tempo-bg-color--" + caterory_bg_color + " tempo-text-color--white\">" + _configZen["commands"][index]["category"] + "</td>" \
                          "<td class=\"tempo-bg-color--" + perm_bg_color + " tempo-text-color--white\">" + _configZen["commands"][index]["permission"] + "</td>" \
                          "</tr>"

        for index in range(len(_configSym["commands"])):

            caterory = _configSym["commands"][index]["category"]

            if caterory == "Zendesk":
                caterory_bg_color = "cyan"
            if caterory == "Zendesk/General":
                caterory_bg_color = "purple"
            if caterory == "General Bot command":
                caterory_bg_color = "blue"
            if caterory == "Miscellaneous Bot command":
                caterory_bg_color = "yellow"

            permission = str(_configSym["commands"][index]["permission"])

            if permission == "Bot Admin":
                perm_bg_color = "red"
            if permission == "Zendesk Agent":
                perm_bg_color = "orange"
            if permission == "All":
                perm_bg_color = "green"

            table_body += "<tr>" \
                          "<td style='border:1px solid black;text-align:left'>" + _configSym["commands"][index]["helptext"] + "</td>" \
                          "<td style='border:1px solid black;text-align:left'>" + _configSym["commands"][index]["param"] + "</td>" \
                          "<td style='border:1px solid black;text-align:left'>" + _configSym["commands"][index]["example"] + "</td>" \
                          "<td style='border:1px solid black;text-align:left'>" + _configSym["commands"][index]["description"] + "</td>" \
                          "<td class=\"tempo-bg-color--" + caterory_bg_color + " tempo-text-color--white\">" + _configSym["commands"][index]["category"] + "</td>" \
                          "<td class=\"tempo-bg-color--" + perm_bg_color + " tempo-text-color--white\">" + _configSym["commands"][index]["permission"] + "</td>" \
                          "</tr>"

        # for index in range(len(message_split)):
        #
        #     if message_split[index] == "more":
        #         botlog.LogSymphonyInfo("Bot Call - Help More")
        #         more = 1
        #
        #         table_body += "</tbody><thead>" \
        #                       "<tr style='background-color:#4D94FF;color:#ffffff;font-size:1rem' class=\"tempo-text-color--white tempo-bg-color--black\">" \
        #                       "<td style='border:1px solid blue;border-bottom: double blue;text-align:center'>MORE COMMANDS</td>" \
        #                       "<td style='border:1px solid blue;border-bottom: double blue;text-align:center'>PARAMETER</td>" \
        #                       "<td style='border:1px solid blue;border-bottom: double blue;text-align:center'>SAMPLE</td>" \
        #                       "<td style='border:1px solid blue;border-bottom: double blue;text-align:center'>DESCRIPTION</td>" \
        #                       "<td style='border:1px solid blue;border-bottom: double blue;text-align:center;max-width:5%'>CATEGORY</td>" \
        #                       "<td style='border:1px solid blue;border-bottom: double blue;text-align:center;max-width:5%'>PERMISSION</td><" \
        #                       "/tr></thead><tbody>"

        _moreconfigPath = os.path.abspath('modules/command/default.json')
        with codecs.open(_moreconfigPath, 'r', 'utf-8-sig') as json_file:
            _moreconfig = json.load(json_file)

        for index in range(len(_moreconfig["commands"])):

            caterory = _moreconfig["commands"][index]["category"]

            if caterory == "Zendesk":
                caterory_bg_color = "cyan"
            if caterory == "Zendesk/General":
                caterory_bg_color = "purple"
            if caterory == "General Bot command":
                caterory_bg_color = "blue"
            if caterory == "Miscellaneous Bot command":
                caterory_bg_color = "yellow"

            permission = str(_moreconfig["commands"][index]["permission"])

            if permission == "Bot Admin":
                perm_bg_color = "red"
            if permission == "Zendesk Agent":
                perm_bg_color = "orange"
            if permission == "All":
                perm_bg_color = "green"
            if permission == "Zendesk Agent/Zendesk End-user":
                perm_bg_color = "yellow"

            table_body += "<tr>" \
                          "<td style='border:1px solid black;text-align:left'>" + _moreconfig["commands"][index]["helptext"] + "</td>" \
                          "<td style='border:1px solid black;text-align:left'>" + _moreconfig["commands"][index]["param"] + "</td>" \
                          "<td style='border:1px solid black;text-align:left'>" + _moreconfig["commands"][index]["example"] + "</td>" \
                          "<td style='border:1px solid black;text-align:left'>" + _moreconfig["commands"][index]["description"] + "</td>" \
                          "<td class=\"tempo-bg-color--" + caterory_bg_color + " tempo-text-color--white\">" + _moreconfig["commands"][index]["category"] + "</td>" \
                          "<td class=\"tempo-bg-color--" + perm_bg_color + " tempo-text-color--white\">" + _moreconfig["commands"][index]["permission"] + "</td>" \
                          "</tr>"
        else:
            pass
        #
        # if more == 0:
        #     table_body += "<tr>" \
        #                   "<td style='border:1px solid black;text-align:left'><b>/help more</b></td>" \
        #                   "<td style='border:1px solid black;text-align:left'>None</td>" \
        #                   "<td style='border:1px solid black;text-align:left'>/help more</td>"\
        #                   "<td style='border:1px solid black;text-align:left'>Recall /help with the word 'more' for some more commands.</td>" \
        #                   "<td class=\"tempo-bg-color--blue tempo-text-color--white\">General Bot command</td>" \
        #                   "<td class=\"tempo-bg-color--green tempo-text-color--white\">Anyone</td>" \
        #                   "</tr>"
        # else:
        #     pass

        table_body += "</tbody></table>"

        table_body = "<card iconSrc=\"https://thumb.ibb.co/csXBgU/Symphony2018_App_Icon_Mobile.png\" accent=\"tempo-bg-color--blue\"><header>" + header + "</header><body>" + table_body + "</body></card>"

        messaging.SendSymphonyMessageV2_noBotLog(messageDetail.StreamId, table_body)

    except:
        return messageDetail.ReplyToChat("Please check that all the config files are in the right place. I am sorry, I was working on a different task, can you please retry")

# def cheatSheet(messageDetail):
#     botlog.LogSymphonyInfo("Bot Call - cheatSheet")
#     message = (messageDetail.Command.MessageText)
#     message_split = message.split()
#     more = 0
#
#     # _configPathZendesk = os.path.abspath('modules/plugins/Zendesk/config.json')
#     #_configPathSymphony = os.path.abspath('modules/plugins/Symp/config.json')
#     _moreconfigPath = os.path.abspath('modules/command/default.json')
#
#     # with codecs.open(_configPathZendesk, 'r', 'utf-8-sig') as json_file:
#     #     _configZen = json.load(json_file)
#
#     # with codecs.open(_configPathSymphony, 'r', 'utf-8-sig') as json_file:
#     #     _configSym = json.load(json_file)
#
#     with codecs.open(_moreconfigPath, 'r', 'utf-8-sig') as json_file:
#         _moreconfig = json.load(json_file)
#
#     header = "<b class =\"tempo-text-color--blue\">Symphony Zendesk Bot Help</b> For more information, please consult <b>Symphony Team</b><br/>"
#     # ---------
#
#     table_body = "<table style='border-collapse:collapse;border:2px solid black;table-layout:auto;max-width:50%;box-shadow: 5px 5px'><thead><tr style='background-color:#4D94FF;color:#ffffff;font-size:1rem' class=\"tempo-text-color--white tempo-bg-color--black\">" \
#                  "<td style='border:1px solid blue;border-bottom: double blue;text-align:center;max-width:15%'>COMMAND</td>" \
#                  "<td style='border:1px solid blue;border-bottom: double blue;text-align:center;max-width:15%'>PARAMETER</td>" \
#                  "<td style='border:1px solid blue;border-bottom: double blue;text-align:center;max-width:20%'>SAMPLE</td>" \
#                  "<td style='border:1px solid blue;border-bottom: double blue;text-align:center;max-width:12.5%'>PERMISSION</td>" \
#                  "</tr></thead><tbody>"
#
#     # Seems we need to set this to a colour the first time to work
#     for index in range(len(_configZen["commands"])):
#
#         table_body += "<tr>" \
#                       "<td style='border:1px solid black;text-align:left'>" + _configZen["commands"][index]["helptext"] + "</td>" \
#                       "<td style='border:1px solid black;text-align:left'>" + _configZen["commands"][index]["param"] + "</td>" \
#                       "<td style='border:1px solid black;text-align:left'>" + _configZen["commands"][index]["example"] + "</td>" \
#                       "<td style='border:1px solid black;text-align:left'>" + _configZen["commands"][index]["permission"] + "</td>" \
#                       "</tr>"
#
#     for index in range(len(_configSym["commands"])):
#
#         table_body += "<tr>" \
#                       "<td style='border:1px solid black;text-align:left'>" + _configSym["commands"][index]["helptext"] + "</td>" \
#                       "<td style='border:1px solid black;text-align:left'>" + _configSym["commands"][index]["param"] + "</td>" \
#                       "<td style='border:1px solid black;text-align:left'>" + _configSym["commands"][index]["example"] + "</td>" \
#                       "<td style='border:1px solid black;text-align:left'>" + _configSym["commands"][index]["permission"] + "</td>" \
#                       "</tr>"
#
#
#     for index in range(len(_moreconfig["commands"])):
#
#         table_body += "<tr>" \
#                       "<td style='border:1px solid black;text-align:left'>" + _moreconfig["commands"][index]["helptext"] + "</td>" \
#                       "<td style='border:1px solid black;text-align:left'>" + _moreconfig["commands"][index]["param"] + "</td>" \
#                       "<td style='border:1px solid black;text-align:left'>" + _moreconfig["commands"][index]["example"] + "</td>" \
#                       "<td style='border:1px solid black;text-align:left'>" + _moreconfig["commands"][index]["permission"] + "</td>" \
#                       "</tr>"
#
#     table_body += "</tbody></table>"
#
#     table_body = "<card iconSrc=\"https://thumb.ibb.co/csXBgU/Symphony2018_App_Icon_Mobile.png\" accent=\"tempo-bg-color--blue\"><header>" + header + "</header><body>" + table_body + "</body></card>"
#
#     messaging.SendSymphonyMessageV2_noBotLog(messageDetail.StreamId, table_body)
#

def botStream(messageDetail):
    botlog.LogSymphonyInfo("###########################")
    botlog.LogSymphonyInfo("Bot Call - Bot Stream Check")
    botlog.LogSymphonyInfo("###########################")

    try:
        try:
            commandCallerUID = messageDetail.FromUserId

            connComp = http.client.HTTPSConnection(_configDef['symphonyinfo']['pod_hostname'])
            sessionTok = callout.GetSessionToken()

            headersCompany = {
                'sessiontoken': sessionTok,
                'cache-control': "no-cache"
            }

            connComp.request("GET", "/pod/v3/users?uid=" + commandCallerUID, headers=headersCompany)

            resComp = connComp.getresponse()
            dataComp = resComp.read()
            data_raw = str(dataComp.decode('utf-8'))
            data_dict = ast.literal_eval(data_raw)

            dataRender = json.dumps(data_dict, indent=2)
            d_org = json.loads(dataRender)

            for index_org in range(len(d_org["users"])):
                firstName = str(d_org["users"][index_org]["firstName"])
                lastName = str(d_org["users"][index_org]["lastName"])
                displayName = str(d_org["users"][index_org]["displayName"])
                companyName = str(d_org["users"][index_org]["company"])
                userID = str(d_org["users"][index_org]["id"])

                botlog.LogSymphonyInfo(str(firstName) + " " + str(lastName) + " from Company/Pod name: " + str(companyName) + " with UID: " + str(userID))
                callerCheck = (firstName + " " + lastName + " - " + displayName + " - " + companyName + " - " + str(userID))

        except:
            return messageDetail.ReplyToChat("Cannot validate user access")

        if callerCheck in (_configDef['AuthUser']['AdminList']):

            message = (messageDetail.Command.MessageText)
            message_split = message.split()
            summary = ""

            all = False
            room = False
            im = False

            for index in range(len(message_split)):
                if message_split[index] == "all" or message_split[index] == "All" or message_split[index] == "ALL":
                    all = True
                    body = {"includeInactiveStreams": 'false'}
                elif message_split[index] == "room" or message_split[index] == "Room" or message_split[index] == "ROOM":
                    room = True
                    body = {"streamTypes": [{"type": "ROOM"}], "includeInactiveStreams": 'false'}
                elif message_split[index] == "im" or message_split[index] == "Im" or message_split[index] == "IM":
                    im = True
                    body = {"streamTypes": [{"type": "IM"}, {"type": "MIM"}], "includeInactiveStreams": 'false'}
                else:
                    summary += message_split[index] + " "
            summary = summary.lstrip().rstrip()

            try:
                createEP = botconfig.SymphonyBaseURL + '/pod/v1/streams/list'
                response = callout.SymphonyPOST(createEP, json.dumps(body))
                r = json.loads(response.ResponseText)
            except:
                return messageDetail.ReplyToChat("Please use IM or Room or All after the command /checkStream. For example: /checkStream IM")

            table_body = ""
            table_header = "<table style='border-collapse:collapse;border:2px solid black;table-layout:auto;width:100%;box-shadow: 5px 5px'><thead><tr style='background-color:#4D94FF;color:#ffffff;font-size:1rem' class=\"tempo-text-color--black tempo-bg-color--black\">" \
                           "<td style='border:1px solid blue;border-bottom: double blue;width:30%;text-align:center'>STREAM ID</td>" \
                           "<td style='border:1px solid blue;border-bottom: double blue;width:5%;text-align:center'>CROSS POD</td>" \
                           "<td style='border:1px solid blue;border-bottom: double blue;width:5%;text-align:center'>ACTIVE</td>" \
                           "<td style='border:1px solid blue;border-bottom: double blue;width:5%;text-align:center'>TYPE</td>" \
                           "<td style='border:1px solid blue;border-bottom: double blue;width:50%;text-align:center'>ROOM NAME OR MEMBER ID</td>" \
                           "</tr></thead><tbody>"

            for index in range(len(r)):
                count = (len(r))
                botStreamID = r[index]["id"]
                crossPod = r[index]["crossPod"]
                active = r[index]["active"]
                streamType = r[index]["streamType"]["type"]
                if im:
                    attribute = r[index]["streamAttributes"]["members"]
                elif room:
                    attribute = r[index]["roomAttributes"]["name"]
                elif all:
                    try:
                        attribute = r[index]["streamAttributes"]["members"]
                    except:
                        attribute = r[index]["roomAttributes"]["name"]

                table_body += "<tr>" \
                              "<td style='border:1px solid black;text-align:center'>" + str(botStreamID) + "</td>" \
                              "<td style='border:1px solid black;text-align:center'>" + str(crossPod) + "</td>" \
                              "<td style='border:1px solid black;text-align:center'>" + str(active) + "</td>" \
                              "<td style='border:1px solid black;text-align:center'>" + str(streamType) + "</td>" \
                              "<td style='border:1px solid black;text-align:center'>" + str(attribute) + "</td>" \
                              "</tr>"

            table_body += "</tbody></table>"
            reply = table_header + table_body

            return messageDetail.ReplyToChatV2_noBotLog(
                "<card iconSrc =\"https://thumb.ibb.co/csXBgU/Symphony2018_App_Icon_Mobile.png\" accent=\"tempo-bg-color--blue\"><header>Please find the result below. Total number of stream with the Bot <b>" + str(
                    count) + "</b> </header><body>" + reply + "</body></card>")

        else:
            return messageDetail.ReplyToChat("You aren't authorised to use this command.")
    except:
        #return messageDetail.ReplyToChat("I am sorry, I was working on a different task, can you please retry")
        return messageDetail.ReplyToChat("the bot failed and it is auro retying the same call once more time")

        try:
            try:
                commandCallerUID = messageDetail.FromUserId

                connComp = http.client.HTTPSConnection(_configDef['symphonyinfo']['pod_hostname'])
                sessionTok = callout.GetSessionToken()

                headersCompany = {
                    'sessiontoken': sessionTok,
                    'cache-control': "no-cache"
                }

                connComp.request("GET", "/pod/v3/users?uid=" + commandCallerUID, headers=headersCompany)

                resComp = connComp.getresponse()
                dataComp = resComp.read()
                data_raw = str(dataComp.decode('utf-8'))
                data_dict = ast.literal_eval(data_raw)

                dataRender = json.dumps(data_dict, indent=2)
                d_org = json.loads(dataRender)

                for index_org in range(len(d_org["users"])):
                    firstName = str(d_org["users"][index_org]["firstName"])
                    lastName = str(d_org["users"][index_org]["lastName"])
                    displayName = str(d_org["users"][index_org]["displayName"])
                    companyName = str(d_org["users"][index_org]["company"])
                    userID = str(d_org["users"][index_org]["id"])

                    botlog.LogSymphonyInfo(str(firstName) + " " + str(lastName) + " from Company/Pod name: " + str(
                        companyName) + " with UID: " + str(userID))
                    callerCheck = (firstName + " " + lastName + " - " + displayName + " - " + companyName + " - " + str(
                        userID))

            except:
                return messageDetail.ReplyToChat("Cannot validate user access")

            if callerCheck in (_configDef['AuthUser']['AdminList']):

                message = (messageDetail.Command.MessageText)
                message_split = message.split()
                summary = ""

                all = False
                room = False
                im = False

                for index in range(len(message_split)):
                    if message_split[index] == "all" or message_split[index] == "All" or message_split[index] == "ALL":
                        all = True
                        body = {"includeInactiveStreams": 'false'}
                    elif message_split[index] == "room" or message_split[index] == "Room" or message_split[
                        index] == "ROOM":
                        room = True
                        body = {"streamTypes": [{"type": "ROOM"}], "includeInactiveStreams": 'false'}
                    elif message_split[index] == "im" or message_split[index] == "Im" or message_split[index] == "IM":
                        im = True
                        body = {"streamTypes": [{"type": "IM"}, {"type": "MIM"}], "includeInactiveStreams": 'false'}
                    else:
                        summary += message_split[index] + " "
                summary = summary.lstrip().rstrip()

                try:
                    createEP = botconfig.SymphonyBaseURL + '/pod/v1/streams/list'
                    response = callout.SymphonyPOST(createEP, json.dumps(body))
                    r = json.loads(response.ResponseText)
                except:
                    return messageDetail.ReplyToChat(
                        "Please use IM or Room or All after the command /checkStream. For example: /checkStream IM")

                table_body = ""
                table_header = "<table style='border-collapse:collapse;border:2px solid black;table-layout:auto;width:100%;box-shadow: 5px 5px'><thead><tr style='background-color:#4D94FF;color:#ffffff;font-size:1rem' class=\"tempo-text-color--black tempo-bg-color--black\">" \
                               "<td style='border:1px solid blue;border-bottom: double blue;width:30%;text-align:center'>STREAM ID</td>" \
                               "<td style='border:1px solid blue;border-bottom: double blue;width:5%;text-align:center'>CROSS POD</td>" \
                               "<td style='border:1px solid blue;border-bottom: double blue;width:5%;text-align:center'>ACTIVE</td>" \
                               "<td style='border:1px solid blue;border-bottom: double blue;width:5%;text-align:center'>TYPE</td>" \
                               "<td style='border:1px solid blue;border-bottom: double blue;width:50%;text-align:center'>ROOM NAME OR MEMBER ID</td>" \
                               "</tr></thead><tbody>"

                for index in range(len(r)):
                    count = (len(r))
                    botStreamID = r[index]["id"]
                    crossPod = r[index]["crossPod"]
                    active = r[index]["active"]
                    streamType = r[index]["streamType"]["type"]
                    if im:
                        attribute = r[index]["streamAttributes"]["members"]
                    elif room:
                        attribute = r[index]["roomAttributes"]["name"]
                    elif all:
                        try:
                            attribute = r[index]["streamAttributes"]["members"]
                        except:
                            attribute = r[index]["roomAttributes"]["name"]

                    table_body += "<tr>" \
                                  "<td style='border:1px solid black;text-align:center'>" + str(botStreamID) + "</td>" \
                                                                                                               "<td style='border:1px solid black;text-align:center'>" + str(
                        crossPod) + "</td>" \
                                    "<td style='border:1px solid black;text-align:center'>" + str(active) + "</td>" \
                                                                                                            "<td style='border:1px solid black;text-align:center'>" + str(
                        streamType) + "</td>" \
                                      "<td style='border:1px solid black;text-align:center'>" + str(attribute) + "</td>" \
                                                                                                                 "</tr>"

                table_body += "</tbody></table>"
                reply = table_header + table_body

                return messageDetail.ReplyToChatV2_noBotLog(
                    "<card iconSrc =\"https://thumb.ibb.co/csXBgU/Symphony2018_App_Icon_Mobile.png\" accent=\"tempo-bg-color--blue\"><header>Please find the result below. Total number of stream with the Bot <b>" + str(
                        count) + "</b> </header><body>" + reply + "</body></card>")

            else:
                return messageDetail.ReplyToChat("You aren't authorised to use this command.")
        except:
            return messageDetail.ReplyToChat("I am sorry, I was working on a different task, can you please retry")

def botMessageBlast(messageDetail):
    botlog.LogSymphonyInfo("##########################")
    botlog.LogSymphonyInfo("Bot Call: Send Bot Message")
    botlog.LogSymphonyInfo("##########################")

    try:
        try:
            commandCallerUID = messageDetail.FromUserId

            connComp = http.client.HTTPSConnection(_configDef['symphonyinfo']['pod_hostname'])
            sessionTok = callout.GetSessionToken()

            headersCompany = {
                'sessiontoken': sessionTok,
                'cache-control': "no-cache"
            }

            connComp.request("GET", "/pod/v3/users?uid=" + commandCallerUID, headers=headersCompany)

            resComp = connComp.getresponse()
            dataComp = resComp.read()
            data_raw = str(dataComp.decode('utf-8'))
            data_dict = ast.literal_eval(data_raw)

            dataRender = json.dumps(data_dict, indent=2)
            d_org = json.loads(dataRender)

            for index_org in range(len(d_org["users"])):
                firstName = str(d_org["users"][index_org]["firstName"])
                lastName = str(d_org["users"][index_org]["lastName"])
                displayName = str(d_org["users"][index_org]["displayName"])
                companyName = str(d_org["users"][index_org]["company"])
                userID = str(d_org["users"][index_org]["id"])

                botlog.LogSymphonyInfo(str(firstName) + " " + str(lastName) + " from Company/Pod name: " + str(companyName) + " with UID: " + str(userID))
                callerCheck = (firstName + " " + lastName + " - " + displayName + " - " + companyName + " - " + str(userID))

        except:
            return messageDetail.ReplyToChat("Cannot validate user access")

        if callerCheck in (_configDef['AuthUser']['AdminList']):

            message = (messageDetail.Command.MessageText)
            message_split = message.split()
            summary = ""

            check = len(message_split)

            if check == 1:
                return messageDetail.ReplyToChat("Please make sure to include a message")
            else:

                for index in range(len(message_split)):
                    if message_split[index] == "all" or message_split[index] == "All" or message_split[index] == "ALL":
                        body = {"includeInactiveStreams": 'false'}
                    elif message_split[index] == "room" or message_split[index] == "Room" or message_split[index] == "ROOM":
                        body = {"streamTypes": [{"type": "ROOM"}], "includeInactiveStreams": 'false'}
                    elif message_split[index] == "im" or message_split[index] == "Im" or message_split[index] == "IM":
                        body = {"streamTypes": [{"type": "IM"}, {"type": "MIM"}], "includeInactiveStreams": 'false'}
                    else:
                        summary += message_split[index] + " "
                summary = summary.lstrip().rstrip()
                # print(summary)

                try:
                    createEP = botconfig.SymphonyBaseURL + '/pod/v1/streams/list'
                    response = callout.SymphonyPOST(createEP, json.dumps(body))
                    r = json.loads(response.ResponseText)
                    #print("response: " + str(r))
                except:
                    return messageDetail.ReplyToChat("Please use IM or Room or All as well as a comment to send, after the command /botMessage. For example: /botMessage IM The bot has been updated")

                for index in range(len(r)):
                    try:
                        messaging.SendSymphonyMessage(r[index]["id"], summary)
                    except:
                        botlog.LogSystemInfo(
                            "The stream is not valid anymore, maybe the bot is no longer connected with the user")
        else:
            return messageDetail.ReplyToChat("You aren't authorised to use this command.")
    except:
        return messageDetail.ReplyToChat("I am sorry, I was working on a different task, can you please retry")

def shutdownBot(messageDetail):
    botlog.LogSymphonyInfo("######################")
    botlog.LogSymphonyInfo("Bot Call: Shutdown Bot")
    botlog.LogSymphonyInfo("######################")

    try:
        try:
            commandCallerUID = messageDetail.FromUserId

            connComp = http.client.HTTPSConnection(_configDef['symphonyinfo']['pod_hostname'])
            sessionTok = callout.GetSessionToken()

            headersCompany = {
                'sessiontoken': sessionTok,
                'cache-control': "no-cache"
            }

            connComp.request("GET", "/pod/v3/users?uid=" + commandCallerUID, headers=headersCompany)

            resComp = connComp.getresponse()
            dataComp = resComp.read()
            data_raw = str(dataComp.decode('utf-8'))
            data_dict = ast.literal_eval(data_raw)

            dataRender = json.dumps(data_dict, indent=2)
            d_org = json.loads(dataRender)

            for index_org in range(len(d_org["users"])):
                firstName = d_org["users"][index_org]["firstName"]
                lastName = d_org["users"][index_org]["lastName"]
                displayName = d_org["users"][index_org]["displayName"]
                companyName = d_org["users"][index_org]["company"]
                userID = str(d_org["users"][index_org]["id"])

                botlog.LogSymphonyInfo(firstName + " " + lastName + " from Company/Pod name: " + str(companyName) + " with UID: " + str(userID))
                callerCheck = (firstName + " " + lastName + " - " + displayName + " - " + companyName + " - " + str(userID))

        except:
            return messageDetail.ReplyToChat("Cannot validate user access")

        if callerCheck in (_configDef['AuthUser']['AdminList']):

            message = (messageDetail.Command.MessageText)
            message_split = message.split()
            summary = ""
            noMessage = (str(len(message_split)))

            if noMessage == "0":
                messageDetail.ReplyToSender("Shutting down Symphony Zendesk Bot now.")
                botlog.LogSystemInfo("Shutdown command received from " + messageDetail.Sender.Email)
                exit(0)

            for index in range(len(message_split)):

                if message_split[index] == "all" or message_split[index] == "All" or message_split[index] == "ALL":
                    body = {"includeInactiveStreams": 'false'}
                elif message_split[index] == "room" or message_split[index] == "Room" or message_split[index] == "ROOM":
                    body = {"streamTypes": [{"type": "ROOM"}], "includeInactiveStreams": 'false'}
                elif message_split[index] == "im" or message_split[index] == "Im" or message_split[index] == "IM":
                    body = {"streamTypes": [{"type": "IM"}, {"type": "MIM"}], "includeInactiveStreams": 'false'}
                else:
                    summary += message_split[index] + " "
            summary = summary.lstrip().rstrip()
            # print(summary)

            try:
                createEP = botconfig.SymphonyBaseURL + '/pod/v1/streams/list'
                response = callout.SymphonyPOST(createEP, json.dumps(body))
                r = json.loads(response.ResponseText)
            except:
                return messageDetail.ReplyToChat(
                    "Please use IM or Room or All as well as a comment to send, after the command /botMessage. For example: /BotMessage IM The bot has been updated")

            for index in range(len(r)):
                try:
                    messaging.SendSymphonyMessage(r[index]["id"], summary)
                except:
                    botlog.LogSystemInfo("The stream is not valid anymore, maybe the bot is no longer connected with the user")

            messageDetail.ReplyToSender("Shutting down Symphony Zendesk Bot now.")
            botlog.LogSystemInfo("Shutdown command received from " + messageDetail.Sender.Email)
            exit(0)

        else:
            return messageDetail.ReplyToChat("You aren't authorised to use this command.")
    except:
        return messageDetail.ReplyToChat("I am sorry, I was working on a different task, can you please retry")


def SendStatusCheck(messageDetail):
    botlog.LogSymphonyInfo("#############################")
    botlog.LogSymphonyInfo("Bot Call: Check Status of Bot")
    botlog.LogSymphonyInfo("#############################")
    import random

    caller_raw = messageDetail.Sender.Name
    caller_split = str(caller_raw).split(" ")
    callername = caller_split[0]

    replies = ["I'm up! I'm up! " + callername, "Five by Five " + callername, "Ready to serve " + callername, "Lets do something productive " + callername + "?", "Listening...",
               "Who's asking?", "Can I <i>help</i> you " + callername + "?", "Who disturbs my slumber?!", "Eat your heart out, Siri.",
               "On your marks, get set, go!", "More work?", "Ready for action " + callername]

    randReply = True

    if len(messageDetail.Command.UnnamedParams) > 0:
        index = messageDetail.Command.UnnamedParams[0]

        if index.isnumeric():
            indexNum = int(index)

            if indexNum < len(replies):
                messageDetail.ReplyToChat(replies[indexNum])
                randReply = False

    if randReply:
        #messageDetail.ReplyToChat(random.choice(replies) +  callername)
        messageDetail.ReplyToChat(random.choice(replies))


def QoD (messageDetail):
    botlog.LogSymphonyInfo("Bot Call: Quote of the Day")

    qodtext = messageDetail.Command.MessageText

    qodcheck = qodtext.split()

    isRandom = len(qodcheck) == 0 or qodcheck[0] == ""

    messageDetail.ReplyToChat("Please ponder on the following Quote:")

    if isRandom:

        conn = http.client.HTTPConnection("quotes.rest")
        headers = {
            'cache-control': "no-cache",
        }
        conn.request("GET", "/qod", headers=headers)
        res = conn.getresponse()
        data = res.read()
        parsed = json.loads(data)
        parsedData = (json.dumps(parsed, indent=4))
        #print("parsedData: " + parsedData)
        qodraw = (data.decode("utf-8")).replace("\n", "")
        #print("qodraw: " + str(qodraw))

        qodrawsplit = qodraw.split("\":")
        checklen = len(qodrawsplit)

        if checklen == 4:
            return messageDetail.ReplyToChat("Quote of the Day will be live again tomorrow :)")
        else:

            qodrawsplitdata = str(qodrawsplit[5][2:][:-23])
            qodrawsplitdata = qodrawsplitdata.replace("\",", "")
            qodrawsplitAuhor = str(qodrawsplit[7][2:][:-21])
            qodrawsplitAuhor = qodrawsplitAuhor.replace("\",", "")

            msg = "<card accent=\"tempo-bg-color--blue\"><header>Quote of the Day by " + str(qodrawsplitAuhor) + "</header><body>" + str(qodrawsplitdata).replace("\\r\\n"," ").replace("\\r\\"," ") + "</body></card>"

        return messageDetail.ReplyToChatV2(str(msg))

    else:
        return messageDetail.ReplyToChat("Please just type /qod to get the Quote of the Day")


def weather(messageDetail):
    botlog.LogSymphonyInfo("Bot Call: Weather")

    message = (messageDetail.Command.MessageText)
    weatherCatcher = message.split()
    location = ""
    days = ""
    rawtwo = 2
    two = str(rawtwo)
    rawthree = 3
    three = str(rawthree)
    rawfour = 4
    four = str(rawfour)
    rawfive = 5
    five = str(rawfive)
    rawsix = 6
    six = str(rawsix)
    rawseven = 7
    seven = str(rawseven)

    catchLength = len(weatherCatcher)
    #print("Lenght is: " + (str(catchLength)))

    try:
        emptyLocation = catchLength == 0 or weatherCatcher[0] == ""
        if emptyLocation:
            return messageDetail.ReplyToChat("Please enter a location, if it is more than one word, e.g New York, please use underscore as in New_York")
        else:
            location = weatherCatcher[0]
            #print("Location: " + location)
    except:
        messageDetail.ReplyToChat("Loading the weather forecast")

    try:
        emptyDays = weatherCatcher[1] == ""
        if emptyDays:
            days = 0
        else:
            days = weatherCatcher[1]
            messageDetail.ReplyToChatV2("Forecasting weather for <b>" + days + "</b> days in <b>" + location + "</b>")
            #print("Days: " + days)
    except:
        messageDetail.ReplyToChatV2("Forecasting weather for today in <b>" + location + "</b>")


    conn = http.client.HTTPSConnection("api.apixu.com")

    headers = {
        'cache-control': "no-cache",
    }

    conn.request("GET", "/v1/forecast.json?key=" + _config['weather']['API_Key'] + "&q=" + location + "&days=" + days + "", headers=headers)

    res = conn.getresponse()
    data = res.read()

    # Checking for location validation
    notmatchingLocation = "{error:{code:1006,message:No matching location found.}}"
    tempWeather = str(data.decode("utf-8")).replace("\"", "")
    #print("tempWeather: " + str(tempWeather))

    if tempWeather == notmatchingLocation:
        return messageDetail.ReplyToChat("The location entered is not valid, please try again.")
    else:

        try:
            # Main weather info - to display regardless of days selected
            weatherRaw = tempWeather.split(":")
            LocationName = weatherRaw[2][:-7]
            Region = weatherRaw[3][:-8]
            Country = weatherRaw[4][:-4]
            LastUpdated = weatherRaw[13][11:] + ":" + weatherRaw[14][:-7]
            TempC = weatherRaw[15][:-7]
            TempF = weatherRaw[16][:-7]
            Condition = weatherRaw[19][:-5]
            CurrentURL = weatherRaw[20][:-5]

            day1date = weatherRaw[38][:-11]
            day1maxtemp = weatherRaw[41][:-10] + " C / " + weatherRaw[42][:-10] + " F"
            day1mintemp = weatherRaw[43][:-10] + " C / " + weatherRaw[44][:-10] + " F"
            day1avgtemp = weatherRaw[45][:-10] + " C / " + weatherRaw[46][:-12] + " F"
            day1maxwind = weatherRaw[47][:-12] + " mph / " + weatherRaw[48][:-15] + " kph"
            day1totalprecip = weatherRaw[49][:-15] + "mm / " + weatherRaw[50][:-10] + "in"
            day1avghumidity = weatherRaw[53][:-10]
            day1condition = weatherRaw[55][:-5]
            day1icon = weatherRaw[56][:-5]
            day1sunrise = weatherRaw[60] + ":" + weatherRaw[61][:-7]
            day1sunset = weatherRaw[62] + ":" + weatherRaw[63][:-9]
            day1moonrise = weatherRaw[64] + ":" + weatherRaw[65][:-8]
        except:
            return messageDetail.ReplyToChat("Sorry, I am not able to get the weather, please try again later")

        if days == 0 or days == 1:
            day1moonset = weatherRaw[66] + ":" + weatherRaw[67][:-5]
        else:
            day1moonset = weatherRaw[66] + ":" + weatherRaw[67][:-8]

        table_body = "<table style='table-layout:fixed;width:100%'>" \
                     "<thead>" \
                     "<tr class=\"tempo-text-color--white tempo-bg-color--black\">" \
                     "<td>Date</td>" \
                     "<td>Max Temp</td>" \
                     "<td>Min Temp</td>" \
                     "<td>Avg Temp</td>" \
                     "<td>Max Wind</td>" \
                     "<td>Tot Precipitation</td>" \
                     "<td>Avg Humidity</td>" \
                     "<td>Condition</td>" \
                     "<td></td>" \
                     "<td>Sunrise</td>" \
                     "<td>Sunset</td>" \
                     "<td>Moonrise</td>" \
                     "<td>Moonset</td>" \
                     "</tr>" \
                     "</thead><tbody>"

        table_body += "<tr><td>" + day1date + "</td><td>" + day1maxtemp + "</td><td>" + day1mintemp + "</td><td>" + day1avgtemp + "</td><td>" + day1maxwind + "</td><td>" + day1totalprecip + "</td><td>" + day1avghumidity + "</td><td>" + day1condition + "</td><td><img src=\"" + day1icon + "\"/></td><td>" + day1sunrise + "</td><td>" + day1sunset + "</td><td>" + day1moonrise + "</td><td>" + day1moonset + "</td></tr>"

        if days == two:

            try:
                #print("2 days")
                day2date = weatherRaw[68][:-11]
                day2maxtemp = weatherRaw[71][:-10] + " C / " + weatherRaw[72][:-10] + " F"
                day2mintemp = weatherRaw[73][:-10] + " C / " + weatherRaw[74][:-10] + " F"
                day2avgtemp = weatherRaw[75][:-10] + " C / " + weatherRaw[76][:-12] + " F"
                day2maxwind = weatherRaw[77][:-12] + " mph / " + weatherRaw[78][:-15] + " kph"
                day2totalprecip = weatherRaw[79][:-15] + "mm / " + weatherRaw[80][:-10] + "in"
                day2avghumidity = weatherRaw[83][:-10]
                day2condition = weatherRaw[85][:-5]
                day2icon = weatherRaw[86][:-5]
                day2sunrise = weatherRaw[90] + ":" + weatherRaw[91][:-7]
                day2sunset = weatherRaw[92] + ":" + weatherRaw[93][:-9]
                day2moonrise = weatherRaw[94] + ":" + weatherRaw[95][:-8]
                day2moonset = weatherRaw[96] + ":" + weatherRaw[97][:-5]
            except:
                return messageDetail.ReplyToChat("Sorry, I am not able to get the weather, please try again later")

            table_body += "<tr><td>" + day2date + "</td><td>" + day2maxtemp + "</td><td>" + day2mintemp + "</td><td>" + day2avgtemp + "</td><td>" + day2maxwind + "</td><td>" + day2totalprecip + "</td><td>" + day2avghumidity + "</td><td>" + day2condition + "</td><td><img src=\"" + day2icon + "\"/></td><td>" + day2sunrise + "</td><td>" + day2sunset + "</td><td>" + day2moonrise + "</td><td>" + day2moonset + "</td></tr>"

        if days == three:

            try:
                #print("2 days")
                day2date = weatherRaw[68][:-11]
                day2maxtemp = weatherRaw[71][:-10] + " C / " + weatherRaw[72][:-10] + " F"
                day2mintemp = weatherRaw[73][:-10] + " C / " + weatherRaw[74][:-10] + " F"
                day2avgtemp = weatherRaw[75][:-10] + " C / " + weatherRaw[76][:-12] + " F"
                day2maxwind = weatherRaw[77][:-12] + " mph / " + weatherRaw[78][:-15] + " kph"
                day2totalprecip = weatherRaw[79][:-15] + "mm / " + weatherRaw[80][:-10] + "in"
                day2avghumidity = weatherRaw[83][:-10]
                day2condition = weatherRaw[85][:-5]
                day2icon = weatherRaw[86][:-5]
                day2sunrise = weatherRaw[90] + ":" + weatherRaw[91][:-7]
                day2sunset = weatherRaw[92] + ":" + weatherRaw[93][:-9]
                day2moonrise = weatherRaw[94] + ":" + weatherRaw[95][:-8]
                day2moonset = weatherRaw[96] + ":" + weatherRaw[97][:-8]
            except:
                return messageDetail.ReplyToChat("Sorry, I am not able to get the weather, please try again later")

            table_body += "<tr><td>" + day2date + "</td><td>" + day2maxtemp + "</td><td>" + day2mintemp + "</td><td>" + day2avgtemp + "</td><td>" + day2maxwind + "</td><td>" + day2totalprecip + "</td><td>" + day2avghumidity + "</td><td>" + day2condition + "</td><td><img src=\"" + day2icon + "\"/></td><td>" + day2sunrise + "</td><td>" + day2sunset + "</td><td>" + day2moonrise + "</td><td>" + day2moonset + "</td></tr>"

            try:
                #print("3 days")
                day3date = weatherRaw[68+30][:-11]
                day3maxtemp = weatherRaw[71+30][:-10] + " C / " + weatherRaw[72][:-10] + " F"
                day3mintemp = weatherRaw[73+30][:-10] + " C / " + weatherRaw[74][:-10] + " F"
                day3avgtemp = weatherRaw[75+30][:-10] + " C / " + weatherRaw[76][:-12] + " F"
                day3maxwind = weatherRaw[77+30][:-12] + " mph / " + weatherRaw[78][:-15] + " kph"
                day3totalprecip = weatherRaw[79+30][:-15] + "mm / " + weatherRaw[80][:-10] + "in"
                day3avghumidity = weatherRaw[83+30][:-10]
                day3condition = weatherRaw[85+30][:-5]
                day3icon = weatherRaw[86+30][:-5]
                day3sunrise = weatherRaw[90+30] + ":" + weatherRaw[91][:-7]
                day3sunset = weatherRaw[92+30] + ":" + weatherRaw[93][:-9]
                day3moonrise = weatherRaw[94+30] + ":" + weatherRaw[95][:-8]
                day3moonset = weatherRaw[96+30] + ":" + weatherRaw[97][:-8]
            except:
                return messageDetail.ReplyToChat("Sorry, I am not able to get the weather, please try again later")

            table_body += "<tr><td>" + day3date + "</td><td>" + day3maxtemp + "</td><td>" + day3mintemp + "</td><td>" + day3avgtemp + "</td><td>" + day3maxwind + "</td><td>" + day3totalprecip + "</td><td>" + day3avghumidity + "</td><td>" + day3condition + "</td><td><img src=\"" + day3icon + "\"/></td><td>" + day3sunrise + "</td><td>" + day3sunset + "</td><td>" + day3moonrise + "</td><td>" + day3moonset + "</td></tr>"


        if days == four:

            try:
                #print("2 days")
                day2date = weatherRaw[68][:-11]
                day2maxtemp = weatherRaw[71][:-10] + " C / " + weatherRaw[72][:-10] + " F"
                day2mintemp = weatherRaw[73][:-10] + " C / " + weatherRaw[74][:-10] + " F"
                day2avgtemp = weatherRaw[75][:-10] + " C / " + weatherRaw[76][:-12] + " F"
                day2maxwind = weatherRaw[77][:-12] + " mph / " + weatherRaw[78][:-15] + " kph"
                day2totalprecip = weatherRaw[79][:-15] + "mm / " + weatherRaw[80][:-10] + "in"
                day2avghumidity = weatherRaw[83][:-10]
                day2condition = weatherRaw[85][:-5]
                day2icon = weatherRaw[86][:-5]
                day2sunrise = weatherRaw[90] + ":" + weatherRaw[91][:-7]
                day2sunset = weatherRaw[92] + ":" + weatherRaw[93][:-9]
                day2moonrise = weatherRaw[94] + ":" + weatherRaw[95][:-8]
                day2moonset = weatherRaw[96] + ":" + weatherRaw[97][:-8]
            except:
                return messageDetail.ReplyToChat("Sorry, I am not able to get the weather, please try again later")

            table_body += "<tr><td>" + day2date + "</td><td>" + day2maxtemp + "</td><td>" + day2mintemp + "</td><td>" + day2avgtemp + "</td><td>" + day2maxwind + "</td><td>" + day2totalprecip + "</td><td>" + day2avghumidity + "</td><td>" + day2condition + "</td><td><img src=\"" + day2icon + "\"/></td><td>" + day2sunrise + "</td><td>" + day2sunset + "</td><td>" + day2moonrise + "</td><td>" + day2moonset + "</td></tr>"

            try:
                #print("3 days")
                day3date = weatherRaw[68+30][:-11]
                day3maxtemp = weatherRaw[71+30][:-10] + " C / " + weatherRaw[72+30][:-10] + " F"
                day3mintemp = weatherRaw[73+30][:-10] + " C / " + weatherRaw[74+30][:-10] + " F"
                day3avgtemp = weatherRaw[75+30][:-10] + " C / " + weatherRaw[76+30][:-12] + " F"
                day3maxwind = weatherRaw[77+30][:-12] + " mph / " + weatherRaw[78+30][:-15] + " kph"
                day3totalprecip = weatherRaw[79+30][:-15] + "mm / " + weatherRaw[80+30][:-10] + "in"
                day3avghumidity = weatherRaw[83+30][:-10]
                day3condition = weatherRaw[85+30][:-5]
                day3icon = weatherRaw[86+30][:-5]
                day3sunrise = weatherRaw[90+30] + ":" + weatherRaw[91+30][:-7]
                day3sunset = weatherRaw[92+30] + ":" + weatherRaw[93+30][:-9]
                day3moonrise = weatherRaw[94+30] + ":" + weatherRaw[95+30][:-8]
                day3moonset = weatherRaw[96+30] + ":" + weatherRaw[97+30][:-8]
            except:
                return messageDetail.ReplyToChat("Sorry, I am not able to get the weather, please try again later")

            table_body += "<tr><td>" + day3date + "</td><td>" + day3maxtemp + "</td><td>" + day3mintemp + "</td><td>" + day3avgtemp + "</td><td>" + day3maxwind + "</td><td>" + day3totalprecip + "</td><td>" + day3avghumidity + "</td><td>" + day3condition + "</td><td><img src=\"" + day3icon + "\"/></td><td>" + day3sunrise + "</td><td>" + day3sunset + "</td><td>" + day3moonrise + "</td><td>" + day3moonset + "</td></tr>"

            try:
                #print("4 days")
                day4date = weatherRaw[68+60][:-11]
                day4maxtemp = weatherRaw[71+60][:-10] + " C / " + weatherRaw[72+60][:-10] + " F"
                day4mintemp = weatherRaw[73+60][:-10] + " C / " + weatherRaw[74+60][:-10] + " F"
                day4avgtemp = weatherRaw[75+60][:-10] + " C / " + weatherRaw[76+60][:-12] + " F"
                day4maxwind = weatherRaw[77+60][:-12] + " mph / " + weatherRaw[78+60][:-15] + " kph"
                day4totalprecip = weatherRaw[79+60][:-15] + "mm / " + weatherRaw[80+60][:-10] + "in"
                day4avghumidity = weatherRaw[83+60][:-10]
                day4condition = weatherRaw[85+60][:-5]
                day4icon = weatherRaw[86+60][:-5]
                day4sunrise = weatherRaw[90+60] + ":" + weatherRaw[91+60][:-7]
                day4sunset = weatherRaw[92+60] + ":" + weatherRaw[93+60][:-9]
                day4moonrise = weatherRaw[94+60] + ":" + weatherRaw[95+60][:-8]
                day4moonset = weatherRaw[96+60] + ":" + weatherRaw[97+60][:-5]
            except:
                return messageDetail.ReplyToChat("Sorry, I am not able to get the weather, please try again later")

            table_body += "<tr><td>" + day4date + "</td><td>" + day4maxtemp + "</td><td>" + day4mintemp + "</td><td>" + day4avgtemp + "</td><td>" + day4maxwind + "</td><td>" + day4totalprecip + "</td><td>" + day4avghumidity + "</td><td>" + day4condition + "</td><td><img src=\"" + day4icon + "\"/></td><td>" + day4sunrise + "</td><td>" + day4sunset + "</td><td>" + day4moonrise + "</td><td>" + day4moonset + "</td></tr>"

        if days == five:
            try:
                #print("2 days")
                day2date = weatherRaw[68][:-11]
                day2maxtemp = weatherRaw[71][:-10] + " C / " + weatherRaw[72][:-10] + " F"
                day2mintemp = weatherRaw[73][:-10] + " C / " + weatherRaw[74][:-10] + " F"
                day2avgtemp = weatherRaw[75][:-10] + " C / " + weatherRaw[76][:-12] + " F"
                day2maxwind = weatherRaw[77][:-12] + " mph / " + weatherRaw[78][:-15] + " kph"
                day2totalprecip = weatherRaw[79][:-15] + "mm / " + weatherRaw[80][:-10] + "in"
                day2avghumidity = weatherRaw[83][:-10]
                day2condition = weatherRaw[85][:-5]
                day2icon = weatherRaw[86][:-5]
                day2sunrise = weatherRaw[90] + ":" + weatherRaw[91][:-7]
                day2sunset = weatherRaw[92] + ":" + weatherRaw[93][:-9]
                day2moonrise = weatherRaw[94] + ":" + weatherRaw[95][:-8]
                day2moonset = weatherRaw[96] + ":" + weatherRaw[97][:-8]
            except:
                return messageDetail.ReplyToChat("Sorry, I am not able to get the weather, please try again later")

            table_body += "<tr><td>" + day2date + "</td><td>" + day2maxtemp + "</td><td>" + day2mintemp + "</td><td>" + day2avgtemp + "</td><td>" + day2maxwind + "</td><td>" + day2totalprecip + "</td><td>" + day2avghumidity + "</td><td>" + day2condition + "</td><td><img src=\"" + day2icon + "\"/></td><td>" + day2sunrise + "</td><td>" + day2sunset + "</td><td>" + day2moonrise + "</td><td>" + day2moonset + "</td></tr>"

            try:
                #print("3 days")
                day3date = weatherRaw[68+30][:-11]
                day3maxtemp = weatherRaw[71+30][:-10] + " C / " + weatherRaw[72+30][:-10] + " F"
                day3mintemp = weatherRaw[73+30][:-10] + " C / " + weatherRaw[74+30][:-10] + " F"
                day3avgtemp = weatherRaw[75+30][:-10] + " C / " + weatherRaw[76+30][:-12] + " F"
                day3maxwind = weatherRaw[77+30][:-12] + " mph / " + weatherRaw[78+30][:-15] + " kph"
                day3totalprecip = weatherRaw[79+30][:-15] + "mm / " + weatherRaw[80+30][:-10] + "in"
                day3avghumidity = weatherRaw[83+30][:-10]
                day3condition = weatherRaw[85+30][:-5]
                day3icon = weatherRaw[86+30][:-5]
                day3sunrise = weatherRaw[90+30] + ":" + weatherRaw[91+30][:-7]
                day3sunset = weatherRaw[92+30] + ":" + weatherRaw[93+30][:-9]
                day3moonrise = weatherRaw[94+30] + ":" + weatherRaw[95+30][:-8]
                day3moonset = weatherRaw[96+30] + ":" + weatherRaw[97+30][:-8]
            except:
                return messageDetail.ReplyToChat("Sorry, I am not able to get the weather, please try again later")

            table_body += "<tr><td>" + day3date + "</td><td>" + day3maxtemp + "</td><td>" + day3mintemp + "</td><td>" + day3avgtemp + "</td><td>" + day3maxwind + "</td><td>" + day3totalprecip + "</td><td>" + day3avghumidity + "</td><td>" + day3condition + "</td><td><img src=\"" + day3icon + "\"/></td><td>" + day3sunrise + "</td><td>" + day3sunset + "</td><td>" + day3moonrise + "</td><td>" + day3moonset + "</td></tr>"

            try:
                #print("4 days")
                day4date = weatherRaw[68+60][:-11]
                day4maxtemp = weatherRaw[71+60][:-10] + " C / " + weatherRaw[72+60][:-10] + " F"
                day4mintemp = weatherRaw[73+60][:-10] + " C / " + weatherRaw[74+60][:-10] + " F"
                day4avgtemp = weatherRaw[75+60][:-10] + " C / " + weatherRaw[76+60][:-12] + " F"
                day4maxwind = weatherRaw[77+60][:-12] + " mph / " + weatherRaw[78+60][:-15] + " kph"
                day4totalprecip = weatherRaw[79+60][:-15] + "mm / " + weatherRaw[80+60][:-10] + "in"
                day4avghumidity = weatherRaw[83+60][:-10]
                day4condition = weatherRaw[85+60][:-5]
                day4icon = weatherRaw[86+60][:-5]
                day4sunrise = weatherRaw[90+60] + ":" + weatherRaw[91+60][:-7]
                day4sunset = weatherRaw[92+60] + ":" + weatherRaw[93+60][:-9]
                day4moonrise = weatherRaw[94+60] + ":" + weatherRaw[95+60][:-8]
                day4moonset = weatherRaw[96+60] + ":" + weatherRaw[97+60][:-8]
            except:
                return messageDetail.ReplyToChat("Sorry, I am not able to get the weather, please try again later")

            table_body += "<tr><td>" + day4date + "</td><td>" + day4maxtemp + "</td><td>" + day4mintemp + "</td><td>" + day4avgtemp + "</td><td>" + day4maxwind + "</td><td>" + day4totalprecip + "</td><td>" + day4avghumidity + "</td><td>" + day4condition + "</td><td><img src=\"" + day4icon + "\"/></td><td>" + day4sunrise + "</td><td>" + day4sunset + "</td><td>" + day4moonrise + "</td><td>" + day4moonset + "</td></tr>"

            try:
                #print("5 days")
                day5date = weatherRaw[68+90][:-11]
                day5maxtemp = weatherRaw[71+90][:-10] + " C / " + weatherRaw[72+90][:-10] + " F"
                day5mintemp = weatherRaw[73+90][:-10] + " C / " + weatherRaw[74+90][:-10] + " F"
                day5avgtemp = weatherRaw[75+90][:-10] + " C / " + weatherRaw[76+90][:-12] + " F"
                day5maxwind = weatherRaw[77+90][:-12] + " mph / " + weatherRaw[78+90][:-15] + " kph"
                day5totalprecip = weatherRaw[79+90][:-15] + "mm / " + weatherRaw[80+90][:-10] + "in"
                day5avghumidity = weatherRaw[83+90][:-10]
                day5condition = weatherRaw[85+90][:-5]
                day5icon = weatherRaw[86+90][:-5]
                day5sunrise = weatherRaw[90+90] + ":" + weatherRaw[91+90][:-7]
                day5sunset = weatherRaw[92+90] + ":" + weatherRaw[93+90][:-9]
                day5moonrise = weatherRaw[94+90] + ":" + weatherRaw[95+90][:-8]
                day5moonset = weatherRaw[96+90] + ":" + weatherRaw[97+90][:-5]
            except:
                return messageDetail.ReplyToChat("Sorry, I am not able to get the weather, please try again later")

            table_body += "<tr><td>" + day5date + "</td><td>" + day5maxtemp + "</td><td>" + day5mintemp + "</td><td>" + day5avgtemp + "</td><td>" + day5maxwind + "</td><td>" + day5totalprecip + "</td><td>" + day5avghumidity + "</td><td>" + day5condition + "</td><td><img src=\"" + day5icon + "\"/></td><td>" + day5sunrise + "</td><td>" + day5sunset + "</td><td>" + day5moonrise + "</td><td>" + day5moonset + "</td></tr>"

        if days == six:

            try:
                #print("2 days")
                day2date = weatherRaw[68][:-11]
                day2maxtemp = weatherRaw[71][:-10] + " C / " + weatherRaw[72][:-10] + " F"
                day2mintemp = weatherRaw[73][:-10] + " C / " + weatherRaw[74][:-10] + " F"
                day2avgtemp = weatherRaw[75][:-10] + " C / " + weatherRaw[76][:-12] + " F"
                day2maxwind = weatherRaw[77][:-12] + " mph / " + weatherRaw[78][:-15] + " kph"
                day2totalprecip = weatherRaw[79][:-15] + "mm / " + weatherRaw[80][:-10] + "in"
                day2avghumidity = weatherRaw[83][:-10]
                day2condition = weatherRaw[85][:-5]
                day2icon = weatherRaw[86][:-5]
                day2sunrise = weatherRaw[90] + ":" + weatherRaw[91][:-7]
                day2sunset = weatherRaw[92] + ":" + weatherRaw[93][:-9]
                day2moonrise = weatherRaw[94] + ":" + weatherRaw[95][:-8]
                day2moonset = weatherRaw[96] + ":" + weatherRaw[97][:-8]
            except:
                return messageDetail.ReplyToChat("Sorry, I am not able to get the weather, please try again later")

            table_body += "<tr><td>" + day2date + "</td><td>" + day2maxtemp + "</td><td>" + day2mintemp + "</td><td>" + day2avgtemp + "</td><td>" + day2maxwind + "</td><td>" + day2totalprecip + "</td><td>" + day2avghumidity + "</td><td>" + day2condition + "</td><td><img src=\"" + day2icon + "\"/></td><td>" + day2sunrise + "</td><td>" + day2sunset + "</td><td>" + day2moonrise + "</td><td>" + day2moonset + "</td></tr>"

            try:
                #print("3 days")
                day3date = weatherRaw[68+30][:-11]
                day3maxtemp = weatherRaw[71+30][:-10] + " C / " + weatherRaw[72+30][:-10] + " F"
                day3mintemp = weatherRaw[73+30][:-10] + " C / " + weatherRaw[74+30][:-10] + " F"
                day3avgtemp = weatherRaw[75+30][:-10] + " C / " + weatherRaw[76+30][:-12] + " F"
                day3maxwind = weatherRaw[77+30][:-12] + " mph / " + weatherRaw[78+30][:-15] + " kph"
                day3totalprecip = weatherRaw[79+30][:-15] + "mm / " + weatherRaw[80+30][:-10] + "in"
                day3avghumidity = weatherRaw[83+30][:-10]
                day3condition = weatherRaw[85+30][:-5]
                day3icon = weatherRaw[86+30][:-5]
                day3sunrise = weatherRaw[90+30] + ":" + weatherRaw[91+30][:-7]
                day3sunset = weatherRaw[92+30] + ":" + weatherRaw[93+30][:-9]
                day3moonrise = weatherRaw[94+30] + ":" + weatherRaw[95+30][:-8]
                day3moonset = weatherRaw[96+30] + ":" + weatherRaw[97+30][:-8]
            except:
                return messageDetail.ReplyToChat("Sorry, I am not able to get the weather, please try again later")

            table_body += "<tr><td>" + day3date + "</td><td>" + day3maxtemp + "</td><td>" + day3mintemp + "</td><td>" + day3avgtemp + "</td><td>" + day3maxwind + "</td><td>" + day3totalprecip + "</td><td>" + day3avghumidity + "</td><td>" + day3condition + "</td><td><img src=\"" + day3icon + "\"/></td><td>" + day3sunrise + "</td><td>" + day3sunset + "</td><td>" + day3moonrise + "</td><td>" + day3moonset + "</td></tr>"

            try:
                #print("4 days")
                day4date = weatherRaw[68+60][:-11]
                day4maxtemp = weatherRaw[71+60][:-10] + " C / " + weatherRaw[72+60][:-10] + " F"
                day4mintemp = weatherRaw[73+60][:-10] + " C / " + weatherRaw[74+60][:-10] + " F"
                day4avgtemp = weatherRaw[75+60][:-10] + " C / " + weatherRaw[76+60][:-12] + " F"
                day4maxwind = weatherRaw[77+60][:-12] + " mph / " + weatherRaw[78+60][:-15] + " kph"
                day4totalprecip = weatherRaw[79+60][:-15] + "mm / " + weatherRaw[80+60][:-10] + "in"
                day4avghumidity = weatherRaw[83+60][:-10]
                day4condition = weatherRaw[85+60][:-5]
                day4icon = weatherRaw[86+60][:-5]
                day4sunrise = weatherRaw[90+60] + ":" + weatherRaw[91+60][:-7]
                day4sunset = weatherRaw[92+60] + ":" + weatherRaw[93+60][:-9]
                day4moonrise = weatherRaw[94+60] + ":" + weatherRaw[95+60][:-8]
                day4moonset = weatherRaw[96+60] + ":" + weatherRaw[97+60][:-8]
            except:
                return messageDetail.ReplyToChat("Sorry, I am not able to get the weather, please try again later")

            table_body += "<tr><td>" + day4date + "</td><td>" + day4maxtemp + "</td><td>" + day4mintemp + "</td><td>" + day4avgtemp + "</td><td>" + day4maxwind + "</td><td>" + day4totalprecip + "</td><td>" + day4avghumidity + "</td><td>" + day4condition + "</td><td><img src=\"" + day4icon + "\"/></td><td>" + day4sunrise + "</td><td>" + day4sunset + "</td><td>" + day4moonrise + "</td><td>" + day4moonset + "</td></tr>"

            try:
                #print("5 days")
                day5date = weatherRaw[68+90][:-11]
                day5maxtemp = weatherRaw[71+90][:-10] + " C / " + weatherRaw[72+90][:-10] + " F"
                day5mintemp = weatherRaw[73+90][:-10] + " C / " + weatherRaw[74+90][:-10] + " F"
                day5avgtemp = weatherRaw[75+90][:-10] + " C / " + weatherRaw[76+90][:-12] + " F"
                day5maxwind = weatherRaw[77+90][:-12] + " mph / " + weatherRaw[78+90][:-15] + " kph"
                day5totalprecip = weatherRaw[79+90][:-15] + "mm / " + weatherRaw[80+90][:-10] + "in"
                day5avghumidity = weatherRaw[83+90][:-10]
                day5condition = weatherRaw[85+90][:-5]
                day5icon = weatherRaw[86+90][:-5]
                day5sunrise = weatherRaw[90+90] + ":" + weatherRaw[91+90][:-7]
                day5sunset = weatherRaw[92+90] + ":" + weatherRaw[93+90][:-9]
                day5moonrise = weatherRaw[94+90] + ":" + weatherRaw[95+90][:-8]
                day5moonset = weatherRaw[96+90] + ":" + weatherRaw[97+90][:-8]
            except:
                return messageDetail.ReplyToChat("Sorry, I am not able to get the weather, please try again later")

            table_body += "<tr><td>" + day5date + "</td><td>" + day5maxtemp + "</td><td>" + day5mintemp + "</td><td>" + day5avgtemp + "</td><td>" + day5maxwind + "</td><td>" + day5totalprecip + "</td><td>" + day5avghumidity + "</td><td>" + day5condition + "</td><td><img src=\"" + day5icon + "\"/></td><td>" + day5sunrise + "</td><td>" + day5sunset + "</td><td>" + day5moonrise + "</td><td>" + day5moonset + "</td></tr>"

            try:
                #print("6 days")
                day6date = weatherRaw[68+120][:-11]
                day6maxtemp = weatherRaw[71+120][:-10] + " C / " + weatherRaw[72+120][:-10] + " F"
                day6mintemp = weatherRaw[73+120][:-10] + " C / " + weatherRaw[74+120][:-10] + " F"
                day6avgtemp = weatherRaw[75+120][:-10] + " C / " + weatherRaw[76+120][:-12] + " F"
                day6maxwind = weatherRaw[77+120][:-12] + " mph / " + weatherRaw[78+120][:-15] + " kph"
                day6totalprecip = weatherRaw[79+120][:-15] + "mm / " + weatherRaw[80+120][:-10] + "in"
                day6avghumidity = weatherRaw[83+120][:-10]
                day6condition = weatherRaw[85+120][:-5]
                day6icon = weatherRaw[86+120][:-5]
                day6sunrise = weatherRaw[90+120] + ":" + weatherRaw[91+120][:-7]
                day6sunset = weatherRaw[92+120] + ":" + weatherRaw[93+120][:-9]
                day6moonrise = weatherRaw[94+120] + ":" + weatherRaw[95+120][:-8]
                day6moonset = weatherRaw[96+120] + ":" + weatherRaw[97+120][:-5]
            except:
                return messageDetail.ReplyToChat("Sorry, I am not able to get the weather, please try again later")

            table_body += "<tr><td>" + day6date + "</td><td>" + day6maxtemp + "</td><td>" + day6mintemp + "</td><td>" + day6avgtemp + "</td><td>" + day6maxwind + "</td><td>" + day6totalprecip + "</td><td>" + day6avghumidity + "</td><td>" + day6condition + "</td><td><img src=\"" + day6icon + "\"/></td><td>" + day6sunrise + "</td><td>" + day6sunset + "</td><td>" + day6moonrise + "</td><td>" + day6moonset + "</td></tr>"


        if days == seven:

            try:
                #print("2 days")
                day2date = weatherRaw[68][:-11]
                day2maxtemp = weatherRaw[71][:-10] + " C / " + weatherRaw[72][:-10] + " F"
                day2mintemp = weatherRaw[73][:-10] + " C / " + weatherRaw[74][:-10] + " F"
                day2avgtemp = weatherRaw[75][:-10] + " C / " + weatherRaw[76][:-12] + " F"
                day2maxwind = weatherRaw[77][:-12] + " mph / " + weatherRaw[78][:-15] + " kph"
                day2totalprecip = weatherRaw[79][:-15] + "mm / " + weatherRaw[80][:-10] + "in"
                day2avghumidity = weatherRaw[83][:-10]
                day2condition = weatherRaw[85][:-5]
                day2icon = weatherRaw[86][:-5]
                day2sunrise = weatherRaw[90] + ":" + weatherRaw[91][:-7]
                day2sunset = weatherRaw[92] + ":" + weatherRaw[93][:-9]
                day2moonrise = weatherRaw[94] + ":" + weatherRaw[95][:-8]
                day2moonset = weatherRaw[96] + ":" + weatherRaw[97][:-8]
            except:
                return messageDetail.ReplyToChat("Sorry, I am not able to get the weather, please try again later")

            table_body += "<tr><td>" + day2date + "</td><td>" + day2maxtemp + "</td><td>" + day2mintemp + "</td><td>" + day2avgtemp + "</td><td>" + day2maxwind + "</td><td>" + day2totalprecip + "</td><td>" + day2avghumidity + "</td><td>" + day2condition + "</td><td><img src=\"" + day2icon + "\"/></td><td>" + day2sunrise + "</td><td>" + day2sunset + "</td><td>" + day2moonrise + "</td><td>" + day2moonset + "</td></tr>"

            try:
                #print("3 days")
                day3date = weatherRaw[68+30][:-11]
                day3maxtemp = weatherRaw[71+30][:-10] + " C / " + weatherRaw[72+30][:-10] + " F"
                day3mintemp = weatherRaw[73+30][:-10] + " C / " + weatherRaw[74+30][:-10] + " F"
                day3avgtemp = weatherRaw[75+30][:-10] + " C / " + weatherRaw[76+30][:-12] + " F"
                day3maxwind = weatherRaw[77+30][:-12] + " mph / " + weatherRaw[78+30][:-15] + " kph"
                day3totalprecip = weatherRaw[79+30][:-15] + "mm / " + weatherRaw[80+30][:-10] + "in"
                day3avghumidity = weatherRaw[83+30][:-10]
                day3condition = weatherRaw[85+30][:-5]
                day3icon = weatherRaw[86+30][:-5]
                day3sunrise = weatherRaw[90+30] + ":" + weatherRaw[91+30][:-7]
                day3sunset = weatherRaw[92+30] + ":" + weatherRaw[93+30][:-9]
                day3moonrise = weatherRaw[94+30] + ":" + weatherRaw[95+30][:-8]
                day3moonset = weatherRaw[96+30] + ":" + weatherRaw[97+30][:-8]
            except:
                return messageDetail.ReplyToChat("Sorry, I am not able to get the weather, please try again later")

            table_body += "<tr><td>" + day3date + "</td><td>" + day3maxtemp + "</td><td>" + day3mintemp + "</td><td>" + day3avgtemp + "</td><td>" + day3maxwind + "</td><td>" + day3totalprecip + "</td><td>" + day3avghumidity + "</td><td>" + day3condition + "</td><td><img src=\"" + day3icon + "\"/></td><td>" + day3sunrise + "</td><td>" + day3sunset + "</td><td>" + day3moonrise + "</td><td>" + day3moonset + "</td></tr>"

            try:
                #print("4 days")
                day4date = weatherRaw[68+60][:-11]
                day4maxtemp = weatherRaw[71+60][:-10] + " C / " + weatherRaw[72+60][:-10] + " F"
                day4mintemp = weatherRaw[73+60][:-10] + " C / " + weatherRaw[74+60][:-10] + " F"
                day4avgtemp = weatherRaw[75+60][:-10] + " C / " + weatherRaw[76+60][:-12] + " F"
                day4maxwind = weatherRaw[77+60][:-12] + " mph / " + weatherRaw[78+60][:-15] + " kph"
                day4totalprecip = weatherRaw[79+60][:-15] + "mm / " + weatherRaw[80+60][:-10] + "in"
                day4avghumidity = weatherRaw[83+60][:-10]
                day4condition = weatherRaw[85+60][:-5]
                day4icon = weatherRaw[86+60][:-5]
                day4sunrise = weatherRaw[90+60] + ":" + weatherRaw[91+60][:-7]
                day4sunset = weatherRaw[92+60] + ":" + weatherRaw[93+60][:-9]
                day4moonrise = weatherRaw[94+60] + ":" + weatherRaw[95+60][:-8]
                day4moonset = weatherRaw[96+60] + ":" + weatherRaw[97+60][:-8]
            except:
                return messageDetail.ReplyToChat("Sorry, I am not able to get the weather, please try again later")

            table_body += "<tr><td>" + day4date + "</td><td>" + day4maxtemp + "</td><td>" + day4mintemp + "</td><td>" + day4avgtemp + "</td><td>" + day4maxwind + "</td><td>" + day4totalprecip + "</td><td>" + day4avghumidity + "</td><td>" + day4condition + "</td><td><img src=\"" + day4icon + "\"/></td><td>" + day4sunrise + "</td><td>" + day4sunset + "</td><td>" + day4moonrise + "</td><td>" + day4moonset + "</td></tr>"

            try:
                #print("5 days")
                day5date = weatherRaw[68+90][:-11]
                day5maxtemp = weatherRaw[71+90][:-10] + " C / " + weatherRaw[72+90][:-10] + " F"
                day5mintemp = weatherRaw[73+90][:-10] + " C / " + weatherRaw[74+90][:-10] + " F"
                day5avgtemp = weatherRaw[75+90][:-10] + " C / " + weatherRaw[76+90][:-12] + " F"
                day5maxwind = weatherRaw[77+90][:-12] + " mph / " + weatherRaw[78+90][:-15] + " kph"
                day5totalprecip = weatherRaw[79+90][:-15] + "mm / " + weatherRaw[80+90][:-10] + "in"
                day5avghumidity = weatherRaw[83+90][:-10]
                day5condition = weatherRaw[85+90][:-5]
                day5icon = weatherRaw[86+90][:-5]
                day5sunrise = weatherRaw[90+90] + ":" + weatherRaw[91+90][:-7]
                day5sunset = weatherRaw[92+90] + ":" + weatherRaw[93+90][:-9]
                day5moonrise = weatherRaw[94+90] + ":" + weatherRaw[95+90][:-8]
                day5moonset = weatherRaw[96+90] + ":" + weatherRaw[97+90][:-8]
            except:
                return messageDetail.ReplyToChat("Sorry, I am not able to get the weather, please try again later")

            table_body += "<tr><td>" + day5date + "</td><td>" + day5maxtemp + "</td><td>" + day5mintemp + "</td><td>" + day5avgtemp + "</td><td>" + day5maxwind + "</td><td>" + day5totalprecip + "</td><td>" + day5avghumidity + "</td><td>" + day5condition + "</td><td><img src=\"" + day5icon + "\"/></td><td>" + day5sunrise + "</td><td>" + day5sunset + "</td><td>" + day5moonrise + "</td><td>" + day5moonset + "</td></tr>"

            try:
                #print("6 days")
                day6date = weatherRaw[68+120][:-11]
                day6maxtemp = weatherRaw[71+120][:-10] + " C / " + weatherRaw[72+120][:-10] + " F"
                day6mintemp = weatherRaw[73+120][:-10] + " C / " + weatherRaw[74+120][:-10] + " F"
                day6avgtemp = weatherRaw[75+120][:-10] + " C / " + weatherRaw[76+120][:-12] + " F"
                day6maxwind = weatherRaw[77+120][:-12] + " mph / " + weatherRaw[78+120][:-15] + " kph"
                day6totalprecip = weatherRaw[79+120][:-15] + "mm / " + weatherRaw[80+120][:-10] + "in"
                day6avghumidity = weatherRaw[83+120][:-10]
                day6condition = weatherRaw[85+120][:-5]
                day6icon = weatherRaw[86+120][:-5]
                day6sunrise = weatherRaw[90+120] + ":" + weatherRaw[91+120][:-7]
                day6sunset = weatherRaw[92+120] + ":" + weatherRaw[93+120][:-9]
                day6moonrise = weatherRaw[94+120] + ":" + weatherRaw[95+120][:-8]
                day6moonset = weatherRaw[96+120] + ":" + weatherRaw[97+120][:-8]
            except:
                return messageDetail.ReplyToChat("Sorry, I am not able to get the weather, please try again later")

            table_body += "<tr><td>" + day6date + "</td><td>" + day6maxtemp + "</td><td>" + day6mintemp + "</td><td>" + day6avgtemp + "</td><td>" + day6maxwind + "</td><td>" + day6totalprecip + "</td><td>" + day6avghumidity + "</td><td>" + day6condition + "</td><td><img src=\"" + day6icon + "\"/></td><td>" + day6sunrise + "</td><td>" + day6sunset + "</td><td>" + day6moonrise + "</td><td>" + day6moonset + "</td></tr>"

            try:
                #print("7 days")
                day7date = weatherRaw[68+150][:-11]
                day7maxtemp = weatherRaw[71+150][:-10] + " C / " + weatherRaw[72+150][:-10] + " F"
                day7mintemp = weatherRaw[73+150][:-10] + " C / " + weatherRaw[74+150][:-10] + " F"
                day7avgtemp = weatherRaw[75+150][:-10] + " C / " + weatherRaw[76+150][:-12] + " F"
                day7maxwind = weatherRaw[77+150][:-12] + " mph / " + weatherRaw[78+150][:-15] + " kph"
                day7totalprecip = weatherRaw[79+150][:-15] + "mm / " + weatherRaw[80+150][:-10] + "in"
                day7avghumidity = weatherRaw[83+150][:-10]
                day7condition = weatherRaw[85+150][:-5]
                day7icon = weatherRaw[86+150][:-5]
                day7sunrise = weatherRaw[90+150] + ":" + weatherRaw[91+150][:-7]
                day7sunset = weatherRaw[92+150] + ":" + weatherRaw[93+150][:-9]
                day7moonrise = weatherRaw[94+150] + ":" + weatherRaw[95+150][:-8]
                day7moonset = weatherRaw[96+150] + ":" + weatherRaw[97+150][:-5]
            except:
                return messageDetail.ReplyToChat("Sorry, I am not able to get the weather, please try again later")

            table_body += "<tr><td>" + day7date + "</td><td>" + day7maxtemp + "</td><td>" + day7mintemp + "</td><td>" + day7avgtemp + "</td><td>" + day7maxwind + "</td><td>" + day7totalprecip + "</td><td>" + day7avghumidity + "</td><td>" + day7condition + "</td><td><img src=\"" + day7icon + "\"/></td><td>" + day7sunrise + "</td><td>" + day7sunset + "</td><td>" + day7moonrise + "</td><td>" + day7moonset + "</td></tr>"

        table_body += "</tbody></table>"

        return messageDetail.ReplyToChatV2_noBotLog("<card iconSrc=\"https://thumb.ibb.co/csXBgU/Symphony2018_App_Icon_Mobile.png\" accent=\"tempo-bg-color--blue\"><header>the current condition in " + LocationName + ", " + Region + ", " + Country + " as of " + LastUpdated + " is " + Condition + ", <img src=\"" + CurrentURL + "\"/> (" + TempC + " C / " + TempF + " F)<br/></header><body>" + table_body + "</body></card>")

def funQuote(messageDetail):
    botlog.LogSymphonyInfo("Bot Call: Fun Quote")

    try:
        conn = http.client.HTTPSConnection(_config['x-mashape']['URL'])

        headers = {
            'x-mashape-key': _config['x-mashape']['API_Key'],
            'cache-control': "no-cache"
        }

        conn.request("GET", "/", headers=headers)

        res = conn.getresponse()
        data = res.read().decode("utf-8")
        #print("data: " + data)

        fundata = str(data)
        quotedata = fundata.split(":")
        quote = quotedata[1][:-9]
        author = quotedata[2][1:][:-12]
        category = quotedata[3][:-2].replace("\"", "")
    except:
        return messageDetail.ReplyToChat("Please try FunQuote later.")

    return messageDetail.ReplyToChat(category + " quote from " + author + ": " + quote)

def joke(messageDetail):
    botlog.LogSymphonyInfo("Bot Call: Joke")

    try:
        conn = http.client.HTTPSConnection(_config['Jokes']['URL'])

        headers = {
            'accept': "application/json",
            'user-agent': _config['Jokes']['user-agent'],
            'cache-control': "no-cache"
        }

        conn.request("GET", "/", headers=headers)

        res = conn.getresponse()
        data = res.read().decode("utf-8")

        render = data.split("\":")
        jokeData = render[2][:-8]
    except:
        return messageDetail.ReplyToChat("Please try Joke later.")

    return messageDetail.ReplyToChat("Here's a joke for you" + jokeData)


def addAcronym(messageDetail):
    botlog.LogSymphonyInfo("Bot Call: Add Acronym")

    try:
        commandCallerUID = messageDetail.FromUserId

        connComp = http.client.HTTPSConnection(_configDef['symphonyinfo']['pod_hostname'])
        sessionTok = callout.GetSessionToken()

        headersCompany = {
            'sessiontoken': sessionTok,
            'cache-control': "no-cache"
        }

        connComp.request("GET", "/pod/v3/users?uid=" + commandCallerUID, headers=headersCompany)

        resComp = connComp.getresponse()
        dataComp = resComp.read()
        data_raw = str(dataComp.decode('utf-8'))
        data_dict = ast.literal_eval(data_raw)

        dataRender = json.dumps(data_dict, indent=2)
        d_org = json.loads(dataRender)

        for index_org in range(len(d_org["users"])):
            firstName = d_org["users"][index_org]["firstName"]
            lastName = d_org["users"][index_org]["lastName"]
            displayName = d_org["users"][index_org]["displayName"]
            companyName = d_org["users"][index_org]["company"]
            userID = str(d_org["users"][index_org]["id"])

            botlog.LogSymphonyInfo(firstName + " " + lastName + " from Company/Pod name: " + str(companyName) + " with UID: " + str(userID))
            callerCheck = (firstName + " " + lastName + " - " + displayName + " - " + companyName + " - " + str(userID))
    except:
        return messageDetail.ReplyToChat("Cannot validate user access")

    if callerCheck in AccessFile:

        try:
            message = (messageDetail.Command.MessageText)
            info = message.split("-")
            acronym = str(info[0]).strip()
            answer = info[1][1:]

            AcronymsDictionary.update({acronym.upper(): answer})
            sortDict(messageDetail)

            return messageDetail.ReplyToChat(acronym + " was successfully added. Thank you for extending my knowledge")

        except:
            return messageDetail.ReplyToChat("Invalid format")
    else:
        return messageDetail.ReplyToChat("You aren't authorised to use this command.")

def removeAcronym(messageDetail):
    botlog.LogSymphonyInfo("Bot Call: Remove Acronym")

    try:
        commandCallerUID = messageDetail.FromUserId

        connComp = http.client.HTTPSConnection(_configDef['symphonyinfo']['pod_hostname'])
        sessionTok = callout.GetSessionToken()

        headersCompany = {
            'sessiontoken': sessionTok,
            'cache-control': "no-cache"
        }

        connComp.request("GET", "/pod/v3/users?uid=" + commandCallerUID, headers=headersCompany)

        resComp = connComp.getresponse()
        dataComp = resComp.read()
        data_raw = str(dataComp.decode('utf-8'))
        data_dict = ast.literal_eval(data_raw)

        dataRender = json.dumps(data_dict, indent=2)
        d_org = json.loads(dataRender)

        for index_org in range(len(d_org["users"])):
            firstName = d_org["users"][index_org]["firstName"]
            lastName = d_org["users"][index_org]["lastName"]
            displayName = d_org["users"][index_org]["displayName"]
            companyName = d_org["users"][index_org]["company"]
            userID = str(d_org["users"][index_org]["id"])

            botlog.LogSymphonyInfo(firstName + " " + lastName + " from Company/Pod name: " + str(companyName) + " with UID: " + str(userID))
            callerCheck = (firstName + " " + lastName + " - " + displayName + " - " + companyName + " - " + str(userID))

    except:
        return messageDetail.ReplyToChat("Cannot validate user access")

    if callerCheck in AccessFile:

        try:

            Acronym = (messageDetail.Command.MessageText)[1:]

            del AcronymsDictionary[Acronym.upper()]

            updatedDictionary = 'AcronymsDictionary = ' + str(AcronymsDictionary)

            #file = open("modules/command/dictionary.py", "w+")
            file = open("Data/dictionary.py", "w+")
            file.write(updatedDictionary)
            file.close()

            return messageDetail.ReplyToChat(Acronym + " was successfully removed.")
        except:
            return messageDetail.ReplyToChat(Acronym + " was not found.")
    else:
        return messageDetail.ReplyToChat("You aren't authorised to use this command.")

def findAcronym(messageDetail):
    botlog.LogSymphonyInfo("Bot Call: Find Acronym")

    try:
        commandCallerUID = messageDetail.FromUserId

        connComp = http.client.HTTPSConnection(_configDef['symphonyinfo']['pod_hostname'])
        sessionTok = callout.GetSessionToken()

        headersCompany = {
            'sessiontoken': sessionTok,
            'cache-control': "no-cache"
        }

        connComp.request("GET", "/pod/v3/users?uid=" + commandCallerUID, headers=headersCompany)

        resComp = connComp.getresponse()
        dataComp = resComp.read()
        data_raw = str(dataComp.decode('utf-8'))
        data_dict = ast.literal_eval(data_raw)

        dataRender = json.dumps(data_dict, indent=2)
        d_org = json.loads(dataRender)

        for index_org in range(len(d_org["users"])):
            firstName = d_org["users"][index_org]["firstName"]
            lastName = d_org["users"][index_org]["lastName"]
            displayName = d_org["users"][index_org]["displayName"]
            companyName = d_org["users"][index_org]["company"]
            userID = str(d_org["users"][index_org]["id"])

            botlog.LogSymphonyInfo(
                firstName + " " + lastName + " from Company/Pod name: " + str(companyName) + " with UID: " + str(userID))
            callerCheck = (firstName + " " + lastName + " - " + displayName + " - " + companyName + " - " + str(userID))

    except:
        return messageDetail.ReplyToChat("Cannot validate user access")

    if callerCheck in AccessFile:

        try:
            Acronym = (messageDetail.Command.MessageText)[1:]

            return messageDetail.ReplyToChat(Acronym.upper() + " - " + AcronymsDictionary[Acronym.upper()])
        except:
            return messageDetail.ReplyToChat("No result for " + Acronym + " found")
    else:
        return messageDetail.ReplyToChat("You aren't authorised to use this command.")

def listAllAcronyms(messageDetail):
    botlog.LogSymphonyInfo("Bot Call: List All Acronyms")

    try:
        commandCallerUID = messageDetail.FromUserId

        connComp = http.client.HTTPSConnection(_configDef['symphonyinfo']['pod_hostname'])
        sessionTok = callout.GetSessionToken()

        headersCompany = {
            'sessiontoken': sessionTok,
            'cache-control': "no-cache"
        }

        connComp.request("GET", "/pod/v3/users?uid=" + commandCallerUID, headers=headersCompany)

        resComp = connComp.getresponse()
        dataComp = resComp.read()
        data_raw = str(dataComp.decode('utf-8'))
        data_dict = ast.literal_eval(data_raw)

        dataRender = json.dumps(data_dict, indent=2)
        d_org = json.loads(dataRender)

        for index_org in range(len(d_org["users"])):
            firstName = d_org["users"][index_org]["firstName"]
            lastName = d_org["users"][index_org]["lastName"]
            displayName = d_org["users"][index_org]["displayName"]
            companyName = d_org["users"][index_org]["company"]
            userID = str(d_org["users"][index_org]["id"])

            botlog.LogSymphonyInfo(
                firstName + " " + lastName + " from Company/Pod name: " + str(companyName) + " with UID: " + str(userID))
            callerCheck = (firstName + " " + lastName + " - " + displayName + " - " + companyName + " - " + str(userID))
    except:
        return messageDetail.ReplyToChat("Cannot validate user access")

    if callerCheck in AccessFile:

        try:

            table_body = ""
            table_header = "<table style='max-width:50%'><thead><tr style='background-color:#4D94FF;color:#ffffff;font-size:1rem' class=\"tempo-text-color--white tempo-bg-color--black\">" \
                         "<td style='max-width:10%'>Acronym</td>" \
                         "</tr></thead><tbody>"

            for acronym in AcronymsDictionary:
                table_body += "<tr>" \
                              "<td>" + acronym + " - " + AcronymsDictionary[acronym] + "</td>" \
                              "</tr>"

            table_body += "</tbody></table>"

            reply = table_header + table_body
            return messageDetail.ReplyToChatV2_noBotLog("<card iconSrc =\"https://thumb.ibb.co/csXBgU/Symphony2018_App_Icon_Mobile.png\" accent=\"tempo-bg-color--blue\"><header>Acronyms List</header><body>" + reply + "</body></card>")

        except:
            return messageDetail.ReplyToChat("Acronyms not found")

def sortDict(messageDetail):

    sortedAcronymsDictionary = {}

    for key in sorted(AcronymsDictionary.keys()):

        sortedAcronymsDictionary.update({key : AcronymsDictionary[key]})


    updatedDictionary = 'AcronymsDictionary = ' + str(sortedAcronymsDictionary)
    #file = open("modules/command/dictionary.py", "w+")
    file = open("data/dictionary.py","w+")
    file.write(updatedDictionary)
    file.close()


def wikiSearch(messageDetail):
    botlog.LogSymphonyInfo("Bot Call: Wiki Search")
    try:

        request = (messageDetail.Command.MessageText)

        my_api_key = _config['Wiki']['API_Key']
        my_cse_id = _config['Wiki']['token']

        service = build("customsearch", "v1", developerKey=my_api_key)
        res = service.cse().list(q=request, cx=my_cse_id, num=3).execute()
        results = res['items']
        print(results)

        table_body = ""
        table_header = "<table style='max-width:95%'><thead><tr style='background-color:#4D94FF;color:#ffffff;font-size:1rem' class=\"tempo-text-color--white tempo-bg-color--black\">" \
                     "<td style='max-width:10%'>Link</td>" \
                     "<td>Information</td>" \
                     "</tr></thead><tbody>"

        for result in results:
            link_raw = result["link"]
            link = str(link_raw).replace(_config['Wiki']['replace'], "")

            table_body += "<tr>" \
                          "<td><a href =\"" + link_raw + "\">" + link + "</a></td>" \
                          "<td>" + result["snippet"] + "</td>" \
                          "</tr>"

        table_body += "</tbody></table>"

        reply = table_header + table_body
        return messageDetail.ReplyToChatV2_noBotLog(reply)

    except:
        return messageDetail.ReplyToChat("Please make sure to use /wiki <data>")