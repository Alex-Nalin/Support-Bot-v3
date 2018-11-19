import http.client
import codecs
import os
import json
import re
import time
import pandas
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import http.client
import modules.symphony.callout as callout
import modules.botlog as botlog
import ast
#from modules.plugins.Zendesk.access import AccessFile
from Data.access import AccessFile

#Grab the config.json Symp parameters
_configPathSym = os.path.abspath('modules/plugins/Symp/config.json')

with codecs.open(_configPathSym, 'r', 'utf-8-sig') as json_file:
    _configSym = json.load(json_file)

#Grab the config.json Zendesk parameters
_configPathZen = os.path.abspath('modules/plugins/Zendesk/config.json')

with codecs.open(_configPathZen, 'r', 'utf-8-sig') as json_file:
    _configZen = json.load(json_file)

#Grab the config.json main parameters
_configPathMain = os.path.abspath('config.json')

with codecs.open(_configPathMain, 'r', 'utf-8-sig') as json_file:
        _configMain = json.load(json_file)

def whois(messageDetail):
    botlog.LogSymphonyInfo("Bot Call: Whois")

    try:
        commandCallerUID = messageDetail.FromUserId

        connComp = http.client.HTTPSConnection(_configMain['symphonyinfo']['pod_hostname'])
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

            botlog.LogSymphonyInfo(firstName + " " + lastName + " (" + displayName + ") from Company/Pod name: " + str(companyName) + " with UID: " + str(userID))
            callerCheck = (firstName + " " + lastName + " - " + displayName + " - " + companyName + " - " + str(userID))
    except:
        return messageDetail.ReplyToChat("Cannot validate user access")

    if callerCheck in AccessFile:

        try:
            flat = messageDetail.Command.MessageFlattened.split("_u_")
            UID = flat[1][:14]
        except:
            return messageDetail.ReplyToChat("Please use @mention")

        connComp.request("GET", "/pod/v3/users?uid=" + UID + "&local=false", headers=headersCompany)

        resComp = connComp.getresponse()
        dataComp = resComp.read()
        data_raw = str(dataComp.decode('utf-8'))
        data_dict = ast.literal_eval(data_raw)

        dataRender = json.dumps(data_dict, indent=2)
        d_org = json.loads(dataRender)

        table_body = ""
        table_header = "<table style='max-width:100%;table-layout:auto'><thead><tr style='background-color:#4D94FF;color:#ffffff;font-size:1rem' class=\"tempo-text-color--white tempo-bg-color--black\">" \
                       "<td style='max-width:20%'>ID</td>" \
                       "<td style='max-width:20%'>EMAIL ADDRESS</td>" \
                       "<td style='max-width:20%'>FIRST NAME</td>" \
                       "<td style='max-width:20%'>LAST NAME</td>" \
                       "<td style='max-width:20%'>DISPLAY NAME</td>" \
                       "<td style='max-width:20%'>TITLE</td>" \
                       "<td style='max-width:20%'>COMPANY</td>" \
                       "<td style='max-width:20%'>LOCATION</td>" \
                       "</tr></thead><tbody>"

        for index_org in range(len(d_org["users"])):

            try:
                try:
                    firstName = d_org["users"][index_org]["firstName"]
                    lastName = d_org["users"][index_org]["lastName"]
                except:
                    return messageDetail.ReplyToChat("I am a Top Secret Agent Bot, I do no share my info :)")
                displayName = d_org["users"][index_org]["displayName"]
                try:
                    title = d_org["users"][index_org]["title"]
                except:
                    title = "N/A"
                try:
                    companyName = d_org["users"][index_org]["company"]
                except:
                    companyName = "N/A"
                userID = str(d_org["users"][index_org]["id"])
                try:
                    emailAddress = str(d_org["users"][index_org]["emailAddress"])
                except:
                    emailAddress = "N/A"
                try:
                    location = str(d_org["users"][index_org]["location"])
                except:
                    location = "N/A"
            except:
                return messageDetail.ReplyToChat("Cannot find user info for Whois command")

            table_body += "<tr>" \
                          "<td>" + str(userID) + "</td>" \
                          "<td>" + str(emailAddress) + "</td>" \
                          "<td>" + str(firstName) + "</td>" \
                          "<td>" + str(lastName) + "</td>" \
                          "<td>" + str(displayName) + "</td>" \
                          "<td>" + str(title) + "</td>" \
                          "<td>" + str(companyName) + "</td>" \
                          "<td>" + str(location) + "</td>" \
                          "</tr>"

            table_body += "</tbody></table>"

        reply = table_header + table_body
        return messageDetail.ReplyToChatV2_noBotLog("<card iconSrc =\"https://thumb.ibb.co/csXBgU/Symphony2018_App_Icon_Mobile.png\" accent=\"tempo-bg-color--blue\"><header>User details</header><body>" + reply + "</body></card>")
    else:
        return messageDetail.ReplyToChat("You aren't authorised to use this command.")

def streamCheck(messageDetail):

    botlog.LogSymphonyInfo("Bot Call: streamCheck")

    try:
        commandCallerUID = messageDetail.FromUserId

        connComp = http.client.HTTPSConnection(_configMain['symphonyinfo']['pod_hostname'])
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

            botlog.LogSymphonyInfo(firstName + " " + lastName + " (" + displayName + ") from Company/Pod name: " + str(companyName) + " with UID: " + str(userID))
            callerCheck = (firstName + " " + lastName + " - " + displayName + " - " + companyName + " - " + str(userID))
    except:
        return messageDetail.ReplyToChat("Cannot validate user access")


    if callerCheck in AccessFile:

        try:
            stream_raw = messageDetail.Command.MessageFlattened.split(" ")
            stream_split = str(stream_raw).split(",")
            stream_split_Data = stream_split[1].replace("'", "").replace("]","")
            streamID = str(stream_split_Data).replace(" ","")
        except:
            return messageDetail.ReplyToChatV2("Please a valid stream ID converted into <a href=\"https://rest-api.symphony.com/docs/message-id\">base64</a>")

        connComp = http.client.HTTPSConnection(_configMain['symphonyinfo']['pod_hostname'])
        sessionTok = callout.GetSessionToken()

        headersCompany = {
            'sessiontoken': sessionTok,
            'cache-control': "no-cache"
        }

        connComp.request("GET", "/pod/v2/streams/" + streamID + "/info", headers=headersCompany)

        res = connComp.getresponse()
        data = res.read().decode("utf-8")

        invalidStreamID = "{\"code\":400,\"message\":\"Invalid stream ID\"}"

        if data == invalidStreamID:
            return messageDetail.ReplyToChatV2("Please enter a valid StreamID/ConversationID, converted into <a href=\"https://rest-api.symphony.com/docs/message-id\">base64</a>")

        data_raw = str(data).split(",\"")

        try:
            stream_id_raw = data_raw[0]
            stream_id_split = str(stream_id_raw).split(":")
            stream_id = str(stream_id_split[1]).replace("\"","")
        except:
            return messageDetail.ReplyToChat("Cannot find stream Id")

        try:
            xpod_raw = data_raw[1]
            xpod_split = str(xpod_raw).split(":")
            xpod = str(xpod_split[1])
        except:
            return messageDetail.ReplyToChat("Cannot find Xpod info")

        try:
            active_raw = data_raw[3]
            active_split = str(active_raw).split(":")
            active = str(active_split[1])
        except:
            return messageDetail.ReplyToChat("Cannot find Active info")

        try:
            last_msg_raw = data_raw[4]
            last_msg_split = str(last_msg_raw).split(":")
            last_msg = str(last_msg_split[1])
        except:
            return messageDetail.ReplyToChat("Cannot find Last Message time")

        try:
            streamType_raw = data_raw[5]
            streamType_split = str(streamType_raw).split(":")
            streamType = str(streamType_split[1]).replace("\"","")
        except:
            return messageDetail.ReplyToChat("Cannot find stream type")

        try:
            attribute_raw = data_raw[6]
            attribute_split = str(attribute_raw).split(":")
            attribute = str(attribute_split[2]).replace("\"","").replace("}","").replace("'","").replace("[","").replace("]","")
        except:
            return messageDetail.ReplyToChat("Cannot find stream attributes")


        table_body = ""
        table_header = "<table style='max-width:100%;table-layout:fixed'><thead><tr style='background-color:#4D94FF;color:#ffffff;font-size:1rem' class=\"tempo-text-color--white tempo-bg-color--black\">" \
                       "<td style='max-width:20%'>ID</td>" \
                       "<td style='max-width:20%'>CROSS POD</td>" \
                       "<td style='max-width:20%'>ACTIVE</td>" \
                       "<td style='max-width:20%'>LAST MSG</td>" \
                       "<td style='max-width:20%'>STREAM TYPE</td>" \
                       "<td style='max-width:20%'>ATTRIBUTES</td>" \
                       "</tr></thead><tbody>"

        table_body += "<tr>" \
                      "<td>" + str(stream_id) + "</td>" \
                      "<td>" + str(xpod) + "</td>" \
                      "<td>" + str(active) + "</td>" \
                      "<td>" + str(last_msg) + "</td>" \
                      "<td>" + str(streamType) + "</td>" \
                      "<td>" + str(attribute) + "</td>" \
                       "</tr>"

        table_body += "</tbody></table>"

        reply = table_header + table_body
        return messageDetail.ReplyToChatV2_noBotLog(
            "<card iconSrc =\"https://thumb.ibb.co/csXBgU/Symphony2018_App_Icon_Mobile.png\" accent=\"tempo-bg-color--blue\"><header>Stream details</header><body>" + reply + "</body></card>")
    else:
        return messageDetail.ReplyToChat("You aren't authorised to use this command.")


