import modules.botconfig as config
import modules.symphony.callout as callout
import http.client
import modules.symphony.messaging as messaging
import json
import os
import codecs
import modules.botlog as botlog
import modules.plugins.Zendesk.commands
from modules.symphony import AutoSendConnectionRequest

#Grab the config.json main parameters
_configPathdDefault = os.path.abspath('config.json')

with codecs.open(_configPathdDefault, 'r', 'utf-8-sig') as json_file:
        _configDef = json.load(json_file)

# #Grab the config.json Symphony parameters
# _configPath = os.path.abspath('modules/plugins/Symp/config.json')
#
# with codecs.open(_configPath, 'r', 'utf-8-sig') as json_file:
#     _config = json.load(json_file)
#     AutoSendConnectionRequest = _config['Symphony']['autoSendConnectionRequest']

def IsValidSendingUser(emailAddress):
    return emailAddress not in config.Blacklist


def GetBotUserId():
    botEmail = config.BotEmailAddress

    return GetSymphonyUserId(botEmail)


def GetSymphonyUserId(emailAddress):
    userEP = config.SymphonyBaseURL + '/pod/v1/user?email=' + emailAddress

    response = callout.SymphonyGET(userEP)

    return response.ResponseData.id


def GetSymphonyUserDetail(userId):
    #userQueryEP = config.SymphonyBaseURL + '/pod/v2/user?uid=' + str(userId) + '&local=true'
    userQueryEP = config.SymphonyBaseURL + '/pod/v2/user?uid=' + str(userId) + '&local=false'

    response = callout.SymphonyGET(userQueryEP)

    if response.Success:
        userObj = response.ResponseData

        return SymphonyUser(user=userObj)
    else:
        return SymphonyUser(user=None)


class SymphonyUser:
    def __init__(self, user=None):  # userId: str, fname: str, lname: str, email: str, company: str):

        if user is None:
            self.Id = '-1'
            self.FirstName = 'Siro'
            self.LastName = 'Nimo'
            self.Email = 'sn@symphony.com'
            self.Name = 'Siro Nimo'
            self.IsValidSender = False
        else:
            self.Id = str(user.id)  # userId
            self.FirstName = user.firstName if hasattr(user, 'firstName') else 'Unknown'  # fname
            self.LastName = user.lastName if hasattr(user, 'lastName') else 'Unknown'  # lname
            try:
                self.Email = user.emailAddress  # email
            except:
                self.Email = "notyetconnectedtobot@symphony.com"

                # sendConnectionRequest = True
                #
                # #autoConnSetup = _config['Symphony']['autoSendConnectionRequest']
                # print("Original: " + str(AutoSendConnectionRequest))
                # print("sendConnectionRequest: " + str(sendConnectionRequest))
                # if AutoSendConnectionRequest == "enable" and sendConnectionRequest:
                #     print("inside condition")
                #
                #     botlog.LogSymphonyInfo("User is not connected to the bot, auto sending connection request")
                #
                #     conn = http.client.HTTPSConnection(_configDef['symphonyinfo']['pod_hostname'])
                #     sessionTok = callout.GetSessionToken()
                #
                #     payload = "{\n\"userId\": " + self.Id + " \n}"
                #
                #     headers = {
                #         'sessiontoken': sessionTok,
                #         'content-type': "application/json",
                #         'cache-control': "no-cache"
                #     }
                #     conn.request("POST", "/pod/v1/connection/create", payload, headers)
                #
                #     res = conn.getresponse()
                #     data = res.read()
                #     print("Data: " + data.decode("utf-8"))
                #
                #     try:
                #         if data.startswith("{\"code\":403,\"message\":\"request to userConnections failed with status 403, message:You have sent maximum allowed (three) contact requests to a user\"}\""):
                #             botlog.LogSymphonyInfo("The user received 3 connection request and cannot receive anymore")
                #             sendConnectionRequest = False
                #
                #         elif data.startswith("{\"userId\":" + self.Id + ",\"status\":\"PENDING_OUTGOING\""):
                #             botlog.LogSymphonyInfo("The Bot connection request has been sent")
                #             sendConnectionRequest = False
                #     except:
                #         sendConnectionRequest = False
                #     else:
                #         botlog.LogSymphonyInfo(str(data))
                # else:
                #     botlog.LogSymphonyInfo("User is not connected to the bot")

            self.Name = user.displayName  # fname + ' ' + lname
            self.Company = user.company  # company
            self.IsValidSender = IsValidSendingUser(self.Email)
        self.FullName = self.FirstName + ' ' + self.LastName

# def sendBotConnectionRequest_test(messageDetail):
#     return messageDetail.ReplyToChat("You are not connected to the Bot, please accept the connection request.")