def UIDCheck(messageDetail):
    botlog.LogSymphonyInfo("Bot Call: UIDCheck")

    try:
        commandCallerUID = messageDetail.FromUserId

        connComp = http.client.HTTPSConnection(_configMain['symphonyinfo']['pod_hostname'])
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

            botlog.LogSymphonyInfo(firstName + " " + lastName + " (" + displayName + ") from Company/Pod name: " + str(companyName) + " with UID: " + str(userID))
            callerCheck = (firstName + " " + lastName + " - " + displayName + " - " + companyName + " - " + str(userID))

    except:
        return messageDetail.ReplyToChat("Cannot validate user access")

    if callerCheck in AccessFile:

        try:
            UID_raw = messageDetail.Command.MessageText
            UID = str(UID_raw).replace(" ", "")
            UID_lenght = len(str(UID))
        except:
            return messageDetail.ReplyToChat("Please use enter UID of the Symphony user to lookup")

        if str(UID_lenght) != "14":
            return messageDetail.ReplyToChat("Please enter a valid UID, with 14 digits")

        connComp = http.client.HTTPSConnection(_configMain['symphonyinfo']['pod_hostname'])
        sessionTok = callout.GetSessionToken()

        headersCompany = {
            'sessiontoken': sessionTok,
            'cache-control': "no-cache"
        }

        connComp.request("GET", "/pod/v3/users?uid=" + UID + "&local=false", headers=headersCompany)

        resComp = connComp.getresponse()
        dataComp = resComp.read()
        data_raw = str(dataComp.decode('utf-8'))
        data_dict = ast.literal_eval(data_raw)

        dataRender = json.dumps(data_dict, indent=2)
        d_org = json.loads(dataRender)

        notValidUI = "{'code': 400, 'message': 'At least one query paramemer (uid or email) needs to be present.'}"
        notValidUID = "{'code': 400, 'message': 'All uids are invalid.'}"

        if str(d_org).startswith(notValidUI):
            return messageDetail.ReplyToChat("Please use enter UID of the Symphony User to Lookup")
        if str(d_org).startswith(notValidUID):
            return messageDetail.ReplyToChat("Please use enter UID of the Symphony User to Lookup")

        table_body = ""
        table_header = "<table style='max-width:100%;table-layout:fixed'><thead><tr style='background-color:#4D94FF;color:#ffffff;font-size:1rem' class=\"tempo-text-color--white tempo-bg-color--black\">" \
                       "<td style='max-width:20%'>ID</td>" \
                       "<td style='max-width:20%'>EMAIL ADDRESS</td>" \
                       "<td style='max-width:20%'>FIRST NAME</td>" \
                       "<td style='max-width:20%'>LAST NAME</td>" \
                       "<td style='max-width:20%'>DISPLAY NAME</td>" \
                       "<td style='max-width:20%'>TITLE</td>" \
                       "<td style='max-width:20%'>COMPANY</td>" \
                       "<td style='max-width:20%'>LOCATION</td>" \
                       "</tr></thead><tbody>"

        for index_org in range(len(d_org["users"])):
            try:
                firstName = d_org["users"][index_org]["firstName"]
                lastName = d_org["users"][index_org]["lastName"]
            except:
                return messageDetail.ReplyToChat("I am a Top Secret Agent Bot, I do no share my info :)")
            displayName = d_org["users"][index_org]["displayName"]
            try:
                title = d_org["users"][index_org]["title"]
            except:
                title = "N/A"
            try:
                companyName = d_org["users"][index_org]["company"]
            except:
                companyName = "N/A"
            userID = str(d_org["users"][index_org]["id"])
            try:
                emailAddress = str(d_org["users"][index_org]["emailAddress"])
            except:
                emailAddress = "N/A"
            try:
                location = str(d_org["users"][index_org]["location"])
            except:
                location = "N/A"

            table_body += "<tr>" \
                          "<td>" + str(userID) + "</td>" \
                          "<td>" + str(emailAddress) + "</td>" \
                          "<td>" + str(firstName) + "</td>" \
                          "<td>" + str(lastName) + "</td>" \
                          "<td>" + str(displayName) + "</td>" \
                          "<td>" + str(title) + "</td>" \
                          "<td>" + str(companyName) + "</td>" \
                          "<td>" + str(location) + "</td>" \
                          "</tr>"

            table_body += "</tbody></table>"

        reply = table_header + table_body
        return messageDetail.ReplyToChatV2_noBotLog("<card iconSrc =\"https://thumb.ibb.co/csXBgU/Symphony2018_App_Icon_Mobile.png\" accent=\"tempo-bg-color--blue\"><header>User details</header><body>" + reply + "</body></card>")
    else:
        return messageDetail.ReplyToChat("You aren't authorised to use this command.")

def jwttoken(messageDetail):

    commandCallerUID = messageDetail.FromUserId

    connComp = http.client.HTTPSConnection(_configMain['symphonyinfo']['pod_hostname'])
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

    if callerCheck in (_configZen['AuthUser']['AdminList']):

        message = (messageDetail.Command.MessageText)
        message_split = message.split()

        try:
            jwt_token = message_split[0]

            botlog.LogSymphonyInfo("New jwt token added")
            (_configSym['jwt_config']['jwt_token']) = jwt_token

            return messageDetail.ReplyToChat("Support Portal token updated")
        except:
            return messageDetail.ReplyToChat("You did not enter a new JWT Token")

    else:
        return messageDetail.ReplyToChat("You aren't authorised to use this command. Please contact Alex Nalin for access")


def ProdPod (messageDetail):

    commandCallerUID = messageDetail.FromUserId

    connComp = http.client.HTTPSConnection(_configMain['symphonyinfo']['pod_hostname'])
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

    if callerCheck in (_configZen['AuthUser']['AdminList']):

        botlog.LogSymphonyInfo("*** Symphony Production Pod Checks ***")

        message = (messageDetail.Command.MessageText)
        message_split = message.split()

        try:
            prod_pod_name = message_split[0]
            botlog.LogSymphonyInfo("Prod Pod Name: " + prod_pod_name)
        except:
            return messageDetail.ReplyToChat("You did not enter a company name")

        try:
            prod_pod_component = message_split[1]
            botlog.LogSymphonyInfo("Prod Pod Component: " + prod_pod_component)
        except:
            return messageDetail.ReplyToChat("You did not enter a component to check")

        if prod_pod_component == "km":
            messageDetail.ReplyToChat("Here's the Production Pod Key Manager info for " + prod_pod_name)
            t0 = time.time()
            print("Start Time: " + str(t0))
            #print("inside KM")

            conn = http.client.HTTPSConnection(prod_pod_name + ".symphony.com")

            headers = {
                'cache-control': "no-cache",
            }

            conn.request("GET", "/keystore/HealthCheck/keymanagers", headers=headers)

            res = conn.getresponse()
            data = res.read()
            datanewraw = (data.decode("utf-8"))
            # print("data_km: " + datanewraw)

            parsed = json.loads(datanewraw)
            datanew = (json.dumps(parsed, indent=4, sort_keys=True))

            t1 = time.time()
            total_n = t1 - t0
            print("Total time: " + str(total_n))

            if total_n >= 3:
                return messageDetail.ReplyToChat("The Pod name is not correct, please check Pod name")
            else:
                #print("KM Details: " + datanew)
                return messageDetail.ReplyToChat(datanew)


        jwt_url = _configSym['jwt_config_url']['jwt_url']
        conn = http.client.HTTPSConnection("" + jwt_url + "")

        jwt = _configSym['jwt_config']['jwt_token']
        headers = {
            'jwt-issued-by-support-portal': "" + jwt + "",
            'cache-control': "no-cache"
            }

        conn.request("GET", "/pod/" +prod_pod_name+ "/" +prod_pod_component+"", headers=headers)

        res = conn.getresponse()
        data = res.read()
        datanew = (data.decode("utf-8"))

        # parsed = json.loads(datanew)
        # datanew = (json.dumps(parsed, indent=2, sort_keys=False))

        botlog.LogSymphonyInfo("datanew: " + datanew)

        # if prod_pod_component == "km":
        #     messageDetail.ReplyToChat("Here's the Production Pod Key Manager info for " + prod_pod_name)
        #     # print("inside KM")
        #
        #     conn = http.client.HTTPSConnection(prod_pod_name + ".symphony.com")
        #
        #     headers = {
        #         'cache-control': "no-cache",
        #     }
        #
        #     conn.request("GET", "/keystore/HealthCheck/keymanagers", headers=headers)
        #
        #     res = conn.getresponse()
        #     data = res.read()
        #     datanewraw = (data.decode("utf-8"))
        #     # print("data_km: " + datanewraw)
        #
        #     parsed = json.loads(datanewraw)
        #     datanew = (json.dumps(parsed, indent=4, sort_keys=True))
        #     #print("KM Details: " + datanew)
        #     return messageDetail.ReplyToChat(datanew)

        jwtexpired = "{\"code\":403,\"details\":\"Verify JWT failed\"}"

        # In case the support portal JTW has expired
        if datanew == "[]":
            return messageDetail.ReplyToChat("There is no data to show for this Pod")

        elif datanew == jwtexpired:
            return messageDetail.ReplyToChat("Please renew your Support Portal Token with command /jwt")

        elif datanew.startswith("{\"code\":400,\"details\":\"No configuration about pod"):
            return messageDetail.ReplyToChat("The Symphony Pod you are looking for is not in the list")
        else:

            try:

                datanewsplit = str(datanew).split("\":")
                #print("datanewsplit: " + str(datanewsplit))
                datanewsplito = str(datanewsplit).split(",")
                #print("datanewsplito: " + str(datanewsplito))

                #if prod_pod_component == "agent" or prod_pod_component == "Agent":
                if prod_pod_component == "agent":
                    messageDetail.ReplyToChat("Here's the Production Pod Agent info for " + prod_pod_name)
                    t0 = time.time()
                    print("Start Time: " + str(t0))

                    # Array definition , set start character and remove end character

                    table_body = ""
                    table_header = "<table><thead><tr class=\"tempo-text-color--white tempo-bg-color--black\">" \
                                    "<th>Agent Hostname</th>" \
                                    "<th>Agent URL</th>" \
                                    "<th>Agent IP</th>" \
                                    "<th>On-Prem?</th>" \
                                    "<th>Agent Version</th>" \
                                    "</tr></thead><tbody>"

                    idx = 1

                    #1st Agent
                    try:
                        if datanewsplito[idx] is not None:                                         #1
                            OnPremFlag = "tempo-text-color--white"
                            agent_hostname = datanewsplito[idx][3:][:-1]                           #1
                            #print("agent_hostname" + datanewsplito[idx] + ": " + agent_hostname)
                            agent_url = datanewsplito[idx+2][3:][:-1]                              #3
                            #print("agent_url" + datanewsplito[idx+2] + ": " + agent_url)
                            agent_ip = datanewsplito[idx+4][3:][:-1]                               #5
                            #print("agent_ip" + datanewsplito[idx+4] + ": " + agent_ip)
                            agent_onprem = datanewsplito[idx+6][2:]                                #7

                            if agent_onprem not in ("true", "false"):
                                #print("agent_onprem" + datanewsplito[idx+6] + ": N/A")
                                agent_onprem = "<b>N/A</b>"
                                OnPremFlag = "tempo-text-color--red"
                                agent_versiono = datanewsplito[idx+6][3:][:-2]                      #7
                                agent_version = agent_versiono.replace("\"}]", "")
                                #print("agent_version" + datanewsplito[idx+6] + ": " + agent_version)
                                idx = 9                                                            #9

                            elif agent_onprem == "false":
                                agent_url = agent_url
                                agent_url_link = agent_url + "/v2/HealthCheck"
                                agent_url_link_created = "<a href =\"" + agent_url_link + "\">" + agent_url + "</a>"
                                #print(agent_url)
                                #print(agent_url_link_created)
                                agent_url = agent_url_link_created

                                #print("agent_onprem: " + agent_onprem)
                                agent_versiono = datanewsplito[idx+8][3:][:-2]                      #9
                                agent_version = agent_versiono.replace("\"}]", "")
                                #print("agent_version" + datanewsplito[idx+8] + ": " + agent_version)
                                idx = 11

                            else:
                                #print("agent_onprem: " + agent_onprem)
                                agent_versiono = datanewsplito[idx+8][3:][:-2]                      #9
                                agent_version = agent_versiono.replace("\"}]", "")
                                #print("agent_version" + datanewsplito[idx+8] + ": " + agent_version)
                                idx = 11                                                           #11

                            table_body += "<tr>" \
                                            "<td>" + agent_hostname + "</td>" \
                                            "<td>" + agent_url + "</td>" \
                                            "<td>" + agent_ip + "</td>" \
                                            "<td class=\"" + OnPremFlag + " tempo-bg-color--blue\">" + agent_onprem + "</td>" \
                                            "<td>" + agent_version + "</td>" \
                                            "</tr>" \

                        #2nd Agent
                        if datanewsplito[idx] is not None:                                         #9 or 11
                            OnPremFlag = "tempo-text-color--white"
                            # Array definition , set start character and remove end character
                            agent_hostname1 = datanewsplito[idx][3:][:-1]                          #9 or 11
                            #print("agent_hostname1" + datanewsplito[idx] + ": " + agent_hostname1)
                            agent_url1 = datanewsplito[idx+2][3:][:-1]                             #11 or 13
                            #print("agent_url1" + datanewsplito[idx+2] + ": " + agent_url1)
                            agent_ip1 = datanewsplito[idx+4][3:][:-1]                              #13 or 15
                            #print("agent_ip1" + datanewsplito[idx+4] + ": " + agent_ip1)
                            agent_onprem1 = datanewsplito[idx+6][2:]                               #15 or 17

                            if agent_onprem1 not in ("true", "false"):
                                #print("agent_onPrem1" + datanewsplito[idx+6] + ": N/A")
                                agent_onprem1 = "<b>N/A</b>"
                                OnPremFlag = "tempo-text-color--red"
                                agent_hostname1 = datanewsplito[idx][3:][:-1]  # 9 or 11
                                #print("agent_hostname1: " + agent_hostname1)
                                agent_url1 = datanewsplito[idx + 2][3:][:-1]  # 11 or 13
                                #print("agent_url1: " + agent_url1)
                                agent_ip1 = datanewsplito[idx + 4][3:][:-1]  # 13 or 15
                                #print("agent_ip1: " + agent_ip1)

                                agent_versiono1 = datanewsplito[idx+6][3:][:-2]                     #15 or 17
                                agent_version1 = agent_versiono1.replace("\"}]", "")
                                #print("agent_version1" + datanewsplito[idx+6] + ": " + agent_version1)
                                idx = 19                                                           #19

                            elif agent_onprem1 == "false":
                                agent_url1 = agent_url1
                                agent_url_link1 = agent_url1 + "/v2/HealthCheck"
                                agent_url_link_created1 = "<a href =\"" + agent_url_link1 + "\">" + agent_url1 + "</a>"
                                #print(agent_url1)
                                # print(agent_url_link_created1)
                                agent_url1 = agent_url_link_created1

                                #print("agent_onprem1: " + agent_onprem1)
                                agent_versiono1 = datanewsplito[idx + 8][3:][:-2]  # 19
                                agent_version1 = agent_versiono1.replace("\"}]", "")
                                #print("agent_version1" + datanewsplito[idx+8] + ": " + agent_version1)
                                idx = 21

                            else:
                                #print("agent_onprem1: " + agent_onprem1)
                                agent_versiono1 = datanewsplito[idx+8][3:][:-2]                     #19
                                agent_version1 = agent_versiono1.replace("\"}]", "")
                                #print("agent_version1" + datanewsplito[idx+8] + ": " + agent_version1)
                                idx = 21                                                           #21

                            table_body += "<tr>" \
                                            "<td>" + agent_hostname1 + "</td>" \
                                            "<td>" + agent_url1 + "</td>" \
                                            "<td>" + agent_ip1 + "</td>" \
                                            "<td class=\"" + OnPremFlag + " tempo-bg-color--blue\">" + agent_onprem1 + "</td>" \
                                            "<td>" + agent_version1 + "</td>" \
                                            "</tr>" \

                        #3rd Agent
                        if datanewsplito[idx] is not None:
                            OnPremFlag = "tempo-text-color--white"
                            # Array definition , set start character and remove end character
                            agent_hostname2 = datanewsplito[idx][3:][:-1]
                            #print("agent_hostname2" + datanewsplito[idx] + ": " + agent_hostname2)
                            agent_url2 = datanewsplito[idx+2][3:][:-1]
                            #print("agent_url2" + datanewsplito[idx+2] + ": " + agent_url2)
                            agent_ip2 = datanewsplito[idx+4][3:][:-1]
                            #print("agent_ip2" + datanewsplito[idx+4] + ": " + agent_ip2)
                            agent_onprem2 = datanewsplito[idx+6][2:]

                            if agent_onprem2 not in ("true", "false"):
                                #print("agent_onprem2" + datanewsplito[idx+6] + ": N/A")
                                agent_onprem2 = "<b>N/A</b>"
                                OnPremFlag = "tempo-text-color--red"
                                agent_versiono2 = datanewsplito[idx+6][3:][:-2]
                                agent_version2 = agent_versiono2.replace("\"}]", "")
                                #print("agent_version2" + datanewsplito[idx+6] + ": " + agent_version2)
                                idx = 29

                            elif agent_onprem2 == "false":
                                agent_url2 = agent_url2
                                agent_url_link2 = agent_url2 + "/v2/HealthCheck"
                                agent_url_link_created2 = "<a href =\"" + agent_url_link2 + "\">" + agent_url2 + "</a>"
                                #print(agent_url2)
                                #print(agent_url_link_created2)
                                agent_url2 = agent_url_link_created2

                                #print("agent_onprem2: " + agent_onprem2)
                                agent_versiono2 = datanewsplito[idx + 8][3:][:-2]
                                agent_version2 = agent_versiono2.replace("\"}]", "")
                                #print("agent_version2" + datanewsplito[idx+8] + ": " + agent_version2)
                                idx = 31

                            else:
                                #print("agent_onprem2: " + agent_onprem2)
                                agent_versiono2 = datanewsplito[idx+8][3:][:-2]
                                agent_version2 = agent_versiono2.replace("\"}]", "")
                                #print("agent_version2" + datanewsplito[idx+8] + ": " + agent_version2)
                                idx = 31

                            table_body += "<tr>" \
                                            "<td>" + agent_hostname2 + "</td>" \
                                            "<td>" + agent_url2 + "</td>" \
                                            "<td>" + agent_ip2 + "</td>" \
                                            "<td class=\"" + OnPremFlag + " tempo-bg-color--blue\">" + agent_onprem2 + "</td>" \
                                            "<td>" + agent_version2 + "</td>" \
                                            "</tr>" \

                        # #4th Agent
                        # if datanewsplito[idx] is not None:
                        #     # Array definition , set start character and remove end character
                        #     agent_hostname3 = datanewsplito[idx][3:][:-1]
                        #     print("agent_hostname3" + datanewsplito[idx] + ": " + agent_hostname3)
                        #     agent_url3 = datanewsplito[idx+2][3:][:-1]
                        #     print("agent_url3" + datanewsplito[idx+2] + ": " + agent_url3)
                        #     agent_ip3 = datanewsplito[idx+4][3:][:-1]
                        #     print("agent_ip3" + datanewsplito[idx+4] + ": " + agent_ip3)
                        #     agent_onprem3 = datanewsplito[idx+6][2:]
                        #
                        #     if agent_onprem3 not in ("true", "false"):
                        #         print("agent_onprem3" + datanewsplito[idx+6] + ": N/A")
                        #         agent_onprem3 = "N/A"
                        #         agent_versiono3 = datanewsplito[idx+6][3:][:-2]
                        #         agent_version3 = agent_versiono3.replace("\"}]", "")
                        #         print("agent_version3" + datanewsplito[idx+6] + ": " + agent_version3)
                        #         idx = 39
                        #
                        #     elif agent_onprem3 == "false":
                        #         agent_url3 = agent_url3
                        #         agent_url_link3 = agent_url3 + "/v2/HealthCheck"
                        #         agent_url_link_created3 = "<a href =\"" + agent_url_link3 + "\">" + agent_url3 + "</a>"
                        #         print(agent_url3)
                        #         #print(agent_url_link_created3)
                        #         agent_url3 = agent_url_link_created3
                        #
                        #         print("agent_onprem3: " + agent_onprem3)
                        #         agent_versiono3 = datanewsplito[idx + 8][3:][:-2]
                        #         agent_version3 = agent_versiono3.replace("\"}]", "")
                        #         print("agent_version3" + datanewsplito[idx+8] + ": " + agent_version3)
                        #         idx = 41
                        #
                        #     else:
                        #         print("agent_onprem3: " + agent_onprem3)
                        #         agent_versiono3 = datanewsplito[idx+8][3:][:-2]
                        #         agent_version3 = agent_versiono3.replace("\"}]", "")
                        #         print("agent_version3" + datanewsplito[idx+8] + ": " + agent_version3)
                        #         idx = 41
                        #
                        #     table_body += "<tr>" \
                        #                     "<td>" + agent_hostname3 + "</td>" \
                        #                     "<td>" + agent_url3 + "</td>" \
                        #                     "<td>" + agent_ip3 + "</td>" \
                        #                     "<td>" + agent_onprem3 + "</td>" \
                        #                     "<td>" + agent_version3 + "</td>" \
                        #                     "</tr>" \
                        #
                        # #5th Agent
                        # if datanewsplito[idx] is not None:
                        #     # Array definition , set start character and remove end character
                        #     agent_hostname4 = datanewsplito[idx][3:][:-1]
                        #     print("agent_hostname4" + datanewsplito[idx] + ": " + agent_hostname4)
                        #     agent_url4 = datanewsplito[idx+2][3:][:-1]
                        #     print("agent_url4" + datanewsplito[idx+2] + ": " + agent_url4)
                        #     agent_ip4 = datanewsplito[idx+4][3:][:-1]
                        #     print("agent_ip4" + datanewsplito[idx+4] + ": " + agent_ip4)
                        #     agent_onprem4 = datanewsplito[idx+6][2:]
                        #
                        #     if agent_onprem4 not in ("true", "false"):
                        #         print("agent_onprem4" + datanewsplito[idx+6] + ": N/A")
                        #         agent_onprem4 = "N/A"
                        #         agent_versiono4 = datanewsplito[idx+6][3:][:-2]
                        #         agent_version4 = agent_versiono4.replace("\"}]", "")
                        #         print("agent_version4" + datanewsplito[idx+6] + ": " + agent_version4)
                        #         idx = 49
                        #
                        #     elif agent_onprem4 == "false":
                        #         agent_url4 = agent_url4
                        #         agent_url_link4 = agent_url4 + "/v2/HealthCheck"
                        #         agent_url_link_created4 = "<a href =\"" + agent_url_link4 + "\">" + agent_url4 + "</a>"
                        #         print(agent_url4)
                        #         #print(agent_url_link_created4)
                        #         agent_url4 = agent_url_link_created4
                        #
                        #         print("agent_onprem4: " + agent_onprem4)
                        #         agent_versiono4 = datanewsplito[idx + 8][3:][:-2]
                        #         agent_version4 = agent_versiono4.replace("\"}]", "")
                        #         print("agent_version4" + datanewsplito[idx+8] + ": " + agent_version4)
                        #         idx = 51
                        #
                        #     else:
                        #         print("agent_onprem4: " + agent_onprem4)
                        #         agent_versiono4 = datanewsplito[idx+8][3:][:-2]
                        #         agent_version4 = agent_versiono4.replace("\"}]", "")
                        #         print("agent_version4" + datanewsplito[idx+8] + ": " + agent_version4)
                        #         idx = 51
                        #
                        #     table_body += "<tr>" \
                        #                     "<td>" + agent_hostname4 + "</td>" \
                        #                     "<td>" + agent_url4 + "</td>" \
                        #                     "<td>" + agent_ip4 + "</td>" \
                        #                     "<td>" + agent_onprem4 + "</td>" \
                        #                     "<td>" + agent_version4 + "</td>" \
                        #                     "</tr>" \
                        #
                        # #6th Agent
                        # if datanewsplito[idx] is not None:
                        #     # Array definition , set start character and remove end character
                        #     agent_hostname5 = datanewsplito[idx][3:][:-1]
                        #     print("agent_hostname5: " + agent_hostname5)
                        #     agent_url5 = datanewsplito[idx+2][3:][:-1]
                        #     print("agent_url5: " + agent_url5)
                        #     agent_ip5 = datanewsplito[idx+4][3:][:-1]
                        #     print("agent_ip5: " + agent_ip5)
                        #     agent_onprem5 = datanewsplito[idx+6][2:]
                        #
                        #     if agent_onprem5 not in ("true", "false"):
                        #         print("agent_onprem5: N/A")
                        #         agent_onprem5 = "N/A"
                        #         agent_versiono5 = datanewsplito[idx+6][3:][:-2]
                        #         agent_version5 = agent_versiono5.replace("\"}]", "")
                        #         print("agent_version5: " + agent_version5)
                        #         idx = 59
                        #
                        #     elif agent_onprem5 == "false":
                        #         agent_url5 = agent_url5
                        #         agent_url_link5 = agent_url5 + "/v2/HealthCheck"
                        #         agent_url_link_created5 = "<a href =\"" + agent_url_link5 + "\">" + agent_url5 + "</a>"
                        #         print(agent_url5)
                        #         #print(agent_url_link_created5)
                        #         agent_url5 = agent_url_link_created5
                        #
                        #         print("agent_onprem5: " + agent_onprem5)
                        #         agent_versiono5 = datanewsplito[idx + 8][3:][:-2]
                        #         agent_version5 = agent_versiono5.replace("\"}]", "")
                        #         print("agent_version5: " + agent_version5)
                        #         idx = 61
                        #
                        #     else:
                        #         print("agent_onprem5: " + agent_onprem5)
                        #         agent_versiono5 = datanewsplito[idx+8][3:][:-2]
                        #         agent_version5 = agent_versiono5.replace("\"}]", "")
                        #         print("agent_version5: " + agent_version5)
                        #         idx = 61
                        #
                        #     table_body += "<tr>" \
                        #                     "<td>" + agent_hostname5 + "</td>" \
                        #                     "<td>" + agent_url5 + "</td>" \
                        #                     "<td>" + agent_ip5 + "</td>" \
                        #                     "<td>" + agent_onprem5 + "</td>" \
                        #                     "<td>" + agent_version5 + "</td>" \
                        #                     "</tr>" \
                        #
                        # #7th Agent
                        # if datanewsplito[idx] is not None:
                        #     # Array definition , set start character and remove end character
                        #     agent_hostname6 = datanewsplito[idx][3:][:-1]
                        #     print("agent_hostname6: " + agent_hostname6)
                        #     agent_url6 = datanewsplito[idx+2][3:][:-1]
                        #     print("agent_url6: " + agent_url6)
                        #     agent_ip6 = datanewsplito[idx+4][3:][:-1]
                        #     print("agent_ip6: " + agent_ip6)
                        #     agent_onprem6 = datanewsplito[idx+6][2:]
                        #
                        #     if agent_onprem6 not in ("true", "false"):
                        #         print("agent_onprem6: N/A")
                        #         agent_onprem6 = "N/A"
                        #         agent_versiono6 = datanewsplito[idx+6][3:][:-2]
                        #         agent_version6 = agent_versiono6.replace("\"}]", "")
                        #         print("agent_version6: " + agent_version6)
                        #         idx = 69
                        #
                        #     elif agent_onprem6 == "false":
                        #         agent_url6 = agent_url6
                        #         agent_url_link6 = agent_url6 + "/v2/HealthCheck"
                        #         agent_url_link_created6 = "<a href =\"" + agent_url_link6 + "\">" + agent_url6 + "</a>"
                        #         print(agent_url6)
                        #         #print(agent_url_link_created6)
                        #         agent_url6 = agent_url_link_created6
                        #
                        #         print("agent_onprem6: " + agent_onprem6)
                        #         agent_versiono6 = datanewsplito[idx + 8][3:][:-2]
                        #         agent_version6 = agent_versiono6.replace("\"}]", "")
                        #         print("agent_version6: " + agent_version6)
                        #         idx = 71
                        #
                        #     else:
                        #         print("agent_onprem6: " + agent_onprem6)
                        #         agent_versiono6 = datanewsplito[idx+8][3:][:-2]
                        #         agent_version6 = agent_versiono6.replace("\"}]", "")
                        #         print("agent_version6: " + agent_version6)
                        #         idx = 71
                        #
                        #     table_body += "<tr>" \
                        #                     "<td>" + agent_hostname6 + "</td>" \
                        #                     "<td>" + agent_url6 + "</td>" \
                        #                     "<td>" + agent_ip6 + "</td>" \
                        #                     "<td>" + agent_onprem6 + "</td>" \
                        #                     "<td>" + agent_version6 + "</td>" \
                        #                     "</tr>" \

                    except IndexError:

                        parsed = json.loads(datanew)
                        datanew = (json.dumps(parsed, indent=2, sort_keys=False))
                        #print("No more info to show")
                        botlog.LogSymphonyInfo(datanew)

                    table_body += "</tbody></table>"
                    datanew = table_header + table_body
                    #print("Table: " + datanew)


                elif prod_pod_component == "ceb":
                    messageDetail.ReplyToChat("Here's the Production Pod CEB info for " + prod_pod_name)
                    t0 = time.time()
                    print("Start Time: " + str(t0))

                    #print("inside CEB")

                    table_body = ""
                    table_header = "<table><thead><tr class=\"tempo-text-color--white tempo-bg-color--black\">" \
                                   "<th>ID</th>" \
                                   "<th>Version</th>" \
                                   "<th>IP Address</th>" \
                                   "<th>Host OS</th>" \
                                   "<th>Archive Directory</th>" \
                                   "<th>Last Conn Time (ms)</th>" \
                                   "<th>Last Conn Time</th>" \
                                   "<th>Is Connected?</th>" \
                                   "<th>Last Content EndTime By Scheduled Job (ms)</th>" \
                                   "<th>Last Content EndTime By Scheduled Job</th>" \
                                   "<th>Scheduled Job Frequency</th>" \
                                   "<th>Next CE Job Run Time(ms)</th>" \
                                   "<th>Next CE Job Run Time</th>" \
                                   "<th>Export Format</th>" \
                                   "</tr></thead><tbody>"

                    try:
                        if datanewsplito[0] is not None:
                            ceb_id = datanewsplito[2][3:][:-1]
                            #print("ceb_id: " + ceb_id)
                            ceb_version = datanewsplito[4][3:][:-1]
                            #print("ceb_version: " + ceb_version)
                            ceb_ipAddress = datanewsplito[6][3:][:-1]
                            #print("ceb_ipAddress: " + ceb_ipAddress)
                            ceb_hostOS = datanewsplito[8][3:][:-1]
                            #print("ceb_hostOS: " + ceb_hostOS)
                            ceb_archiveDirectory = datanewsplito[10][3:][:-1]
                            #print("ceb_archiveDirectory: " + ceb_archiveDirectory)
                            ceb_lastConnectionTimeInMillisecond = datanewsplito[12][2:]
                            #print("ceb_lastConnectionTimeInMillisecond: " + ceb_lastConnectionTimeInMillisecond)
                            ceb_lastConnectionTime = datanewsplito[14][3:][:-1]
                            #print("ceb_lastConnectionTime: " + ceb_lastConnectionTime)
                            ceb_isConnected = datanewsplito[16][2:][:-2]
                            #print("ceb_isConnected: " + ceb_isConnected)
                            ceb_lastContentEndTimeInMillisecondsByScheduledJob = datanewsplito[18][2:]
                            #print("ceb_lastContentEndTimeInMillisecondsByScheduledJob: " + ceb_lastContentEndTimeInMillisecondsByScheduledJob)
                            ceb_lastContentEndTimeByScheduledJob = datanewsplito[20][3:][:-1]
                            #print("ceb_lastContentEndTimeByScheduledJob: " + ceb_lastContentEndTimeByScheduledJob)
                            ceb_scheduledJobFrequency = datanewsplito[22][2:]
                            #print("ceb_scheduledJobFrequency: " + ceb_scheduledJobFrequency)
                            ceb_nextCEJobRunTimeInMilliseconds = datanewsplito[24][2:]
                            #print("ceb_nextCEJobRunTimeInMilliseconds: " + ceb_nextCEJobRunTimeInMilliseconds)
                            ceb_nextCEJobRunTime = datanewsplito[26][3:][:-1]
                            #print("ceb_nextCEJobRunTime: " + ceb_nextCEJobRunTime)
                            ceb_exportFormat = datanewsplito[28][3:][:-4]
                            #print("ceb_exportFormat: " + ceb_exportFormat)

                        table_body += "<tr>" \
                                      "<td>" + ceb_id + "</td>" \
                                      "<td class=\"tempo-text-color--white tempo-bg-color--blue\">" + ceb_version + "</td>" \
                                      "<td>" + ceb_ipAddress + "</td>" \
                                      "<td>" + ceb_hostOS + "</td>" \
                                      "<td>" + ceb_archiveDirectory + "</td>" \
                                      "<td>" + ceb_lastConnectionTimeInMillisecond + "</td>" \
                                      "<td>" + ceb_lastConnectionTime + "</td>" \
                                      "<td class=\"tempo-text-color--white tempo-bg-color--blue\">" + ceb_isConnected + "</td>" \
                                      "<td>" + ceb_lastContentEndTimeInMillisecondsByScheduledJob + "</td>" \
                                      "<td>" + ceb_lastContentEndTimeByScheduledJob + "</td>" \
                                      "<td>" + ceb_scheduledJobFrequency + "</td>" \
                                      "<td>" + ceb_nextCEJobRunTimeInMilliseconds + "</td>" \
                                      "<td>" + ceb_nextCEJobRunTime + "</td>" \
                                      "<td>" + ceb_exportFormat + "</td>" \
                                      "</tr>" \

                    except IndexError:

                        parsed = json.loads(datanew)
                        datanew = (json.dumps(parsed, indent=2, sort_keys=False))

                        #print("No more info to show")
                        botlog.LogSymphonyInfo("This Pod does not seem to be using Content Export")
                        messageDetail.ReplyToChat("This Pod is not using Content Export, please see raw data")
                        t1 = time.time()
                        total_n = t1 - t0
                        print("Total time: " + str(total_n))
                        return messageDetail.ReplyToChat(datanew)

                    table_body += "</tbody></table>"
                    datanew = table_header + table_body


                # elif prod_pod_component == "km":
                #     #print("inside KM")
                #
                #     conn = http.client.HTTPSConnection(prod_pod_name+".symphony.com")
                #
                #     headers = {
                #         'cache-control': "no-cache",
                #     }
                #
                #     conn.request("GET", "/keystore/HealthCheck/keymanagers", headers=headers)
                #
                #     res = conn.getresponse()
                #     data = res.read()
                #     datanewraw = (data.decode("utf-8"))
                #     #print("data_km: " + datanewraw)
                #
                #     parsed = json.loads(datanewraw)
                #     datanew = (json.dumps(parsed, indent=4, sort_keys=True))
                #     print("KM Details: " + datanew)


                elif prod_pod_component not in ("agent", "km", "ceb"):
                    return messageDetail.ReplyToChat("You did not specify a component to check such as agent, km or ceb")

                else:
                    print("There is no information for such component")
            except:
                return messageDetail.ReplyToChat("There is no information to show, please check the logs")

        t1 = time.time()
        total_n = t1 - t0
        print("Total time: " + str(total_n))

        if total_n >= 3:
            return messageDetail.ReplyToChat("The Pod name is not correct, please check Pod name")
        else:

            return messageDetail.ReplyToChatV2_noBotLog(datanew)
    else:
        return messageDetail.ReplyToChat("You aren't authorised to use this command. Please contact Alex Nalin for access")


# def deactivateUser(messageDetail):
#
#     commandCallerUID = messageDetail.FromUserId
#
#     connComp = http.client.HTTPSConnection(_configDef['symphonyinfo']['pod_hostname'])
#     sessionTok = callout.GetSessionToken()
#
#     headersCompany = {
#         'sessiontoken': sessionTok,
#         'cache-control': "no-cache"
#     }
#
#     connComp.request("GET", "/pod/v3/users?uid=" + commandCallerUID, headers=headersCompany)
#
#     resComp = connComp.getresponse()
#     dataComp = resComp.read()
#     data_raw = str(dataComp.decode('utf-8'))
#     data_dict = ast.literal_eval(data_raw)
#
#     dataRender = json.dumps(data_dict, indent=2)
#     d_org = json.loads(dataRender)
#
#     for index_org in range(len(d_org["users"])):
#         firstName = d_org["users"][index_org]["firstName"]
#         lastName = d_org["users"][index_org]["lastName"]
#         displayName = d_org["users"][index_org]["displayName"]
#         companyName = d_org["users"][index_org]["company"]
#         userID = str(d_org["users"][index_org]["id"])
#
#         botlog.LogSymphonyInfo(firstName + " " + lastName + " from Company/Pod name: " + str(companyName) + " with UID: " + str(userID))
#         callerCheck = (firstName + " " + lastName + " - " + displayName + " - " + companyName + " - " + str(userID))
#
#     if callerCheck in (_configZen['AuthUser']['AdminList']):
#
#         messageDetail.ReplyToChat("Please look for a file picker popup to select your excel file to be processed. It could be behind another application")
#
#         try:
#             Tk().withdraw()
#             filename = askopenfilename()
#             df = pandas.read_excel(filename)
#
#         except:
#             return messageDetail.ReplyToChat("The file is not valid, please select an excel file with file extension .xlsx or .xls ")
#
#         #print the column names
#         #print(df.columns)
#         #get the values for a given column
#
#         try:
#             values = df['userId'].values
#         except:
#             return messageDetail.ReplyToChatV2("Make sure the column header is <b>userId</b>")
#
#         values = str(values).replace("\n", "")
#         #print(values)
#         order = str(values).split(" ")
#         #print(order)
#         #get a data frame with selected columns
#         # FORMAT = ['First', 'Second', 'Third']
#         # df_selected = df[FORMAT]
#
#         invalidUserID = ""
#         validUserID = ""
#
#         messageDetail.ReplyToChat("Please wait while I process this request")
#
#         for index in range(len(order)):
#
#             desc = order[index]
#             userid = desc.replace("[", "").replace("]", "")
#             #print(userid)
#
#             conn = http.client.HTTPSConnection(_configDef['symphonyinfo']['pod_hostname'])
#
#             payload = "{\n\t\"status\": \"DISABLED\"\n}"
#             headers = {
#                 'sessiontoken': callout.GetSessionToken(),
#                 'content-type': "application/json",
#                 'cache-control': "no-cache",
#             }
#             conn.request("POST", "/pod/v1/admin/user/" + userid + "/status/update", payload, headers)
#
#             res = conn.getresponse()
#             data = res.read()
#
#             useridCheck = data.decode("utf-8")
#             #print(useridCheck)
#
#             #This is to check that correct Pod is used in the config file and handle the error.
#             incorrectPod = "{\"message\":\"Invalid session token\"}"
#             deactivated = "{\"format\":\"TEXT\",\"message\":\"OK\"}"
#
#             if useridCheck == incorrectPod:
#                 return messageDetail.ReplyToChat("Please make sure you have set the correct Pod url info in the Config file.")
#
#             elif useridCheck.startswith("{\"code\":400,\"message\":\"Invalid user"):
#                 invalidUserID += userid + ", "
#
#             elif useridCheck == deactivated:
#                 validUserID += userid + ", "
#
#         if useridCheck == deactivated:
#             return messageDetail.ReplyToChatV2("<p>User(s) have been de-activated:</p><p>" + validUserID + "</p>")
#
#         elif useridCheck.startswith("{\"code\":400,\"message\":\"Invalid user"):
#             return messageDetail.ReplyToChatV2("<p>The following UserID(s), do(es) not exist, please check if it's from the correct Pod or missing a digit:</p><p>" + invalidUserID + "</p>")
#
#         else:
#             return messageDetail.ReplyToChat("Something did not work, the Pod URL is valid and Userid is valid. Please check the excel file itself")
#
#     else:
#         return messageDetail.ReplyToChat("You aren't authorised to use this command. Please contact Alex Nalin for access")
#
#
# def reactivateUser(messageDetail):
#
#     commandCallerUID = messageDetail.FromUserId
#
#     connComp = http.client.HTTPSConnection(_configDef['symphonyinfo']['pod_hostname'])
#     sessionTok = callout.GetSessionToken()
#
#     headersCompany = {
#         'sessiontoken': sessionTok,
#         'cache-control': "no-cache"
#     }
#
#     connComp.request("GET", "/pod/v3/users?uid=" + commandCallerUID, headers=headersCompany)
#
#     resComp = connComp.getresponse()
#     dataComp = resComp.read()
#     data_raw = str(dataComp.decode('utf-8'))
#     data_dict = ast.literal_eval(data_raw)
#
#     dataRender = json.dumps(data_dict, indent=2)
#     d_org = json.loads(dataRender)
#
#     for index_org in range(len(d_org["users"])):
#         firstName = d_org["users"][index_org]["firstName"]
#         lastName = d_org["users"][index_org]["lastName"]
#         displayName = d_org["users"][index_org]["displayName"]
#         companyName = d_org["users"][index_org]["company"]
#         userID = str(d_org["users"][index_org]["id"])
#
#         botlog.LogSymphonyInfo(firstName + " " + lastName + " from Company/Pod name: " + str(companyName) + " with UID: " + str(userID))
#         callerCheck = (firstName + " " + lastName + " - " + displayName + " - " + companyName + " - " + str(userID))
#
#     if callerCheck in (_configZen['AuthUser']['AdminList']):
#
#         messageDetail.ReplyToChat("Please look for a file picker popup to select your excel file to be processed. It could be behind another application")
#
#         try:
#             Tk().withdraw()
#             filename = askopenfilename()
#             df = pandas.read_excel(filename)
#
#         except:
#             return messageDetail.ReplyToChat("The file is not valid, please select an excel file with file extension .xlsx or .xls ")
#
#         #print the column names
#         #print(df.columns)
#         #get the values for a given column
#
#         try:
#             values = df['userId'].values
#         except:
#             return messageDetail.ReplyToChatV2("Make sure the column header is <b>userId</b>")
#
#         values = str(values).replace("\n", "")
#         #print(values)
#         order = str(values).split(" ")
#         #print(order)
#         #get a data frame with selected columns
#         # FORMAT = ['First', 'Second', 'Third']
#         # df_selected = df[FORMAT]
#
#         invalidUserID = ""
#         validUserID = ""
#
#         messageDetail.ReplyToChat("Please wait while I process this request")
#
#         for index in range(len(order)):
#
#             desc = order[index]
#             userid = desc.replace("[", "").replace("]", "")
#             #print(userid)
#
#             conn = http.client.HTTPSConnection(_configDef['symphonyinfo']['pod_hostname'])
#
#             payload = "{\n\t\"status\": \"ENABLED\"\n}"
#             headers = {
#                 'sessiontoken': callout.GetSessionToken(),
#                 'content-type': "application/json",
#                 'cache-control': "no-cache",
#             }
#             conn.request("POST", "/pod/v1/admin/user/" + userid + "/status/update", payload, headers)
#
#             res = conn.getresponse()
#             data = res.read()
#
#             useridCheck = data.decode("utf-8")
#             #print(useridCheck)
#
#             #This is to check that correct Pod is used in the config file and handle the error.
#             incorrectPod = "{\"message\":\"Invalid session token\"}"
#             reactivated = "{\"format\":\"TEXT\",\"message\":\"OK\"}"
#
#             if useridCheck == incorrectPod:
#                 return messageDetail.ReplyToChat("Please make sure you have set the correct Pod url info in the Config file.")
#
#             elif useridCheck.startswith("{\"code\":400,\"message\":\"Invalid user"):
#                 invalidUserID += userid + ", "
#
#             elif useridCheck == reactivated:
#                 validUserID += userid + ", "
#
#         if useridCheck == reactivated:
#             return messageDetail.ReplyToChatV2("<p>User(s) have been re-activated:</p><p>" + validUserID + "</p>")
#
#         elif useridCheck.startswith("{\"code\":400,\"message\":\"Invalid user"):
#             return messageDetail.ReplyToChatV2("<p>The following UserID(s), do(es) not exist, please check if it's from the correct Pod or missing a digit:</p><p>" + invalidUserID + "</p>")
#
#         else:
#             return messageDetail.ReplyToChat("Something did not work, the Pod URL is valid and Userid is valid. Please check the excel file itself")
#
#     else:
#         return messageDetail.ReplyToChat("You aren't authorised to use this command. Please contact Alex Nalin for access")


# def createRoomAddUser(messageDetail):
#
#     commandCallerUID = messageDetail.FromUserId
#
#     connComp = http.client.HTTPSConnection(_configDef['symphonyinfo']['pod_hostname'])
#     sessionTok = callout.GetSessionToken()
#
#     headersCompany = {
#         'sessiontoken': sessionTok,
#         'cache-control': "no-cache"
#     }
#
#     connComp.request("GET", "/pod/v3/users?uid=" + commandCallerUID, headers=headersCompany)
#
#     resComp = connComp.getresponse()
#     dataComp = resComp.read()
#     data_raw = str(dataComp.decode('utf-8'))
#     data_dict = ast.literal_eval(data_raw)
#
#     dataRender = json.dumps(data_dict, indent=2)
#     d_org = json.loads(dataRender)
#
#     for index_org in range(len(d_org["users"])):
#         firstName = d_org["users"][index_org]["firstName"]
#         lastName = d_org["users"][index_org]["lastName"]
#         displayName = d_org["users"][index_org]["displayName"]
#         companyName = d_org["users"][index_org]["company"]
#         userID = str(d_org["users"][index_org]["id"])
#
#         botlog.LogSymphonyInfo(firstName + " " + lastName + " from Company/Pod name: " + str(companyName) + " with UID: " + str(userID))
#         callerCheck = (firstName + " " + lastName + " - " + displayName + " - " + companyName + " - " + str(userID))
#
#     if callerCheck in AccessFile:
#
#         message = (messageDetail.Command.MessageText)
#         message_split = message.split(",")
#
#         try:
#             roomName = message_split[0]
#             #print("Room Name: " + roomName)
#             roomdesc = message_split[1]
#             #print("Room Description: " + roomdesc)
#         except:
#             return messageDetail.ReplyToChat("You did not enter a Room name or Description. Make sure to use comma in between the two value (,)")
#
#         conn = http.client.HTTPSConnection(_configDef['symphonyinfo']['pod_hostname'])
#         sessionTok = callout.GetSessionToken()
#
#         payload = "{   \r\n    \"name\": \"" + roomName + "\",\r\n    \"description\": \"" + roomdesc + "\",\r\n    \"keywords\": [\r\n        {\"key\": \"Symphony\", \"value\": \"SymphonyZendeskBot\"},\r\n        {\"key\": \"Support\", \"value\": \"API Team\"}\r\n    ],\r\n    \"membersCanInvite\": true,\r\n    \"discoverable\": false,\r\n    \"public\": false,\r\n    \"readOnly\": false,\r\n    \"copyProtected\": false,\r\n    \"crossPod\": true,\r\n    \"viewHistory\": false\r\n}"
#
#         headers = {
#             'sessiontoken': sessionTok,
#             'content-type': "application/json",
#             'cache-control': "no-cache"
#         }
#
#         conn.request("POST", "/pod/v3/room/create", payload, headers)
#
#         res = conn.getresponse()
#         data_raw = res.read().decode("utf-8")
#
#         data = json.dumps(data_raw, indent=2)
#         data_dict = ast.literal_eval(data)
#         d_room = json.loads(data_dict)
#
#         table_body = ""
#         table_header = "<table><thead><tr class=\"tempo-text-color--white tempo-bg-color--black\">" \
#                        "<th>Room name</th>" \
#                        "<th>Description</th>" \
#                        "<th>Members Can Invite</th>" \
#                        "<th>Discoverable</th>" \
#                        "<th>Read Only</th>" \
#                        "<th>Copy Protected</th>" \
#                        "<th>Cross Pod</th>" \
#                        "<th>View History</th>" \
#                        "<th>MultiLateral Room</th>" \
#                        "<th>Public</th>" \
#                        "<th>Stream ID</th>" \
#                        "</tr></thead><tbody>"
#
#         messageDetail.ReplyToChat("Room created with following details: ")
#
#         name = str(d_room["roomAttributes"]["name"])
#         description = str(d_room["roomAttributes"]["description"])
#         membersCanInvite = str(d_room["roomAttributes"]["membersCanInvite"])
#         discoverable = str(d_room["roomAttributes"]["discoverable"])
#         readOnly = str(d_room["roomAttributes"]["readOnly"])
#         copyProtected = str(d_room["roomAttributes"]["copyProtected"])
#         crossPod = str(d_room["roomAttributes"]["crossPod"])
#         viewHistory = str(d_room["roomAttributes"]["viewHistory"])
#         multiLateralRoom = str(d_room["roomAttributes"]["multiLateralRoom"])
#         public = str(d_room["roomAttributes"]["public"])
#         streamID = str(d_room["roomSystemInfo"]["id"])
#
#         table_body += "<tr>" \
#                       "<td>" + name + "</td>" \
#                       "<td>" + description + "</td>" \
#                       "<td>" + membersCanInvite + "</td>" \
#                       "<td>" + discoverable + "</td>" \
#                       "<td>" + readOnly + "</td>" \
#                       "<td>" + copyProtected + "</td>" \
#                       "<td>" + crossPod + "</td>" \
#                       "<td>" + viewHistory + "</td>" \
#                       "<td>" + multiLateralRoom + "</td>" \
#                       "<td>" + public + "</td>" \
#                       "<td>" + streamID + "</td>" \
#                       "</tr>"
#
#     ##### Add User to Room
#
#         payload_adduser = "{\n\t\"id\": 70368744177929, \"id\": 71811853189656\n}"
#         conn.request("POST", "/pod/v1/room/" + streamID + "/membership/add", payload_adduser, headers)
#
#         res = conn.getresponse()
#         data_addUser = res.read().decode("utf-8")
#         print(data_addUser)
#
#         messageDetail.ReplyToChatV2("user(s) added to the room " + name)
#
#         table_body += "</tbody></table>"
#         render = table_header + table_body
#         return messageDetail.ReplyToChatV2_noBotLog(render)
#
#     else:
#         return messageDetail.ReplyToChat("You aren't authorised to use this command. Please contact Alex Nalin for access")


# def userCheck(messageDetail):
#
#     commandCallerUID = messageDetail.FromUserId
#
#     connComp = http.client.HTTPSConnection(_configDef['symphonyinfo']['pod_hostname'])
#     sessionTok = callout.GetSessionToken()
#
#     headersCompany = {
#         'sessiontoken': sessionTok,
#         'cache-control': "no-cache"
#     }
#
#     connComp.request("GET", "/pod/v3/users?uid=" + commandCallerUID, headers=headersCompany)
#
#     resComp = connComp.getresponse()
#     dataComp = resComp.read()
#     data_raw = str(dataComp.decode('utf-8'))
#     data_dict = ast.literal_eval(data_raw)
#
#     dataRender = json.dumps(data_dict, indent=2)
#     d_org = json.loads(dataRender)
#
#     for index_org in range(len(d_org["users"])):
#         firstName = d_org["users"][index_org]["firstName"]
#         lastName = d_org["users"][index_org]["lastName"]
#         displayName = d_org["users"][index_org]["displayName"]
#         companyName = d_org["users"][index_org]["company"]
#         userID = str(d_org["users"][index_org]["id"])
#
#         botlog.LogSymphonyInfo(firstName + " " + lastName + " from Company/Pod name: " + str(companyName) + " with UID: " + str(userID))
#         callerCheck = (firstName + " " + lastName + " - " + displayName + " - " + companyName + " - " + str(userID))
#
#     if callerCheck in (_configZen['AuthUser']['AdminList']):
#
#         conn = http.client.HTTPSConnection(_configDef['symphonyinfo']['pod_hostname'])
#
#         headers = {
#             'sessiontoken': callout.GetSessionToken(),
#             'cache-control': "no-cache"
#         }
#
#         conn.request("GET", "/pod/v1/admin/stream/" + _configZen['AuthUser']['RoomStream'] + "/membership/list", headers=headers)
#
#         res = conn.getresponse()
#         data_raw = res.read().decode("utf-8")
#
#         data = json.dumps(data_raw, indent=2)
#         data_dict = ast.literal_eval(data)
#         userAccess = json.loads(data_dict)
#
#         table_body = ""
#         table_header = "<table style='border-collapse:collapse;border:2px solid black;table-layout:fixed;max-width:25%;box-shadow: 5px 5px'><thead><tr style='background-color:#4D94FF;color:#ffffff;font-size:1rem' class=\"tempo-text-color--white tempo-bg-color--black\">" \
#                        "<td style='border:1px solid blue;border-bottom: double blue;width:60%;text-align:center'>DISPLAY NAME</td>" \
#                        "<td style='border:1px solid blue;border-bottom: double blue;width:40%;text-align:center'>USER FROM DIFFERENT POD?</td>" \
#                        "</tr></thead><tbody>"
#
#         for index in range(len(userAccess["members"])):
#
#             displayName = str(userAccess["members"][index]["user"]["displayName"])
#             external = str(userAccess["members"][index]["user"]["isExternal"])
#
#             table_body += "<tr>" \
#                           "<td style='border:1px solid black;text-align:center'>" + str(displayName) + "</td>" \
#                           "<td style='border:1px solid black;text-align:center'>" + str(external) + "</td>" \
#                           "</tr>"
#
#         table_body += "</tbody></table>"
#         render = table_header + table_body
#
#         return messageDetail.ReplyToChatV2_noBotLog(
#             "<card iconSrc =\"https://thumb.ibb.co/csXBgU/Symphony2018_App_Icon_Mobile.png\" accent=\"tempo-bg-color--blue\"><header>Please find the result below</header><body>" + render + "</body></card>")
#
#     else:
#         return messageDetail.ReplyToChat("You aren't authorised to use this command.")