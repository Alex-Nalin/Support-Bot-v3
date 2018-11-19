from zdesk import Zendesk
import json
import os
import codecs
#import modules.symphony.user as user
import http.client
import requests
import base64
import re
import modules.botlog as botlog
import modules.symphony.callout as callout
import ast
from datetime import date, datetime, timedelta
from Data.access import AccessFile
import time
from hurry.filesize import size

global setEnableDisable

#Grab the config.json main parameters
_configPathdDefault = os.path.abspath('config.json')

with codecs.open(_configPathdDefault, 'r', 'utf-8-sig') as json_file:
        _configDef = json.load(json_file)

#Zendesk libary
testconfig = {
        'zdesk_email': _configDef['zdesk_config']['zdesk_email'],
        'zdesk_password': _configDef['zdesk_config']['zdesk_password'],
        'zdesk_url': _configDef['zdesk_config']['zdesk_url'],
        'zdesk_token': True
        }
zendesk = Zendesk(**testconfig)

#Zendesk API call config/header
conn = http.client.HTTPSConnection(_configDef['zdesk_config']['zdesk_api'])

# Converting id by real value
## https://support.zendesk.com/hc/en-us/articles/115000510267-Authentication-for-API-requests
## Generate the base64 authorization:
## <emailaddress>/token:<Zendesk_API_Token>
headers = {
    'username': _configDef['zdesk_config']['zdesk_email'] + "/token",
    'password': _configDef['zdesk_config']['zdesk_password'],
    'authorization': _configDef['zdesk_config']['zdesk_auth'],
    'cache-control': "no-cache",
    'Content-Type': 'application/json',
    'zdesk_token': True
    }

#Symphony API call Config/header
connComp = http.client.HTTPSConnection(_configDef['symphonyinfo']['pod_hostname'])
sessionTok = callout.GetSessionToken()

headersCompany = {
    'sessiontoken': sessionTok,
    'cache-control': "no-cache"
    }

#############################
#######   SEARCH   ##########
#############################
def searchZD(messageDetail):
    botlog.LogSymphonyInfo("Bot Call: Search Zendesk")

    try:

        organization = ""

        # commandCallerUID = messageDetail.FromUserId
        #
        # ## Checking who is calling this command to allow only search about own company/Org/Pod
        # ############################
        # connComp = http.client.HTTPSConnection(_configDef['symphonyinfo']['pod_hostname'])
        # sessionTok = callout.GetSessionToken()
        #
        # headersCompany = {
        #     'sessiontoken': sessionTok,
        #     'cache-control': "no-cache"
        # }
        #
        # connComp.request("GET", "/pod/v3/users?uid=" + commandCallerUID, headers=headersCompany)
        #
        # resComp = connComp.getresponse()
        # dataComp = resComp.read()
        # data_raw = str(dataComp.decode('utf-8'))
        # data_dict = ast.literal_eval(data_raw)
        #
        # dataRender = json.dumps(data_dict, indent=2)
        # d_org = json.loads(dataRender)
        #
        # for index_org in range(len(d_org["users"])):
        #     companyName = d_org["users"][index_org]["company"]
        #     botlog.LogSymphonyInfo("Call is coming from Company/Pod name: " + str(companyName))

        #
        # ## If company is not in the list, change the company name searched for by their internal company name, Else check that user is allowed to run that search in Symphony
        # if str(companyName) not in (_configDef['AuthCompany']['PodList']):
        #     botlog.LogSymphonyInfo("Bot call info: The calling user is not from inside Symphony, the search result will display deails for his company only")
        #     messageDetail.ReplyToChat("This search feature is limited to your company only. Pulling the data from Zendesk and rendering it now. Please wait:")
        #
        #     status = ""
        #     indexB = ""
        #     message = (messageDetail.Command.MessageText)
        #     message_split = message.split()
        #
        #     notNeeded = True
        #     # Parse the messages received
        #     for index in range(len(message_split)):
        #
        #         if message_split[index][:2] == "-o" or message_split[index][:1] == "o" or message_split[index][:6] == "-open" or message_split[index][:6] == "-opened" or message_split[index][:4] == "open" or message_split[index][:5] == "opened":
        #             status = "status:open "
        #         elif message_split[index][:2] == "-n" or message_split[index][:1] == "n" or message_split[index][:4] == "-new" or message_split[index][:3] == "new":
        #             status = "status:new "
        #         elif message_split[index][:2] == "-s" or message_split[index][:1] == "s" or message_split[index][:7] == "-solved" or message_split[index][:6] == "solved":
        #             status = "status:solved "
        #         elif message_split[index][:2] == "-c" or message_split[index][:1] == "c" or message_split[index][:7] == "-closed" or message_split[index][:6] == "closed":
        #             status = "status:closed "
        #         elif message_split[index][:2] == "-p" or message_split[index][:1] == "p" or message_split[index][:8] == "-pending" or message_split[index][:7] == "pending":
        #             status = "status:pending "
        #         elif message_split[index][:2] == "-u" or message_split[index][:1] == "u" or message_split[index][:11] == "-unresolved" or message_split[index][:10] == "unresolved":
        #             status = "status<solved "
        #         else:
        #             organization += message_split[index]
        #
        #         organization = str(companyName)
        #
        #         query = (status + "type:ticket sort:desc organization:" + organization)
        #
        #         if index == 1:
        #             botlog.LogSymphonyInfo("Search query: " + query)
        #
        #         try:
        #             results_dict = zendesk.search(query=query)
        #
        #             data = json.dumps(results_dict, indent=2)
        #             d_dict = json.loads(data)
        #             d = d_dict
        #         except:
        #             return messageDetail.ReplyToChat("I am having difficulty to process this query, please try again in few seconds")
        #
        #         table_body = ""
        #         table_header = "<table style='border-collapse:collapse;border:2px solid black;table-layout:auto;width:100%;box-shadow: 5px 5px'>" \
        #                        "<thead>" \
        #                        "<tr style='background-color:#4D94FF;color:#ffffff;font-size:1rem' class=\"tempo-text-color--white tempo-bg-color--black\">" \
        #                        "<td style='border:1px solid blue;border-bottom: double blue;width:15%;text-align:center'>SUBJECT</td>" \
        #                        "<td style='border:1px solid blue;border-bottom: double blue;width:35%;text-align:center'>DESCRIPTION</td>" \
        #                        "<td style='border:1px solid blue;border-bottom: double blue;width:2%;text-align:center'>ID</td>" \
        #                        "<td style='border:1px solid blue;border-bottom: double blue;width:10.5%;text-align:center'>REQUESTER</td>" \
        #                        "<td style='border:1px solid blue;border-bottom: double blue;width:7.5%;text-align:center'>REQUESTED</td>" \
        #                        "<td style='border:1px solid blue;border-bottom: double blue;width:7.5%;text-align:center'>ASSIGNEE</td>" \
        #                        "<td style='border:1px solid blue;border-bottom: double blue;width:7.5%;text-align:center'>UPDATED</td>" \
        #                        "<td style='border:1px solid blue;border-bottom: double blue;width:5%;text-align:center'>STATUS</td>" \
        #                        "<td style='border:1px solid blue;border-bottom: double blue;width:5%;text-align:center'>PRIORITY</td>" \
        #                        "<td style='border:1px solid blue;border-bottom: double blue;width:5%;text-align:center'>SEVERITY</td>" \
        #                        "</tr></thead><tbody>"
        #
        #
        #     for indexB in range(len(d["results"])):
        #         assignee_flag = False
        #         try:
        #             # strip out conflicting HTML tags in descriptions
        #             description_temp = d["results"][indexB]["description"]
        #             description = description_temp.replace("<", "&lt;")
        #             ticketid = str(d["results"][indexB]["id"])
        #
        #             # Getting IDs of requeters to be processed
        #             requesterid = str(d["results"][indexB]["requester_id"])
        #         except:
        #             return messageDetail.ReplyToChat("Cannot read ticket info")
        #
        #         try:
        #             # To get the name of the requester given the requesterID
        #             conn.request("GET", "/api/v2/users/" + requesterid, headers=headers)
        #             res = conn.getresponse()
        #             userRequesterId = res.read()
        #             tempUserRequester = str(userRequesterId.decode('utf-8'))
        #             data = json.dumps(tempUserRequester, indent=2)
        #             data_dict = ast.literal_eval(data)
        #             d_req = json.loads(data_dict)
        #             req_name = str(d_req["user"]["name"])
        #             requesterName = req_name
        #         except:
        #             botlog.LogSymphonyInfo("Cannot requester info")
        #
        #         # Getting IDs of assignee to be processed
        #         try:
        #             assigneeid = str(d["results"][indexB]["assignee_id"])
        #
        #             # To get the name of the assignee given the assigneeID
        #             conn.request("GET", "/api/v2/users/" + assigneeid, headers=headers)
        #             res = conn.getresponse()
        #             userAssigneeId = res.read()
        #             tempUserAssignee = str(userAssigneeId.decode('utf-8'))
        #
        #             data = json.dumps(tempUserAssignee, indent=2)
        #             data_dict = ast.literal_eval(data)
        #             d_assign = json.loads(data_dict)
        #             assign_name = str(d_assign["user"]["name"])
        #             assigneeName = assign_name
        #
        #         except:
        #             assigneeName = "Not assigned"
        #             assignee_flag = True
        #
        #         requesterTicket = (_configDef['zdesk_config']['zdesk_link']) + str(ticketid) + "/requester/requested_tickets"
        #         assigneeTicket = (_configDef['zdesk_config']['zdesk_url']) + "/agent/users/" + assigneeid + "/assigned_tickets"
        #
        #         if assignee_flag:
        #             table_body += "<tr>" \
        #                           "<td style='border:1px solid black;text-align:left'>" + d["results"][indexB]["subject"] + "</td>" \
        #                           "<td style='border:1px solid black;text-align:left'>" + description + "</td>" \
        #                           "<td style='border:1px solid black;text-align:center'><a href=\"" + (_configDef['zdesk_config']['zdesk_link']) + str(ticketid) + "\">" + str(ticketid) + "</a></td>" \
        #                           "<td style='border:1px solid black;text-align:center'><a href=\"" + requesterTicket + "\">" + str(requesterName) + "</a></td>" \
        #                           "<td style='border:1px solid black;text-align:center'>" + str(d["results"][indexB]["created_at"]).replace("T", " ").replace("Z", "") + "</td>" \
        #                           "<td style='border:1px solid black;text-align:center'>" + assigneeName + "</td>" \
        #                           "<td style='border:1px solid black;text-align:center'>" + str(d["results"][indexB]["updated_at"]).replace("T", " ").replace("Z", "") + "</td>" \
        #                           "<td style='border:1px solid black;text-align:center'>" + d["results"][indexB]["status"] + "</td>"
        #
        #         else:
        #             table_body += "<tr>" \
        #                           "<td style='border:1px solid black;text-align:left'>" + d["results"][indexB]["subject"] + "</td>" \
        #                           "<td style='border:1px solid black;text-align:left'>" + description + "</td>" \
        #                           "<td style='border:1px solid black;text-align:center'><a href=\"" + (_configDef['zdesk_config']['zdesk_link']) + str(ticketid) + "\">" + str(ticketid) + "</a></td>" \
        #                           "<td style='border:1px solid black;text-align:center'><a href=\"" + requesterTicket + "\">" + str(requesterName) + "</a></td>" \
        #                           "<td style='border:1px solid black;text-align:center'>" + str(d["results"][indexB]["created_at"]).replace("T", " ").replace("Z", "")+ "</td>" \
        #                           "<td style='border:1px solid black;text-align:center'><a href=\"" + assigneeTicket + "\">" + str(assigneeName) + "</a></td>" \
        #                           "<td style='border:1px solid black;text-align:center'>" + str(d["results"][indexB]["updated_at"]).replace("T", " ").replace("Z", "") + "</td>" \
        #                           "<td style='border:1px solid black;text-align:center'>" + d["results"][indexB]["status"] + "</td>"
        #
        #         try:
        #             table_body += "<td style='border:1px solid black;text-align:center'>" + d["results"][indexB]["priority"] + "</td>"
        #         except:
        #             table_body += "<td style='border:1px solid black;text-align:center'>Not set</td>"
        #
        #         if (len(d["results"][indexB]["tags"])) == 0:
        #             noTag = True
        #         else:
        #             noTag = False
        #
        #         notSet = True
        #         if noTag:
        #             table_body += "<td style='border:1px solid black;text-align:center'>Not set</td>"
        #             notSet = False
        #
        #         sev = ""
        #         for index_tags in range(len(d["results"][indexB]["tags"])):
        #             tags = str((d["results"][indexB]["tags"][index_tags]))
        #
        #             if tags.startswith("severity_1"):
        #                 sev = "Severity 1"
        #                 notSet = False
        #                 table_body += "<td style='border:1px solid black;text-align:center'>" + sev + " " + "</td>"
        #             elif tags.startswith("severity_2"):
        #                 sev = "Severity 2"
        #                 notSet = False
        #                 table_body += "<td style='border:1px solid black;text-align:center'>" + sev + " " + "</td>"
        #             elif tags.startswith("severity_3"):
        #                 sev = "Severity 3"
        #                 notSet = False
        #                 table_body += "<td style='border:1px solid black;text-align:center'>" + sev + " " + "</td>"
        #             elif tags.startswith("severity_4"):
        #                 sev = "Severity 4"
        #                 notSet = False
        #                 table_body += "<td style='border:1px solid black;text-align:center'>" + sev + " " + "</td>"
        #
        #         if notSet:
        #             table_body += "<td style='border:1px solid black;text-align:center'>Not Set</td>"
        #             notSet = False
        #
        #         table_body += "</tr>"
        #
        #     try:
        #         ticketid = str(d["results"][indexB]["id"])
        #     except:
        #         return messageDetail.ReplyToChat("You did not enter a valid search or no entry found for that search")
        #
        #     table_body += "</tbody></table>"
        #
        #     reply = table_header + table_body
        #
        #     return messageDetail.ReplyToChatV2_noBotLog("<card iconSrc =\"https://thumb.ibb.co/csXBgU/Symphony2018_App_Icon_Mobile.png\" accent=\"tempo-bg-color--blue\"><header>Please find the result below</header><body>" + reply + "</body></card>")
        #
        # ## Internal check for user
        # else:

        try:
            commandCallerUID = messageDetail.FromUserId

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
            return messageDetail.ReplyToChat("I was not able to validate the user access, please try again")

        if callerCheck in AccessFile:

            callername = messageDetail.Sender.Name
            status = ""
            indexB= ""
            organization = ""
            query = ""
            message = (messageDetail.Command.MessageText)
            message_split = message.split()

            statusCheck = str(len(message_split))

            # Parse the messages received
            for index in range(len(message_split)):

                if message_split[index][:2] == "-o" or message_split[index][:1] == "o" or message_split[index][:6] == "-open" or message_split[index][:6] == "-opened" or message_split[index][:4] == "open" or message_split[index][:5] == "opened":
                    status = "status:open "
                    status_message = "open"
                elif message_split[index][:2] == "-n" or message_split[index][:1] == "n" or message_split[index][:4] == "-new" or message_split[index][:3] == "new":
                    status = "status:new "
                    status_message = "new"
                elif message_split[index][:2] == "-s" or message_split[index][:1] == "s" or message_split[index][:7] == "-solved" or message_split[index][:6] == "solved":
                    status = "status:solved "
                    status_message = "solved"
                elif message_split[index][:2] == "-c" or message_split[index][:1] == "c" or message_split[index][:7] == "-closed" or message_split[index][:6] == "closed":
                    status = "status:closed "
                    status_message = "closed"
                elif message_split[index][:2] == "-p" or message_split[index][:1] == "p" or message_split[index][:8] == "-pending" or message_split[index][:7] == "pending":
                    status = "status:pending "
                    status_message = "pending"
                elif message_split[index][:2] == "-u" or message_split[index][:1] == "u" or message_split[index][:11] == "-unresolved" or message_split[index][:10] == "unresolved":
                    status = "status<solved "
                    status_message = "unresolved"
                else:
                    organization += message_split[index]
                    if statusCheck == "1":
                        messageDetail.ReplyToChatV2("Pulling <b>all tickets</b> from Zendesk for <b>" + str(organization) + "</b>, rendering the result now, please wait.")

                query = (str(status) + "type:ticket sort:desc organization:" + str(organization))

                if index == 1:
                    botlog.LogSymphonyInfo("Search query: " + query)
                    messageDetail.ReplyToChatV2("Pulling <b>" + str(status_message) + "</b> tickets from Zendesk for <b>" + str(organization) + "</b>, rendering the result now, please wait.")

################################
                try:
                    headers = {
                        'username': _configDef['zdesk_config']['zdesk_email'] + "/token",
                        'password': _configDef['zdesk_config']['zdesk_password'],
                        'authorization': _configDef['zdesk_config']['zdesk_auth'],
                        'cache-control': "no-cache",
                        'Content-Type': 'application/json',
                    }

                    url = _configDef['zdesk_config']['zdesk_url']+"/api/v2/search"

                    #querystring = {"query": "status:open type:ticket organization:hsbc", "sort_by": "status", "sort_order": "desc"}
                    #querystring = {"query": "status:" + str(status_message) + " type:ticket organization:" + str(organization) + "", "sort_by": "status","sort_order": "desc"}
                    querystring = {"query": ""+ query + "", "sort_by": "status", "sort_order": "desc"}

                    response = requests.request("GET", str(url), headers=headers, params=querystring)
                    data = response.json()
                except:
                    return messageDetail.ReplyToChat("I was not able to run the zendesk query, please try again")
#################################

                table_body = ""
                table_header = "<table style='border-collapse:collapse;border:2px solid black;table-layout:auto;width:100%;box-shadow: 5px 5px'><thead><tr style='background-color:#4D94FF;color:#ffffff;font-size:1rem' class=\"tempo-text-color--black tempo-bg-color--black\">" \
                                "<td style='border:1px solid blue;border-bottom: double blue;width:15%;text-align:center'>SUBJECT</td>" \
                                "<td style='border:1px solid blue;border-bottom: double blue;width:35%;text-align:center'>DESCRIPTION</td>" \
                                "<td style='border:1px solid blue;border-bottom: double blue;width:2%;text-align:center'>ID</td>" \
                                "<td style='border:1px solid blue;border-bottom: double blue;width:10.5%;text-align:center'>REQUESTER</td>" \
                                "<td style='border:1px solid blue;border-bottom: double blue;width:7.5%;text-align:center'>REQUESTED</td>" \
                                "<td style='border:1px solid blue;border-bottom: double blue;width:7.5%;text-align:center'>ASSIGNEE</td>" \
                                "<td style='border:1px solid blue;border-bottom: double blue;width:7.5%;text-align:center'>UPDATED</td>" \
                                "<td style='border:1px solid blue;border-bottom: double blue;width:5%;text-align:center'>STATUS</td>" \
                                "<td style='border:1px solid blue;border-bottom: double blue;width:5%;text-align:center'>PRIORITY</td>" \
                                "<td style='border:1px solid blue;border-bottom: double blue;width:5%;text-align:center'>SEVERITY</td>" \
                                "</tr></thead><tbody>"

            for result in data['results']:

                try:
                    assignee_flag = False
                    # strip out conflicting HTML tags in descriptions
                    description_temp = str(result["description"])
                    description = str(description_temp).replace("<", "&lt;")
                    ticketid = str(result["id"])

                    # Getting IDs of requesters to be processed
                    requesterid = str(result["requester_id"])
                except:
                    botlog.LogSymphonyInfo("Cannot get ticket info")

                try:
                    # To get the name of the requester given the requesterID
                    conn.request("GET", "/api/v2/users/" + str(requesterid), headers=headers)
                    res = conn.getresponse()
                    userRequesterId = res.read()
                    tempUserRequester = str(userRequesterId.decode('utf-8'))
                    data = json.dumps(tempUserRequester, indent=2)
                    data_dict = ast.literal_eval(data)
                    d_req = json.loads(data_dict)
                    req_name = str(d_req["user"]["name"])
                    requesterName = req_name
                except:
                    requesterName = "N/A"
                    botlog.LogSymphonyInfo("Cannot get requester info")

                # Getting IDs of assignee to be processed
                try:
                    assigneeid = str(result["assignee_id"])

                    # To get the name of the assignee given the assigneeID
                    conn.request("GET", "/api/v2/users/" + str(assigneeid), headers=headers)
                    res = conn.getresponse()
                    userAssigneeId = res.read()
                    tempUserAssignee = str(userAssigneeId.decode('utf-8'))

                    data = json.dumps(tempUserAssignee, indent=2)
                    data_dict = ast.literal_eval(data)
                    d_assign = json.loads(data_dict)
                    assign_name = str(d_assign["user"]["name"])
                    assigneeName = assign_name

                except:
                    assigneeName = "N/A"
                    assignee_flag = True

                requesterTicket = (_configDef['zdesk_config']['zdesk_link']) + str(ticketid) + "/requester/requested_tickets"
                assigneeTicket = (_configDef['zdesk_config']['zdesk_url']) + "/agent/users/" + str(assigneeid) + "/assigned_tickets"

                ticketSubject = str(result["subject"])

                if assignee_flag:
                    table_body += "<tr>" \
                                  "<td style='border:1px solid black;text-align:left'>" + str(result["subject"]) + "</td>" \
                                  "<td style='border:1px solid black;text-align:left'>" + str(description) + "</td>" \
                                  "<td style='border:1px solid black;text-align:center'><a href=\"" + (_configDef['zdesk_config']['zdesk_link']) + str(ticketid) + "\">" + str(ticketid) + "</a></td>" \
                                  "<td style='border:1px solid black;text-align:center'><a href=\"" + str(requesterTicket) + "\">" + str(requesterName) + "</a></td>" \
                                  "<td style='border:1px solid black;text-align:center'>" + str(result["created_at"]).replace("T", " ").replace("Z", "") + "</td>" \
                                  "<td style='border:1px solid black;text-align:center'>" + str(assigneeName) + "</td>" \
                                  "<td style='border:1px solid black;text-align:center'>" + str(result["updated_at"]).replace("T", " ").replace("Z", "") + "</td>" \
                                  "<td style='border:1px solid black;text-align:center'>" + str(result["status"]) + "</td>"

                else:
                    table_body += "<tr>" \
                                  "<td style='border:1px solid black;text-align:left'>" + str(result["subject"]) + "</td>" \
                                  "<td style='border:1px solid black;text-align:left'>" + str(description) + "</td>" \
                                  "<td style='border:1px solid black;text-align:center'><a href=\"" + (_configDef['zdesk_config']['zdesk_link']) + str(ticketid) + "\">" + str(ticketid) + "</a></td>" \
                                  "<td style='border:1px solid black;text-align:center'><a href=\"" + str(requesterTicket) + "\">" + str(requesterName) + "</a></td>" \
                                  "<td style='border:1px solid black;text-align:center'>" + str(result["created_at"]).replace("T", " ").replace("Z", "")+ "</td>" \
                                  "<td style='border:1px solid black;text-align:center'><a href=\"" + str(assigneeTicket) + "\">" + str(assigneeName) + "</a></td>" \
                                  "<td style='border:1px solid black;text-align:center'>" + str(result["updated_at"]).replace("T", " ").replace("Z", "") + "</td>" \
                                  "<td style='border:1px solid black;text-align:center'>" + str(result["status"]) + "</td>"

                try:
                    table_body += "<td style='border:1px solid black;text-align:center'>" + result["priority"] + "</td>"
                except:
                    table_body += "<td style='border:1px solid black;text-align:center'>Not set</td>"

                if (len(result["tags"])) == 0:
                    noTag = True
                else:
                    noTag = False

                notSet = True
                if noTag:
                    table_body += "<td style='border:1px solid black;text-align:center'>Not set</td>"
                    notSet = False

                sev = ""
                for index_tags in range(len(result["tags"])):
                    tags = str((result["tags"][index_tags]))

                    if tags.startswith("severity_1"):
                        sev = "Severity 1"
                        notSet = False
                        table_body += "<td style='border:1px solid black;text-align:center'>" + str(sev) + " " + "</td>"
                    elif tags.startswith("severity_2"):
                        sev = "Severity 2"
                        notSet = False
                        table_body += "<td style='border:1px solid black;text-align:center'>" + str(sev) + " " + "</td>"
                    elif tags.startswith("severity_3"):
                        sev = "Severity 3"
                        notSet = False
                        table_body += "<td style='border:1px solid black;text-align:center'>" + str(sev) + " " + "</td>"
                    elif tags.startswith("severity_4"):
                        sev = "Severity 4"
                        notSet = False
                        table_body += "<td style='border:1px solid black;text-align:center'>" + str(sev) + " " + "</td>"

                if notSet:
                    table_body += "<td style='border:1px solid black;text-align:center'>Not Set</td>"
                    notSet = False

                table_body += "</tr>"

            try:
                ticketid = str(result["id"])
            except:
                return messageDetail.ReplyToChat("You did not enter a valid search or no entry found for that search")

            table_body += "</tbody></table>"

            reply = table_header + table_body

            return messageDetail.ReplyToChatV2_noBotLog("<card iconSrc =\"https://thumb.ibb.co/csXBgU/Symphony2018_App_Icon_Mobile.png\" accent=\"tempo-bg-color--blue\"><header>Please find the result below</header><body>" + reply + "</body></card>")

        else:
            return messageDetail.ReplyToChat("You aren't authorised to use this command.")
    except:
        return messageDetail.ReplyToChat("I am sorry, I was working on a different task, can you please retry")


def searchMyTickets(messageDetail):
    botlog.LogSymphonyInfo("####################################")
    botlog.LogSymphonyInfo("Bot Call: Search my Zendesk tickets")
    botlog.LogSymphonyInfo("####################################")

    try:
        commandCallerUID = messageDetail.FromUserId

        # Calling the API endpoint to get display name
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
            emailZendesk = str(d_org["users"][index_org]["emailAddress"])

            botlog.LogSymphonyInfo(firstName + " " + lastName + " (" + displayName + ") from Company/Pod name: " + str(companyName) + " with UID: " + str(userID))
            #callerCheck = (firstName + " " + lastName + " - " + displayName + " - " + companyName + " - " + str(userID))


        #if callerCheck in AccessFile:

        callername = messageDetail.Sender.Name
        status = ""
        status_message = ""
        indexB= ""
        requesterData = ""
        query = ""
        message = (messageDetail.Command.MessageText)
        message_split = message.split()

        statusCheck = str(len(message_split))

        if statusCheck == "0":
            message_split = "unresolved"
            status = "status<solved "
            status_message = "unresolved"

        elif statusCheck == "1":
            try:
                detail = messageDetail.Command.MessageFlattened.split(" ")
                #print(detail)
                flat = messageDetail.Command.MessageFlattened.split("_u_")
                #print(flat)

                UID = flat[1][:int(_configDef['UID'])]
                #print(str(UID))
                botlog.LogSymphonyInfo("User UI: " + UID)

                # Calling the API endpoint to get display name
                connComp = http.client.HTTPSConnection(_configDef['symphonyinfo']['pod_hostname'])
                sessionTok = callout.GetSessionToken()

                headersCompany = {
                    'sessiontoken': sessionTok,
                    'cache-control': "no-cache"
                }

                try:
                    connComp.request("GET", "/pod/v3/users?uid=" + UID, headers=headersCompany)

                    resComp = connComp.getresponse()
                    dataComp = resComp.read()
                    data_raw = str(dataComp.decode('utf-8'))
                    data_dict = ast.literal_eval(data_raw)

                    dataRender = json.dumps(data_dict, indent=2)
                    d_org = json.loads(dataRender)
                except:
                    return messageDetail.ReplyToChat(
                        "Please check the UID of the user, also make sure its digit matches the Config's setting.")

                connectionRequired = ""
                connectionRequired = True
                for index_org in range(len(d_org["users"])):
                    firstName = d_org["users"][index_org]["firstName"]
                    lastName = d_org["users"][index_org]["lastName"]
                    #company = d_org["users"][index_org]["company"]
                    # print(company)
                    #try:
                    emailZendesk = d_org["users"][index_org]["emailAddress"]
                    #print("User is connected: " + emailAddress)
                    #email_address = emailAddress
                    connectionRequired = False
                    #except:
                    connectionRequired = True
                    # messageDetail.ReplyToChat("User is not connected with me")
                    #messageDetail.ReplyToChatV2("Rendering Zendesk Ticket raised by <b>" + firstName + " " + lastName + "</b>, please wait")
            except:
                botlog.LogSymphonyInfo("No user was @mentioned for the SearchMyTicket function")

        # Parse the messages received
        for index in range(len(message_split)):

            if str(message_split[index][:4]).strip() == "Open" or message_split[index][:5] == "Opened" or str(message_split[index][:4]).strip() == "open" or message_split[index][:5] == "opened":
                status = "status:open "
                status_message = "open"
                #messageDetail.ReplyToChatV2("Pulling <b>" + str(status_message) + "</b> tickets from Zendesk raised by <b>" + firstName + " " + lastName + "</b>, rendering the result now, please wait.")
            elif str(message_split[index][:3]).strip() == "New" or str(message_split[index][:3]).strip() == "new":
                status = "status:new "
                status_message = "new"
                #messageDetail.ReplyToChatV2("Pulling <b>" + str(status_message) + "</b> tickets from Zendesk raised by <b>" + firstName + " " + lastName + "</b>, rendering the result now, please wait.")
            elif str(message_split[index][:6]).strip() == "Solved" or str(message_split[index][:6]).strip() == "solved":
                status = "status:solved "
                status_message = "solved"
                #messageDetail.ReplyToChatV2("Pulling <b>" + str(status_message) + "</b> tickets from Zendesk raised by <b>" + firstName + " " + lastName + "</b>, rendering the result now, please wait.")
            elif str(message_split[index][:6]).strip() == "Closed" or str(message_split[index][:6]).strip() == "closed":
                status = "status:closed "
                status_message = "closed"
                #messageDetail.ReplyToChatV2("Pulling <b>" + str(status_message) + "</b> tickets from Zendesk raised by <b>" + firstName + " " + lastName + "</b>, rendering the result now, please wait.")
            elif str(message_split[index][:7]).strip() == "Pending" or str(message_split[index][:7]).strip() == "pending":
                status = "status:pending "
                status_message = "pending"
                #messageDetail.ReplyToChatV2("Pulling <b>" + str(status_message) + "</b> tickets from Zendesk raised by <b>" + firstName + " " + lastName + "</b>, rendering the result now, please wait.")
            elif str(message_split[index][:10]).strip() == "Unresolved" or str(message_split[index][:10]).strip() == "unresolved":
                status = "status<solved "
                status_message = "unresolved"
                #messageDetail.ReplyToChatV2("Pulling <b>" + str(status_message) + "</b> tickets from Zendesk raised by <b>" + firstName + " " + lastName + "</b>, rendering the result now, please wait.")
            elif str(message_split[index][:3]).strip() == "All" or str(message_split[index][:3]).strip() == "all" and index == 0:
                status = ""
                status_message = "all"
                #messageDetail.ReplyToChatV2("Pulling <b>" + str(status_message) + "</b> tickets from Zendesk raised by <b>" + firstName + " " + lastName + "</b>, rendering the result now, please wait.")
            else:
                requesterData += message_split[index]

            query = (str(status) + "type:ticket requester:" + str(emailZendesk))
        botlog.LogSymphonyInfo("query: " + query)
        messageDetail.ReplyToChat("Rendering all <b>" + status_message + "</b> Zendesk Tickets requested by <b>" + firstName + " " + lastName + "</b> , please wait.")

        if index == 1:
            botlog.LogSymphonyInfo("Search query: " + query)
            messageDetail.ReplyToChatV2("Pulling <b>" + str(emailZendesk) + "</b> tickets from Zendesk raised by <b>" + firstName + " " + lastName + "</b>, rendering the result now, please wait.")

    ################################
        try:
            #Using the bot as Zendesk Admin to view all info for tickets as well as requests endpoints
            headers = {
                'username': _configDef['zdesk_config']['zdesk_email'] + "/token",
                'password': _configDef['zdesk_config']['zdesk_password'],
                'authorization': _configDef['zdesk_config']['zdesk_auth'],
                'cache-control': "no-cache",
                'Content-Type': 'application/json',
            }

            # base64Encoded = base64.b64encode(bytes((emailZendesk + "/token:" + _configDef['zdesk_config']['zdesk_password']), 'utf-8'))
            # base64Enc = (base64Encoded.decode("utf-8"))
            # print(str(base64Enc))
            # base = ("Basic " + base64Enc)
            # print(str(base))
            #
            # headers = {
            #     'email_address': emailZendesk + "/token",
            #     'password': (_configDef['zdesk_config']['zdesk_password']),
            #     'authorization': base,
            #     'cache-control': "no-cache",
            #     'content-type': "application/json"
            # }
            #print(str(headers))

            url = _configDef['zdesk_config']['zdesk_url']+"/api/v2/search"

            querystring = {"query": ""+ str(query)}
            #print(querystring)

            response = requests.request("GET", str(url), headers=headers, params=querystring)
            data = response.json()
            #print(data)
        except:
            return messageDetail.ReplyToChat("I was not able to run the zendesk query, please try again")
    #################################

        table_body = ""
        table_header = "<table style='border-collapse:collapse;border:2px solid black;table-layout:auto;width:100%;box-shadow: 5px 5px'><thead><tr style='background-color:#4D94FF;color:#ffffff;font-size:1rem' class=\"tempo-text-color--black tempo-bg-color--black\">" \
                        "<td style='border:1px solid blue;border-bottom: double blue;width:15%;text-align:center'>SUBJECT</td>" \
                        "<td style='border:1px solid blue;border-bottom: double blue;width:35%;text-align:center'>DESCRIPTION</td>" \
                        "<td style='border:1px solid blue;border-bottom: double blue;width:2%;text-align:center'>ID</td>" \
                        "<td style='border:1px solid blue;border-bottom: double blue;width:10.5%;text-align:center'>REQUESTER</td>" \
                        "<td style='border:1px solid blue;border-bottom: double blue;width:7.5%;text-align:center'>REQUESTED</td>" \
                        "<td style='border:1px solid blue;border-bottom: double blue;width:7.5%;text-align:center'>ASSIGNEE</td>" \
                        "<td style='border:1px solid blue;border-bottom: double blue;width:7.5%;text-align:center'>UPDATED</td>" \
                        "<td style='border:1px solid blue;border-bottom: double blue;width:5%;text-align:center'>STATUS</td>" \
                        "<td style='border:1px solid blue;border-bottom: double blue;width:5%;text-align:center'>PRIORITY</td>" \
                        "<td style='border:1px solid blue;border-bottom: double blue;width:5%;text-align:center'>SEVERITY</td>" \
                        "</tr></thead><tbody>"

        for result in data['results']:

            try:
                assignee_flag = False
                # strip out conflicting HTML tags in descriptions
                description_temp = str(result["description"])
                description = str(description_temp).replace("<", "&lt;").replace("\"", "&quot;").replace("&", "&amp;").replace("'","&apos;").replace(">","&gt;")
                ticketid = str(result["id"])

                # Getting IDs of requesters to be processed
                requesterid = str(result["requester_id"])
            except:
                botlog.LogSymphonyInfo("Cannot get ticket info")

            try:
                # To get the name of the requester given the requesterID
                conn.request("GET", "/api/v2/users/" + str(requesterid), headers=headers)
                res = conn.getresponse()
                userRequesterId = res.read()
                tempUserRequester = str(userRequesterId.decode('utf-8'))
                data = json.dumps(tempUserRequester, indent=2)
                data_dict = ast.literal_eval(data)
                d_req = json.loads(data_dict)
                req_name = str(d_req["user"]["name"])
                requesterName = req_name
            except:
                try:
                    botlog.LogSymphonyInfo("Inside second try for requester name value")
                    # To get the name of the requester given the requesterID
                    conn.request("GET", "/api/v2/users/" + str(requesterid), headers=headers)
                    res = conn.getresponse()
                    userRequesterId = res.read()
                    tempUserRequester = str(userRequesterId.decode('utf-8'))
                    data = json.dumps(tempUserRequester, indent=2)
                    data_dict = ast.literal_eval(data)
                    d_req = json.loads(data_dict)
                    req_name = str(d_req["user"]["name"])
                    requesterName = req_name
                except:
                    requesterName = "N/A"
                    botlog.LogSymphonyInfo("Cannot get requester info")

            # Getting IDs of assignee to be processed
            try:
                assigneeid = str(result["assignee_id"])

                # To get the name of the assignee given the assigneeID
                conn.request("GET", "/api/v2/users/" + str(assigneeid), headers=headers)
                res = conn.getresponse()
                userAssigneeId = res.read()
                tempUserAssignee = str(userAssigneeId.decode('utf-8'))

                data = json.dumps(tempUserAssignee, indent=2)
                data_dict = ast.literal_eval(data)
                d_assign = json.loads(data_dict)
                assign_name = str(d_assign["user"]["name"])
                assigneeName = assign_name

            except:
                try:
                    botlog.LogSymphonyInfo("Inside second try for assignee name value")
                    assigneeid = str(result["assignee_id"])

                    # To get the name of the assignee given the assigneeID
                    conn.request("GET", "/api/v2/users/" + str(assigneeid), headers=headers)
                    res = conn.getresponse()
                    userAssigneeId = res.read()
                    tempUserAssignee = str(userAssigneeId.decode('utf-8'))

                    data = json.dumps(tempUserAssignee, indent=2)
                    data_dict = ast.literal_eval(data)
                    d_assign = json.loads(data_dict)
                    assign_name = str(d_assign["user"]["name"])
                    assigneeName = assign_name

                except:
                    assigneeName = "N/A"
                    assignee_flag = True

            requesterTicket = (_configDef['zdesk_config']['zdesk_link']) + str(ticketid) + "/requester/requested_tickets"
            assigneeTicket = (_configDef['zdesk_config']['zdesk_url']) + "/agent/users/" + str(assigneeid) + "/assigned_tickets"

            ticketSubject_temp = str(result["subject"])
            ticketSubject = str(ticketSubject_temp).replace("<", "&lt;").replace("\"", "&quot;").replace("&", "&amp;").replace("'","&apos;").replace(">","&gt;")

            if assignee_flag:
                table_body += "<tr>" \
                              "<td style='border:1px solid black;text-align:left'>" + str(ticketSubject) + "</td>" \
                              "<td style='border:1px solid black;text-align:left'>" + str(description) + "</td>" \
                              "<td style='border:1px solid black;text-align:center'><a href=\"" + (_configDef['zdesk_config']['zdesk_link']) + str(ticketid) + "\">" + str(ticketid) + "</a></td>" \
                              "<td style='border:1px solid black;text-align:center'><a href=\"" + str(requesterTicket) + "\">" + str(requesterName) + "</a></td>" \
                              "<td style='border:1px solid black;text-align:center'>" + str(result["created_at"]).replace("T", " ").replace("Z", "") + "</td>" \
                              "<td style='border:1px solid black;text-align:center'>" + str(assigneeName) + "</td>" \
                              "<td style='border:1px solid black;text-align:center'>" + str(result["updated_at"]).replace("T", " ").replace("Z", "") + "</td>" \
                              "<td style='border:1px solid black;text-align:center'>" + str(result["status"]) + "</td>"

            else:
                table_body += "<tr>" \
                              "<td style='border:1px solid black;text-align:left'>" + str(ticketSubject) + "</td>" \
                              "<td style='border:1px solid black;text-align:left'>" + str(description) + "</td>" \
                              "<td style='border:1px solid black;text-align:center'><a href=\"" + (_configDef['zdesk_config']['zdesk_link']) + str(ticketid) + "\">" + str(ticketid) + "</a></td>" \
                              "<td style='border:1px solid black;text-align:center'><a href=\"" + str(requesterTicket) + "\">" + str(requesterName) + "</a></td>" \
                              "<td style='border:1px solid black;text-align:center'>" + str(result["created_at"]).replace("T", " ").replace("Z", "")+ "</td>" \
                              "<td style='border:1px solid black;text-align:center'><a href=\"" + str(assigneeTicket) + "\">" + str(assigneeName) + "</a></td>" \
                              "<td style='border:1px solid black;text-align:center'>" + str(result["updated_at"]).replace("T", " ").replace("Z", "") + "</td>" \
                              "<td style='border:1px solid black;text-align:center'>" + str(result["status"]) + "</td>"

            try:
                table_body += "<td style='border:1px solid black;text-align:center'>" + result["priority"] + "</td>"
            except:
                table_body += "<td style='border:1px solid black;text-align:center'>Not set</td>"

            if (len(result["tags"])) == 0:
                noTag = True
            else:
                noTag = False

            notSet = True
            if noTag:
                table_body += "<td style='border:1px solid black;text-align:center'>Not set</td>"
                notSet = False

            sev = ""
            for index_tags in range(len(result["tags"])):
                tags = str((result["tags"][index_tags]))

                if tags.startswith("severity_1"):
                    sev = "Severity 1"
                    notSet = False
                    table_body += "<td style='border:1px solid black;text-align:center'>" + str(sev) + " " + "</td>"
                elif tags.startswith("severity_2"):
                    sev = "Severity 2"
                    notSet = False
                    table_body += "<td style='border:1px solid black;text-align:center'>" + str(sev) + " " + "</td>"
                elif tags.startswith("severity_3"):
                    sev = "Severity 3"
                    notSet = False
                    table_body += "<td style='border:1px solid black;text-align:center'>" + str(sev) + " " + "</td>"
                elif tags.startswith("severity_4"):
                    sev = "Severity 4"
                    notSet = False
                    table_body += "<td style='border:1px solid black;text-align:center'>" + str(sev) + " " + "</td>"

            if notSet:
                table_body += "<td style='border:1px solid black;text-align:center'>Not Set</td>"
                notSet = False

            table_body += "</tr>"

        try:
            ticketid = str(result["id"])
        except:
            return messageDetail.ReplyToChat("You did not enter a valid search or no entry found for that search")

        table_body += "</tbody></table>"

        reply = table_header + table_body

        return messageDetail.ReplyToChatV2_noBotLog("<card iconSrc =\"https://thumb.ibb.co/csXBgU/Symphony2018_App_Icon_Mobile.png\" accent=\"tempo-bg-color--blue\"><header>Please find the result below</header><body>" + reply + "</body></card>")

    # else:
    #     return messageDetail.ReplyToChat("You aren't authorised to use this command.")
    except:
        return messageDetail.ReplyToChat("I am sorry, I was working on a different task, can you please retry")

#############################
########   SHOW   ###########
#############################
def showZD (messageDetail):
    botlog.LogSymphonyInfo("##############################")
    botlog.LogSymphonyInfo("Bot Call: Show Zendesk ticket")
    botlog.LogSymphonyInfo("##############################")

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
        d_org = json.loads(str(dataRender))

        for index_org in range(len(d_org["users"])):
            firstName = str(d_org["users"][index_org]["firstName"])
            lastName = str(d_org["users"][index_org]["lastName"])
            displayName = str(d_org["users"][index_org]["displayName"])
            companyName = str(d_org["users"][index_org]["company"])
            userID = str(d_org["users"][index_org]["id"])

            #################################################

            try:
                emailAddress = str(d_org["users"][index_org]["emailAddress"])
                botlog.LogSymphonyInfo("User is connected: " + emailAddress)
                emailZendesk = emailAddress
                connectionRequired = False
            except:
                connectionRequired = True

            # if connectionRequired:

            data_lenght = len(dataComp)

            if data_lenght > 450:
                try:
                    #print("inside > 450")
                    query = "type:user " + emailAddress
                except:
                    query = "type:user " + firstName + " " + lastName
                botlog.LogSymphonyInfo(query)
            elif data_lenght < 450:
                try:
                    #print("inside < 450")
                    #query = "type:user " + emailAddress + " organization:" + companyName
                    query = "type:user " + emailAddress
                except:
                    #query = "type:user " + firstName + " " + lastName + " organization:" + companyName
                    query = "type:user " + firstName + " " + lastName
                botlog.LogSymphonyInfo(query)
            else:
                return messageDetail.ReplyToChat("No user information available")

                botlog.LogSymphonyInfo(query)
            results = zendesk.search(query=query)
            #print(results)

            if str(results).startswith(
                    "{'results': [], 'facets': None, 'next_page': None, 'previous_page': None, 'count': 0}"):
                return messageDetail.ReplyToChat(
                    "This user does not exist on Zendesk, the name is misspelled or does not belong to this organisation.")
            elif str(results).startswith(
                    "{'results': [], 'facets': {'type': {'entry': 0, 'ticket': 0, 'organization': 0, 'user': 0, 'article': 0, 'group': 0}}, 'next_page': None, 'previous_page': None, 'count': 0}"):
                return messageDetail.ReplyToChat(
                    "This organisation/company does not exist in Zendesk or name is misspelled.")
            else:

                data = json.dumps(results, indent=2)
                d = json.loads(data)

                for index in range(len(d["results"])):
                    # name = d["results"][index]["name"]
                    # email = str(d["results"][index]["email"])
                    role = str(d["results"][index]["role"])
                    #print(role)
                    botlog.LogSymphonyInfo("The calling user is a Zendesk " + role)

                    if role == "Administrator" or role == "admin" or role == "Agent" or role == "agent":
                        isAllowed = True
                        #print(role)
                        botlog.LogSymphonyInfo("Role of the calling user: " + role)

            #################################################

            botlog.LogSymphonyInfo(str(firstName) + " " + str(lastName) + " (" + str(displayName) + ") from Company/Pod name: " + str(companyName) + " with UID: " + str(userID))
            #callerCheck = (str(firstName) + " " + str(lastName) + " - " + str(displayName) + " - " + str(companyName) + " - " + str(userID))

        #if callerCheck in AccessFile and isAllowed:

        showRequest = (messageDetail.Command.MessageText)
        message_split = str(showRequest).split()

        wrongZDID = ""
        table_bodyFull = ""
        reply = ""
        isnext = False

        for index in range(len(message_split)):
            zdid = str(message_split[index]).strip()
            assignee_flag = False

            if len(message_split) == 1:
                try:

                    conn = http.client.HTTPSConnection(_configDef['zdesk_config']['zdesk_api'])

                    headers = {
                        'username': _configDef['zdesk_config']['zdesk_email'] + "/token",
                        'password': _configDef['zdesk_config']['zdesk_password'],
                        'authorization': _configDef['zdesk_config']['zdesk_auth'],
                        'cache-control': "no-cache",
                        'Content-Type': 'application/json',
                        'zdesk_token': True
                    }

                    # base64Encoded = base64.b64encode(bytes((emailZendesk + "/token:" + _configDef['zdesk_config']['zdesk_password']), 'utf-8'))
                    # base64Enc = (base64Encoded.decode("utf-8"))
                    # print(str(base64Enc))
                    # base = ("Basic " + base64Enc)
                    # print(str(base))
                    #
                    # headers = {
                    #     'email_address': emailZendesk + "/token",
                    #     'password': (_configDef['zdesk_config']['zdesk_password']),
                    #     'authorization': base,
                    #     'cache-control': "no-cache",
                    #     'content-type': "application/json"
                    # }

                    conn.request("GET", "/api/v2/tickets/" + zdid + ".json", headers=headers)
                    res = conn.getresponse()
                    data = res.read()
                    request_raw = data.decode("utf-8")

                    ticketDoesNotExist = "{\"error\":\"RecordNotFound","description\":\"Not found\"}"

                    if request_raw.startswith(ticketDoesNotExist):
                        return messageDetail.ReplyToChatV2("<b>There is no such Zendesk ticket number: " + str(zdid) + "</b>")
                    else:
                        isnext = True
                        messageDetail.ReplyToChat("Rendering the data from Zendesk for the requested ticket")
                except:
                    return messageDetail.ReplyToChatV2("<b>There is no such Zendesk ticket number: " + str(zdid) + "</b>")
            else:
                try:

                    conn = http.client.HTTPSConnection(_configDef['zdesk_config']['zdesk_api'])

                    headers = {
                        'username': _configDef['zdesk_config']['zdesk_email'] + "/token",
                        'password': _configDef['zdesk_config']['zdesk_password'],
                        'authorization': _configDef['zdesk_config']['zdesk_auth'],
                        'cache-control': "no-cache",
                        'Content-Type': 'application/json',
                        'zdesk_token': True
                    }

                    conn.request("GET", "/api/v2/tickets/" + zdid + ".json", headers=headers)
                    res = conn.getresponse()
                    data = res.read()
                    request_raw = data.decode("utf-8")

                    ticketDoesNotExist = "{\"error\":\"RecordNotFound","description\":\"Not found\"}"

                    if request_raw.startswith(ticketDoesNotExist):
                        isnext = False
                        wrongID = True
                        wrongZDID += zdid + " "

                    else:
                        isnext = True
                        if index == 1:
                            messageDetail.ReplyToChat("Rendering the data from Zendesk for the requested tickets")
                except:
                    isnext = False
                    wrongID = True
                    wrongZDID += zdid + " "

            if isnext:

                try:
                    data = json.dumps(request_raw, indent=2)
                    data_dict = ast.literal_eval(data)
                    d = json.loads(data_dict)

                    #for index in range(len(request_raw["request"])):
                    # requestid = str(d["request"]["id"])
                    # requeststatus = d["request"]["status"]
                    # requestpriority = d["request"]["priority"]
                    # requestsubject = d["request"]["subject"]
                    # requestdescription_temps = d["request"]["description"]
                    # requestdescription = requestdescription_temps.replace("<", "&lt;")
                    # requestorganization_id = str(d["request"]["organization_id"])
                    # requestrequester_id = str(d["request"]["requester_id"])
                    # #print(requestrequester_id)
                    # requestcreated_at = str(d["request"]["created_at"])
                    # requestupdated_at = str(d["request"]["updated_at"])
                    # requestassignee_id = str(d["request"]["assignee_id"])

                    requestid = str(d["ticket"]["id"])
                    requeststatus = str(d["ticket"]["status"])
                    requestpriority = str(d["ticket"]["priority"])
                    requestsubject_temp = str(d["ticket"]["subject"])
                    requestsubject = str(requestsubject_temp).replace("<", "&lt;").replace("\"", "&quot;").replace("&", "&amp;").replace("'","&apos;").replace(">","&gt;")
                    requestdescription_temps = str(d["ticket"]["description"])
                    requestdescription = str(requestdescription_temps).replace("<", "&lt;").replace("\"", "&quot;").replace("&", "&amp;").replace("'","&apos;").replace(">","&gt;")
                    requestorganization_id = str(d["ticket"]["organization_id"])
                    requestrequester_id = str(d["ticket"]["requester_id"])
                    requestcreated_at = str(d["ticket"]["created_at"]).replace("T", " ").replace("Z", "")
                    requestupdated_at = str(d["ticket"]["updated_at"]).replace("T", " ").replace("Z", "")
                    requestassignee_id = str(d["ticket"]["assignee_id"])
                    requestseverity = str(d["ticket"]["tags"]).replace("[']", "")
                except:
                    return messageDetail.ReplyToChat("Cannot get ticket info for ID " + str(zdid))


                if (len(d["ticket"]["tags"])) == 0:
                    noTag = True
                else:
                    noTag = False

                notSet = True

                if noTag:
                    sev = "Not set"
                    notSet = False

                for index_tags in range(len(d["ticket"]["tags"])):
                    tags = str((d["ticket"]["tags"][index_tags]))

                    if tags.startswith("severity_1"):
                        sev = "Severity 1"
                        notSet = False
                    elif tags.startswith("severity_2"):
                        sev = "Severity 2"
                        notSet = False
                    elif tags.startswith("severity_3"):
                        sev = "Severity 3"
                        notSet = False
                    elif tags.startswith("severity_4"):
                        sev = "Severity 4"
                        notSet = False

                if notSet:
                    sev = "Not Set"
                    notSet = False

                requestseverity = sev

                request_id = str(requestid)
                request_priority = str(requestpriority)
                request_subject = str(requestsubject)
                request_desc = str(requestdescription)
                request_org = str(requestorganization_id)
                request_requestor = str(requestrequester_id)
                request_created = str(requestcreated_at)
                request_updated = str(requestupdated_at)
                request_severity = str(requestseverity)

                try:
                    # To get the name of the requester given the requesterID
                    conn.request("GET", "/api/v2/users/" + request_requestor, headers=headers)
                    res = conn.getresponse()
                    userRequesterId = res.read()
                    tempUserRequester = str(userRequesterId.decode('utf-8'))

                    data = json.dumps(tempUserRequester, indent=2)
                    data_dict = ast.literal_eval(data)
                    d = json.loads(data_dict)
                    req_name = str(d["user"]["name"])
                    requesterName = req_name
                except:
                    try:
                        botlog.LogSymphonyInfo("Inside second try for requester name in showZD")
                        # To get the name of the requester given the requesterID
                        conn.request("GET", "/api/v2/users/" + request_requestor, headers=headers)
                        res = conn.getresponse()
                        userRequesterId = res.read()
                        tempUserRequester = str(userRequesterId.decode('utf-8'))

                        data = json.dumps(tempUserRequester, indent=2)
                        data_dict = ast.literal_eval(data)
                        d = json.loads(data_dict)
                        req_name = str(d["user"]["name"])
                        requesterName = req_name
                    except:
                        requesterName = "N/A"
                        messageDetail.ReplyToChat("Cannot get requester info")

                # Getting IDs of requester and assignee to be processed
                try:
                    request_assignee = str(requestassignee_id)

                    # To get the name of the assignee given the assigneeID
                    conn.request("GET", "/api/v2/users/" + request_assignee, headers=headers)
                    res = conn.getresponse()
                    userAssigneeId = res.read()
                    tempUserAssignee = str(userAssigneeId.decode('utf-8'))

                    data = json.dumps(tempUserAssignee, indent=2)
                    data_dict = ast.literal_eval(data)
                    d = json.loads(data_dict)
                    assign_name = str(d["user"]["name"])
                    assigneeName = assign_name
                except:
                    try:
                        botlog.LogSymphonyInfo("Inside second try for assginee name value in ShowZD")
                        request_assignee = str(requestassignee_id)

                        # To get the name of the assignee given the assigneeID
                        conn.request("GET", "/api/v2/users/" + request_assignee, headers=headers)
                        res = conn.getresponse()
                        userAssigneeId = res.read()
                        tempUserAssignee = str(userAssigneeId.decode('utf-8'))

                        data = json.dumps(tempUserAssignee, indent=2)
                        data_dict = ast.literal_eval(data)
                        d = json.loads(data_dict)
                        assign_name = str(d["user"]["name"])
                        assigneeName = assign_name

                    except:
                        assigneeName = "N/A"
                        assignee_flag = True

                requesterTicket = (_configDef['zdesk_config']['zdesk_link']) + str(request_id) + "/requester/requested_tickets"
                assigneeTicket = (_configDef['zdesk_config']['zdesk_url']) + "/agent/users/" + str(request_assignee) + "/assigned_tickets"
                OrgTicket = (_configDef['zdesk_config']['zdesk_link']) + str(request_id) + "/organization/tickets"

                try:
                    # Convert the Zendesk ID to company name
                    conn.request("GET", "/api/v2/users/" + str(requestrequester_id) + "/organizations.json", headers=headers)
                    res = conn.getresponse()
                    companyID = res.read()
                    compNameRaw = str(companyID.decode("utf-8"))

                    data = json.dumps(compNameRaw, indent=2)
                    data_dict = ast.literal_eval(data)
                    d = json.loads(data_dict)
                    org_Name = str(d["organizations"][0]["name"])
                    orgName = org_Name
                except:
                    try:
                        botlog.LogSymphonyInfo("Inside Second try for Org name value")
                        # Convert the Zendesk ID to company namer
                        conn.request("GET", "/api/v2/users/" + str(requestrequester_id) + "/organizations.json",
                                     headers=headers)
                        res = conn.getresponse()
                        companyID = res.read()
                        compNameRaw = str(companyID.decode("utf-8"))

                        data = json.dumps(compNameRaw, indent=2)
                        data_dict = ast.literal_eval(data)
                        d = json.loads(data_dict)
                        org_Name = str(d["organizations"][0]["name"])
                        orgName = org_Name
                    except:
                        orgName = "N/A"
                        messageDetail.ReplyToChat("Cannot get company info")

                table_body = ""
                table_header = "<table style='border-collapse:collapse;border:2px solid black;table-layout:auto;width:100%;box-shadow: 5px 5px'><thead><tr style='background-color:#4D94FF;color:#ffffff;font-size:1rem' class=\"tempo-text-color--white tempo-bg-color--black\">" \
                                   "<td style='width:20%;border:1px solid blue;border-bottom: double blue;text-align:center'>SUBJECT</td>" \
                                   "<td style='width:30%;border:1px solid blue;border-bottom: double blue;text-align:center'>DESCRIPTION</td>" \
                                   "<td style='width:2.5%;border:1px solid blue;border-bottom: double blue;text-align:center'>ID</td>" \
                                   "<td style='width:3%;border:1px solid blue;border-bottom: double blue;text-align:center'>STATUS</td>" \
                                   "<td style='width:3%;border:1px solid blue;border-bottom: double blue;text-align:center'>PRIORITY</td>" \
                                   "<td style='width:3.5%;border:1px solid blue;border-bottom: double blue;text-align:center'>SEVERITY</td>" \
                                   "<td style='width:5%;border:1px solid blue;border-bottom: double blue;text-align:center'>COMPANY</td>" \
                                   "<td style='width:7%;border:1px solid blue;border-bottom: double blue;text-align:center'>REQUESTER</td>" \
                                   "<td style='width:7%;border:1px solid blue;border-bottom: double blue;text-align:center'>CREATED</td>" \
                                   "<td style='width:7%;border:1px solid blue;border-bottom: double blue;text-align:center'>UPDATED</td>" \
                                   "<td style='width:7%;border:1px solid blue;border-bottom: double blue;text-align:center'>ASSIGNEE</td>" \
                                   "</tr></thead><tbody>"

                if assignee_flag:

                    table_body += "<tr>" \
                                  "<td style='border:1px solid black;text-align:left'>" + str(request_subject) + "</td>" \
                                  "<td style='border:1px solid black;text-align:left'>" + str(request_desc) + "</td>" \
                                  "<td style='border:1px solid black;text-align:center'><a href=\"" + (_configDef['zdesk_config']['zdesk_link']) + str(request_id) + "\">" + str(request_id) + "</a></td>" \
                                  "<td style='border:1px solid black;text-align:center'>" + str(requeststatus) + "</td>" \
                                  "<td style='border:1px solid black;text-align:center'>" + str(request_priority) + "</td>" \
                                  "<td style='border:1px solid black;text-align:center'>" + str(request_severity) + "</td>" \
                                  "<td style='border:1px solid black;text-align:center'><a href=\"" + str(OrgTicket) + "\">" + str(orgName) + "</a></td>" \
                                  "<td style='border:1px solid black;text-align:center'><a href=\"" + str(requesterTicket) + "\">" + str(requesterName) + "</a></td>" \
                                  "<td style='border:1px solid black;text-align:center'>" + str(request_created) + "</td>" \
                                  "<td style='border:1px solid black;text-align:center'>" + str(request_updated) + "</td>" \
                                  "<td style='border:1px solid black;text-align:center'>" + str(assigneeName) + "</td>" \
                                  "</tr>" \

                else:
                    table_body += "<tr>" \
                                  "<td style='border:1px solid black;text-align:left'>" + str(request_subject) + "</td>" \
                                  "<td style='border:1px solid black;text-align:left'>" + str(request_desc) + "</td>" \
                                  "<td style='border:1px solid black;text-align:center'><a href=\"" + (_configDef['zdesk_config']['zdesk_link']) + str(request_id) + "\">" + str(request_id) + "</a></td>" \
                                  "<td style='border:1px solid black;text-align:center'>" + requeststatus + "</td>" \
                                  "<td style='border:1px solid black;text-align:center'>" + str(request_priority) + "</td>" \
                                  "<td style='border:1px solid black;text-align:center'>" + str(request_severity) + "</td>" \
                                  "<td style='border:1px solid black;text-align:center'><a href=\"" + str(OrgTicket) + "\">" + str(orgName) + "</a></td>" \
                                  "<td style='border:1px solid black;text-align:center'><a href=\"" + str(requesterTicket) + "\">" + str(requesterName) + "</a></td>" \
                                  "<td style='border:1px solid black;text-align:center'>" + str(request_created) + "</td>" \
                                  "<td style='border:1px solid black;text-align:center'>" + str(request_updated) + "</td>" \
                                  "<td style='border:1px solid black;text-align:center'><a href=\"" + str(assigneeTicket) + "\">" + str(assigneeName) + "</a></td>" \
                                  "</tr>" \

                table_bodyFull += str(table_body)
                reply = table_header + table_bodyFull + "</tbody></table>"

        try:
            if wrongID:
                if index == len(message_split) - 1:
                    return messageDetail.ReplyToChatV2(reply + "<p></p><b>There is no such Zendesk ticket number: " + wrongZDID + "</b>")
        except:
            if index == len(message_split) - 1:
                #messageDetail.ReplyToChatV2(reply)
                messageDetail.ReplyToChatV2_noBotLog("<card iconSrc =\"https://thumb.ibb.co/csXBgU/Symphony2018_App_Icon_Mobile.png\" accent=\"tempo-bg-color--blue\"><header>Please find the result below</header><body>" + reply + "</body></card>")

        # else:
        #     return messageDetail.ReplyToChat("You aren't authorised to use this command.")

    except:
        return messageDetail.ReplyToChat("I am sorry, I was working on a different task, can you please retry")


def showTicketComments (messageDetail):
    botlog.LogSymphonyInfo("######################################")
    botlog.LogSymphonyInfo("Bot Call: Show Zendesk ticket comments")
    botlog.LogSymphonyInfo("######################################")

    try:
        privateComment = False
        isAllowed = ""
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
        d_org = json.loads(str(dataRender))

        for index_org in range(len(d_org["users"])):
            firstName = str(d_org["users"][index_org]["firstName"])
            lastName = str(d_org["users"][index_org]["lastName"])
            displayName = str(d_org["users"][index_org]["displayName"])
            companyName = str(d_org["users"][index_org]["company"])
            userID = str(d_org["users"][index_org]["id"])

            #################################################

            try:
                emailAddress = str(d_org["users"][index_org]["emailAddress"])
                #print("User is connected: " + emailAddress)
                emailZendesk = emailAddress
                connectionRequired = False
            except:
                connectionRequired = True

        #if connectionRequired:

            data_lenght = len(dataComp)

            if data_lenght > 450:
                try:
                    #print("inside > 450")
                    query = "type:user " + emailAddress
                except:
                    query = "type:user " + firstName + " " + lastName
                botlog.LogSymphonyInfo(query)
            elif data_lenght < 450:
                try:
                    #print("inside < 450")
                    #query = "type:user " + emailAddress + " organization:" + companyName
                    query = "type:user " + emailAddress
                except:
                    #query = "type:user " + firstName + " " + lastName + " organization:" + companyName
                    query = "type:user " + firstName + " " + lastName
                botlog.LogSymphonyInfo(query)
            else:
                return messageDetail.ReplyToChat("No user information available")

                botlog.LogSymphonyInfo(query)
            results = zendesk.search(query=query)
            #print(results)

            if str(results).startswith(
                    "{'results': [], 'facets': None, 'next_page': None, 'previous_page': None, 'count': 0}"):
                return messageDetail.ReplyToChat(
                    "This user does not exist on Zendesk, the name is misspelled or does not belong to this organisation.")
            elif str(results).startswith(
                    "{'results': [], 'facets': {'type': {'entry': 0, 'ticket': 0, 'organization': 0, 'user': 0, 'article': 0, 'group': 0}}, 'next_page': None, 'previous_page': None, 'count': 0}"):
                return messageDetail.ReplyToChat(
                    "This organisation/company does not exist in Zendesk or name is misspelled.")
            else:

                data = json.dumps(results, indent=2)
                d = json.loads(data)

                for index in range(len(d["results"])):
                    #name = d["results"][index]["name"]
                    #email = str(d["results"][index]["email"])
                    role = str(d["results"][index]["role"])
                    #print(role)
                    #botlog.LogSymphonyInfo("The calling user is a Zendesk " + role)

                    if role == "Administrator" or role == "admin" or role == "Agent" or role == "agent":
                        isAllowed = True
                        #print(role)
                        botlog.LogSymphonyInfo("Role of the calling user: " + role)

            #################################################

        botlog.LogSymphonyInfo(str(firstName) + " " + str(lastName) + " (" + str(displayName) + ") from Company/Pod name: " + str(companyName) + " with UID: " + str(userID))
        callerCheck = (str(firstName) + " " + str(lastName) + " - " + str(displayName) + " - " + str(companyName) + " - " + str(userID))

        if callerCheck in AccessFile and isAllowed:
            botlog.LogSymphonyInfo("Inside access list: User is Agent with the bot and " + role + " on Zendesl")

            showRequest = (messageDetail.Command.MessageText)
            message_split = str(showRequest).split()
            try:
                ticketID = str(message_split[0])
            except:
                return messageDetail.ReplyToChat("Please use this format: <b>/showTicketComments ticketid</b>")

            ## Calling user is Agent on Zendesk and also added to the Bot list as Agent

            # base64Encoded = base64.b64encode(bytes((emailZendesk + "/token:" + _configDef['zdesk_config']['zdesk_password']), 'utf-8'))
            # base64Enc = (base64Encoded.decode("utf-8"))
            # #print(str(base64Enc))
            # base = ("Basic " + base64Enc)
            # #print(str(base))
            #
            # headers = {
            #     'email_address': emailZendesk + "/token",
            #     'password': (_configDef['zdesk_config']['zdesk_password']),
            #     'authorization': base,
            #     'cache-control': "no-cache",
            #     'content-type': "application/json"
            # }

            ###############################

            ## Not sure yet why but some tickets cannot be viewed as Agent but need Admin access on Zendesk
            ## If access is only given as agent, this will not work (555) and return a forbidden message but work for some ticket ids (560)
            headers = {
                'username': _configDef['zdesk_config']['zdesk_email'] + "/token",
                'password': _configDef['zdesk_config']['zdesk_password'],
                'authorization': _configDef['zdesk_config']['zdesk_auth'],
                'cache-control': "no-cache",
                'Content-Type': 'application/json',
            }

            url = _configDef['zdesk_config']['zdesk_url'] + "/api/v2/tickets/" + ticketID + "/comments"

            response = requests.request("GET", url, headers=headers)

            data = response.json()
            #print(data)

            invalidTicket = "{'error': 'RecordNotFound', 'description': 'Not found'}"
            invalid = "{'error': {'title': 'Invalid attribute', 'message': 'You passed an invalid value for the ticket_id attribute. Invalid parameter: ticket_id must be an integer'}}"
            forbidden = "{'error': {'title': 'Forbidden', 'message': 'You do not have access to this page. Please contact the account owner of this help desk for further help.'}}"

            if str(data).startswith(invalidTicket):
                return messageDetail.ReplyToChatV2("This Ticket ID, " + ticketID + " does not exist on Zendesk")

            if str(data).startswith(invalid):
                return messageDetail.ReplyToChatV2("Please use this format: <b>/showTicketComments ticketid</b>")

            if str(data).startswith(forbidden):
                return messageDetail.ReplyToChatV2("To view the comments on this ticket, you need to be Zendesk Admin, not yet sure why")

            messageDetail.ReplyToChat("Rendering all the comments/updates for Zendesk Ticket: <b>" + ticketID + "</b>, please wait.")

            table_body = ""
            table_header = "<table style='border-collapse:collapse;border:2px solid black;table-layout:auto;width:100%;box-shadow: 5px 5px'><thead><tr style='background-color:#4D94FF;color:#ffffff;font-size:1rem' class=\"tempo-text-color--white tempo-bg-color--black\">" \
                           "<td style='width:60%;border:1px solid blue;border-bottom: double blue;text-align:center'>COMMENT</td>" \
                           "<td style='width:10%;border:1px solid blue;border-bottom: double blue;text-align:center'>AUTHOR</td>" \
                           "<td style='width:10%;border:1px solid blue;border-bottom: double blue;text-align:center'>TYPE</td>" \
                           "<td style='width:10%;border:1px solid blue;border-bottom: double blue;text-align:center'>ATTACHMENT</td>"\
                           "<td style='width:10%;border:1px solid blue;border-bottom: double blue;text-align:center'>CREATED AT</td>" \
                           "</tr></thead><tbody>"

            file = ""
            full_file =""
            hasFile = True
            for result in data['comments']:
                author_id = str(result["author_id"])
                body = str(result["body"]).replace("<", "&lt;").replace("\"", "&quot;").replace("&", "&amp;").replace("'","&apos;").replace(">","&gt;")
                privacy = str(result["public"])

                if str(privacy) == "False":
                    privateComment = True
                    public = "Private"
                else:
                    #privateComment = False
                    public = "Public"

                attachments = str(result["attachments"])

                ####################################

                data_dict = ast.literal_eval(attachments)
                dataRender = json.dumps(data_dict, indent=2)
                d = json.loads(dataRender)
                #print("d: " + str(d))

                if str(d) == "[]":
                    full_file = "No Attachment"
                    hasFile = False

                else:
                    full_file = ""
                    for index in range(len(d)):

                        if hasFile:
                            botlog.LogSymphonyInfo("No attachment")
                        else:
                            file_name = d[index]["file_name"]
                            #print(str(file_name))
                            content_url = d[index]["content_url"]
                            #print(str(content_url))
                            sizefile = d[index]["size"]
                            file = "<a href=\"" + str(content_url) + "\">" + str(file_name) + "</a> (" + size(sizefile) + ")"
                            full_file += file + " "
                            #print(full_file)

                ####################################

                created_at = str(result["created_at"]).replace("T", " ").replace("Z", "")

                try:
                    # To get the name of the requester given the requesterID
                    conn.request("GET", "/api/v2/users/" + author_id, headers=headers)
                    res = conn.getresponse()
                    userRequesterId = res.read()
                    tempUserRequester = str(userRequesterId.decode('utf-8'))

                    data = json.dumps(tempUserRequester, indent=2)
                    data_dict = ast.literal_eval(data)
                    d = json.loads(data_dict)
                    req_name = str(d["user"]["name"])
                    author_id = req_name
                except:
                    try:
                        botlog.LogSymphonyInfo("inside second try for requester name value inside showTicketComments")
                        # To get the name of the requester given the requesterID
                        conn.request("GET", "/api/v2/users/" + author_id, headers=headers)
                        res = conn.getresponse()
                        userRequesterId = res.read()
                        tempUserRequester = str(userRequesterId.decode('utf-8'))

                        data = json.dumps(tempUserRequester, indent=2)
                        data_dict = ast.literal_eval(data)
                        d = json.loads(data_dict)
                        req_name = str(d["user"]["name"])
                        author_id = req_name
                    except:
                        author_id = "N/A"


                    #messageDetail.ReplyToChat("Cannot get requester info")

                table_body += "<tr>" \
                              "<td style='border:1px solid black;text-align:left'>" + str(body) + "</td>" \
                              "<td style='border:1px solid black;text-align:center'>" + str(author_id) + "</td>" \
                              "<td style='border:1px solid black;text-align:center'>" + str(public) + "</td>" \
                              "<td style='border:1px solid black;text-align:center'>" + str(full_file) + "</td>"\
                              "<td style='border:1px solid black;text-align:center'>" + str(created_at) + "</td>" \
                              "</tr>"

            table_body += "</tbody></table>"

            reply = table_header + table_body
            #print(privateComment)
            if privateComment:
                messageDetail.ReplyToChatV2_noBotLog("There is 1 or more private comments in this Zendesk Ticket. For confidentiality reasons, I will respond to you in a 1:1 chat.")
                return messageDetail.ReplyToSenderv2_noBotLog(
                    "<card iconSrc =\"https://thumb.ibb.co/csXBgU/Symphony2018_App_Icon_Mobile.png\" accent=\"tempo-bg-color--blue\"><header>Please find the comments below</header><body>" + reply + "</body></card>")
            else:
                return messageDetail.ReplyToChatV2_noBotLog("<card iconSrc =\"https://thumb.ibb.co/csXBgU/Symphony2018_App_Icon_Mobile.png\" accent=\"tempo-bg-color--blue\"><header>Please find the comments below</header><body>" + reply + "</body></card>")

        else:

            botlog.LogSymphonyInfo("The calling user is either not added to the Zendesk Agent List or he/she is not an Agent on the Zendesk Instance.")
            showRequest = (messageDetail.Command.MessageText)
            message_split = str(showRequest).split()
            try:
                ticketID = str(message_split[0])
            except:
                return messageDetail.ReplyToChat("Please use this format: <b>/showTicketComments ticketid</b>")

    ########################

            ## if using _configDef['ZendeskBot'] need to add it to the configDef part in main config.json:
            ##   "ZendeskBot": "ZendeskBot@ZendeskBot.com",

            ## This is used to simulate an agent call as end user, this user is not in the Bot Agent List (access file)
            #base64Encoded = base64.b64encode(bytes((_configDef['ZendeskBot'] + "/token:" + _configDef['zdesk_config']['zdesk_password']), 'utf-8'))
            # base64Encoded = base64.b64encode(bytes((emailZendesk + "/token:" + _configDef['zdesk_config']['zdesk_password']), 'utf-8'))
            # base64Enc = (base64Encoded.decode("utf-8"))
            # print(str(base64Enc))
            # base = ("Basic " + base64Enc)
            # print(str(base))
            #
            # headers = {
            #     'email_address': emailZendesk + "/token",
            #     'password': (_configDef['zdesk_config']['zdesk_password']),
            #     'authorization': base,
            #     'cache-control': "no-cache",
            #     'content-type': "application/json"
            # }
    #######################

            headers = {
                'username': _configDef['zdesk_config']['zdesk_email'] + "/token",
                'password': _configDef['zdesk_config']['zdesk_password'],
                'authorization': _configDef['zdesk_config']['zdesk_auth'],
                'cache-control': "no-cache",
                'Content-Type': 'application/json',
            }

            url = _configDef['zdesk_config']['zdesk_url'] + "/api/v2/requests/" + ticketID + "/comments"

            response = requests.request("GET", url, headers=headers)

            data = response.json()
            #print(data)

            invalid = "{'error': {'title': 'Invalid attribute', 'message': 'You passed an invalid value for the ticket_id attribute. Invalid parameter: ticket_id must be an integer'}}"

            invalidReq = "{'error': {'title': 'Forbidden', 'message': 'You do not have access to this page. Please contact the account owner of this help desk for further help.'}}"

            if str(data).startswith(invalid):
                return messageDetail.ReplyToChat("Please use this format: <b>/showTicketComments ticketid</b>")

            if str(data).startswith(invalidReq):
                return messageDetail.ReplyToChat("You are not not a Zendesk Agent or not part of the Zendesk Agent List")

            messageDetail.ReplyToChatV2("You are not a <b>Zendesk Agent</b> or not part of the Bot <b>Zendesk Agent List</b>, the following will show all <b>public updates</b>. Rendering the comments for Zendesk Ticket: <b>" + ticketID + "</b> as an <b>End-User</b>, please wait.")

            table_body = ""
            table_header = "<table style='border-collapse:collapse;border:2px solid black;table-layout:auto;width:100%;box-shadow: 5px 5px'><thead><tr style='background-color:#4D94FF;color:#ffffff;font-size:1rem' class=\"tempo-text-color--white tempo-bg-color--black\">" \
                           "<td style='width:60%;border:1px solid blue;border-bottom: double blue;text-align:center'>COMMENT</td>" \
                           "<td style='width:10%;border:1px solid blue;border-bottom: double blue;text-align:center'>AUTHOR</td>" \
                           "<td style='width:10%;border:1px solid blue;border-bottom: double blue;text-align:center'>PUBLIC</td>" \
                           "<td style='width:10%;border:1px solid blue;border-bottom: double blue;text-align:center'>ATTACHMENT</td>" \
                           "<td style='width:10%;border:1px solid blue;border-bottom: double blue;text-align:center'>CREATED AT</td>" \
                           "</tr></thead><tbody>"

            file = ""
            full_file =""
            hasFile = True
            for result in data['comments']:
                author_id = str(result["author_id"])
                body = str(result["body"]).replace("<", "&lt;").replace("\"", "&quot;").replace("&", "&amp;").replace("'","&apos;").replace(">","&gt;")
                public = str(result["public"])
                attachments = str(result["attachments"])

                ####################################

                data_dict = ast.literal_eval(attachments)
                dataRender = json.dumps(data_dict, indent=2)
                d = json.loads(dataRender)
                #print("d: " + str(d))

                if str(d) == "[]":
                    full_file = "No Attachment"
                    hasFile = False

                else:
                    full_file = ""
                    for index in range(len(d)):

                        if hasFile:
                            botlog.LogSymphonyInfo("No attachment")
                        else:
                            file_name = d[index]["file_name"]
                            #print(str(file_name))
                            content_url = d[index]["content_url"]
                            #print(str(content_url))
                            sizefile = d[index]["size"]
                            file = "<a href=\"" + str(content_url) + "\">" + str(file_name) + "</a> (" + size(sizefile)+")"
                            full_file += file + " "
                            #print(full_file)

                ####################################

                created_at = str(result["created_at"]).replace("T", " ").replace("Z", "")

                try:
                    # To get the name of the requester given the requesterID
                    conn.request("GET", "/api/v2/users/" + author_id, headers=headers)
                    res = conn.getresponse()
                    userRequesterId = res.read()
                    tempUserRequester = str(userRequesterId.decode('utf-8'))

                    data = json.dumps(tempUserRequester, indent=2)
                    data_dict = ast.literal_eval(data)
                    d = json.loads(data_dict)
                    req_name = str(d["user"]["name"])
                    author_id = req_name
                except:
                    try:
                        botlog.LogSymphonyInfo("Inside second try for author name value in showTicketComments")
                        # To get the name of the requester given the requesterID
                        conn.request("GET", "/api/v2/users/" + author_id, headers=headers)
                        res = conn.getresponse()
                        userRequesterId = res.read()
                        tempUserRequester = str(userRequesterId.decode('utf-8'))

                        data = json.dumps(tempUserRequester, indent=2)
                        data_dict = ast.literal_eval(data)
                        d = json.loads(data_dict)
                        req_name = str(d["user"]["name"])
                        author_id = req_name
                    except:
                        author_id = "N/A"

                    # messageDetail.ReplyToChat("Cannot get requester info")

                table_body += "<tr>" \
                              "<td style='border:1px solid black;text-align:left'>" + str(body) + "</td>" \
                              "<td style='border:1px solid black;text-align:center'>" + str(author_id) + "</td>" \
                              "<td style='border:1px solid black;text-align:center'>" + str(public) + "</td>" \
                              "<td style='border:1px solid black;text-align:center'>" + str(full_file) + "</td>" \
                              "<td style='border:1px solid black;text-align:center'>" + str(created_at) + "</td>" \
                              "</tr>"

            table_body += "</tbody></table>"

            reply = table_header + table_body

            return messageDetail.ReplyToChatV2_noBotLog(
                "<card iconSrc =\"https://thumb.ibb.co/csXBgU/Symphony2018_App_Icon_Mobile.png\" accent=\"tempo-bg-color--blue\"><header>Please find the comments below</header><body>" + reply + "</body></card>")
    except:
        return messageDetail.ReplyToChat("I am sorry, I was working on a different task, can you please retry")


#############################
########   USER   ###########
#############################
def userZD(messageDetail):
    botlog.LogSymphonyInfo("###########################")
    botlog.LogSymphonyInfo("Bot Call: Find Zendesk User")
    botlog.LogSymphonyInfo("###########################")

    try:
        isAllowed = False
        commandCallerUID = messageDetail.FromUserId

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

            #################################################

            try:
                emailAddress = str(d_org["users"][index_org]["emailAddress"])
                # print("User is connected: " + emailAddress)
                emailZendesk = emailAddress
                connectionRequired = False
            except:
                connectionRequired = True

            # if connectionRequired:

            data_lenght = len(dataComp)

            if data_lenght > 450:
                try:
                    # print("inside > 450")
                    query = "type:user " + emailAddress
                except:
                    query = "type:user " + firstName + " " + lastName
                # print(query)
            elif data_lenght < 450:
                try:
                    # print("inside < 450")
                    # query = "type:user " + emailAddress + " organization:" + companyName
                    query = "type:user " + emailAddress
                except:
                    # query = "type:user " + firstName + " " + lastName + " organization:" + companyName
                    query = "type:user " + firstName + " " + lastName
                # print(query)
            else:
                return messageDetail.ReplyToChat("No user information available")

                botlog.LogSymphonyInfo(query)
            results = zendesk.search(query=query)
            # print(results)

            if str(results).startswith(
                    "{'results': [], 'facets': None, 'next_page': None, 'previous_page': None, 'count': 0}"):
                return messageDetail.ReplyToChat(
                    "This user does not exist on Zendesk, the name is misspelled or does not belong to this organisation.")
            elif str(results).startswith(
                    "{'results': [], 'facets': {'type': {'entry': 0, 'ticket': 0, 'organization': 0, 'user': 0, 'article': 0, 'group': 0}}, 'next_page': None, 'previous_page': None, 'count': 0}"):
                return messageDetail.ReplyToChat(
                    "This organisation/company does not exist in Zendesk or name is misspelled.")
            else:

                data = json.dumps(results, indent=2)
                d = json.loads(data)

                for index in range(len(d["results"])):
                    # name = d["results"][index]["name"]
                    # email = str(d["results"][index]["email"])
                    role = str(d["results"][index]["role"])
                    # print(role)
                    botlog.LogSymphonyInfo("The calling user is a Zendesk " + role)

                    if role == "Administrator" or role == "admin" or role == "Agent" or role == "agent":
                        isAllowed = True
                        botlog.LogSymphonyInfo("Role of the calling user: " + role)
                    else:
                        isAllowed = False

            #################################################

            botlog.LogSymphonyInfo(firstName + " " + lastName + " (" + displayName + ") from Company/Pod name: " + str(companyName) + " with UID: " + str(userID))
            callerCheck = (firstName + " " + lastName + " - " + displayName + " - " + companyName + " - " + str(userID))

        if callerCheck in AccessFile and isAllowed:

            botlog.LogSymphonyInfo("User is part of the Agent list and is an Admin or Agent on Zendesk")

            caller_raw = messageDetail.Sender.Name
            caller_split = str(caller_raw).split(" ")
            caller = caller_split[0]

            # Parse the input
            query = ""
            results = ""
            isIM = ""

            message = (messageDetail.Command.MessageText)
            message_split = message.split("|")

            try:
                userSplit = message_split[0]
                userEntered = True
            except:
                userSplit = ""
                userEntered = False

            try:
                organization = str(message_split[1]).strip()
                orgEntered = True
            except:
                organization = ""
                orgEntered = False

            ####################################

            headers = {
                'username': _configDef['zdesk_config']['zdesk_email'] + "/token",
                'password': _configDef['zdesk_config']['zdesk_password'],
                'authorization': _configDef['zdesk_config']['zdesk_auth'],
                'cache-control': "no-cache",
                'Content-Type': 'application/json',
            }

            url = _configDef['zdesk_config']['zdesk_url'] + "/api/v2/search"

            # User search only
            if userEntered and orgEntered == False:
                query += "type:user\"" + str(userSplit[1:]) + "\""
                querystring = {"query": "type:user " + str(userSplit[1:]) + ""}
                print(querystring)

                response = requests.request("GET", str(url), headers=headers, params=querystring)
                data = response.json()

                noUserFound = "{'results': [], 'facets': None, 'next_page': None, 'previous_page': None, 'count': 0}"

                if str(data).startswith(noUserFound):
                    return messageDetail.ReplyToChat("There is no user with this information")

                if query == "type:user\"\"":
                    return messageDetail.ReplyToChat("You have searched for all users on your Zendesk, I will ignore this request to avoid any performance issue")

                else:
                    botlog.LogSymphonyInfo("Getting user information from Zendesk")

            # User and Organisation search
            if userEntered and orgEntered:
                query += "type:user" + str(userSplit) + " organization:" + str(organization[1:])

                querystring = {"query": "type:user" + str(userSplit) + " organization:" + str(organization[1:]) + ""}

                if str(query).startswith("type:user  organization:"):
                    messageDetail.ReplyToChat("Please check your 1:1 IM with me to see the full list of users from " + str(organization[1:]))
                    messageDetail.ReplyToSenderv2("Hi " + str(caller) + ", Loading all users from Zendesk under organization <b>" + str(organization[1:]) + "</b>, please wait")
                    isIM = True

                response = requests.request("GET", url, headers=headers, params=querystring)
                data = response.json()

            if str(results).startswith("{'results': [], 'facets': None, 'next_page': None, 'previous_page': None, 'count': 0}"):
                return messageDetail.ReplyToChat("This user does not exist on Zendesk, name is misspelled or does not belong to this organisation")
            elif str(results).startswith("{'results': [], 'facets': {'type': {'entry': 0, 'ticket': 0, 'organization': 0, 'user': 0, 'article': 0, 'group': 0}}, 'next_page': None, 'previous_page': None, 'count': 0}"):
                return messageDetail.ReplyToChat("This organisation/company does not exist in Zendesk or is misspelled")
            else:

                table_body = ""
                table_header = "<table style='border-collapse:collapse;border:2px solid black;table-layout:auto;width:100%;box-shadow: 5px 5px'><thead><tr style='background-color:#4D94FF;color:#ffffff;font-size:1rem' class=\"tempo-text-color--white tempo-bg-color--black\">" \
                               "<td style='width:25%;border:1px solid blue;border-bottom: double blue;text-align:center'>NAME</td>" \
                               "<td style='width:25%;border:1px solid blue;border-bottom: double blue;text-align:center'>EMAIL ADDRESS</td>" \
                               "<td style='width:25%;border:1px solid blue;border-bottom: double blue;text-align:center'>COMPANY</td>" \
                               "<td style='width:25%;border:1px solid blue;border-bottom: double blue;text-align:center'>ROLE</td>" \
                               "</tr></thead><tbody>"

                for result in data['results']:
                    name = str(result["name"])
                    zdID = str(result["id"])

                    ###############################

                    conn = http.client.HTTPSConnection(_configDef['zdesk_config']['zdesk_api'])

                    headers = {
                        'username': _configDef['zdesk_config']['zdesk_email'] + "/token",
                        'password': _configDef['zdesk_config']['zdesk_password'],
                        'authorization': _configDef['zdesk_config']['zdesk_auth'],
                        'cache-control': "no-cache",
                        'Content-Type': 'application/json',
                    }

                    # To get the name of the requester given the requesterID
                    conn.request("GET", "/api/v2/users/" + str(zdID) + "/organizations", headers=headers)
                    res = conn.getresponse()
                    organizationsID = res.read()
                    tempOrganizationsID = str(organizationsID.decode('utf-8'))

                    data = json.dumps(tempOrganizationsID, indent=2)
                    data_dict = ast.literal_eval(data)
                    d_req = json.loads(str(data_dict))
                    org_Name = str(d_req["organizations"][0]["name"])

                    ###############################

                    comData = org_Name

                    email = str(result["email"])
                    organization_id = str(result["organization_id"])
                    userZRole = str(result["role"])

                    orglink = (_configDef['zdesk_config']['zdesk_org']) + str(organization_id) + "/tickets"
                    user_link = (_configDef['zdesk_config']['zdesk_user']) + str(zdID) + "/requested_tickets"

                    table_body += "<tr>" \
                                  "<td style='border:1px solid black;text-align:center'><a href=\"" + str(user_link) + "\">" + str(name) + "</a></td>" \
                                  "<td style='border:1px solid black;text-align:center'><a href=\"mailto:" + str(email) + "?Subject=Symphony%20Communication\">" + str(email) + "</a></td>" \
                                  "<td style='border:1px solid black;text-align:center'><a href=\"" + str(orglink) + "\">" + str(comData) + "</a></td>" \
                                  "<td style='border:1px solid black;text-align:center'>" + str(userZRole) + "</td>" \
                                  "</tr>"

                table_body += "</tbody></table>"

                reply = table_header + table_body

                if isIM:
                    return messageDetail.ReplyToSenderv2_noBotLog(
                        "<card iconSrc=\"https://thumb.ibb.co/csXBgU/Symphony2018_App_Icon_Mobile.png\" accent=\"tempo-bg-color--blue\"><header>These are all the users under the organisation <b>" + organization[1:] + "</b></header><body>" + reply + "</body></card>")
                else:
                    return messageDetail.ReplyToChatV2_noBotLog("<card iconSrc =\"https://thumb.ibb.co/csXBgU/Symphony2018_App_Icon_Mobile.png\" accent=\"tempo-bg-color--blue\"><header>Please find the result below</header><body>" + reply + "</body></card>")
        else:
            return messageDetail.ReplyToChat("You aren't authorised to use this command. You are either not Added to the Bot as an Agent or you are not an Agent/Staff on Zendesk")
    except:
        try:
            botlog.LogSymphonyInfo("Inside second try for UserZD")
            isAllowed = False
            commandCallerUID = messageDetail.FromUserId

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

                #################################################

                try:
                    emailAddress = str(d_org["users"][index_org]["emailAddress"])
                    # print("User is connected: " + emailAddress)
                    emailZendesk = emailAddress
                    connectionRequired = False
                except:
                    connectionRequired = True

                # if connectionRequired:

                data_lenght = len(dataComp)

                if data_lenght > 450:
                    try:
                        # print("inside > 450")
                        query = "type:user " + emailAddress
                    except:
                        query = "type:user " + firstName + " " + lastName
                    # print(query)
                elif data_lenght < 450:
                    try:
                        # print("inside < 450")
                        # query = "type:user " + emailAddress + " organization:" + companyName
                        query = "type:user " + emailAddress
                    except:
                        # query = "type:user " + firstName + " " + lastName + " organization:" + companyName
                        query = "type:user " + firstName + " " + lastName
                    # print(query)
                else:
                    return messageDetail.ReplyToChat("No user information available")

                    botlog.LogSymphonyInfo(query)
                results = zendesk.search(query=query)
                # print(results)

                if str(results).startswith("{'results': [], 'facets': None, 'next_page': None, 'previous_page': None, 'count': 0}"):
                    return messageDetail.ReplyToChat("This user does not exist on Zendesk, the name is misspelled or does not belong to this organisation.")
                elif str(results).startswith("{'results': [], 'facets': {'type': {'entry': 0, 'ticket': 0, 'organization': 0, 'user': 0, 'article': 0, 'group': 0}}, 'next_page': None, 'previous_page': None, 'count': 0}"):
                    return messageDetail.ReplyToChat("This organisation/company does not exist in Zendesk or name is misspelled.")
                else:

                    data = json.dumps(results, indent=2)
                    d = json.loads(data)

                    for index in range(len(d["results"])):
                        # name = d["results"][index]["name"]
                        # email = str(d["results"][index]["email"])
                        role = str(d["results"][index]["role"])
                        # print(role)
                        botlog.LogSymphonyInfo("The calling user is a Zendesk " + role)

                        if role == "Administrator" or role == "admin" or role == "Agent" or role == "agent":
                            isAllowed = True
                            botlog.LogSymphonyInfo("Role of the calling user: " + role)
                        else:
                            isAllowed = False

                #################################################

                botlog.LogSymphonyInfo(firstName + " " + lastName + " (" + displayName + ") from Company/Pod name: " + str(companyName) + " with UID: " + str(userID))
                callerCheck = (firstName + " " + lastName + " - " + displayName + " - " + companyName + " - " + str(userID))

            if callerCheck in AccessFile and isAllowed:

                botlog.LogSymphonyInfo("User is part of the Agent list and is an Admin or Agent on Zendesk")

                caller_raw = messageDetail.Sender.Name
                caller_split = str(caller_raw).split(" ")
                caller = caller_split[0]

                # Parse the input
                query = ""
                results = ""
                isIM = ""

                message = (messageDetail.Command.MessageText)
                message_split = message.split("|")

                try:
                    userSplit = message_split[0]
                    userEntered = True
                except:
                    userSplit = ""
                    userEntered = False

                try:
                    organization = str(message_split[1]).strip()
                    orgEntered = True
                except:
                    organization = ""
                    orgEntered = False

                ####################################

                headers = {
                    'username': _configDef['zdesk_config']['zdesk_email'] + "/token",
                    'password': _configDef['zdesk_config']['zdesk_password'],
                    'authorization': _configDef['zdesk_config']['zdesk_auth'],
                    'cache-control': "no-cache",
                    'Content-Type': 'application/json',
                }

                url = _configDef['zdesk_config']['zdesk_url'] + "/api/v2/search"

                # User search only
                if userEntered and orgEntered == False:
                    query += "type:user\"" + str(userSplit[1:]) + "\""
                    querystring = {"query": "type:user " + str(userSplit[1:]) + ""}

                    response = requests.request("GET", str(url), headers=headers, params=querystring)
                    data = response.json()

                    noUserFound = "{'results': [], 'facets': None, 'next_page': None, 'previous_page': None, 'count': 0}"

                    if str(data).startswith(noUserFound):
                        return messageDetail.ReplyToChat("There is no user with this information")

                    if query == "type:user\"\"":
                        return messageDetail.ReplyToChat("You have searched for all users on your Zendesk, I will ignore this request to avoid any performance issue")

                    else:
                        botlog.LogSymphonyInfo("Getting user information from Zendesk")

                # User and Organisation search
                if userEntered and orgEntered:
                    query += "type:user" + str(userSplit) + " organization:" + str(organization[1:])

                    querystring = {"query": "type:user" + str(userSplit) + " organization:" + str(organization[1:]) + ""}

                    if str(query).startswith("type:user  organization:"):
                        messageDetail.ReplyToChat("Please check your 1:1 IM with me to see the full list of users from " + str(organization[1:]))
                        messageDetail.ReplyToSenderv2("Hi " + str(caller) + ", Loading all users from Zendesk under organization <b>" + str(organization[1:]) + "</b>, please wait")
                        isIM = True

                    response = requests.request("GET", url, headers=headers, params=querystring)
                    data = response.json()

                if str(results).startswith("{'results': [], 'facets': None, 'next_page': None, 'previous_page': None, 'count': 0}"):
                    return messageDetail.ReplyToChat("This user does not exist on Zendesk, name is misspelled or does not belong to this organisation")
                elif str(results).startswith("{'results': [], 'facets': {'type': {'entry': 0, 'ticket': 0, 'organization': 0, 'user': 0, 'article': 0, 'group': 0}}, 'next_page': None, 'previous_page': None, 'count': 0}"):
                    return messageDetail.ReplyToChat("This organisation/company does not exist in Zendesk or is misspelled")
                else:

                    table_body = ""
                    table_header = "<table style='border-collapse:collapse;border:2px solid black;table-layout:auto;width:100%;box-shadow: 5px 5px'><thead><tr style='background-color:#4D94FF;color:#ffffff;font-size:1rem' class=\"tempo-text-color--white tempo-bg-color--black\">" \
                                   "<td style='width:25%;border:1px solid blue;border-bottom: double blue;text-align:center'>NAME</td>" \
                                   "<td style='width:25%;border:1px solid blue;border-bottom: double blue;text-align:center'>EMAIL ADDRESS</td>" \
                                   "<td style='width:25%;border:1px solid blue;border-bottom: double blue;text-align:center'>COMPANY</td>" \
                                   "<td style='width:25%;border:1px solid blue;border-bottom: double blue;text-align:center'>ROLE</td>" \
                                   "</tr></thead><tbody>"

                    for result in data['results']:
                        name = str(result["name"])
                        zdID = str(result["id"])

                        ###############################

                        conn = http.client.HTTPSConnection(_configDef['zdesk_config']['zdesk_api'])

                        headers = {
                            'username': _configDef['zdesk_config']['zdesk_email'] + "/token",
                            'password': _configDef['zdesk_config']['zdesk_password'],
                            'authorization': _configDef['zdesk_config']['zdesk_auth'],
                            'cache-control': "no-cache",
                            'Content-Type': 'application/json',
                        }

                        # To get the name of the requester given the requesterID
                        conn.request("GET", "/api/v2/users/" + str(zdID) + "/organizations", headers=headers)
                        res = conn.getresponse()
                        organizationsID = res.read()
                        tempOrganizationsID = str(organizationsID.decode('utf-8'))

                        data = json.dumps(tempOrganizationsID, indent=2)
                        data_dict = ast.literal_eval(data)
                        d_req = json.loads(str(data_dict))
                        org_Name = str(d_req["organizations"][0]["name"])

                        ###############################

                        comData = org_Name

                        email = str(result["email"])
                        organization_id = str(result["organization_id"])
                        userZRole = str(result["role"])

                        orglink = (_configDef['zdesk_config']['zdesk_org']) + str(organization_id) + "/tickets"
                        user_link = (_configDef['zdesk_config']['zdesk_user']) + str(zdID) + "/requested_tickets"

                        table_body += "<tr>" \
                                      "<td style='border:1px solid black;text-align:center'><a href=\"" + str(user_link) + "\">" + str(name) + "</a></td>" \
                                      "<td style='border:1px solid black;text-align:center'><a href=\"mailto:" + str(email) + "?Subject=Symphony%20Communication\">" + str(email) + "</a></td>" \
                                      "<td style='border:1px solid black;text-align:center'><a href=\"" + str(orglink) + "\">" + str(comData) + "</a></td>" \
                                      "<td style='border:1px solid black;text-align:center'>" + str(userZRole) + "</td>" \
                                      "</tr>"

                    table_body += "</tbody></table>"

                    reply = table_header + table_body

                    if isIM:
                        return messageDetail.ReplyToSenderv2_noBotLog(
                            "<card iconSrc=\"https://thumb.ibb.co/csXBgU/Symphony2018_App_Icon_Mobile.png\" accent=\"tempo-bg-color--blue\"><header>These are all the users under the organisation <b>" + organization[1:] + "</b></header><body>" + reply + "</body></card>")
                    else:
                        return messageDetail.ReplyToChatV2_noBotLog("<card iconSrc =\"https://thumb.ibb.co/csXBgU/Symphony2018_App_Icon_Mobile.png\" accent=\"tempo-bg-color--blue\"><header>Please find the result below</header><body>" + reply + "</body></card>")
            else:
                return messageDetail.ReplyToChat("You aren't authorised to use this command. You are either not Added to the Bot as an Agent or you are not an Agent/Staff on Zendesk")
        except:
            return messageDetail.ReplyToChat("I am sorry, I was working on a different task, can you please retry")

####################################
########  Recent Tickets  ##########
####################################
def recentZD(messageDetail):
    botlog.LogSymphonyInfo("#################################################")
    botlog.LogSymphonyInfo("Bot Call: Recent Zendesk Tickets raised or viewed")
    botlog.LogSymphonyInfo("#################################################")

    try:
        isAllowed = False
        commandCallerUID = messageDetail.FromUserId

        try:
            connComp.request("GET", "/pod/v3/users?uid=" + commandCallerUID, headers=headersCompany)
        except:
            return messageDetail.ReplyToChat("I am having difficulty to find this user id: " + commandCallerUID)

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

            #################################################

            try:
                emailAddress = str(d_org["users"][index_org]["emailAddress"])
                #print("User is connected: " + emailAddress)
                emailZendesk = emailAddress
                connectionRequired = False
            except:
                connectionRequired = True

            # if connectionRequired:

            data_lenght = len(dataComp)

            if data_lenght > 450:
                try:
                    #print("inside > 450")
                    query = "type:user " + emailAddress
                except:
                    query = "type:user " + firstName + " " + lastName
                botlog.LogSymphonyInfo(query)
            elif data_lenght < 450:
                try:
                    #print("inside < 450")
                    #query = "type:user " + emailAddress + " organization:" + companyName
                    query = "type:user " + emailAddress
                except:
                    #query = "type:user " + firstName + " " + lastName + " organization:" + companyName
                    query = "type:user " + firstName + " " + lastName
                botlog.LogSymphonyInfo(query)
            else:
                return messageDetail.ReplyToChat("No user information available")

                botlog.LogSymphonyInfo(query)
            results = zendesk.search(query=query)
            #print(results)

            if str(results).startswith(
                    "{'results': [], 'facets': None, 'next_page': None, 'previous_page': None, 'count': 0}"):
                return messageDetail.ReplyToChat(
                    "This user does not exist on Zendesk, the name is misspelled or does not belong to this organisation.")
            elif str(results).startswith(
                    "{'results': [], 'facets': {'type': {'entry': 0, 'ticket': 0, 'organization': 0, 'user': 0, 'article': 0, 'group': 0}}, 'next_page': None, 'previous_page': None, 'count': 0}"):
                return messageDetail.ReplyToChat(
                    "This organisation/company does not exist in Zendesk or name is misspelled.")
            else:

                data = json.dumps(results, indent=2)
                d = json.loads(data)

                for index in range(len(d["results"])):
                    # name = d["results"][index]["name"]
                    # email = str(d["results"][index]["email"])
                    role = str(d["results"][index]["role"])
                    #print(role)
                    botlog.LogSymphonyInfo("The calling user is a Zendesk " + role)

                    if role == "Administrator" or role == "admin" or role == "Agent" or role == "agent":
                        isAllowed = True
                        #print(role)
                        botlog.LogSymphonyInfo("Role of the calling user: " + role)
                    else:
                        isAllowed = False

            #################################################

            botlog.LogSymphonyInfo(firstName + " " + lastName + " (" + displayName + ") from Company/Pod name: " + str(companyName) + " with UID: " + str(userID))
            callerCheck = (firstName + " " + lastName + " - " + displayName + " - " + companyName + " - " + str(userID))

        if callerCheck in AccessFile and isAllowed:

            botlog.LogSymphonyInfo("Calling user is added to the bot as Agent and also on Zendesk as Admin or Agent")
        #if messageDetail.Sender.Name in AccessFile:

            # noAssignee = False
            messageDetail.ReplyToChat("Pulling the data from Zendesk and rendering it now, please wait...")

            conn = http.client.HTTPSConnection(_configDef['zdesk_config']['zdesk_api'])

            # headers = {
            #     'username': _configDef['zdesk_config']['zdesk_email'] + "/token",
            #     'password': _configDef['zdesk_config']['zdesk_password'],
            #     'authorization': _configDef['zdesk_config']['zdesk_auth'],
            #     'cache-control': "no-cache",
            #     'Content-Type': "application/json"
            # }

            base64Encoded = base64.b64encode(bytes((emailZendesk + "/token:" + _configDef['zdesk_config']['zdesk_password']), 'utf-8'))
            base64Enc = (base64Encoded.decode("utf-8"))
            #print(str(base64Enc))
            base = ("Basic " + base64Enc)
            #print(str(base))

            headers = {
                        'email_address': emailZendesk +"/token",
                        'password': (_configDef['zdesk_config']['zdesk_password']),
                        'authorization': base,
                        'cache-control': "no-cache",
                        'content-type': "application/json"
            }

            conn.request("GET", "/api/v2/tickets/recent.json?include=users", headers=headers)

            res = conn.getresponse()
            tickets = res.read().decode("utf-8")
            d = json.loads(tickets)
            #print(d)

            noRecentTicket = "{'tickets': [], 'users': [], 'next_page': None, 'previous_page': None, 'count': 0}"
            if str(d).startswith(noRecentTicket):
                return messageDetail.ReplyToChat("There is no recently viewed ticket to show")

            table_body = ""
            table_header = "<table style='border-collapse:collapse;border:2px solid black;table-layout:auto;width:100%;box-shadow: 5px 5px'><thead><tr style='background-color:#4D94FF;color:#ffffff;font-size:1rem' class=\"tempo-text-color--white tempo-bg-color--black\">" \
                           "<td style='width:20%;border:1px solid blue;border-bottom: double blue;text-align:center'>SUBJECT</td>" \
                           "<td style='width:30%;border:1px solid blue;border-bottom: double blue;text-align:center'>DESCRIPTION</td>" \
                           "<td style='width:2%;border:1px solid blue;border-bottom: double blue;text-align:center'>ID</td>" \
                           "<td style='width:3%;border:1px solid blue;border-bottom: double blue;text-align:center'>PRIORITY</td>" \
                           "<td style='width:3%;border:1px solid blue;border-bottom: double blue;text-align:center'>STATUS</td>" \
                           "<td style='width:7%;border:1px solid blue;border-bottom: double blue;text-align:center'>CREATED</td>" \
                           "<td style='width:7%;border:1px solid blue;border-bottom: double blue;text-align:center'>UPDATED</td>" \
                           "<td style='width:7%;border:1px solid blue;border-bottom: double blue;text-align:center'>REQUESTER</td>" \
                           "<td style='width:5%;border:1px solid blue;border-bottom: double blue;text-align:center'>COMPANY</td>" \
                           "<td style='width:7%;border:1px solid blue;border-bottom: double blue;text-align:center'>ASSIGNEE</td>" \
                           "<td style='width:4%;border:1px solid blue;border-bottom: double blue;text-align:center'>SEVERITY</td>" \
                           "</tr></thead><tbody>"

            for index in range(len(d["tickets"])):
                ticketid = str(d["tickets"][index]["id"])
                subject_temp = d["tickets"][index]["subject"]
                subject = str(subject_temp).replace("<", "&lt;").replace("\"", "&quot;").replace("&", "&amp;").replace("'","&apos;").replace(">","&gt;")
                description_temp = d["tickets"][index]["description"]
                description = str(description_temp).replace("<", "&lt;").replace("\"", "&quot;").replace("&", "&amp;").replace("'","&apos;").replace(">","&gt;")
                priority = str(d["tickets"][index]["priority"])
                status = d["tickets"][index]["status"]
                created_at = str(d["tickets"][index]["created_at"]).replace("T", " ").replace("Z", "")
                updated_at = str(d["tickets"][index]["updated_at"]).replace("T", " ").replace("Z", "")
                requester_id = str(d["tickets"][index]["requester_id"])

                noAssignee = False

                try:
                    # To get the name of the requester given the requesterID
                    conn.request("GET", "/api/v2/users/" + requester_id, headers=headers)
                    res = conn.getresponse()
                    userRequesterId = res.read()
                    tempUserRequester = str(userRequesterId.decode('utf-8'))

                    data = json.dumps(tempUserRequester, indent=2)
                    data_dict = ast.literal_eval(data)
                    d_req = json.loads(data_dict)
                    requesterName = str(d_req["user"]["name"])

                except:
                    requesterName = "None"

                organization_id = str(d["tickets"][index]["organization_id"])

                try:
                    # Convert the Zendesk ID to company name
                    conn.request("GET", "/api/v2/users/" + requester_id + "/organizations.json", headers=headers)
                    res = conn.getresponse()
                    companyID = res.read()
                    compNameRaw = str(companyID.decode("utf-8"))

                    data = json.dumps(compNameRaw, indent=2)
                    data_dict = ast.literal_eval(data)
                    d_org = json.loads(data_dict)
                    org_Name = str(d_org["organizations"][0]["name"])
                    organization = org_Name

                except:
                    organization = "None"

                assignee_id = str(d["tickets"][index]["assignee_id"])

                try:
                    # To get the name of the assignee given the assignee_id
                    conn.request("GET", "/api/v2/users/" + assignee_id, headers=headers)
                    res = conn.getresponse()
                    userAssigneeId = res.read()
                    tempUserAssignee = str(userAssigneeId.decode('utf-8'))

                    data = json.dumps(tempUserAssignee, indent=2)
                    data_dict = ast.literal_eval(data)
                    d_assign = json.loads(data_dict)
                    assign_name = str(d_assign["user"]["name"])
                    assigneeName = assign_name

                except:
                    assigneeName = "None"
                    noAssignee = True

                tags = str(d["tickets"][index]["tags"])

                if (len(d["tickets"][index]["tags"])) == 0:
                    noTag = True
                else:
                    noTag = False

                notSet = True

                if noTag:
                    sev = "Not set"
                    notSet = False

                for index_tags in range(len(d["tickets"][index]["tags"])):
                    tags = str((d["tickets"][index]["tags"][index_tags]))

                    if tags.startswith("severity_1"):
                        sev = "Severity 1"
                        notSet = False
                    elif tags.startswith("severity_2"):
                        sev = "Severity 2"
                        notSet = False
                    elif tags.startswith("severity_3"):
                        sev = "Severity 3"
                        notSet = False
                    elif tags.startswith("severity_4"):
                        sev = "Severity 4"
                        notSet = False

                if notSet:
                    sev = "Not Set"
                    notSet = False

                tags = sev

                requesterTicket = (_configDef['zdesk_config']['zdesk_link']) + str(ticketid) + "/requester/requested_tickets"
                OrgTicket = (_configDef['zdesk_config']['zdesk_link']) + str(ticketid) + "/organization/tickets"
                assigneeTicket = (_configDef['zdesk_config']['zdesk_url']) + "/agent/users/" + str(assignee_id) + "/assigned_tickets"

                if noAssignee:

                    table_body += "<tr>" \
                                  "<td style='border:1px solid black;text-align:left'>" + subject + "</td>" \
                                  "<td style='border:1px solid black;text-align:left'>" + description + "</td>" \
                                  "<td style='border:1px solid black;text-align:center'><a href=\"" + (_configDef['zdesk_config']['zdesk_link']) + str(ticketid) + "\">" + str(ticketid) + "</a></td>" \
                                  "<td style='border:1px solid black;text-align:center'>" + priority + "</td>" \
                                  "<td style='border:1px solid black;text-align:center'>" + status + "</td>" \
                                  "<td style='border:1px solid black;text-align:center'>" + created_at + "</td>" \
                                  "<td style='border:1px solid black;text-align:center'>" + updated_at + "</td>" \
                                  "<td style='border:1px solid black;text-align:center'><a href=\"" + requesterTicket + "\">" + str(requesterName) + "</a></td>" \
                                  "<td style='border:1px solid black;text-align:center'><a href=\"" + OrgTicket + "\">" + organization + "</a></td>" \
                                  "<td style='border:1px solid black;text-align:center'>" + str(assigneeName) + "</td>" \
                                  "<td style='border:1px solid black;text-align:center'>" + tags + "</td>" \
                                  "</tr>"

                else:

                    table_body += "<tr>" \
                                  "<td style='border:1px solid black;text-align:left'>" + subject + "</td>" \
                                  "<td style='border:1px solid black;text-align:left'>" + description + "</td>" \
                                  "<td style='border:1px solid black;text-align:center'><a href=\"" + (_configDef['zdesk_config']['zdesk_link']) + str(ticketid) + "\">" + str(ticketid) + "</a></td>" \
                                  "<td style='border:1px solid black;text-align:center'>" + priority + "</td>" \
                                  "<td style='border:1px solid black;text-align:center'>" + status + "</td>" \
                                  "<td style='border:1px solid black;text-align:center'>" + created_at + "</td>" \
                                  "<td style='border:1px solid black;text-align:center'>" + updated_at + "</td>" \
                                  "<td style='border:1px solid black;text-align:center'><a href=\"" + requesterTicket + "\">" + str(requesterName) + "</a></td>" \
                                  "<td style='border:1px solid black;text-align:center'><a href=\"" + OrgTicket + "\">" + organization + "</a></td>" \
                                  "<td style='border:1px solid black;text-align:center'><a href=\"" + assigneeTicket + "\">" + str(assigneeName) + "</a></td>" \
                                  "<td style='border:1px solid black;text-align:center'>" + tags + "</td>" \
                                  "</tr>"

            table_body += "</tbody></table>"

            reply = table_header + table_body
            return messageDetail.ReplyToChatV2_noBotLog("<card iconSrc =\"https://thumb.ibb.co/csXBgU/Symphony2018_App_Icon_Mobile.png\" accent=\"tempo-bg-color--blue\"><header>Please find below Zendesk ticket recently opened or viewed by the Zendesk Agents</header><body>" + reply + "</body></card>")

        else:
            botlog.LogSymphonyInfo("The calling using is an end user, cannot call the function /recent")
            return messageDetail.ReplyToChat("You aren't authorised to use this command. If required, please contact your Zendesk Admin to review your role")
    except:
        try:
            botlog.LogSymphonyInfo("Inside second try for recent")
            isAllowed = False
            commandCallerUID = messageDetail.FromUserId

            try:
                connComp.request("GET", "/pod/v3/users?uid=" + commandCallerUID, headers=headersCompany)
            except:
                return messageDetail.ReplyToChat("I am having difficulty to find this user id: " + commandCallerUID)

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

                #################################################

                try:
                    emailAddress = str(d_org["users"][index_org]["emailAddress"])
                    # print("User is connected: " + emailAddress)
                    emailZendesk = emailAddress
                    connectionRequired = False
                except:
                    connectionRequired = True

                # if connectionRequired:

                data_lenght = len(dataComp)

                if data_lenght > 450:
                    try:
                        # print("inside > 450")
                        query = "type:user " + emailAddress
                    except:
                        query = "type:user " + firstName + " " + lastName
                    botlog.LogSymphonyInfo(query)
                elif data_lenght < 450:
                    try:
                        # print("inside < 450")
                        # query = "type:user " + emailAddress + " organization:" + companyName
                        query = "type:user " + emailAddress
                    except:
                        # query = "type:user " + firstName + " " + lastName + " organization:" + companyName
                        query = "type:user " + firstName + " " + lastName
                    botlog.LogSymphonyInfo(query)
                else:
                    return messageDetail.ReplyToChat("No user information available")

                    botlog.LogSymphonyInfo(query)
                results = zendesk.search(query=query)
                # print(results)

                if str(results).startswith(
                        "{'results': [], 'facets': None, 'next_page': None, 'previous_page': None, 'count': 0}"):
                    return messageDetail.ReplyToChat(
                        "This user does not exist on Zendesk, the name is misspelled or does not belong to this organisation.")
                elif str(results).startswith(
                        "{'results': [], 'facets': {'type': {'entry': 0, 'ticket': 0, 'organization': 0, 'user': 0, 'article': 0, 'group': 0}}, 'next_page': None, 'previous_page': None, 'count': 0}"):
                    return messageDetail.ReplyToChat(
                        "This organisation/company does not exist in Zendesk or name is misspelled.")
                else:

                    data = json.dumps(results, indent=2)
                    d = json.loads(data)

                    for index in range(len(d["results"])):
                        # name = d["results"][index]["name"]
                        # email = str(d["results"][index]["email"])
                        role = str(d["results"][index]["role"])
                        #print(role)
                        botlog.LogSymphonyInfo("The calling user is a Zendesk " + role)

                        if role == "Administrator" or role == "admin" or role == "Agent" or role == "agent":
                            isAllowed = True
                            #print(role)
                            botlog.LogSymphonyInfo("Role of the calling user: " + role)
                        else:
                            isAllowed = False

                #################################################

                botlog.LogSymphonyInfo(
                    firstName + " " + lastName + " (" + displayName + ") from Company/Pod name: " + str(
                        companyName) + " with UID: " + str(userID))
                callerCheck = (firstName + " " + lastName + " - " + displayName + " - " + companyName + " - " + str(
                    userID))

            if callerCheck in AccessFile and isAllowed:

                botlog.LogSymphonyInfo(
                    "Calling user is added to the bot as Agent and also on Zendesk as Admin or Agent")
                # if messageDetail.Sender.Name in AccessFile:

                # noAssignee = False
                messageDetail.ReplyToChat("Pulling the data from Zendesk and rendering it now, please wait...")

                conn = http.client.HTTPSConnection(_configDef['zdesk_config']['zdesk_api'])

                # headers = {
                #     'username': _configDef['zdesk_config']['zdesk_email'] + "/token",
                #     'password': _configDef['zdesk_config']['zdesk_password'],
                #     'authorization': _configDef['zdesk_config']['zdesk_auth'],
                #     'cache-control': "no-cache",
                #     'Content-Type': "application/json"
                # }

                base64Encoded = base64.b64encode(
                    bytes((emailZendesk + "/token:" + _configDef['zdesk_config']['zdesk_password']), 'utf-8'))
                base64Enc = (base64Encoded.decode("utf-8"))
                # print(str(base64Enc))
                base = ("Basic " + base64Enc)
                # print(str(base))

                headers = {
                    'email_address': emailZendesk + "/token",
                    'password': (_configDef['zdesk_config']['zdesk_password']),
                    'authorization': base,
                    'cache-control': "no-cache",
                    'content-type': "application/json"
                }

                conn.request("GET", "/api/v2/tickets/recent.json?include=users", headers=headers)

                res = conn.getresponse()
                tickets = res.read().decode("utf-8")
                d = json.loads(tickets)
                # print(d)

                noRecentTicket = "{'tickets': [], 'users': [], 'next_page': None, 'previous_page': None, 'count': 0}"
                if str(d).startswith(noRecentTicket):
                    return messageDetail.ReplyToChat("There is no recently viewed ticket to show")

                table_body = ""
                table_header = "<table style='border-collapse:collapse;border:2px solid black;table-layout:auto;width:100%;box-shadow: 5px 5px'><thead><tr style='background-color:#4D94FF;color:#ffffff;font-size:1rem' class=\"tempo-text-color--white tempo-bg-color--black\">" \
                               "<td style='width:20%;border:1px solid blue;border-bottom: double blue;text-align:center'>SUBJECT</td>" \
                               "<td style='width:30%;border:1px solid blue;border-bottom: double blue;text-align:center'>DESCRIPTION</td>" \
                               "<td style='width:2%;border:1px solid blue;border-bottom: double blue;text-align:center'>ID</td>" \
                               "<td style='width:3%;border:1px solid blue;border-bottom: double blue;text-align:center'>PRIORITY</td>" \
                               "<td style='width:3%;border:1px solid blue;border-bottom: double blue;text-align:center'>STATUS</td>" \
                               "<td style='width:7%;border:1px solid blue;border-bottom: double blue;text-align:center'>CREATED</td>" \
                               "<td style='width:7%;border:1px solid blue;border-bottom: double blue;text-align:center'>UPDATED</td>" \
                               "<td style='width:7%;border:1px solid blue;border-bottom: double blue;text-align:center'>REQUESTER</td>" \
                               "<td style='width:5%;border:1px solid blue;border-bottom: double blue;text-align:center'>COMPANY</td>" \
                               "<td style='width:7%;border:1px solid blue;border-bottom: double blue;text-align:center'>ASSIGNEE</td>" \
                               "<td style='width:4%;border:1px solid blue;border-bottom: double blue;text-align:center'>SEVERITY</td>" \
                               "</tr></thead><tbody>"

                for index in range(len(d["tickets"])):
                    ticketid = str(d["tickets"][index]["id"])
                    subject_temp = d["tickets"][index]["subject"]
                    subject = str(subject_temp).replace("<", "&lt;").replace("\"", "&quot;").replace("&","&amp;").replace("'", "&apos;").replace(">", "&gt;")
                    description_temp = d["tickets"][index]["description"]
                    description = str(description_temp).replace("<", "&lt;").replace("\"", "&quot;").replace("&","&amp;").replace("'", "&apos;").replace(">", "&gt;")
                    priority = str(d["tickets"][index]["priority"])
                    status = d["tickets"][index]["status"]
                    created_at = str(d["tickets"][index]["created_at"]).replace("T", " ").replace("Z", "")
                    updated_at = str(d["tickets"][index]["updated_at"]).replace("T", " ").replace("Z", "")
                    requester_id = str(d["tickets"][index]["requester_id"])

                    noAssignee = False

                    try:
                        # To get the name of the requester given the requesterID
                        conn.request("GET", "/api/v2/users/" + requester_id, headers=headers)
                        res = conn.getresponse()
                        userRequesterId = res.read()
                        tempUserRequester = str(userRequesterId.decode('utf-8'))

                        data = json.dumps(tempUserRequester, indent=2)
                        data_dict = ast.literal_eval(data)
                        d_req = json.loads(data_dict)
                        requesterName = str(d_req["user"]["name"])

                    except:
                        requesterName = "None"

                    organization_id = str(d["tickets"][index]["organization_id"])

                    try:
                        # Convert the Zendesk ID to company name
                        conn.request("GET", "/api/v2/users/" + requester_id + "/organizations.json", headers=headers)
                        res = conn.getresponse()
                        companyID = res.read()
                        compNameRaw = str(companyID.decode("utf-8"))

                        data = json.dumps(compNameRaw, indent=2)
                        data_dict = ast.literal_eval(data)
                        d_org = json.loads(data_dict)
                        org_Name = str(d_org["organizations"][0]["name"])
                        organization = org_Name

                    except:
                        organization = "None"

                    assignee_id = str(d["tickets"][index]["assignee_id"])

                    try:
                        # To get the name of the assignee given the assignee_id
                        conn.request("GET", "/api/v2/users/" + assignee_id, headers=headers)
                        res = conn.getresponse()
                        userAssigneeId = res.read()
                        tempUserAssignee = str(userAssigneeId.decode('utf-8'))

                        data = json.dumps(tempUserAssignee, indent=2)
                        data_dict = ast.literal_eval(data)
                        d_assign = json.loads(data_dict)
                        assign_name = str(d_assign["user"]["name"])
                        assigneeName = assign_name

                    except:
                        assigneeName = "None"
                        noAssignee = True

                    tags = str(d["tickets"][index]["tags"])

                    if (len(d["tickets"][index]["tags"])) == 0:
                        noTag = True
                    else:
                        noTag = False

                    notSet = True

                    if noTag:
                        sev = "Not set"
                        notSet = False

                    for index_tags in range(len(d["tickets"][index]["tags"])):
                        tags = str((d["tickets"][index]["tags"][index_tags]))

                        if tags.startswith("severity_1"):
                            sev = "Severity 1"
                            notSet = False
                        elif tags.startswith("severity_2"):
                            sev = "Severity 2"
                            notSet = False
                        elif tags.startswith("severity_3"):
                            sev = "Severity 3"
                            notSet = False
                        elif tags.startswith("severity_4"):
                            sev = "Severity 4"
                            notSet = False

                    if notSet:
                        sev = "Not Set"
                        notSet = False

                    tags = sev

                    requesterTicket = (_configDef['zdesk_config']['zdesk_link']) + str(
                        ticketid) + "/requester/requested_tickets"
                    OrgTicket = (_configDef['zdesk_config']['zdesk_link']) + str(ticketid) + "/organization/tickets"
                    assigneeTicket = (_configDef['zdesk_config']['zdesk_url']) + "/agent/users/" + str(
                        assignee_id) + "/assigned_tickets"

                    if noAssignee:

                        table_body += "<tr>" \
                                      "<td style='border:1px solid black;text-align:left'>" + subject + "</td>" \
                                      "<td style='border:1px solid black;text-align:left'>" + description + "</td>" \
                                      "<td style='border:1px solid black;text-align:center'><a href=\"" + (_configDef['zdesk_config']['zdesk_link']) + str(ticketid) + "\">" + str(ticketid) + "</a></td>" \
                                      "<td style='border:1px solid black;text-align:center'>" + priority + "</td>" \
                                      "<td style='border:1px solid black;text-align:center'>" + status + "</td>" \
                                      "<td style='border:1px solid black;text-align:center'>" + created_at + "</td>" \
                                      "<td style='border:1px solid black;text-align:center'>" + updated_at + "</td>" \
                                      "<td style='border:1px solid black;text-align:center'><a href=\"" + requesterTicket + "\">" + str(requesterName) + "</a></td>" \
                                      "<td style='border:1px solid black;text-align:center'><a href=\"" + OrgTicket + "\">" + organization + "</a></td>" \
                                      "<td style='border:1px solid black;text-align:center'>" + str(assigneeName) + "</td>" \
                                      "<td style='border:1px solid black;text-align:center'>" + tags + "</td>" \
                                      "</tr>"

                    else:

                        table_body += "<tr>" \
                                      "<td style='border:1px solid black;text-align:left'>" + subject + "</td>" \
                                      "<td style='border:1px solid black;text-align:left'>" + description + "</td>" \
                                      "<td style='border:1px solid black;text-align:center'><a href=\"" + (_configDef['zdesk_config']['zdesk_link']) + str(ticketid) + "\">" + str(ticketid) + "</a></td>" \
                                      "<td style='border:1px solid black;text-align:center'>" + priority + "</td>" \
                                      "<td style='border:1px solid black;text-align:center'>" + status + "</td>" \
                                      "<td style='border:1px solid black;text-align:center'>" + created_at + "</td>" \
                                      "<td style='border:1px solid black;text-align:center'>" + updated_at + "</td>" \
                                      "<td style='border:1px solid black;text-align:center'><a href=\"" + requesterTicket + "\">" + str(requesterName) + "</a></td>" \
                                      "<td style='border:1px solid black;text-align:center'><a href=\"" + OrgTicket + "\">" + organization + "</a></td>" \
                                      "<td style='border:1px solid black;text-align:center'><a href=\"" + assigneeTicket + "\">" + str(assigneeName) + "</a></td>" \
                                      "<td style='border:1px solid black;text-align:center'>" + tags + "</td>" \
                                      "</tr>"

                table_body += "</tbody></table>"

                reply = table_header + table_body
                return messageDetail.ReplyToChatV2_noBotLog(
                    "<card iconSrc =\"https://thumb.ibb.co/csXBgU/Symphony2018_App_Icon_Mobile.png\" accent=\"tempo-bg-color--blue\"><header>Please find below Zendesk ticket recently opened or viewed by the Zendesk Agents</header><body>" + reply + "</body></card>")

            else:
                botlog.LogSymphonyInfo("The calling using is an end user, cannot call the function /recent")
                return messageDetail.ReplyToChat(
                    "You aren't authorised to use this command. If required, please contact your Zendesk Admin to review your role")
        except:
            return messageDetail.ReplyToChat("I am sorry, I was working on a different task, can you please retry")

####################################
#########  CREATE TICKET  ##########
####################################
def TicketCreate(messageDetail):
    botlog.LogSymphonyInfo("#####################################")
    botlog.LogSymphonyInfo("Bot Call: Create Agent Zendesk Ticket")
    botlog.LogSymphonyInfo("#####################################")

    try:
        isAllowed = False
        commandCallerUID = messageDetail.FromUserId

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
            #emailAddress = str(d_org["users"][index_org]["emailAddress"])

            #################################################

            try:
                emailAddress = str(d_org["users"][index_org]["emailAddress"])
                #print("User is connected: " + emailAddress)
                emailZendesk = emailAddress
                connectionRequired = False
            except:
                connectionRequired = True

            # if connectionRequired:

            data_lenght = len(dataComp)

            if data_lenght > 450:
                try:
                    #print("inside > 450")
                    query = "type:user " + emailAddress
                except:
                    query = "type:user " + firstName + " " + lastName
                botlog.LogSymphonyInfo(query)
            elif data_lenght < 450:
                try:
                    #print("inside < 450")
                    #query = "type:user " + emailAddress + " organization:" + companyName
                    query = "type:user " + emailAddress
                except:
                    #query = "type:user " + firstName + " " + lastName + " organization:" + companyName
                    query = "type:user " + firstName + " " + lastName
                botlog.LogSymphonyInfo(query)
            else:
                return messageDetail.ReplyToChat("No user information available")

                botlog.LogSymphonyInfo(query)
            results = zendesk.search(query=query)
            #print(results)

            if str(results).startswith(
                    "{'results': [], 'facets': None, 'next_page': None, 'previous_page': None, 'count': 0}"):
                return messageDetail.ReplyToChat(
                    "This user does not exist on Zendesk, the name is misspelled or does not belong to this organisation.")
            elif str(results).startswith(
                    "{'results': [], 'facets': {'type': {'entry': 0, 'ticket': 0, 'organization': 0, 'user': 0, 'article': 0, 'group': 0}}, 'next_page': None, 'previous_page': None, 'count': 0}"):
                return messageDetail.ReplyToChat(
                    "This organisation/company does not exist in Zendesk or name is misspelled.")
            else:

                data = json.dumps(results, indent=2)
                d = json.loads(data)

                for index in range(len(d["results"])):
                    # name = d["results"][index]["name"]
                    # email = str(d["results"][index]["email"])
                    role = str(d["results"][index]["role"])
                    #print(role)
                    botlog.LogSymphonyInfo("The calling user is a Zendesk " + role)

                    if role == "Administrator" or role == "admin" or role == "Agent" or role == "agent":
                        isAllowed = True
                        #print(role)
                        botlog.LogSymphonyInfo("Role of the calling user: " + role)
                    else:
                        isAllowed = False

            #################################################

            botlog.LogSymphonyInfo(firstName + " " + lastName + " (" + displayName + ") from Company/Pod name: " + str(companyName) + " with UID: " + str(userID))
            callerCheck = (firstName + " " + lastName + " - " + displayName + " - " + companyName + " - " + str(userID))

        if callerCheck in AccessFile and isAllowed:

            callername = messageDetail.Sender.Name

            botlog.LogSymphonyInfo("**********")
            botlog.LogSymphonyInfo("Zendesk - createTicket function invoked by " + callername + " with the below details:")

            #splitting the message from Symphony into 3 by ,
            # details is taking 2nd and 3rd array object to use in ticket creation
            try:
                detail = messageDetail.Command.MessageFlattened.split("|")
                #print(detail)
            except:
                return messageDetail.ReplyToChat("No data to split")
            #flat is used for getting the uid from flattened
            try:
                flat = messageDetail.Command.MessageFlattened.split("_u_")
                #print(flat)
            except:
                return messageDetail.ReplyToChatV2("Please use the following format: <b>/createTicket subject, description</b>")

            try:
                #Removing the string of the function in the output
                ticketSubject = str(detail[0][14:]).replace("&quot;", "\"").replace("&amp;","&").replace("&lt;","<").replace("&apos;","'").replace("&gt;",">")
                botlog.LogSymphonyInfo("Ticket Subject: " + ticketSubject)
            except:
                return messageDetail.ReplyToChatV2("You did not enter a Subject. Please use the following format: <b>/createTicket subject, description</b>")
            try:
                ticketDescription = str(detail[1]).replace("&quot;", "\"").replace("&amp;","&").replace("&lt;","<").replace("&apos;","'").replace("&gt;",">")
                botlog.LogSymphonyInfo("Ticket Description: " + ticketDescription)
                botlog.LogSymphonyInfo("**********")
            except:
                return messageDetail.ReplyToChatV2("You did not enter a Subject. Please use the following format: <b>/createTicket subject, description</b>")


            new_ticket = \
            {
                    'ticket': {
                        'requester': {
                            'name': firstName + " " + lastName,
                            'email': emailAddress,
                        },
                #{
                    'subject': str(companyName) + ": " + ticketSubject,
                    'comment': ticketDescription,
                    'priority': "normal",
                    'type': "incident",
                    'ticket_field_entries':

                    [
                        {   #This will use the zendesl custom field to get the severity
                            #Using the parameter to be able to change this in the config file directly
                            'ticket_field_id': _configDef['zdesk_config']['zdesk_sev_field'],
                            'value': 'severity_3'
                        },
                    ]
                }
            }

            ####################################

            # base64Encoded = base64.b64encode(
            #     bytes((emailZendesk + "/token:" + _configDef['zdesk_config']['zdesk_password']), 'utf-8'))
            # base64Enc = (base64Encoded.decode("utf-8"))
            # print(str(base64Enc))
            # base = ("Basic " + base64Enc)
            # print(str(base))
            #
            # headers = {
            #     'email_address': emailZendesk + "/token",
            #     'password': (_configDef['zdesk_config']['zdesk_password']),
            #     'authorization': base,
            #     'cache-control': "no-cache",
            #     'content-type': "application/json"
            # }

            ####################################

            testconfig = {
                'zdesk_email': _configDef['zdesk_config']['zdesk_email'],
                'zdesk_password': _configDef['zdesk_config']['zdesk_password'],
                'zdesk_url': _configDef['zdesk_config']['zdesk_url'],
                'zdesk_token': True
            }
            zendesk = Zendesk(**testconfig)

            ####################################

            #Create a ticket and get its URL.
            result = zendesk.ticket_create(data=new_ticket)
            #print("Ticket is the following " +result)
            ticketidSplit = result.split("/")
            ticketURLid = ticketidSplit[6][:-5]
            #print("Ticket ID " +ticketURLid)

            tempLink = _configDef['zdesk_config']['zdesk_link'] + ticketURLid
            result = tempLink
            linkCreated = "<a href =\"" + _configDef['zdesk_config']['zdesk_link'] + ticketURLid + "\">" + result +"</a>"

            #print("Link for ticket " +linkCreated)
            return messageDetail.ReplyToChatV2("New Zendesk Ticket created: " +linkCreated)

        else:
            return messageDetail.ReplyToChat("You aren't authorised to use this command.")
    except:
        return messageDetail.ReplyToChat("I am sorry, I was working on a different task, can you please retry")


###############################
######### CREATE REQUEST ######
###############################
def RequestCreate(messageDetail):
###########################################################
##### GETTING THE @METION AND PARSING ITS EMAIL ADDRESS ####

    botlog.LogSymphonyInfo("#########################################")
    botlog.LogSymphonyInfo("Bot Call: Create end-user Zendesk Request")
    botlog.LogSymphonyInfo("#########################################")

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
            try:
                emailZendesk = str(d_org["users"][index_org]["emailAddress"])
            except:
                return messageDetail.ReplyToChat("No Email address was found for this user. Maybe not connected yet with the bot?")

            botlog.LogSymphonyInfo(firstName + " " + lastName + " (" + displayName + ") from Company/Pod name: " + str(companyName) + " with UID: " + str(userID))
            callerCheck = (firstName + " " + lastName + " - " + displayName + " - " + companyName + " - " + str(userID))

        if callerCheck in AccessFile:

            query = ""
            callername = messageDetail.Sender.Name

            botlog.LogSymphonyInfo("**********")
            botlog.LogSymphonyInfo("Zendesk - createRequest function invoked by " + callername + " with the below details:")

            emailZendesk = ""

            # splitting the message from Symphony into 3 by ,
            # details is taking 2nd and 3rd array object to use in ticket creation
            try:
                detail = messageDetail.Command.MessageFlattened.split("|")
                #print(detail)
            except:
                return messageDetail.ReplyToChat("Please use this format: /createRequest @mention| subject| description")
            # flat is used for getting the uid from flattened
            try:
                flat = messageDetail.Command.MessageFlattened.split("_u_")
                #print(flat)
            except:
                return messageDetail.ReplyToChat("Please use this format: /createRequest @mention| subject| description")

            # removing excess characters to just get the UID
            ############################################################
            try:
                UID = flat[1][:int(_configDef['UID'])]
                botlog.LogSymphonyInfo("User UI: " + UID)
            except:
                return messageDetail.ReplyToChat("You are part of the Zendesk Agent list, please use the following format for your call: <b>/createRequest @mention| subject| description</b>")

            # Calling the API endpoint to get display name
            connComp = http.client.HTTPSConnection(_configDef['symphonyinfo']['pod_hostname'])
            sessionTok = callout.GetSessionToken()

            headersCompany = {
                'sessiontoken': sessionTok,
                'cache-control': "no-cache"
            }

            try:
                connComp.request("GET", "/pod/v3/users?uid=" + UID, headers=headersCompany)

                resComp = connComp.getresponse()
                dataComp = resComp.read()
                data_raw = str(dataComp.decode('utf-8'))
                data_dict = ast.literal_eval(data_raw)

                dataRender = json.dumps(data_dict, indent=2)
                d_org = json.loads(dataRender)
                #print(d_org)
            except:
                return messageDetail.ReplyToChat("Please check the UID of the user, also make sure its digit matches the Config's setting.")

            connectionRequired = ""
            connectionRequired = True
            for index_org in range(len(d_org["users"])):
                firstName = d_org["users"][index_org]["firstName"]
                lastName = d_org["users"][index_org]["lastName"]
                company = d_org["users"][index_org]["company"]
                #print(company)
                try:
                    emailAddress = d_org["users"][index_org]["emailAddress"]
                    #print("User is connected: " + emailAddress)
                    emailZendesk = emailAddress
                    connectionRequired = False
                except:
                    connectionRequired = True
                    #messageDetail.ReplyToChat("User is not connected with me")
                    # messageDetail.ReplyToChat("User is not connected with me. Shall I send a Connection Request? Y/N")
                    #
                    # #askQuestion(messageDetail)
                    #
                    # autoConnection = ""
                    # def ask(messageDetail):
                    #
                    #     messageDetail.ReplyToChat("Y or N?")
                    #     time.sleep(10)
                    #
                    #     autoConnection = messageDetail.Command.MessageText
                    #     print(autoConnection)
                    #
                    # # while 1:
                    # #     print("waiting")
                    # #     autoConnection = messageDetail.Command.MessageText
                    # #     print(autoConnection)
                    # #     if autoConnection == "Y" or autoConnection == "N":
                    # #         break
                    #
                    # ask(messageDetail)
                    #
                    # autoConnection = messageDetail.Command.MessageText
                    # print(autoConnection)
                    #
                    # if autoConnection == "Y":
                    #     messageDetail.ReplyToChat("You said Yes")
                    # if autoConnection == "N":
                    #     messageDetail.ReplyToChat("You said No")

            if connectionRequired:

                data_lenght = len(dataComp)

                if data_lenght > 450:
                    try:
                        #print("inside > 450")
                        # query = "type:user " + firstName + " " + lastName + "email:" + emailAddress
                        query = "type:user " + emailAddress
                    except:
                        query = "type:user " + firstName + " " + lastName
                    #print(query)
                elif data_lenght < 450:
                    try:
                        #print("inside < 450")
                        # query = "type:user " + firstName + " " + lastName + "email:" + emailAddress + "organization:" + company
                        #query = "type:user " + emailAddress + " organization:" + company
                        query = "type:user " + emailAddress
                    except:
                        #query = "type:user " + firstName + " " + lastName + " organization:" + company
                        query = "type:user " + firstName + " " + lastName
                    #print(query)
                else:
                    return messageDetail.ReplyToChat("No user information available")

                botlog.LogSymphonyInfo(query)
                results = zendesk.search(query=query)
                #print(results)

                if str(results).startswith("{'results': [], 'facets': None, 'next_page': None, 'previous_page': None, 'count': 0}"):
                    return messageDetail.ReplyToChat("This user does not exist on Zendesk, the name is misspelled or does not belong to this organisation. Please use this format: /createRequest @mention| subject| description")
                elif str(results).startswith("{'results': [], 'facets': {'type': {'entry': 0, 'ticket': 0, 'organization': 0, 'user': 0, 'article': 0, 'group': 0}}, 'next_page': None, 'previous_page': None, 'count': 0}"):
                    return messageDetail.ReplyToChat("This organisation/company does not exist in Zendesk or name is misspelled. Please use this format: /createRequest @mention| subject| description")
                else:

                    data = json.dumps(results, indent=2)
                    d = json.loads(data)

                    for index in range(len(d["results"])):
                        name = d["results"][index]["name"]
                        email = str(d["results"][index]["email"])
                        #print("EmailAddress from Zendesk: " + email)
                    emailZendesk = email
            else:
                botlog.LogSymphonyInfo("Email Address: " + emailZendesk)
            # except:
            #     return messageDetail.ReplyToChat("You did not enter a Requester or the requester's email address is not valid. Please use this format: /createRequest @mention, subject, description")

            try:
                requestSubject = str(detail[1]).replace("&quot;", "\"").replace("&amp;","&").replace("&lt;","<").replace("&apos;","'").replace("&gt;",">")
                botlog.LogSymphonyInfo("Request Subject: " + requestSubject)
            except:
                return messageDetail.ReplyToChat("You did not enter a Subject. Please use this format: /createRequest @mention| subject| description")

            try:
                requestComment = str(detail[2]).replace("&quot;", "\"").replace("&amp;","&").replace("&lt;","<").replace("&apos;","'").replace("&gt;",">")
                botlog.LogSymphonyInfo("Request Description: " + requestComment)
                botlog.LogSymphonyInfo("**********")
            except:
                return messageDetail.ReplyToChat("You did not enter a description/comment. Please use this format: /createRequest @mention| subject| description")


            conn = http.client.HTTPSConnection(_configDef['zdesk_config']['zdesk_api'])

            payload = "{\n\"request\": \n{\n\"subject\": \"" + company + ":" + str(requestSubject) + "\", \n \"priority\": \"normal\",\n\"type\": \"incident\",\n\"comment\": \n{\n\"body\": \"" + str(requestComment) + "\"\n}\n}\n}"

            # payload = \
            # {
            #         'request': {
            #             # 'requester': {
            #             #     'name': '',
            #             #     'email': '',
            #             # },
            #     #{
            #         'subject': str(requestSubject),
            #         'comment':
            #             {
            #                 'body': str(requestComment)
            #             },
            #         'priority': "normal",
            #         'type': "incident",
            #         'ticket_field_entries':
            #             {
            #                 'ticket_field_id': _configDef['zdesk_config']['zdesk_sev_field'],
            #                 'value': 'severity_3'
            #             },
            #     }
            # }

            #print(type(payload))

            base64Encoded = base64.b64encode(bytes((emailZendesk + "/token:" + _configDef['zdesk_config']['zdesk_password']), 'utf-8'))
            base64Enc = (base64Encoded.decode("utf-8"))
            #print(str(base64Enc))
            base = ("Basic " + base64Enc)
            #print(str(base))

            headers = {
                        'email_address': emailZendesk +"/token",
                        'password': (_configDef['zdesk_config']['zdesk_password']),
                        'authorization': base,
                        'cache-control': "no-cache",
                        'content-type': "application/json"
            }
            #print(str(headers))

            conn.request("POST", "/api/v2/requests.json", payload, headers)

            res = conn.getresponse()
            data = res.read()
            tempdata = (data.decode("utf-8"))
            result = str(tempdata)

            ticketidSplit = result.split(":")
            ticketURLid = ticketidSplit[4][:-9]

            link = _configDef['zdesk_config']['zdesk_link'] + ticketURLid
            linkCreated = "<a href =\"" + _configDef['zdesk_config']['zdesk_link'] + ticketURLid + "\">" + link + "</a>"

            messageDetail.ReplyToChatV2("New Zendesk Request created: " + linkCreated)

    ##      Will show the Ticket details in a table format.
            headers_ticket = {
                        'email_address': emailZendesk +"/token",
                        'password': (_configDef['zdesk_config']['zdesk_password']),
                        'authorization': base
            }

            try:

                conn.request("GET", "/api/v2/tickets/" + ticketURLid + ".json", headers=headers_ticket)
                res = conn.getresponse()
                data = res.read()
                request_raw = data.decode("utf-8")

                data_raw = json.dumps(request_raw, indent=2)
                data_dict = ast.literal_eval(data_raw)
                d = json.loads(data_dict)

                requestid = str(d["ticket"]["id"])
                requeststatus = str(d["ticket"]["status"])
                requestpriority = str(d["ticket"]["priority"])
                requestseverity = str(d["ticket"]["tags"])

                if (len(d["ticket"]["tags"])) == 0:
                    noTag = True
                else:
                    noTag = False

                notSet = True

                if noTag:
                    sev = "Not set"
                    notSet = False

                for index_tags in range(len(d["ticket"]["tags"])):
                    tags = str((d["ticket"]["tags"][index_tags]))

                    if tags.startswith("severity_1"):
                        sev = "Severity 1"
                        notSet = False
                    elif tags.startswith("severity_2"):
                        sev = "Severity 2"
                        notSet = False
                    elif tags.startswith("severity_3"):
                        sev = "Severity 3"
                        notSet = False
                    elif tags.startswith("severity_4"):
                        sev = "Severity 4"
                        notSet = False

                if notSet:
                    sev = "Not Set"
                    notSet = False

                requestseverity = sev

                requestsubject_temps = str(d["ticket"]["subject"])
                requestsubject = str(requestsubject_temps).replace("<", "&lt;").replace("\"", "&quot;").replace("&", "&amp;").replace("'","&apos;").replace(">","&gt;")
                requestdescription_temps = str(d["ticket"]["description"])
                requestdescription = str(requestdescription_temps).replace("<", "&lt;").replace("\"", "&quot;").replace("&", "&amp;").replace("'","&apos;").replace(">","&gt;")
                requestorganization_id = str(d["ticket"]["organization_id"])
                requestrequester_id = str(d["ticket"]["requester_id"])
                requestcreated_at = str(d["ticket"]["created_at"]).replace("T", " ").replace("Z", "")
                requestupdated_at = str(d["ticket"]["updated_at"]).replace("T", " ").replace("Z", "")
                requestassignee_id = str(d["ticket"]["assignee_id"])

            except:
                conn.request("GET", "/api/v2/requests/" + ticketURLid + ".json", headers=headers_ticket)
                res = conn.getresponse()
                data = res.read()
                request_raw = data.decode("utf-8")

                data_raw = json.dumps(request_raw, indent=2)
                data_dict = ast.literal_eval(data_raw)
                d = json.loads(data_dict)

                requestid = str(d["request"]["id"])
                requeststatus = str(d["request"]["status"])
                requestpriority = str(d["request"]["priority"])
                #requestseverity = str(d["request"]["severity"])
                requestsubject_temps = str(d["request"]["subject"])
                requestsubject = requestsubject_temps.replace("<", "&lt;").replace("\"", "&quot;").replace("&", "&amp;").replace("'","&apos;").replace(">","&gt;")
                requestdescription_temps = str(d["request"]["description"])
                requestdescription = str(requestdescription_temps).replace("<", "&lt;").replace("\"", "&quot;").replace("&", "&amp;").replace("'","&apos;").replace(">","&gt;")
                requestorganization_id = str(d["request"]["organization_id"])
                requestrequester_id = str(d["request"]["requester_id"])
                requestcreated_at = str(d["request"]["created_at"]).replace("T", " ").replace("Z", "")
                requestupdated_at = str(d["request"]["updated_at"]).replace("T", " ").replace("Z", "")
                requestassignee_id = str(d["request"]["assignee_id"])

            request_id = str(requestid)
            request_status = str(requeststatus)
            request_priority = str(requestpriority)
            #request_severity = str(requestseverity)
            request_severity = ("Not set")
            request_subject = str(requestsubject)
            request_desc = str(requestdescription)
            desc = str(request_desc)
            request_org = str(requestorganization_id)
            request_requestor = str(requestrequester_id)
            request_created = str(requestcreated_at)
            request_updated = str(requestupdated_at)

            # To get the name of the requester given the requesterID

            headers_users = {
                        'email_address': _configDef['zdesk_config']['zdesk_email'] + "/token",
                        'password': (_configDef['zdesk_config']['zdesk_password']),
                        'authorization': _configDef['zdesk_config']['zdesk_auth'],
                        'content-type': "application/json"
            }

            conn.request("GET", "/api/v2/users/" + request_requestor, headers=headers_users)
            res = conn.getresponse()
            userRequesterId = res.read()
            tempUserRequester = str(userRequesterId.decode('utf-8'))

            data = json.dumps(tempUserRequester, indent=2)
            data_dict = ast.literal_eval(data)
            d = json.loads(data_dict)
            req_name = str(d["user"]["name"])
            requesterName = req_name

            try:
                request_assignee = str(requestassignee_id)
                # To get the name of the assignee given the assigneeID
                conn.request("GET", "/api/v2/users/" + request_assignee, headers=headers)
                res = conn.getresponse()
                userAssigneeId = res.read()
                tempUserAssignee = str(userAssigneeId.decode('utf-8'))

                data = json.dumps(tempUserAssignee, indent=2)
                data_dict = ast.literal_eval(data)
                d = json.loads(data_dict)
                assign_name = str(d["user"]["name"])
                assigneeName = assign_name

            except:
                assigneeName = "Not assigned"
                assignee_flag = True

            requesterTicket = (_configDef['zdesk_config']['zdesk_link']) + str(request_id) + "/requester/requested_tickets"
            assigneeTicket = (_configDef['zdesk_config']['zdesk_url']) + "/agent/users/" + request_assignee + "/assigned_tickets"
            OrgTicket = (_configDef['zdesk_config']['zdesk_link']) + str(request_id) + "/organization/tickets"

            # Convert the Zendesk ID to company name
            headers_org = {
                        'email_address': _configDef['zdesk_config']['zdesk_email'] + "/token",
                        'password': (_configDef['zdesk_config']['zdesk_password']),
                        'authorization': _configDef['zdesk_config']['zdesk_auth'],
                        'content-type': "application/json"
            }

            conn.request("GET", "/api/v2/users/" + requestrequester_id + "/organizations.json", headers=headers_org)
            res = conn.getresponse()
            companyID = res.read()
            compNameRaw = str(companyID.decode("utf-8"))

            data = json.dumps(compNameRaw, indent=2)
            data_dict = ast.literal_eval(data)
            d = json.loads(data_dict)
            org_Name = str(d["organizations"][0]["name"])
            orgName = str(org_Name)

            table_body = ""
            table_header = "<table style='border-collapse:collapse;border:2px solid black;table-layout:auto;width:100%;box-shadow: 5px 5px'><thead><tr style='background-color:#4D94FF;color:#ffffff;font-size:1rem' class=\"tempo-text-color--white tempo-bg-color--black\">" \
                           "<td style='width:20%;border:1px solid blue;border-bottom: double blue;text-align:center'>SUBJECT</td>" \
                           "<td style='width:30%;border:1px solid blue;border-bottom: double blue;text-align:center'>DESCRIPTION</td>" \
                           "<td style='width:2.5%;border:1px solid blue;border-bottom: double blue;text-align:center'>ID</td>" \
                           "<td style='width:3%;border:1px solid blue;border-bottom: double blue;text-align:center'>STATUS</td>" \
                           "<td style='width:3%;border:1px solid blue;border-bottom: double blue;text-align:center'>PRIORITY</td>" \
                           "<td style='width:3.5%;border:1px solid blue;border-bottom: double blue;text-align:center'>SEVERITY</td>" \
                           "<td style='width:5%;border:1px solid blue;border-bottom: double blue;text-align:center'>COMPANY</td>" \
                           "<td style='width:7%;border:1px solid blue;border-bottom: double blue;text-align:center'>REQUESTER</td>" \
                           "<td style='width:7%;border:1px solid blue;border-bottom: double blue;text-align:center'>CREATED</td>" \
                           "<td style='width:7%;border:1px solid blue;border-bottom: double blue;text-align:center'>UPDATED</td>" \
                           "<td style='width:7%;border:1px solid blue;border-bottom: double blue;text-align:center'>ASSIGNEE</td>" \
                           "</tr></thead><tbody>"

            if assignee_flag:

                table_body += "<tr>" \
                              "<td style='border:1px solid black;text-align:left'>" + request_subject + "</td>" \
                              "<td style='border:1px solid black;text-align:left'>" + desc + "</td>" \
                              "<td style='border:1px solid black;text-align:center'><a href=\"" + (_configDef['zdesk_config']['zdesk_link']) + str(request_id) + "\">" + str(request_id) + "</a></td>" \
                              "<td style='border:1px solid black;text-align:center'>" + request_status + "</td>" \
                              "<td style='border:1px solid black;text-align:center'>" + request_priority + "</td>" \
                              "<td style='border:1px solid black;text-align:center'>" + str(request_severity) + "</td>" \
                              "<td style='border:1px solid black;text-align:center'><a href=\"" + OrgTicket + "\">" + orgName + "</a></td>" \
                              "<td style='border:1px solid black;text-align:center'><a href=\"" + requesterTicket + "\">" + str(requesterName) + "</a></td>" \
                              "<td style='border:1px solid black;text-align:center'>" + request_created + "</td>" \
                              "<td style='border:1px solid black;text-align:center'>" + request_updated + "</td>" \
                              "<td style='border:1px solid black;text-align:center'>" + assigneeName + "</td>" \
                              "</tr>" \
                              "</tbody></table>"

            else:
                table_body += "<tr>" \
                              "<td style='border:1px solid black;text-align:left'>" + request_subject + "</td>" \
                              "<td style='border:1px solid black;text-align:left'>" + desc + "</td>" \
                              "<td style='border:1px solid black;text-align:center'><a href=\"" + (_configDef['zdesk_config']['zdesk_link']) + str(request_id) + "\">" + str(request_id) + "</a></td>" \
                              "<td style='border:1px solid black;text-align:center'>" + request_status + "</td>" \
                              "<td style='border:1px solid black;text-align:center'>" + request_priority + "</td>" \
                              "<td style='border:1px solid black;text-align:center'>" + str(request_severity) + "</td>" \
                              "<td style='border:1px solid black;text-align:center'><a href=\"" + OrgTicket + "\">" + orgName + "</a></td>" \
                              "<td style='border:1px solid black;text-align:center'><a href=\"" + requesterTicket + "\">" + str(requesterName) + "</a></td>" \
                              "<td style='border:1px solid black;text-align:center'>" + request_created + "</td>" \
                              "<td style='border:1px solid black;text-align:center'>" + request_updated + "</td>" \
                              "<td style='border:1px solid black;text-align:center'><a href=\"" + assigneeTicket + "\">" + str(assigneeName) + "</a></td>" \
                              "</tr>" \
                              "</tbody></table>"

            reply = table_header + table_body
            return messageDetail.ReplyToChatV2(reply)

        else:
            botlog.LogSymphonyInfo("This is an End-User Request Create. The calling user will be the requester.")

        ############################

            try:
                detail = messageDetail.Command.MessageFlattened.split("|")
                #print(detail)
            except:
                return messageDetail.ReplyToChat("Please use this format: /createRequest subject| description")

            try:
                requestSubject = str(detail[0][:15]).replace("&quot;", "\"").replace("&amp;","&").replace("&lt;","<").replace("&apos;","'").replace("&gt;",">")
                botlog.LogSymphonyInfo("Request Subject: " + requestSubject)
            except:
                return messageDetail.ReplyToChat(
                    "You did not enter a Subject. Please use this format: /createRequest subject| description")

            try:
                requestComment = str(detail[1]).replace("&quot;", "\"").replace("&amp;","&").replace("&lt;","<").replace("&apos;","'").replace("&gt;",">")
                botlog.LogSymphonyInfo("Request Description: " + requestComment)
                botlog.LogSymphonyInfo("**********")
            except:
                return messageDetail.ReplyToChat(
                    "You did not enter a description/comment. Please use this format: /createRequest subject| description")

            conn = http.client.HTTPSConnection(_configDef['zdesk_config']['zdesk_api'])

            payload = "{\n\"request\": \n{\n\"subject\": \"" + companyName + ":" + str(requestSubject) + "\", \n \"priority\": \"normal\",\n\"type\": \"incident\",\n\"comment\": \n{\n\"body\": \"" + str(
                requestComment) + "\"\n}\n}\n}"

            # payload = \
            # {
            #         'request': {
            #             # 'requester': {
            #             #     'name': '',
            #             #     'email': '',
            #             # },
            #     #{
            #         'subject': str(requestSubject),
            #         'comment':
            #             {
            #                 'body': str(requestComment)
            #             },
            #         'priority': "normal",
            #         'type': "incident",
            #         'ticket_field_entries':
            #             {
            #                 'ticket_field_id': _configDef['zdesk_config']['zdesk_sev_field'],
            #                 'value': 'severity_3'
            #             },
            #     }
            # }

            # print(type(payload))

            base64Encoded = base64.b64encode(bytes((emailZendesk + "/token:" + _configDef['zdesk_config']['zdesk_password']), 'utf-8'))
            base64Enc = (base64Encoded.decode("utf-8"))
            #print(str(base64Enc))
            base = ("Basic " + base64Enc)
            #print(str(base))

            headers = {
                'email_address': emailZendesk + "/token",
                'password': (_configDef['zdesk_config']['zdesk_password']),
                'authorization': base,
                'cache-control': "no-cache",
                'content-type': "application/json"
            }
            #print(str(headers))

            conn.request("POST", "/api/v2/requests.json", payload, headers)

            res = conn.getresponse()
            data = res.read()
            tempdata = (data.decode("utf-8"))
            result = str(tempdata)

            ticketidSplit = result.split(":")
            ticketURLid = ticketidSplit[4][:-9]

            link = _configDef['zdesk_config']['zdesk_link'] + ticketURLid
            linkCreated = "<a href =\"" + _configDef['zdesk_config']['zdesk_link'] + ticketURLid + "\">" + link + "</a>"

            messageDetail.ReplyToChatV2("New Zendesk Request created: " + linkCreated)

            ##      Will show the Ticket details in a table format.
            headers_ticket = {
                'email_address': emailZendesk + "/token",
                'password': (_configDef['zdesk_config']['zdesk_password']),
                'authorization': base
            }

            try:

                conn.request("GET", "/api/v2/tickets/" + ticketURLid + ".json", headers=headers_ticket)
                res = conn.getresponse()
                data = res.read()
                request_raw = data.decode("utf-8")

                data_raw = json.dumps(request_raw, indent=2)
                data_dict = ast.literal_eval(data_raw)
                d = json.loads(data_dict)

                requestid = str(d["ticket"]["id"])
                requeststatus = str(d["ticket"]["status"])
                requestpriority = str(d["ticket"]["priority"])
                requestseverity = str(d["ticket"]["tags"])

                if (len(d["ticket"]["tags"])) == 0:
                    noTag = True
                else:
                    noTag = False

                notSet = True

                if noTag:
                    sev = "Not set"
                    notSet = False

                for index_tags in range(len(d["ticket"]["tags"])):
                    tags = str((d["ticket"]["tags"][index_tags]))

                    if tags.startswith("severity_1"):
                        sev = "Severity 1"
                        notSet = False
                    elif tags.startswith("severity_2"):
                        sev = "Severity 2"
                        notSet = False
                    elif tags.startswith("severity_3"):
                        sev = "Severity 3"
                        notSet = False
                    elif tags.startswith("severity_4"):
                        sev = "Severity 4"
                        notSet = False

                if notSet:
                    sev = "Not Set"
                    notSet = False

                requestseverity = sev

                requestsubject_temps = str(d["ticket"]["subject"]).replace("<", "&lt;").replace("\"", "&quot;").replace("&", "&amp;").replace("'","&apos;").replace(">","&gt;")
                requestsubject = str(requestsubject_temps)
                requestdescription_temps = str(d["ticket"]["description"])
                requestdescription = str(requestdescription_temps).replace("<", "&lt;").replace("\"", "&quot;").replace("&", "&amp;").replace("'","&apos;").replace(">","&gt;")
                requestorganization_id = str(d["ticket"]["organization_id"])
                requestrequester_id = str(d["ticket"]["requester_id"])
                requestcreated_at = str(d["ticket"]["created_at"]).replace("T", " ").replace("Z", "")
                requestupdated_at = str(d["ticket"]["updated_at"]).replace("T", " ").replace("Z", "")
                requestassignee_id = str(d["ticket"]["assignee_id"])

            except:
                conn.request("GET", "/api/v2/requests/" + ticketURLid + ".json", headers=headers_ticket)
                res = conn.getresponse()
                data = res.read()
                request_raw = data.decode("utf-8")

                data_raw = json.dumps(request_raw, indent=2)
                data_dict = ast.literal_eval(data_raw)
                d = json.loads(data_dict)

                requestid = str(d["request"]["id"])
                requeststatus = str(d["request"]["status"])
                requestpriority = str(d["request"]["priority"])
                # requestseverity = str(d["request"]["severity"])
                requestsubject_temps = str(d["request"]["subject"])
                requestsubject = str(requestsubject_temps).replace("<", "&lt;").replace("\"", "&quot;").replace("&", "&amp;").replace("'","&apos;").replace(">","&gt;")
                requestdescription_temps = str(d["request"]["description"])
                requestdescription = str(requestdescription_temps).replace("<", "&lt;").replace("\"", "&quot;").replace("&", "&amp;").replace("'","&apos;").replace(">","&gt;")
                requestorganization_id = str(d["request"]["organization_id"])
                requestrequester_id = str(d["request"]["requester_id"])
                requestcreated_at = str(d["request"]["created_at"]).replace("T", " ").replace("Z", "")
                requestupdated_at = str(d["request"]["updated_at"]).replace("T", " ").replace("Z", "")
                requestassignee_id = str(d["request"]["assignee_id"])

            request_id = str(requestid)
            request_status = str(requeststatus)
            request_priority = str(requestpriority)
            # request_severity = str(requestseverity)
            request_severity = ("Not set")
            request_subject = str(requestsubject)
            request_desc = str(requestdescription)
            desc = str(request_desc)
            request_org = str(requestorganization_id)
            request_requestor = str(requestrequester_id)
            request_created = str(requestcreated_at)
            request_updated = str(requestupdated_at)

            # To get the name of the requester given the requesterID

            headers_users = {
                'email_address': _configDef['zdesk_config']['zdesk_email'] + "/token",
                'password': (_configDef['zdesk_config']['zdesk_password']),
                'authorization': _configDef['zdesk_config']['zdesk_auth'],
                'content-type': "application/json"
            }

            conn.request("GET", "/api/v2/users/" + request_requestor, headers=headers_users)
            res = conn.getresponse()
            userRequesterId = res.read()
            tempUserRequester = str(userRequesterId.decode('utf-8'))

            data = json.dumps(tempUserRequester, indent=2)
            data_dict = ast.literal_eval(data)
            d = json.loads(data_dict)
            req_name = str(d["user"]["name"])
            requesterName = req_name

            try:
                request_assignee = str(requestassignee_id)
                # To get the name of the assignee given the assigneeID
                conn.request("GET", "/api/v2/users/" + request_assignee, headers=headers)
                res = conn.getresponse()
                userAssigneeId = res.read()
                tempUserAssignee = str(userAssigneeId.decode('utf-8'))

                data = json.dumps(tempUserAssignee, indent=2)
                data_dict = ast.literal_eval(data)
                d = json.loads(data_dict)
                assign_name = str(d["user"]["name"])
                assigneeName = assign_name

            except:
                assigneeName = "Not assigned"
                assignee_flag = True

            requesterTicket = (_configDef['zdesk_config']['zdesk_link']) + str(request_id) + "/requester/requested_tickets"
            assigneeTicket = (_configDef['zdesk_config']['zdesk_url']) + "/agent/users/" + request_assignee + "/assigned_tickets"
            OrgTicket = (_configDef['zdesk_config']['zdesk_link']) + str(request_id) + "/organization/tickets"

            # Convert the Zendesk ID to company name
            headers_org = {
                'email_address': _configDef['zdesk_config']['zdesk_email'] + "/token",
                'password': (_configDef['zdesk_config']['zdesk_password']),
                'authorization': _configDef['zdesk_config']['zdesk_auth'],
                'content-type': "application/json"
            }

            conn.request("GET", "/api/v2/users/" + requestrequester_id + "/organizations.json", headers=headers_org)
            res = conn.getresponse()
            companyID = res.read()
            compNameRaw = str(companyID.decode("utf-8"))

            data = json.dumps(compNameRaw, indent=2)
            data_dict = ast.literal_eval(data)
            d = json.loads(data_dict)
            org_Name = str(d["organizations"][0]["name"])
            orgName = str(org_Name)

            table_body = ""
            table_header = "<table style='border-collapse:collapse;border:2px solid black;table-layout:auto;width:100%;box-shadow: 5px 5px'><thead><tr style='background-color:#4D94FF;color:#ffffff;font-size:1rem' class=\"tempo-text-color--white tempo-bg-color--black\">" \
                           "<td style='width:20%;border:1px solid blue;border-bottom: double blue;text-align:center'>SUBJECT</td>" \
                           "<td style='width:30%;border:1px solid blue;border-bottom: double blue;text-align:center'>DESCRIPTION</td>" \
                           "<td style='width:2.5%;border:1px solid blue;border-bottom: double blue;text-align:center'>ID</td>" \
                           "<td style='width:3%;border:1px solid blue;border-bottom: double blue;text-align:center'>STATUS</td>" \
                           "<td style='width:3%;border:1px solid blue;border-bottom: double blue;text-align:center'>PRIORITY</td>" \
                           "<td style='width:3.5%;border:1px solid blue;border-bottom: double blue;text-align:center'>SEVERITY</td>" \
                           "<td style='width:5%;border:1px solid blue;border-bottom: double blue;text-align:center'>COMPANY</td>" \
                           "<td style='width:7%;border:1px solid blue;border-bottom: double blue;text-align:center'>REQUESTER</td>" \
                           "<td style='width:7%;border:1px solid blue;border-bottom: double blue;text-align:center'>CREATED</td>" \
                           "<td style='width:7%;border:1px solid blue;border-bottom: double blue;text-align:center'>UPDATED</td>" \
                           "<td style='width:7%;border:1px solid blue;border-bottom: double blue;text-align:center'>ASSIGNEE</td>" \
                           "</tr></thead><tbody>"

            if assignee_flag:

                table_body += "<tr>" \
                              "<td style='border:1px solid black;text-align:left'>" + request_subject + "</td>" \
                              "<td style='border:1px solid black;text-align:left'>" + desc + "</td>" \
                              "<td style='border:1px solid black;text-align:center'><a href=\"" + (_configDef['zdesk_config']['zdesk_link']) + str(request_id) + "\">" + str(request_id) + "</a></td>" \
                              "<td style='border:1px solid black;text-align:center'>" + request_status + "</td>" \
                              "<td style='border:1px solid black;text-align:center'>" + request_priority + "</td>" \
                              "<td style='border:1px solid black;text-align:center'>" + str(request_severity) + "</td>" \
                              "<td style='border:1px solid black;text-align:center'><a href=\"" + OrgTicket + "\">" + orgName + "</a></td>" \
                              "<td style='border:1px solid black;text-align:center'><a href=\"" + requesterTicket + "\">" + str(requesterName) + "</a></td>" \
                              "<td style='border:1px solid black;text-align:center'>" + request_created + "</td>" \
                              "<td style='border:1px solid black;text-align:center'>" + request_updated + "</td>" \
                              "<td style='border:1px solid black;text-align:center'>" + assigneeName + "</td>" \
                              "</tr>" \
                              "</tbody></table>"

            else:
                table_body += "<tr>" \
                              "<td style='border:1px solid black;text-align:left'>" + request_subject + "</td>" \
                              "<td style='border:1px solid black;text-align:left'>" + desc + "</td>" \
                              "<td style='border:1px solid black;text-align:center'><a href=\"" + (_configDef['zdesk_config']['zdesk_link']) + str(request_id) + "\">" + str(request_id) + "</a></td>" \
                              "<td style='border:1px solid black;text-align:center'>" + request_status + "</td>" \
                              "<td style='border:1px solid black;text-align:center'>" + request_priority + "</td>" \
                              "<td style='border:1px solid black;text-align:center'>" + str(request_severity) + "</td>" \
                              "<td style='border:1px solid black;text-align:center'><a href=\"" + OrgTicket + "\">" + orgName + "</a></td>" \
                              "<td style='border:1px solid black;text-align:center'><a href=\"" + requesterTicket + "\">" + str(requesterName) + "</a></td>" \
                              "<td style='border:1px solid black;text-align:center'>" + request_created + "</td>" \
                              "<td style='border:1px solid black;text-align:center'>" + request_updated + "</td>" \
                              "<td style='border:1px solid black;text-align:center'><a href=\"" + assigneeTicket + "\">" + str(assigneeName) + "</a></td>" \
                              "</tr>" \
                              "</tbody></table>"

                reply = table_header + table_body
                return messageDetail.ReplyToChatV2_noBotLog(reply)

    ############################

    except:
        return messageDetail.ReplyToChat("I am sorry, I was working on a different task, can you please retry")


def newTicketToday(messageDetail):
    botlog.LogSymphonyInfo("################################################")
    botlog.LogSymphonyInfo("Bot Call: Retrieve ticket(s) created based today")
    botlog.LogSymphonyInfo("################################################")

    try:
        isAllowed = False
        commandCallerUID = messageDetail.FromUserId

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

            ##############################
            try:
                emailAddress = d_org["users"][index_org]["emailAddress"]
                #print("User is connected: " + emailAddress)
                emailZendesk = emailAddress
                #print(emailZendesk)
                connectionRequired = False
                # isAllowed = True
            except:
                connectionRequired = True

            # if connectionRequired:

            data_lenght = len(dataComp)

            if data_lenght > 450:
                try:
                    #print("inside > 450")
                    query = "type:user " + emailAddress
                except:
                    query = "type:user " + firstName + " " + lastName
                #print(query)
            elif data_lenght < 450:
                try:
                    #print("inside < 450")
                    #query = "type:user " + emailAddress + " organization:" + companyName
                    query = "type:user " + emailAddress
                except:
                    #query = "type:user " + firstName + " " + lastName + " organization:" + companyName
                    query = "type:user " + firstName + " " + lastName
                #print(query)
            else:
                return messageDetail.ReplyToChat("No user information available")

            #print(query)
            results = zendesk.search(query=query)
            #print(results)

            if str(results).startswith(
                    "{'results': [], 'facets': None, 'next_page': None, 'previous_page': None, 'count': 0}"):
                return messageDetail.ReplyToChat(
                    "This user does not exist on Zendesk, the name is misspelled or does not belong to this organisation")
            elif str(results).startswith(
                    "{'results': [], 'facets': {'type': {'entry': 0, 'ticket': 0, 'organization': 0, 'user': 0, 'article': 0, 'group': 0}}, 'next_page': None, 'previous_page': None, 'count': 0}"):
                return messageDetail.ReplyToChat(
                    "This organisation/company does not exist in Zendesk or name is misspelled.")
            else:

                data = json.dumps(results, indent=2)
                d = json.loads(data)

                for index in range(len(d["results"])):
                    name = d["results"][index]["name"]
                    email = str(d["results"][index]["email"])
                    #print("EmailAddress from Zendesk: " + email)

                    role = str(d["results"][index]["role"])
                    botlog.LogSymphonyInfo("The calling user is a Zendesk " + role)

                    #if role == "Administrator" or role == "admin" or role == "Agent" or role == "agent":
                    if role == "Administrator" or role == "admin" or role == "Agent" or role == "agent":
                        isAllowed = True
                        botlog.LogSymphonyInfo("User is an " + role + " on Zendesk")
                    else:
                        isAllowed = False

                emailZendesk = email

            botlog.LogSymphonyInfo(firstName + " " + lastName + " (" + displayName + ") from Company/Pod name: " + str(companyName) + " with UID: " + str(userID))
            callerCheck = (firstName + " " + lastName + " - " + displayName + " - " + companyName + " - " + str(userID))


        if callerCheck in AccessFile and isAllowed:
            botlog.LogSymphonyInfo("User is an " + role + " on Zendesk and an Agent or Admin with the bot")

            showRequest = (messageDetail.Command.MessageText)
            message_split = showRequest.split()

            try:
                todayMinusDays = message_split[0]
                todayTicket = int(todayMinusDays)
            except:
                return messageDetail.ReplyToChat("Please use number of days to check back such as /today 1")

            if int(todayMinusDays) > 7:
                return messageDetail.ReplyToChat("For optimal performance, please use 7 days or less in your query")

            ticketdate_raw = datetime.today() - timedelta(days=int(todayTicket))
            ticketdate = str(ticketdate_raw)[:-16]

            conn = http.client.HTTPSConnection(_configDef['zdesk_config']['zdesk_api'])

            headers = {
                'username': _configDef['zdesk_config']['zdesk_email'] + "/token",
                'password': _configDef['zdesk_config']['zdesk_password'],
                'authorization': _configDef['zdesk_config']['zdesk_auth'],
                'cache-control': "no-cache",
                'Content-Type': 'application/json',
            }

            # base64Encoded = base64.b64encode(bytes((emailZendesk + "/token:" + _configDef['zdesk_config']['zdesk_password']), 'utf-8'))
            # base64Enc = (base64Encoded.decode("utf-8"))
            # print(str(base64Enc))
            # base = ("Basic " + base64Enc)
            # print(str(base))
            #
            # headers = {
            #             'email_address': emailZendesk +"/token",
            #             'password': (_configDef['zdesk_config']['zdesk_password']),
            #             'authorization': base,
            #             'cache-control': "no-cache",
            #             'content-type': "application/json"
            # }

            conn.request("GET", "/api/v2/search?query=type%3Aticket%20created%3E" + str(ticketdate), headers=headers)

            res = conn.getresponse()
            data = res.read().decode("utf-8")
            reply = str(data)
            #print(data)

            messageDetail.ReplyToChatV2("Loading Tickets created from " + ticketdate + " Please wait.")

            if str(reply).startswith("{\"results\":[],\"facets\":null,\"next_page\":null,\"previous_page\":null,\"count\":0}"):
                return messageDetail.ReplyToChatV2("No Zendesk ticket was created on " + ticketdate)

            data = json.dumps(reply, indent=2)
            data_dict = ast.literal_eval(data)
            d_tick = json.loads(data_dict)
            #print(d_tick)

            table_body = ""
            table_header = "<table style='border-collapse:collapse;border:2px solid black;table-layout:auto;width:100%;box-shadow: 5px 5px'><thead><tr style='background-color:#4D94FF;color:#ffffff;font-size:1rem' class=\"tempo-text-color--white tempo-bg-color--black\">" \
                           "<td style='width:20%;border:1px solid blue;border-bottom: double blue;text-align:center'>SUBJECT</td>" \
                           "<td style='width:30%;border:1px solid blue;border-bottom: double blue;text-align:center'>DESCRIPTION</td>" \
                           "<td style='width:2.5%;border:1px solid blue;border-bottom: double blue;text-align:center'>ID</td>" \
                           "<td style='width:3%;border:1px solid blue;border-bottom: double blue;text-align:center'>STATUS</td>" \
                           "<td style='width:3%;border:1px solid blue;border-bottom: double blue;text-align:center'>PRIORITY</td>" \
                           "<td style='width:3.5%;border:1px solid blue;border-bottom: double blue;text-align:center'>SEVERITY</td>" \
                           "<td style='width:5%;border:1px solid blue;border-bottom: double blue;text-align:center'>COMPANY</td>" \
                           "<td style='width:7%;border:1px solid blue;border-bottom: double blue;text-align:center'>REQUESTER</td>" \
                           "<td style='width:7%;border:1px solid blue;border-bottom: double blue;text-align:center'>CREATED</td>" \
                           "<td style='width:7%;border:1px solid blue;border-bottom: double blue;text-align:center'>UPDATED</td>" \
                           "<td style='width:7%;border:1px solid blue;border-bottom: double blue;text-align:center'>ASSIGNEE</td>" \
                           "</tr></thead><tbody>"

            index = 1
            for index in range(len(d_tick["results"])):

                requestid = str(d_tick["results"][index]["id"])
                #print(requestid)
                requeststatus = str(d_tick["results"][index]["status"])
                #print(requeststatus)
                requestpriority = str(d_tick["results"][index]["priority"])
                #print(requestpriority)
                requestseverity = str(d_tick["results"][index]["tags"])

                if (len(d_tick["results"][index]["tags"])) == 0:
                    noTag = True
                else:
                    noTag = False

                notSet = True

                if noTag:
                    sev = "Not set"
                    notSet = False

                for index_tags in range(len(d_tick["results"][index]["tags"])):
                    tags = str((d_tick["results"][index]["tags"][index_tags]))

                    if tags.startswith("severity_1"):
                        sev = "Severity 1"
                        notSet = False
                    elif tags.startswith("severity_2"):
                        sev = "Severity 2"
                        notSet = False
                    elif tags.startswith("severity_3"):
                        sev = "Severity 3"
                        notSet = False
                    elif tags.startswith("severity_4"):
                        sev = "Severity 4"
                        notSet = False

                if notSet:
                    sev = "Not Set"
                    notSet = False

                requestseverity = sev
                assignee_flag = False
                #print(sev)

                requestsubject_temps = str(d_tick["results"][index]["subject"])
                requestsubject = str(requestsubject_temps).replace("<", "&lt;").replace("\"", "&quot;").replace("&", "&amp;").replace("'","&apos;").replace(">","&gt;")
                requestdescription_temps = str(d_tick["results"][index]["description"])
                requestdescription = str(requestdescription_temps).replace("<", "&lt;").replace("\"", "&quot;").replace("&", "&amp;").replace("'","&apos;").replace(">","&gt;")
                requestorganization_id = str(d_tick["results"][index]["organization_id"])
                requestrequester_id = str(d_tick["results"][index]["requester_id"])
                #print(requestrequester_id)
                requestcreated_at = str(d_tick["results"][index]["created_at"]).replace("T", " ").replace("Z", "")
                requestupdated_at = str(d_tick["results"][index]["updated_at"]).replace("T", " ").replace("Z", "")
                requestassignee_id = str(d_tick["results"][index]["assignee_id"])

                request_id = str(requestid)
                #print(request_id)
                request_status = str(requeststatus)
                request_priority = str(requestpriority)
                request_severity = str(requestseverity)
                request_subject = str(requestsubject)
                request_desc = str(requestdescription)
                desc = str(request_desc)
                request_org = str(requestorganization_id)
                request_requestor = str(requestrequester_id)
                #print(request_requestor)
                request_created = str(requestcreated_at)
                request_updated = str(requestupdated_at)

                # To get the name of the requester given the requesterID
                conn.request("GET", "/api/v2/users/" + request_requestor, headers=headers)
                res = conn.getresponse()
                userRequesterId = res.read()
                tempUserRequester = str(userRequesterId.decode('utf-8'))

                data = json.dumps(tempUserRequester, indent=2)
                data_dict = ast.literal_eval(data)
                d_req = json.loads(data_dict)
                req_name = str(d_req["user"]["name"])
                requesterName = req_name
                #print(requesterName)

                try:
                    request_assignee = str(requestassignee_id)

                    # To get the name of the assignee given the assigneeID
                    conn.request("GET", "/api/v2/users/" + request_assignee, headers=headers)
                    res = conn.getresponse()
                    userAssigneeId = res.read()
                    tempUserAssignee = str(userAssigneeId.decode('utf-8'))

                    data = json.dumps(tempUserAssignee, indent=2)
                    data_dict = ast.literal_eval(data)
                    d_user = json.loads(data_dict)
                    assign_name = str(d_user["user"]["name"])
                    assigneeName = assign_name
                    #print(assigneeName)

                except:
                    assigneeName = "Not assigned"
                    assignee_flag = True

                requesterTicket = (_configDef['zdesk_config']['zdesk_link']) + str(request_id) + "/requester/requested_tickets"
                assigneeTicket = (_configDef['zdesk_config']['zdesk_url']) + "/agent/users/" + str(request_assignee) + "/assigned_tickets"
                OrgTicket = (_configDef['zdesk_config']['zdesk_link']) + str(request_id) + "/organization/tickets"

                # Convert the Zendesk ID to company name
                conn.request("GET", "/api/v2/users/" + requestrequester_id + "/organizations.json", headers=headers)
                res = conn.getresponse()
                companyID = res.read()
                compNameRaw = str(companyID.decode("utf-8"))

                data = json.dumps(compNameRaw, indent=2)
                data_dict = ast.literal_eval(data)
                d_org = json.loads(data_dict)
                org_Name = str(d_org["organizations"][0]["name"])
                orgName = str(org_Name)
                #print(orgName)

                if assignee_flag:

                    table_body += "<tr>" \
                                  "<td style='border:1px solid black;text-align:left'>" + request_subject + "</td>" \
                                  "<td style='border:1px solid black;text-align:left'>" + desc + "</td>" \
                                  "<td style='border:1px solid black;text-align:center'><a href=\"" + (_configDef['zdesk_config']['zdesk_link']) + str(request_id) + "\">" + str(request_id) + "</a></td>" \
                                  "<td style='border:1px solid black;text-align:center'>" + request_status + "</td>" \
                                  "<td style='border:1px solid black;text-align:center'>" + request_priority + "</td>" \
                                  "<td style='border:1px solid black;text-align:center'>" + request_severity + "</td>" \
                                  "<td style='border:1px solid black;text-align:center'><a href=\"" + OrgTicket + "\">" + orgName + "</a></td>" \
                                  "<td style='border:1px solid black;text-align:center'><a href=\"" + requesterTicket + "\">" + str(requesterName) + "</a></td>" \
                                  "<td style='border:1px solid black;text-align:center'>" + request_created + "</td>" \
                                  "<td style='border:1px solid black;text-align:center'>" + request_updated + "</td>" \
                                  "<td style='border:1px solid black;text-align:center'>" + assigneeName + "</td>" \
                                  "</tr>"

                else:
                    table_body += "<tr>" \
                                  "<td style='border:1px solid black;text-align:left'>" + request_subject + "</td>" \
                                  "<td style='border:1px solid black;text-align:left'>" + desc + "</td>" \
                                  "<td style='border:1px solid black;text-align:center'><a href=\"" + (_configDef['zdesk_config']['zdesk_link']) + str(request_id) + "\">" + str(request_id) + "</a></td>" \
                                  "<td style='border:1px solid black;text-align:center'>" + request_status + "</td>" \
                                  "<td style='border:1px solid black;text-align:center'>" + request_priority + "</td>" \
                                  "<td style='border:1px solid black;text-align:center'>" + request_severity + "</td>" \
                                  "<td style='border:1px solid black;text-align:center'><a href=\"" + OrgTicket + "\">" + orgName + "</a></td>" \
                                  "<td style='border:1px solid black;text-align:center'><a href=\"" + requesterTicket + "\">" + str(requesterName) + "</a></td>" \
                                  "<td style='border:1px solid black;text-align:center'>" + request_created + "</td>" \
                                  "<td style='border:1px solid black;text-align:center'>" + request_updated + "</td>" \
                                  "<td style='border:1px solid black;text-align:center'><a href=\"" + assigneeTicket + "\">" + str(assigneeName) + "</a></td>" \
                                  "</tr>"

            table_body += "</tbody></table>"
            render = table_header + table_body
            return messageDetail.ReplyToChatV2("<card iconSrc =\"https://thumb.ibb.co/csXBgU/Symphony2018_App_Icon_Mobile.png\" accent=\"tempo-bg-color--blue\"><header>Please find below Zendesk ticket(s) recently opened</header><body>" + render + "</body></card>")
        else:
            return messageDetail.ReplyToChat("You aren't authorised to use this command. You are either not added to the Agent list with the Bot or you are not an Admin or Agent/staff on Zendesk")
    except:
        try:
            botlog.LogSymphonyInfo("Inside second try for newTicketToday")
            isAllowed = False
            commandCallerUID = messageDetail.FromUserId

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

                ##############################
                try:
                    emailAddress = d_org["users"][index_org]["emailAddress"]
                    # print("User is connected: " + emailAddress)
                    emailZendesk = emailAddress
                    # print(emailZendesk)
                    connectionRequired = False
                    # isAllowed = True
                except:
                    connectionRequired = True

                # if connectionRequired:

                data_lenght = len(dataComp)

                if data_lenght > 450:
                    try:
                        # print("inside > 450")
                        query = "type:user " + emailAddress
                    except:
                        query = "type:user " + firstName + " " + lastName
                    # print(query)
                elif data_lenght < 450:
                    try:
                        # print("inside < 450")
                        # query = "type:user " + emailAddress + " organization:" + companyName
                        query = "type:user " + emailAddress
                    except:
                        # query = "type:user " + firstName + " " + lastName + " organization:" + companyName
                        query = "type:user " + firstName + " " + lastName
                    # print(query)
                else:
                    return messageDetail.ReplyToChat("No user information available")

                # print(query)
                results = zendesk.search(query=query)
                # print(results)

                if str(results).startswith(
                        "{'results': [], 'facets': None, 'next_page': None, 'previous_page': None, 'count': 0}"):
                    return messageDetail.ReplyToChat(
                        "This user does not exist on Zendesk, the name is misspelled or does not belong to this organisation")
                elif str(results).startswith(
                        "{'results': [], 'facets': {'type': {'entry': 0, 'ticket': 0, 'organization': 0, 'user': 0, 'article': 0, 'group': 0}}, 'next_page': None, 'previous_page': None, 'count': 0}"):
                    return messageDetail.ReplyToChat(
                        "This organisation/company does not exist in Zendesk or name is misspelled.")
                else:

                    data = json.dumps(results, indent=2)
                    d = json.loads(data)

                    for index in range(len(d["results"])):
                        name = d["results"][index]["name"]
                        email = str(d["results"][index]["email"])
                        # print("EmailAddress from Zendesk: " + email)

                        role = str(d["results"][index]["role"])
                        botlog.LogSymphonyInfo("The calling user is a Zendesk " + role)

                        # if role == "Administrator" or role == "admin" or role == "Agent" or role == "agent":
                        if role == "Administrator" or role == "admin" or role == "Agent" or role == "agent":
                            isAllowed = True
                            botlog.LogSymphonyInfo("User is an " + role + " on Zendesk")
                        else:
                            isAllowed = False

                    emailZendesk = email

                botlog.LogSymphonyInfo(
                    firstName + " " + lastName + " (" + displayName + ") from Company/Pod name: " + str(
                        companyName) + " with UID: " + str(userID))
                callerCheck = (firstName + " " + lastName + " - " + displayName + " - " + companyName + " - " + str(
                    userID))

            if callerCheck in AccessFile and isAllowed:
                botlog.LogSymphonyInfo("User is an " + role + " on Zendesk and an Agent or Admin with the bot")

                showRequest = (messageDetail.Command.MessageText)
                message_split = showRequest.split()

                try:
                    todayMinusDays = message_split[0]
                    todayTicket = int(todayMinusDays)
                except:
                    return messageDetail.ReplyToChat("Please use number of days to check back such as /today 1")

                if int(todayMinusDays) > 7:
                    return messageDetail.ReplyToChat("For optimal performance, please use 7 days or less in your query")

                ticketdate_raw = datetime.today() - timedelta(days=int(todayTicket))
                ticketdate = str(ticketdate_raw)[:-16]

                conn = http.client.HTTPSConnection(_configDef['zdesk_config']['zdesk_api'])

                headers = {
                    'username': _configDef['zdesk_config']['zdesk_email'] + "/token",
                    'password': _configDef['zdesk_config']['zdesk_password'],
                    'authorization': _configDef['zdesk_config']['zdesk_auth'],
                    'cache-control': "no-cache",
                    'Content-Type': 'application/json',
                }

                # base64Encoded = base64.b64encode(bytes((emailZendesk + "/token:" + _configDef['zdesk_config']['zdesk_password']), 'utf-8'))
                # base64Enc = (base64Encoded.decode("utf-8"))
                # print(str(base64Enc))
                # base = ("Basic " + base64Enc)
                # print(str(base))
                #
                # headers = {
                #             'email_address': emailZendesk +"/token",
                #             'password': (_configDef['zdesk_config']['zdesk_password']),
                #             'authorization': base,
                #             'cache-control': "no-cache",
                #             'content-type': "application/json"
                # }

                conn.request("GET", "/api/v2/search?query=type%3Aticket%20created%3E" + str(ticketdate),
                             headers=headers)

                res = conn.getresponse()
                data = res.read().decode("utf-8")
                reply = str(data)
                # print(data)

                messageDetail.ReplyToChatV2("Loading Tickets created from " + ticketdate + " Please wait.")

                if str(reply).startswith(
                        "{\"results\":[],\"facets\":null,\"next_page\":null,\"previous_page\":null,\"count\":0}"):
                    return messageDetail.ReplyToChatV2("No Zendesk ticket was created on " + ticketdate)

                data = json.dumps(reply, indent=2)
                data_dict = ast.literal_eval(data)
                d_tick = json.loads(data_dict)
                # print(d_tick)

                table_body = ""
                table_header = "<table style='border-collapse:collapse;border:2px solid black;table-layout:auto;width:100%;box-shadow: 5px 5px'><thead><tr style='background-color:#4D94FF;color:#ffffff;font-size:1rem' class=\"tempo-text-color--white tempo-bg-color--black\">" \
                               "<td style='width:20%;border:1px solid blue;border-bottom: double blue;text-align:center'>SUBJECT</td>" \
                               "<td style='width:30%;border:1px solid blue;border-bottom: double blue;text-align:center'>DESCRIPTION</td>" \
                               "<td style='width:2.5%;border:1px solid blue;border-bottom: double blue;text-align:center'>ID</td>" \
                               "<td style='width:3%;border:1px solid blue;border-bottom: double blue;text-align:center'>STATUS</td>" \
                               "<td style='width:3%;border:1px solid blue;border-bottom: double blue;text-align:center'>PRIORITY</td>" \
                               "<td style='width:3.5%;border:1px solid blue;border-bottom: double blue;text-align:center'>SEVERITY</td>" \
                               "<td style='width:5%;border:1px solid blue;border-bottom: double blue;text-align:center'>COMPANY</td>" \
                               "<td style='width:7%;border:1px solid blue;border-bottom: double blue;text-align:center'>REQUESTER</td>" \
                               "<td style='width:7%;border:1px solid blue;border-bottom: double blue;text-align:center'>CREATED</td>" \
                               "<td style='width:7%;border:1px solid blue;border-bottom: double blue;text-align:center'>UPDATED</td>" \
                               "<td style='width:7%;border:1px solid blue;border-bottom: double blue;text-align:center'>ASSIGNEE</td>" \
                               "</tr></thead><tbody>"

                index = 1
                for index in range(len(d_tick["results"])):

                    requestid = str(d_tick["results"][index]["id"])
                    # print(requestid)
                    requeststatus = str(d_tick["results"][index]["status"])
                    # print(requeststatus)
                    requestpriority = str(d_tick["results"][index]["priority"])
                    # print(requestpriority)
                    requestseverity = str(d_tick["results"][index]["tags"])

                    if (len(d_tick["results"][index]["tags"])) == 0:
                        noTag = True
                    else:
                        noTag = False

                    notSet = True

                    if noTag:
                        sev = "Not set"
                        notSet = False

                    for index_tags in range(len(d_tick["results"][index]["tags"])):
                        tags = str((d_tick["results"][index]["tags"][index_tags]))

                        if tags.startswith("severity_1"):
                            sev = "Severity 1"
                            notSet = False
                        elif tags.startswith("severity_2"):
                            sev = "Severity 2"
                            notSet = False
                        elif tags.startswith("severity_3"):
                            sev = "Severity 3"
                            notSet = False
                        elif tags.startswith("severity_4"):
                            sev = "Severity 4"
                            notSet = False

                    if notSet:
                        sev = "Not Set"
                        notSet = False

                    requestseverity = sev
                    assignee_flag = False
                    # print(sev)

                    requestsubject_temps = str(d_tick["results"][index]["subject"])
                    requestsubject = str(requestsubject_temps).replace("<", "&lt;").replace("\"", "&quot;").replace("&","&amp;").replace("'", "&apos;").replace(">", "&gt;")
                    requestdescription_temps = str(d_tick["results"][index]["description"])
                    requestdescription = str(requestdescription_temps).replace("<", "&lt;").replace("\"","&quot;").replace("&", "&amp;").replace("'", "&apos;").replace(">", "&gt;")
                    requestorganization_id = str(d_tick["results"][index]["organization_id"])
                    requestrequester_id = str(d_tick["results"][index]["requester_id"])
                    # print(requestrequester_id)
                    requestcreated_at = str(d_tick["results"][index]["created_at"]).replace("T", " ").replace("Z", "")
                    requestupdated_at = str(d_tick["results"][index]["updated_at"]).replace("T", " ").replace("Z", "")
                    requestassignee_id = str(d_tick["results"][index]["assignee_id"])

                    request_id = str(requestid)
                    # print(request_id)
                    request_status = str(requeststatus)
                    request_priority = str(requestpriority)
                    request_severity = str(requestseverity)
                    request_subject = str(requestsubject)
                    request_desc = str(requestdescription)
                    desc = str(request_desc)
                    request_org = str(requestorganization_id)
                    request_requestor = str(requestrequester_id)
                    # print(request_requestor)
                    request_created = str(requestcreated_at)
                    request_updated = str(requestupdated_at)

                    # To get the name of the requester given the requesterID
                    conn.request("GET", "/api/v2/users/" + request_requestor, headers=headers)
                    res = conn.getresponse()
                    userRequesterId = res.read()
                    tempUserRequester = str(userRequesterId.decode('utf-8'))

                    data = json.dumps(tempUserRequester, indent=2)
                    data_dict = ast.literal_eval(data)
                    d_req = json.loads(data_dict)
                    req_name = str(d_req["user"]["name"])
                    requesterName = req_name
                    # print(requesterName)

                    try:
                        request_assignee = str(requestassignee_id)

                        # To get the name of the assignee given the assigneeID
                        conn.request("GET", "/api/v2/users/" + request_assignee, headers=headers)
                        res = conn.getresponse()
                        userAssigneeId = res.read()
                        tempUserAssignee = str(userAssigneeId.decode('utf-8'))

                        data = json.dumps(tempUserAssignee, indent=2)
                        data_dict = ast.literal_eval(data)
                        d_user = json.loads(data_dict)
                        assign_name = str(d_user["user"]["name"])
                        assigneeName = assign_name
                        # print(assigneeName)

                    except:
                        assigneeName = "Not assigned"
                        assignee_flag = True

                    requesterTicket = (_configDef['zdesk_config']['zdesk_link']) + str(request_id) + "/requester/requested_tickets"
                    assigneeTicket = (_configDef['zdesk_config']['zdesk_url']) + "/agent/users/" + str(request_assignee) + "/assigned_tickets"
                    OrgTicket = (_configDef['zdesk_config']['zdesk_link']) + str(request_id) + "/organization/tickets"

                    # Convert the Zendesk ID to company name
                    conn.request("GET", "/api/v2/users/" + requestrequester_id + "/organizations.json", headers=headers)
                    res = conn.getresponse()
                    companyID = res.read()
                    compNameRaw = str(companyID.decode("utf-8"))

                    data = json.dumps(compNameRaw, indent=2)
                    data_dict = ast.literal_eval(data)
                    d_org = json.loads(data_dict)
                    org_Name = str(d_org["organizations"][0]["name"])
                    orgName = str(org_Name)
                    # print(orgName)

                    if assignee_flag:

                        table_body += "<tr>" \
                                      "<td style='border:1px solid black;text-align:left'>" + request_subject + "</td>" \
                                      "<td style='border:1px solid black;text-align:left'>" + desc + "</td>" \
                                      "<td style='border:1px solid black;text-align:center'><a href=\"" + (_configDef['zdesk_config']['zdesk_link']) + str(request_id) + "\">" + str(request_id) + "</a></td>" \
                                      "<td style='border:1px solid black;text-align:center'>" + request_status + "</td>" \
                                      "<td style='border:1px solid black;text-align:center'>" + request_priority + "</td>" \
                                      "<td style='border:1px solid black;text-align:center'>" + request_severity + "</td>" \
                                      "<td style='border:1px solid black;text-align:center'><a href=\"" + OrgTicket + "\">" + orgName + "</a></td>" \
                                      "<td style='border:1px solid black;text-align:center'><a href=\"" + requesterTicket + "\">" + str(requesterName) + "</a></td>" \
                                      "<td style='border:1px solid black;text-align:center'>" + request_created + "</td>" \
                                      "<td style='border:1px solid black;text-align:center'>" + request_updated + "</td>" \
                                      "<td style='border:1px solid black;text-align:center'>" + assigneeName + "</td>" \
                                      "</tr>"

                    else:
                        table_body += "<tr>" \
                                      "<td style='border:1px solid black;text-align:left'>" + request_subject + "</td>" \
                                      "<td style='border:1px solid black;text-align:left'>" + desc + "</td>" \
                                      "<td style='border:1px solid black;text-align:center'><a href=\"" + (_configDef['zdesk_config']['zdesk_link']) + str(request_id) + "\">" + str(request_id) + "</a></td>" \
                                      "<td style='border:1px solid black;text-align:center'>" + request_status + "</td>" \
                                      "<td style='border:1px solid black;text-align:center'>" + request_priority + "</td>" \
                                      "<td style='border:1px solid black;text-align:center'>" + request_severity + "</td>" \
                                      "<td style='border:1px solid black;text-align:center'><a href=\"" + OrgTicket + "\">" + orgName + "</a></td>" \
                                      "<td style='border:1px solid black;text-align:center'><a href=\"" + requesterTicket + "\">" + str(requesterName) + "</a></td>" \
                                      "<td style='border:1px solid black;text-align:center'>" + request_created + "</td>" \
                                      "<td style='border:1px solid black;text-align:center'>" + request_updated + "</td>" \
                                      "<td style='border:1px solid black;text-align:center'><a href=\"" + assigneeTicket + "\">" + str(assigneeName) + "</a></td>" \
                                      "</tr>"

                table_body += "</tbody></table>"
                render = table_header + table_body
                return messageDetail.ReplyToChatV2(
                    "<card iconSrc =\"https://thumb.ibb.co/csXBgU/Symphony2018_App_Icon_Mobile.png\" accent=\"tempo-bg-color--blue\"><header>Please find below Zendesk ticket(s) recently opened</header><body>" + render + "</body></card>")
            else:
                return messageDetail.ReplyToChat(
                    "You aren't authorised to use this command. You are either not added to the Agent list with the Bot or you are not an Admin or Agent/staff on Zendesk")
        except:
            return messageDetail.ReplyToChat("I am sorry, I was working on a different task, can you please retry")

def ticketUpdate(messageDetail):
    botlog.LogSymphonyInfo("###############################")
    botlog.LogSymphonyInfo("Bot Call: Ticket Update/comment")
    botlog.LogSymphonyInfo("###############################")

    try:
        isAllowed = False
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

        assignee_flag = ""

        for index_org in range(len(d_org["users"])):
            firstName = d_org["users"][index_org]["firstName"]
            lastName = d_org["users"][index_org]["lastName"]
            displayName = d_org["users"][index_org]["displayName"]
            companyName = d_org["users"][index_org]["company"]
            userID = str(d_org["users"][index_org]["id"])

            ##############################
            try:
                emailAddress = d_org["users"][index_org]["emailAddress"]
                botlog.LogSymphonyInfo("User is connected: " + emailAddress)
                emailZendesk = emailAddress
                #print(emailZendesk)
                connectionRequired = False
                #isAllowed = True
            except:
                connectionRequired = True

        #if connectionRequired:

            data_lenght = len(dataComp)

            if data_lenght > 450:
                try:
                    #print("inside > 450")
                    query = "type:user " + emailAddress
                except:
                    query = "type:user " + firstName + " " + lastName
                botlog.LogSymphonyInfo(query)
            elif data_lenght < 450:
                try:
                    #print("inside < 450")
                    #query = "type:user " + emailAddress + " organization:" + companyName
                    query = "type:user " + emailAddress
                except:
                    #query = "type:user " + firstName + " " + lastName + " organization:" + companyName
                    query = "type:user " + firstName + " " + lastName
                botlog.LogSymphonyInfo(query)
            else:
                return messageDetail.ReplyToChat("No user information available")

            botlog.LogSymphonyInfo(query)
            results = zendesk.search(query=query)
            #botlog.LogSymphonyInfo(str(results))

            if str(results).startswith(
                    "{'results': [], 'facets': None, 'next_page': None, 'previous_page': None, 'count': 0}"):
                return messageDetail.ReplyToChat(
                    "This user does not exist on Zendesk, the name is misspelled or does not belong to this organisation. Please use this format: /ticketUpdate ticketid| comment| status, public/private")
            elif str(results).startswith(
                    "{'results': [], 'facets': {'type': {'entry': 0, 'ticket': 0, 'organization': 0, 'user': 0, 'article': 0, 'group': 0}}, 'next_page': None, 'previous_page': None, 'count': 0}"):
                return messageDetail.ReplyToChat(
                    "This organisation/company does not exist in Zendesk or name is misspelled. Please use this format: /ticketUpdate ticketid| comment| status| public/private")
            else:

                data = json.dumps(results, indent=2)
                d = json.loads(data)

                for index in range(len(d["results"])):
                    name = d["results"][index]["name"]
                    email = str(d["results"][index]["email"])
                    #print("EmailAddress from Zendesk: " + email)
                    ZendeskUserID = str(d["results"][index]["id"])
                    botlog.LogSymphonyInfo("Zendesk User ID: " + ZendeskUserID)

                    role = str(d["results"][index]["role"])
                    botlog.LogSymphonyInfo("The calling user is a Zendesk " + role)

                    if role == "Administrator" or role == "admin" or role == "Agent" or role == "agent":
                        isAllowed = True
                    else:
                        isAllowed = False

                emailZendesk = email

        # else:
        #     botlog.LogSymphonyInfo("Calling user's Email Address: " + emailZendesk)

            ##############################

            botlog.LogSymphonyInfo(firstName + " " + lastName + " (" + displayName + ") from Company/Pod name: " + str(companyName) + " with UID: " + str(userID))
            callerCheck = (firstName + " " + lastName + " - " + displayName + " - " + companyName + " - " + str(userID))

        if callerCheck in AccessFile and isAllowed:
            botlog.LogSymphonyInfo("Calling user is part of Zendesk Agent List and is an Zendesk Agent or Admin.")
            comment_status = ""

            showRequest = (messageDetail.Command.MessageText)
            message_split = showRequest.split("|")

            ### /update idt, comment, status, private/false or public/true
            try:
                idt = str(message_split[0][1:]).strip()
                comment = str(message_split[1][1:]).replace("&quot;", "\"").replace("&amp;", "&").replace("&lt;", "<").replace("&apos;", "'").replace("&gt;", ">")
                status = str(message_split[2][1:]).strip()
                if str(status) == "open" or status == "Open" or status == "pending" or status == "Pending" or status == "hold" or status == "Hold" or status == "solved" or status == "Solved":
                    botlog.LogSymphonyInfo("Changed status to: " + status)
                    if str(status) == "open":
                        status = "open"
                    elif str(status) == "Pending":
                        status = "pending"
                    elif str(status) == "Hold":
                        status = "hold"
                    elif str(status) == "Solved":
                        status = "solved"
                elif str(status) == "New" or str(status) == "new":
                    return messageDetail.ReplyToChatV2(
                        "You cannot update a ticket and set its status to <b>new</b> but can only update it with the following: <b>open, pending, hold or solved</b>")
                elif str(status) == "Closed" or str(status) == "closed" or str(status) == "Close" or str(status) == "close":
                    return messageDetail.ReplyToChatV2(
                        "You cannot <b>close</b> a ticket directly but you can set it to <b>solved</b> instead.")
                else:
                    return messageDetail.ReplyToChatV2("You did not select a valid status, open/pending/hold/solved")
                public_private = str(message_split[3][1:]).strip()
                if public_private == "true" or public_private == "True" or public_private == "public" or public_private == "Public":
                    comment_status = "Public"
                    public_private = "true"

                elif public_private == "false" or public_private == "False" or public_private == "private" or public_private == "Private":
                    comment_status = "Private"
                    public_private = "false"

                else:
                    return messageDetail.ReplyToChatV2("You did not enter a valid value for public/private field, either false to make it private or true to make it public")
            except:
                return messageDetail.ReplyToChatV2("Please enter all the required fields: <b>Ticket ID</b>| <b>comment</b>| <b>status (open/pending/on hold/solved) </b>| <b>true (public)/false (private)</b>")

            conn = http.client.HTTPSConnection(_configDef['zdesk_config']['zdesk_api'])

            payload = "{\"ticket\": \n\t{\n\t\t\"status\": \"" + status + "\", \n\t\t\"priority\" : \"normal\",\n\t\t\"comment\": \n\t\t\t{\t\"public\" : \"" + public_private + "\",\n\t\t\t\t\"body\": \"" + comment + "\" \n\t\t\t}\n\t}\n}"
            #print("Payload: " + payload)

            ################################

            base64Encoded = base64.b64encode(bytes((emailZendesk + "/token:" + _configDef['zdesk_config']['zdesk_password']), 'utf-8'))
            base64Enc = (base64Encoded.decode("utf-8"))
            #print(str(base64Enc))
            base = ("Basic " + base64Enc)
            #print(str(base))

            headers = {
                'email_address': emailZendesk + "/token",
                'password': (_configDef['zdesk_config']['zdesk_password']),
                'authorization': base,
                'cache-control': "no-cache",
                'content-type': "application/json"
            }

            ################################

            conn.request("PUT", "/api/v2/tickets/" + idt, payload, headers)

            res = conn.getresponse()
            data = res.read().decode("utf-8")
            #print("Response: " + data)

            ticketDoesNotExist = "{\"error\":\"RecordNotFound", "description\":\"Not found\"}"

            if data.startswith(ticketDoesNotExist):
                return messageDetail.ReplyToChatV2("<b>There is no such Zendesk ticket number: " + idt + "</b>")
            if data.startswith("{\"error\": {\""):
                return messageDetail.ReplyToChatV2("Please enter all the required fields: <b>Ticket ID</b>| <b>comment</b>| <b>status (open/pending/hold/solved) </b>| <b>true (public)/false (private)</b>")
            else:
                messageDetail.ReplyToChatV2(comment_status +" comment added to ticket <b>" + idt + "</b>")

                try:
            #      Will show the Ticket details in a table format.
                    conn.request("GET", "/api/v2/tickets/" + idt + ".json", headers=headers)
                    res = conn.getresponse()
                    data = res.read()
                    request_raw = data.decode("utf-8")

                    data_raw = json.dumps(request_raw, indent=2)
                    data_dict = ast.literal_eval(data_raw)
                    d = json.loads(data_dict)

                    requestid = str(d["ticket"]["id"])
                    requeststatus = str(d["ticket"]["status"])
                    requestpriority = str(d["ticket"]["priority"])
                    requestseverity = str(d["ticket"]["tags"])

                except:
                    return messageDetail.ReplyToChatV2("You are not a Zendesk Agent, please upgrade your Zendesk account and try again. Comment was not added.")

                if (len(d["ticket"]["tags"])) == 0:
                    noTag = True
                else:
                    noTag = False

                notSet = True

                if noTag:
                    sev = "Not set"
                    notSet = False

                for index_tags in range(len(d["ticket"]["tags"])):
                    tags = str((d["ticket"]["tags"][index_tags]))

                    if tags.startswith("severity_1"):
                        sev = "Severity 1"
                        notSet = False
                    elif tags.startswith("severity_2"):
                        sev = "Severity 2"
                        notSet = False
                    elif tags.startswith("severity_3"):
                        sev = "Severity 3"
                        notSet = False
                    elif tags.startswith("severity_4"):
                        sev = "Severity 4"
                        notSet = False

                if notSet:
                    sev = "Not Set"
                    notSet = False

                requestseverity = sev

                requestsubject_temps = str(d["ticket"]["subject"])
                requestsubject = str(requestsubject_temps).replace("<", "&lt;").replace("\"", "&quot;").replace("&", "&amp;").replace("'","&apos;").replace(">","&gt;")
                requestdescription_temps = str(d["ticket"]["description"])
                requestdescription = str(requestdescription_temps).replace("<", "&lt;").replace("\"", "&quot;").replace("&", "&amp;").replace("'","&apos;").replace(">","&gt;")
                requestorganization_id = str(d["ticket"]["organization_id"])
                requestrequester_id = str(d["ticket"]["requester_id"])
                requestcreated_at = str(d["ticket"]["created_at"]).replace("T", " ").replace("Z", "")
                requestupdated_at = str(d["ticket"]["updated_at"]).replace("T", " ").replace("Z", "")
                requestassignee_id = str(d["ticket"]["assignee_id"])

                request_id = str(requestid)
                request_status = str(requeststatus)
                request_priority = str(requestpriority)
                request_severity = str(requestseverity)
                request_subject = str(requestsubject)
                request_desc = str(requestdescription)
                desc = str(request_desc)
                request_org = str(requestorganization_id)
                request_requestor = str(requestrequester_id)
                request_created = str(requestcreated_at)
                request_updated = str(requestupdated_at)

                # To get the name of the requester given the requesterID
                conn.request("GET", "/api/v2/users/" + request_requestor, headers=headers)
                res = conn.getresponse()
                userRequesterId = res.read()
                tempUserRequester = str(userRequesterId.decode('utf-8'))

                data = json.dumps(tempUserRequester, indent=2)
                data_dict = ast.literal_eval(data)
                d = json.loads(data_dict)
                req_name = str(d["user"]["name"])
                requesterName = req_name

                try:
                    request_assignee = str(requestassignee_id)

                    # To get the name of the assignee given the assigneeID
                    conn.request("GET", "/api/v2/users/" + request_assignee, headers=headers)
                    res = conn.getresponse()
                    userAssigneeId = res.read()
                    tempUserAssignee = str(userAssigneeId.decode('utf-8'))

                    data = json.dumps(tempUserAssignee, indent=2)
                    data_dict = ast.literal_eval(data)
                    d = json.loads(data_dict)
                    assign_name = str(d["user"]["name"])
                    assigneeName = assign_name

                except:
                    assigneeName = "Not assigned"
                    assignee_flag = True

                requesterTicket = (_configDef['zdesk_config']['zdesk_link']) + str(request_id) + "/requester/requested_tickets"
                assigneeTicket = (_configDef['zdesk_config']['zdesk_url']) + "/agent/users/" + request_assignee + "/assigned_tickets"
                OrgTicket = (_configDef['zdesk_config']['zdesk_link']) + str(request_id) + "/organization/tickets"

                # Convert the Zendesk ID to company name
                conn.request("GET", "/api/v2/users/" + requestrequester_id + "/organizations.json", headers=headers)
                res = conn.getresponse()
                companyID = res.read()
                compNameRaw = str(companyID.decode("utf-8"))

                data = json.dumps(compNameRaw, indent=2)
                data_dict = ast.literal_eval(data)
                d = json.loads(data_dict)
                org_Name = str(d["organizations"][0]["name"])
                orgName = str(org_Name)

                table_body = ""
                table_header = "<table style='border-collapse:collapse;border:2px solid black;table-layout:auto;width:100%;box-shadow: 5px 5px'><thead><tr style='background-color:#4D94FF;color:#ffffff;font-size:1rem' class=\"tempo-text-color--white tempo-bg-color--black\">" \
                               "<td style='width:20%;border:1px solid blue;border-bottom: double blue;text-align:center'>SUBJECT</td>" \
                               "<td style='width:30%;border:1px solid blue;border-bottom: double blue;text-align:center'>DESCRIPTION</td>" \
                               "<td style='width:2.5%;border:1px solid blue;border-bottom: double blue;text-align:center'>ID</td>" \
                               "<td style='width:3%;border:1px solid blue;border-bottom: double blue;text-align:center'>STATUS</td>" \
                               "<td style='width:3%;border:1px solid blue;border-bottom: double blue;text-align:center'>PRIORITY</td>" \
                               "<td style='width:3.5%;border:1px solid blue;border-bottom: double blue;text-align:center'>SEVERITY</td>" \
                               "<td style='width:5%;border:1px solid blue;border-bottom: double blue;text-align:center'>COMPANY</td>" \
                               "<td style='width:7%;border:1px solid blue;border-bottom: double blue;text-align:center'>REQUESTER</td>" \
                               "<td style='width:7%;border:1px solid blue;border-bottom: double blue;text-align:center'>CREATED</td>" \
                               "<td style='width:7%;border:1px solid blue;border-bottom: double blue;text-align:center'>UPDATED</td>" \
                               "<td style='width:7%;border:1px solid blue;border-bottom: double blue;text-align:center'>ASSIGNEE</td>" \
                               "</tr></thead><tbody>"

                if assignee_flag:

                    table_body += "<tr>" \
                                  "<td style='border:1px solid black;text-align:left'>" + request_subject + "</td>" \
                                  "<td style='border:1px solid black;text-align:left'>" + desc + "</td>" \
                                  "<td style='border:1px solid black;text-align:center'><a href=\"" + (_configDef['zdesk_config']['zdesk_link']) + str(request_id) + "\">" + str(request_id) + "</a></td>" \
                                  "<td style='border:1px solid black;text-align:center'>" + request_status + "</td>" \
                                  "<td style='border:1px solid black;text-align:center'>" + request_priority + "</td>" \
                                  "<td style='border:1px solid black;text-align:center'>" + request_severity + "</td>" \
                                  "<td style='border:1px solid black;text-align:center'><a href=\"" + OrgTicket + "\">" + orgName + "</a></td>" \
                                  "<td style='border:1px solid black;text-align:center'><a href=\"" + requesterTicket + "\">" + str(requesterName) + "</a></td>" \
                                  "<td style='border:1px solid black;text-align:center'>" + request_created + "</td>" \
                                  "<td style='border:1px solid black;text-align:center'>" + request_updated + "</td>" \
                                  "<td style='border:1px solid black;text-align:center'>" + assigneeName + "</td>" \
                                  "</tr>"

                else:
                    table_body += "<tr>" \
                                  "<td style='border:1px solid black;text-align:left'>" + request_subject + "</td>" \
                                  "<td style='border:1px solid black;text-align:left'>" + desc + "</td>" \
                                  "<td style='border:1px solid black;text-align:center'><a href=\"" + (_configDef['zdesk_config']['zdesk_link']) + str(request_id) + "\">" + str(request_id) + "</a></td>" \
                                  "<td style='border:1px solid black;text-align:center'>" + request_status + "</td>" \
                                  "<td style='border:1px solid black;text-align:center'>" + request_priority + "</td>" \
                                  "<td style='border:1px solid black;text-align:center'>" + request_severity + "</td>" \
                                  "<td style='border:1px solid black;text-align:center'><a href=\"" + OrgTicket + "\">" + orgName + "</a></td>" \
                                  "<td style='border:1px solid black;text-align:center'><a href=\"" + requesterTicket + "\">" + str(requesterName) + "</a></td>" \
                                  "<td style='border:1px solid black;text-align:center'>" + request_created + "</td>" \
                                  "<td style='border:1px solid black;text-align:center'>" + request_updated + "</td>" \
                                  "<td style='border:1px solid black;text-align:center'><a href=\"" + assigneeTicket + "\">" + str(assigneeName) + "</a></td>" \
                                  "</tr>"

                table_body += "</tbody></table>"
                reply = table_header + table_body
                return messageDetail.ReplyToChatV2_noBotLog(reply)
        else:
            #return messageDetail.ReplyToChat("You aren't authorised to use this command.")
            botlog.LogSymphonyInfo("The calling user is either not added to the Zendesk Agent List or he/she is not an Agent on the Zendesk Instance")

            showRequest = (messageDetail.Command.MessageText)
            message_split = showRequest.split("|")

            ### /update idt, comment, status, private/false or public/true
            try:
                idt = str(message_split[0][1:]).strip()
                #print(idt)
                comment = str(message_split[1][1:]).replace("&quot;", "\"").replace("&amp;","&").replace("&lt;","<").replace("&apos;","'").replace("&gt;",">")
                #print(comment)
                # public_private = message_split[3][1:]
                # if public_private == "true" or public_private == "True" or public_private == "public" or public_private == "Public":
                #     comment_status = "Public"
                #     public_private = "true"
                #     messageDetail.ReplyToChatV2("You are not a Zendesk Agent but your public comment will be added to ticket " + idt)
                #
                # elif public_private == "false" or public_private == "False" or public_private == "private" or public_private == "Private":
                #     comment_status = "Private"
                #     public_private = "false"
                #     return messageDetail.ReplyToChatV2("You are not a Zendesk Agent and therefore your Private comment cannot be added.")
                #
                # else:
                #     return messageDetail.ReplyToChatV2("You are not a Zendesk Agent aor you are not part of the Zendesk Agent List.")
            except:
                return messageDetail.ReplyToChatV2("Please enter all the required fields: <b>Ticket ID</b>, <b>comment</b>")


            #################################

            conn = http.client.HTTPSConnection(_configDef['zdesk_config']['zdesk_api'])

            payload = "{\"request\": {\"comment\": {\"body\": \"" + comment + "\"}}}"
            #print(payload)

            base64Encoded = base64.b64encode(bytes((emailZendesk + "/token:" + _configDef['zdesk_config']['zdesk_password']), 'utf-8'))

            base64Enc = (base64Encoded.decode("utf-8"))
            #print(str(base64Enc))
            base = ("Basic " + base64Enc)
            #print(str(base))

            headers = {
                'content-type': "application/json",
                'authorization': base
            }

            #try:

            conn.request("PUT", "/api/v2/requests/" + idt, payload, headers)

            res = conn.getresponse()
            data = res.read().decode("utf-8")
            #print(str(data))

            #################################

            try:
                data_raw = json.dumps(data, indent=2)
                data_dict = ast.literal_eval(data_raw)
                d = json.loads(data_dict)

                requester_id = str(d["request"]["requester_id"])
                #print(str(requester_id))
                collaborator_ids = str(d["request"]["collaborator_ids"]).replace("[","").replace("]","").replace(",","")
                #print(str(collaborator_ids))

                isRequesterPart = requester_id + " " + collaborator_ids
                #print(str(isRequesterPart))

                if str(ZendeskUserID) in isRequesterPart:
                    botlog.LogSymphonyInfo("The calling user is either the requester or is a CCed person in the ticket. The calling user can add an update to this ticket.")
                else:
                    return messageDetail.ReplyToChatV2("I am sorry, you are not this Zendesk Ticker requester nor CCed on it. I cannot add your comment/update.")
            except:
                return messageDetail.ReplyToChatV2(
                    "I am sorry, you are not this Zendesk Ticker requester nor CCed on it. I cannot add your comment/update.")
            #################################

            ticketDoesNotExist = "{\"error\":\"RecordNotFound", "description\":\"Not found\"}"

            if data.startswith(ticketDoesNotExist):
                return messageDetail.ReplyToChatV2("<b>There is no such Zendesk ticket number: " + idt + "</b>")
            if data.startswith("{\"error\": {\""):
                return messageDetail.ReplyToChatV2(
                    "Please enter all the required fields: <b>Ticket ID</b>| <b>comment</b>")
            else:
                #return messageDetail.ReplyToChatV2(comment_status + " comment added to ticket " + idt + ". You can use /showTicketComments " + idt + " to see its comment(s)")
                return messageDetail.ReplyToChatV2("Public comment/update added to Zendesk ticket " + idt + ". You can use /showTicketComments " + idt + " to see its comment(s)")

                    # ##      Will show the Ticket details in a table format.
                    # conn.request("GET", "/api/v2/tickets/" + idt + ".json", headers=headers)
                    # res = conn.getresponse()
                    # data = res.read()
                    # request_raw = data.decode("utf-8")
                    #
                    # data_raw = json.dumps(request_raw, indent=2)
                    # data_dict = ast.literal_eval(data_raw)
                    # d = json.loads(data_dict)
                    #
                    # requestid = str(d["ticket"]["id"])
                    # requeststatus = str(d["ticket"]["status"])
                    # requestpriority = str(d["ticket"]["priority"])
                    # requestseverity = str(d["ticket"]["tags"])
                    #
                    # if (len(d["ticket"]["tags"])) == 0:
                    #     noTag = True
                    # else:
                    #     noTag = False
                    #
                    # notSet = True
                    #
                    # if noTag:
                    #     sev = "Not set"
                    #     notSet = False
                    #
                    # for index_tags in range(len(d["ticket"]["tags"])):
                    #     tags = str((d["ticket"]["tags"][index_tags]))
                    #
                    #     if tags.startswith("severity_1"):
                    #         sev = "Severity 1"
                    #         notSet = False
                    #     elif tags.startswith("severity_2"):
                    #         sev = "Severity 2"
                    #         notSet = False
                    #     elif tags.startswith("severity_3"):
                    #         sev = "Severity 3"
                    #         notSet = False
                    #     elif tags.startswith("severity_4"):
                    #         sev = "Severity 4"
                    #         notSet = False
                    #
                    # if notSet:
                    #     sev = "Not Set"
                    #     notSet = False
                    #
                    # requestseverity = sev
                    #
                    # requestsubject = str(d["ticket"]["subject"])
                    # requestdescription_temps = str(d["ticket"]["description"])
                    # requestdescription = requestdescription_temps.replace("<", "&lt;")
                    # requestorganization_id = str(d["ticket"]["organization_id"])
                    # requestrequester_id = str(d["ticket"]["requester_id"])
                    # requestcreated_at = str(d["ticket"]["created_at"]).replace("T", " ").replace("Z", "")
                    # requestupdated_at = str(d["ticket"]["updated_at"]).replace("T", " ").replace("Z", "")
                    # requestassignee_id = str(d["ticket"]["assignee_id"])
                    #
                    # request_id = str(requestid)
                    # request_status = str(requeststatus)
                    # request_priority = str(requestpriority)
                    # request_severity = str(requestseverity)
                    # request_subject = str(requestsubject)
                    # request_desc = str(requestdescription)
                    # desc = str(request_desc)
                    # request_org = str(requestorganization_id)
                    # request_requestor = str(requestrequester_id)
                    # request_created = str(requestcreated_at)
                    # request_updated = str(requestupdated_at)
                    #
                    # # To get the name of the requester given the requesterID
                    # conn.request("GET", "/api/v2/users/" + request_requestor, headers=headers)
                    # res = conn.getresponse()
                    # userRequesterId = res.read()
                    # tempUserRequester = str(userRequesterId.decode('utf-8'))
                    #
                    # data = json.dumps(tempUserRequester, indent=2)
                    # data_dict = ast.literal_eval(data)
                    # d = json.loads(data_dict)
                    # req_name = str(d["user"]["name"])
                    # requesterName = req_name
                    #
                    # try:
                    #     request_assignee = str(requestassignee_id)
                    #
                    #     # To get the name of the assignee given the assigneeID
                    #     conn.request("GET", "/api/v2/users/" + request_assignee, headers=headers)
                    #     res = conn.getresponse()
                    #     userAssigneeId = res.read()
                    #     tempUserAssignee = str(userAssigneeId.decode('utf-8'))
                    #
                    #     data = json.dumps(tempUserAssignee, indent=2)
                    #     data_dict = ast.literal_eval(data)
                    #     d = json.loads(data_dict)
                    #     assign_name = str(d["user"]["name"])
                    #     assigneeName = assign_name
                    #
                    # except:
                    #     assigneeName = "Not assigned"
                    #     assignee_flag = True
                    #
                    # requesterTicket = (_configDef['zdesk_config']['zdesk_link']) + str(request_id) + "/requester/requested_tickets"
                    # assigneeTicket = (_configDef['zdesk_config']['zdesk_url']) + "/agent/users/" + request_assignee + "/assigned_tickets"
                    # OrgTicket = (_configDef['zdesk_config']['zdesk_link']) + str(request_id) + "/organization/tickets"
                    #
                    # # Convert the Zendesk ID to company name
                    # conn.request("GET", "/api/v2/users/" + requestrequester_id + "/organizations.json", headers=headers)
                    # res = conn.getresponse()
                    # companyID = res.read()
                    # compNameRaw = str(companyID.decode("utf-8"))
                    #
                    # data = json.dumps(compNameRaw, indent=2)
                    # data_dict = ast.literal_eval(data)
                    # d = json.loads(data_dict)
                    # org_Name = str(d["organizations"][0]["name"])
                    # orgName = str(org_Name)
                    #
                    # table_body = ""
                    # table_header = "<table style='border-collapse:collapse;border:2px solid black;table-layout:auto;width:100%;box-shadow: 5px 5px'><thead><tr style='background-color:#4D94FF;color:#ffffff;font-size:1rem' class=\"tempo-text-color--white tempo-bg-color--black\">" \
                    #                "<td style='width:20%;border:1px solid blue;border-bottom: double blue;text-align:center'>SUBJECT</td>" \
                    #                "<td style='width:30%;border:1px solid blue;border-bottom: double blue;text-align:center'>DESCRIPTION</td>" \
                    #                "<td style='width:2.5%;border:1px solid blue;border-bottom: double blue;text-align:center'>ID</td>" \
                    #                "<td style='width:3%;border:1px solid blue;border-bottom: double blue;text-align:center'>STATUS</td>" \
                    #                "<td style='width:3%;border:1px solid blue;border-bottom: double blue;text-align:center'>PRIORITY</td>" \
                    #                "<td style='width:3.5%;border:1px solid blue;border-bottom: double blue;text-align:center'>SEVERITY</td>" \
                    #                "<td style='width:5%;border:1px solid blue;border-bottom: double blue;text-align:center'>COMPANY</td>" \
                    #                "<td style='width:7%;border:1px solid blue;border-bottom: double blue;text-align:center'>REQUESTER</td>" \
                    #                "<td style='width:7%;border:1px solid blue;border-bottom: double blue;text-align:center'>CREATED</td>" \
                    #                "<td style='width:7%;border:1px solid blue;border-bottom: double blue;text-align:center'>UPDATED</td>" \
                    #                "<td style='width:7%;border:1px solid blue;border-bottom: double blue;text-align:center'>ASSIGNEE</td>" \
                    #                "</tr></thead><tbody>"
                    #
                    # if assignee_flag:
                    #
                    #     table_body += "<tr>" \
                    #                   "<td style='border:1px solid black;text-align:left'>" + request_subject + "</td>" \
                    #                   "<td style='border:1px solid black;text-align:left'>" + desc + "</td>" \
                    #                   "<td style='border:1px solid black;text-align:center'><a href=\"" + (_configDef['zdesk_config']['zdesk_link']) + str(request_id) + "\">" + str(request_id) + "</a></td>" \
                    #                   "<td style='border:1px solid black;text-align:center'>" + request_status + "</td>" \
                    #                   "<td style='border:1px solid black;text-align:center'>" + request_priority + "</td>" \
                    #                   "<td style='border:1px solid black;text-align:center'>" + request_severity + "</td>" \
                    #                   "<td style='border:1px solid black;text-align:center'><a href=\"" + OrgTicket + "\">" + orgName + "</a></td>" \
                    #                   "<td style='border:1px solid black;text-align:center'><a href=\"" + requesterTicket + "\">" + str(requesterName) + "</a></td>" \
                    #                   "<td style='border:1px solid black;text-align:center'>" + request_created + "</td>" \
                    #                   "<td style='border:1px solid black;text-align:center'>" + request_updated + "</td>" \
                    #                   "<td style='border:1px solid black;text-align:center'>" + assigneeName + "</td>" \
                    #                   "</tr>"
                    #
                    # else:
                    #     table_body += "<tr>" \
                    #                   "<td style='border:1px solid black;text-align:left'>" + request_subject + "</td>" \
                    #                   "<td style='border:1px solid black;text-align:left'>" + desc + "</td>" \
                    #                   "<td style='border:1px solid black;text-align:center'><a href=\"" + (_configDef['zdesk_config']['zdesk_link']) + str(request_id) + "\">" + str(request_id) + "</a></td>" \
                    #                   "<td style='border:1px solid black;text-align:center'>" + request_status + "</td>" \
                    #                   "<td style='border:1px solid black;text-align:center'>" + request_priority + "</td>" \
                    #                   "<td style='border:1px solid black;text-align:center'>" + request_severity + "</td>" \
                    #                   "<td style='border:1px solid black;text-align:center'><a href=\"" + OrgTicket + "\">" + orgName + "</a></td>" \
                    #                   "<td style='border:1px solid black;text-align:center'><a href=\"" + requesterTicket + "\">" + str(requesterName) + "</a></td>" \
                    #                   "<td style='border:1px solid black;text-align:center'>" + request_created + "</td>" \
                    #                   "<td style='border:1px solid black;text-align:center'>" + request_updated + "</td>" \
                    #                   "<td style='border:1px solid black;text-align:center'><a href=\"" + assigneeTicket + "\">" + str(assigneeName) + "</a></td>" \
                    #                   "</tr>"
                    #
                    # table_body += "</tbody></table>"
                    # reply = table_header + table_body
                    # return messageDetail.ReplyToChatV2(reply)
            # except:
            #     return messageDetail.ReplyToChat("I am sorry, I cannot find this ticket id on Zendesk, please check and try again")

    except:
        return messageDetail.ReplyToChat("I am sorry, I was working on a different task, can you please retry")


def assignTicket(messageDetail):
    botlog.LogSymphonyInfo("#############################")
    botlog.LogSymphonyInfo("Bot Call: Assign Ticker Owner")
    botlog.LogSymphonyInfo("#############################")

    try:
        isAllowed = False
        callerCheck = ""
        assign_email =""
        commandCallerUID = messageDetail.FromUserId

        connComp = http.client.HTTPSConnection(_configDef['symphonyinfo']['pod_hostname'])
        sessionTok = callout.GetSessionToken()

        headersCompany = {
            'sessiontoken': sessionTok,
            'cache-control': "no-cache"
        }

        try:
            connComp.request("GET", "/pod/v3/users?uid=" + commandCallerUID, headers=headersCompany)
        except:
            return messageDetail.ReplyToChat("I am having difficulty to find this user id: " + commandCallerUID)

        resComp = connComp.getresponse()
        dataComp = resComp.read()
        data_raw = str(dataComp.decode('utf-8'))
        data_dict = ast.literal_eval(data_raw)

        dataRender = json.dumps(data_dict, indent=2)
        d_org = json.loads(dataRender)

        assignee_flag = ""

        for index_org in range(len(d_org["users"])):
            firstName = d_org["users"][index_org]["firstName"]
            lastName = d_org["users"][index_org]["lastName"]
            displayName = d_org["users"][index_org]["displayName"]
            companyName = d_org["users"][index_org]["company"]
            userID = str(d_org["users"][index_org]["id"])

            try:
                emailAddress = d_org["users"][index_org]["emailAddress"]
                botlog.LogSymphonyInfo("User is connected: " + emailAddress)
                emailZendesk = emailAddress
                connectionRequired = False
            except:
                #print("User is not connected")
                connectionRequired = True

        #if connectionRequired:
            #print("inside not connected")
            data_lenght = len(dataComp)
            #print(data_lenght)

            if data_lenght > 450:
                # query = "type:user " + firstName + " " + lastName
                try:
                    query = "type:user " + emailAddress
                except:
                    query = "type:user " + firstName + " " + lastName
                botlog.LogSymphonyInfo(query)
            elif data_lenght < 450:
                #This will only work if the pod name is the same as the zendesk org/account
                #query = "type:user " + firstName + " " + lastName + " organization:" + company
                # query = "type:user " + firstName + " " + lastName
                try:
                    query = "type:user " + emailAddress
                except:
                    query = "type:user " + firstName + " " + lastName
                botlog.LogSymphonyInfo(query)
            else:
                return messageDetail.ReplyToChat("No user information available")

            results = zendesk.search(query=query)
            #print(results)

            if str(results).startswith(
                    "{'results': [], 'facets': None, 'next_page': None, 'previous_page': None, 'count': 0}"):
                return messageDetail.ReplyToChat(
                    "This user, <b>" + firstName + " " + lastName + "</b>, does not exist on Zendesk, the name is misspelled.")
            elif str(results).startswith(
                    "{'results': [], 'facets': {'type': {'entry': 0, 'ticket': 0, 'organization': 0, 'user': 0, 'article': 0, 'group': 0}}, 'next_page': None, 'previous_page': None, 'count': 0}"):
                return messageDetail.ReplyToChat(
                    "This organisation/company does not exist in Zendesk or name, <b>" + firstName + " " + lastName + "</b>, is misspelled. Only Agents can be assigned ticket to. Please use this format: /ticketUpdate ticketid, subject, description")
            else:

                data = json.dumps(results, indent=2)
                d = json.loads(data)
                #print(d)

                for index in range(len(d["results"])):
                    name = d["results"][index]["name"]
                    email = str(d["results"][index]["email"])
                    ZDuserId = str(d["results"][index]["id"])
                    role = str(d["results"][index]["role"])
                    emailAddress = email
                    if role == "end-user" or role == "End-user":
                        botlog.LogSymphonyInfo("The user's Zendesk role is " + role)
                        isAllowed = False
                        return messageDetail.ReplyToChatV2("This user, <b>" + name + " (" + email + "</b>), is Not an Agent on this Zendesk instance, please check via <b> /user </b> to find more information about Zensesk users and their role")
                    elif role == "Admin" or role == "admin" or role == "Agent" or role == "agent":
                        isAllowed = True


        botlog.LogSymphonyInfo(firstName + " " + lastName + " (" + displayName + ") from Company/Pod name: " + str(companyName) + " with UID: " + str(userID))
        callerCheck = (firstName + " " + lastName + " - " + displayName + " - " + companyName + " - " + str(userID))

        callingUser = firstName + " " + lastName
        callingUserEMail = emailAddress

        if callerCheck in AccessFile and isAllowed:
            botlog.LogSymphonyInfo("User is Agent with the bot as well as with Zendesk")
            try:
                ticketid = messageDetail.Command.MessageText
                #print(ticketid)
                ticketID = str(ticketid).strip()
                #print(ticketID)
                detail = messageDetail.Command.MessageFlattened.split("_u_")
                UID = detail[1]
                #print(UID_mentioned)
            except:
                return messageDetail.ReplyToChat("Please use this format: /assignTicket id @mention user")

            # ############################
            #
            # conn = http.client.HTTPSConnection(_configDef['zdesk_config']['zdesk_api'])
            #
            # headers = {
            #     'username': _configDef['zdesk_config']['zdesk_email'] + "/token",
            #     'password': _configDef['zdesk_config']['zdesk_password'],
            #     'authorization': _configDef['zdesk_config']['zdesk_auth'],
            #     'cache-control': "no-cache",
            #     'Content-Type': "application/json"
            # }
            #
            # conn.request("GET", "/api/v2/tickets/" + ticketID + ".json", headers=headers)
            # res = conn.getresponse()
            # data = res.read()
            # request_raw = data.decode("utf-8")
            #
            # ticketDoesNotExist = "{\"error\":\"RecordNotFound", "description\":\"Not found\"}"
            #
            # if request_raw.startswith(ticketDoesNotExist):
            #     return messageDetail.ReplyToChatV2(
            #         "<b>There is no such Zendesk ticket number: " + str(ticketID) + "</b>")
            #
            # try:
            #     data = json.dumps(request_raw, indent=2)
            #     data_dict = ast.literal_eval(data)
            #     d = json.loads(data_dict)
            #
            #     # for index in range(len(request_raw["request"])):
            #     # requestid = str(d["request"]["id"])
            #     # requestassignee_id = str(d["request"]["assignee_id"])
            #
            #     requestid = str(d["ticket"]["id"])
            #     requestassignee_id = str(d["ticket"]["assignee_id"])
            # except:
            #     messageDetail.ReplyToChat("Cannot get ticket info for ID " + str(ticketID))
            #
            # try:
            #     request_assignee = str(requestassignee_id)
            #
            #     # To get the name of the assignee given the assigneeID
            #     conn.request("GET", "/api/v2/users/" + request_assignee, headers=headers)
            #     res = conn.getresponse()
            #     userAssigneeId = res.read()
            #     tempUserAssignee = str(userAssigneeId.decode('utf-8'))
            #
            #     data = json.dumps(tempUserAssignee, indent=2)
            #     data_dict = ast.literal_eval(data)
            #     d = json.loads(data_dict)
            #     print(d)
            #
            #     assign_name = str(d["user"]["name"])
            #     assign_email = str(d["user"]["email"])
            #     assigneeName = assign_name
            #     print(assigneeName)
            # except:
            #     assigneeName = "N/A"
            #
            #
            # ############################


            # Calling the API endpoint to get display name
            connComp = http.client.HTTPSConnection(_configDef['symphonyinfo']['pod_hostname'])
            sessionTok = callout.GetSessionToken()

            headersCompany = {
                'sessiontoken': sessionTok,
                'cache-control': "no-cache"
            }

            try:
                connComp.request("GET", "/pod/v3/users?uid=" + UID, headers=headersCompany)

                resComp = connComp.getresponse()
                dataComp = resComp.read()
                data_raw = str(dataComp.decode('utf-8'))
                data_dict = ast.literal_eval(data_raw)

                dataRender = json.dumps(data_dict, indent=2)
                d_org = json.loads(dataRender)
                #print(d_org)
            except:
                return messageDetail.ReplyToChat("There is no user information")

            connectionRequired = ""
            connectionRequired = True
            for index_org in range(len(d_org["users"])):
                firstName = d_org["users"][index_org]["firstName"]
                #print(firstName)
                lastName = d_org["users"][index_org]["lastName"]
                #print(lastName)
                company = d_org["users"][index_org]["company"]
                #print(company)
                # print(company)
                try:
                    emailAddress = d_org["users"][index_org]["emailAddress"]
                    #print("User is connected: " + emailAddress)
                    emailZendesk = emailAddress
                    connectionRequired = False
                except:
                    #print("User is not connected")
                    connectionRequired = True

            if connectionRequired:
                #print("inside not connected")
                data_lenght = len(dataComp)
                #print(data_lenght)

                if data_lenght > 450:
                    query = "type:user " + str(firstName) + " " + str(lastName)
                    #print(query)
                elif data_lenght < 450:
                    #This will only work if the pod name is the same as the zendesk org/account
                    #query = "type:user " + firstName + " " + lastName + " organization:" + company
                    query = "type:user " + str(firstName) + " " + str(lastName)
                    #print(query)
                else:
                    return messageDetail.ReplyToChat("No user information available")

                results = zendesk.search(query=query)
                #print(results)

                if str(results).startswith(
                        "{'results': [], 'facets': None, 'next_page': None, 'previous_page': None, 'count': 0}"):
                    return messageDetail.ReplyToChat(
                        "This user, <b>" + firstName + " " + lastName + "</b>, does not exist on Zendesk, the name is misspelled or does not belong to this organisation, <b>" + company + "</b>.")
                elif str(results).startswith(
                        "{'results': [], 'facets': {'type': {'entry': 0, 'ticket': 0, 'organization': 0, 'user': 0, 'article': 0, 'group': 0}}, 'next_page': None, 'previous_page': None, 'count': 0}"):
                    return messageDetail.ReplyToChat(
                        "This organisation/company, <b>" + company + "</b>, does not exist in Zendesk or name, <b>" + firstName + " " + lastName + "</b>, is misspelled. Only Agents can be assigned ticket to. Please use this format: /assignTicket ticketid @mention")
                else:

                    data = json.dumps(results, indent=2)
                    d = json.loads(data)
                    #print(d)

                    for index in range(len(d["results"])):
                        name = d["results"][index]["name"]
                        emai = str(d["results"][index]["email"])
                        ZDuserId = str(d["results"][index]["id"])
                        role = str(d["results"][index]["role"])

                        if role == "end-user" or role == "End-user":
                            return messageDetail.ReplyToChatV2("This user, <b>" + name + " (" + email + "</b>), is Not an Agent on this Zendesk instance, please check via <b> /user </b> to find more information about Zensesk users and their role")

    ######           ## This is if the called user is an agent and it will add the user as an assignee and post an internal update

                    ############################

                    conn = http.client.HTTPSConnection(_configDef['zdesk_config']['zdesk_api'])

                    headers = {
                        'username': _configDef['zdesk_config']['zdesk_email'] + "/token",
                        'password': _configDef['zdesk_config']['zdesk_password'],
                        'authorization': _configDef['zdesk_config']['zdesk_auth'],
                        'cache-control': "no-cache",
                        'Content-Type': "application/json"
                    }

                    conn.request("GET", "/api/v2/tickets/" + ticketID + ".json", headers=headers)
                    res = conn.getresponse()
                    data = res.read()
                    request_raw = data.decode("utf-8")

                    ticketDoesNotExist = "{\"error\":\"RecordNotFound", "description\":\"Not found\"}"

                    if request_raw.startswith(ticketDoesNotExist):
                        return messageDetail.ReplyToChatV2(
                            "<b>There is no such Zendesk ticket number: " + str(ticketID) + "</b>")

                    try:
                        data = json.dumps(request_raw, indent=2)
                        data_dict = ast.literal_eval(data)
                        d = json.loads(data_dict)

                        # for index in range(len(request_raw["request"])):
                        # requestid = str(d["request"]["id"])
                        # requestassignee_id = str(d["request"]["assignee_id"])

                        requestid = str(d["ticket"]["id"])
                        requestassignee_id = str(d["ticket"]["assignee_id"])
                    except:
                        return messageDetail.ReplyToChat("Cannot get ticket info for ID " + str(ticketID))

                    try:
                        request_assignee = str(requestassignee_id)

                        # To get the name of the assignee given the assigneeID
                        conn.request("GET", "/api/v2/users/" + request_assignee, headers=headers)
                        res = conn.getresponse()
                        userAssigneeId = res.read()
                        tempUserAssignee = str(userAssigneeId.decode('utf-8'))

                        data = json.dumps(tempUserAssignee, indent=2)
                        data_dict = ast.literal_eval(data)
                        d = json.loads(data_dict)
                        #print(d)

                        assign_name = str(d["user"]["name"])
                        assign_email = str(d["user"]["email"])
                        assigneeName = assign_name
                        #print(assigneeName)
                    except:
                        try:
                            botlog.LogSymphonyInfo("Inside second try for assignee name value in assignTicket")
                            request_assignee = str(requestassignee_id)

                            # To get the name of the assignee given the assigneeID
                            conn.request("GET", "/api/v2/users/" + request_assignee, headers=headers)
                            res = conn.getresponse()
                            userAssigneeId = res.read()
                            tempUserAssignee = str(userAssigneeId.decode('utf-8'))

                            data = json.dumps(tempUserAssignee, indent=2)
                            data_dict = ast.literal_eval(data)
                            d = json.loads(data_dict)
                            # print(d)

                            assign_name = str(d["user"]["name"])
                            assign_email = str(d["user"]["email"])
                            assigneeName = assign_name
                            # print(assigneeName)
                        except:
                            assigneeName = "N/A"

                    if str(assign_email) == str(email):
                        return messageDetail.ReplyToChatV2("This Zendesk Agent, <b>" + assigneeName + "</b> is already assigned to Zendesk Ticket : <b>" + str(ticketID) + "</b>")

                    #else:
                    ############################
                    conn = http.client.HTTPSConnection(_configDef['zdesk_config']['zdesk_api'])

                    #payload = "{\r\n  \"ticket\": {\r\n    \"assignee_id\": " + ZDuserId+ "\r\n  }\r\n}"

                    payload = "{\r\n  \"ticket\": {\r\n    \"assignee_id\": " + ZDuserId + ",\r\n    \"comment\":{\r\n    \t\"public\":\"Private\",\r\n    \t\"body\":\"" + callingUser + " assigned this ticket to " + name + "\"\r\n    }\r\n  }\r\n}"
                    #print(payload)

                    ## Using the bot to post an internal commment about the assignment
                    headers = {
                        'username': _configDef['zdesk_config']['zdesk_email'] + "/token",
                        'password': _configDef['zdesk_config']['zdesk_password'],
                        'authorization': _configDef['zdesk_config']['zdesk_auth'],
                        'cache-control': "no-cache",
                        'Content-Type': "application/json"
                    }

                    #################################

                    # base64Encoded = base64.b64encode(bytes((callingUserEMail + "/token:" + _configDef['zdesk_config']['zdesk_password']), 'utf-8'))
                    # base64Enc = (base64Encoded.decode("utf-8"))
                    # print(str(base64Enc))
                    # base = ("Basic " + base64Enc)
                    # print(str(base))
                    #
                    # headers = {
                    #     'email_address': callingUserEMail + "/token",
                    #     'password': (_configDef['zdesk_config']['zdesk_password']),
                    #     'authorization': base,
                    #     'cache-control': "no-cache",
                    #     'content-type': "application/json"
                    # }

                    ###############################

                    conn.request("PUT", "/api/v2/tickets/" + ticketID, payload, headers)

                    res = conn.getresponse()
                    data = res.read().decode("utf-8")

                    #print(data)

                    invalidTicket = "{\"error\":\"RecordNotFound","description\":\"Not found\"}"

                    if data.startswith(invalidTicket):
                        return messageDetail.ReplyToChatV2("This Zendesk Ticket ID does not exist, please check and try again.")

                    # messageDetail.ReplyToChatV2("Zendesk Ticket <a href =\"" + (_configDef['zdesk_config']['zdesk_link']) + str(ticketID) + "\">" + str(ticketID) + "</a> is successfully asigned to " + name)

                    idt = ticketID

                    ##      Will show the Ticket details in a table format.

                    base64Encoded = base64.b64encode(bytes((callingUserEMail + "/token:" + _configDef['zdesk_config']['zdesk_password']), 'utf-8'))
                    base64Enc = (base64Encoded.decode("utf-8"))
                    #print(str(base64Enc))
                    base = ("Basic " + base64Enc)
                    #print(str(base))

                    headers = {
                        'email_address': callingUserEMail + "/token",
                        'password': (_configDef['zdesk_config']['zdesk_password']),
                        'authorization': base,
                        'cache-control': "no-cache",
                        'content-type': "application/json"
                    }

                    conn.request("GET", "/api/v2/tickets/" + idt + ".json", headers=headers)
                    res = conn.getresponse()
                    data = res.read()
                    request_raw = data.decode("utf-8")

                    data_raw = json.dumps(request_raw, indent=2)
                    data_dict = ast.literal_eval(data_raw)
                    d = json.loads(data_dict)

                    messageDetail.ReplyToChatV2("Zendesk Ticket <a href =\"" + (_configDef['zdesk_config']['zdesk_link']) + str(ticketID) + "\">" + str(ticketID) + "</a> is successfully asigned to " + name)

                    requestid = str(d["ticket"]["id"])
                    requeststatus = str(d["ticket"]["status"])
                    requestpriority = str(d["ticket"]["priority"])
                    requestseverity = str(d["ticket"]["tags"])

                    if (len(d["ticket"]["tags"])) == 0:
                        noTag = True
                    else:
                        noTag = False

                    notSet = True

                    if noTag:
                        sev = "Not set"
                        notSet = False

                    for index_tags in range(len(d["ticket"]["tags"])):
                        tags = str((d["ticket"]["tags"][index_tags]))

                        if tags.startswith("severity_1"):
                            sev = "Severity 1"
                            notSet = False
                        elif tags.startswith("severity_2"):
                            sev = "Severity 2"
                            notSet = False
                        elif tags.startswith("severity_3"):
                            sev = "Severity 3"
                            notSet = False
                        elif tags.startswith("severity_4"):
                            sev = "Severity 4"
                            notSet = False

                    if notSet:
                        sev = "Not Set"
                        notSet = False

                    requestseverity = sev

                    requestsubject_temps = str(d["ticket"]["subject"])
                    requestsubject = str(requestsubject_temps).replace("<", "&lt;").replace("\"", "&quot;").replace("&", "&amp;").replace("'","&apos;").replace(">","&gt;")
                    requestdescription_temps = str(d["ticket"]["description"])
                    requestdescription = str(requestdescription_temps).replace("<", "&lt;").replace("\"", "&quot;").replace("&", "&amp;").replace("'","&apos;").replace(">","&gt;")
                    requestorganization_id = str(d["ticket"]["organization_id"])
                    requestrequester_id = str(d["ticket"]["requester_id"])
                    requestcreated_at = str(d["ticket"]["created_at"]).replace("T", " ").replace("Z", "")
                    requestupdated_at = str(d["ticket"]["updated_at"]).replace("T", " ").replace("Z", "")
                    requestassignee_id = str(d["ticket"]["assignee_id"])

                    request_id = str(requestid)
                    request_status = str(requeststatus)
                    request_priority = str(requestpriority)
                    request_severity = str(requestseverity)
                    request_subject = str(requestsubject)
                    request_desc = str(requestdescription)
                    desc = str(request_desc)
                    request_org = str(requestorganization_id)
                    request_requestor = str(requestrequester_id)
                    request_created = str(requestcreated_at)
                    request_updated = str(requestupdated_at)

                    # To get the name of the requester given the requesterID
                    conn.request("GET", "/api/v2/users/" + request_requestor, headers=headers)
                    res = conn.getresponse()
                    userRequesterId = res.read()
                    tempUserRequester = str(userRequesterId.decode('utf-8'))

                    data = json.dumps(tempUserRequester, indent=2)
                    data_dict = ast.literal_eval(data)
                    d = json.loads(data_dict)
                    req_name = str(d["user"]["name"])
                    requesterName = req_name

                    try:
                        request_assignee = str(requestassignee_id)

                        # To get the name of the assignee given the assigneeID
                        conn.request("GET", "/api/v2/users/" + request_assignee, headers=headers)
                        res = conn.getresponse()
                        userAssigneeId = res.read()
                        tempUserAssignee = str(userAssigneeId.decode('utf-8'))

                        data = json.dumps(tempUserAssignee, indent=2)
                        data_dict = ast.literal_eval(data)
                        d = json.loads(data_dict)
                        assign_name = str(d["user"]["name"])
                        assigneeName = assign_name

                    except:
                        assigneeName = "Not assigned"
                        assignee_flag = True

                    requesterTicket = (_configDef['zdesk_config']['zdesk_link']) + str(request_id) + "/requester/requested_tickets"
                    assigneeTicket = (_configDef['zdesk_config']['zdesk_url']) + "/agent/users/" + request_assignee + "/assigned_tickets"
                    OrgTicket = (_configDef['zdesk_config']['zdesk_link']) + str(request_id) + "/organization/tickets"

                    # Convert the Zendesk ID to company name
                    conn.request("GET", "/api/v2/users/" + requestrequester_id + "/organizations.json", headers=headers)
                    res = conn.getresponse()
                    companyID = res.read()
                    compNameRaw = str(companyID.decode("utf-8"))

                    data = json.dumps(compNameRaw, indent=2)
                    data_dict = ast.literal_eval(data)
                    d = json.loads(data_dict)
                    org_Name = str(d["organizations"][0]["name"])
                    orgName = str(org_Name)

                    table_body = ""
                    table_header = "<table style='border-collapse:collapse;border:2px solid black;table-layout:auto;width:100%;box-shadow: 5px 5px'><thead><tr style='background-color:#4D94FF;color:#ffffff;font-size:1rem' class=\"tempo-text-color--white tempo-bg-color--black\">" \
                                   "<td style='width:20%;border:1px solid blue;border-bottom: double blue;text-align:center'>SUBJECT</td>" \
                                   "<td style='width:30%;border:1px solid blue;border-bottom: double blue;text-align:center'>DESCRIPTION</td>" \
                                   "<td style='width:2.5%;border:1px solid blue;border-bottom: double blue;text-align:center'>ID</td>" \
                                   "<td style='width:3%;border:1px solid blue;border-bottom: double blue;text-align:center'>STATUS</td>" \
                                   "<td style='width:3%;border:1px solid blue;border-bottom: double blue;text-align:center'>PRIORITY</td>" \
                                   "<td style='width:3.5%;border:1px solid blue;border-bottom: double blue;text-align:center'>SEVERITY</td>" \
                                   "<td style='width:5%;border:1px solid blue;border-bottom: double blue;text-align:center'>COMPANY</td>" \
                                   "<td style='width:7%;border:1px solid blue;border-bottom: double blue;text-align:center'>REQUESTER</td>" \
                                   "<td style='width:7%;border:1px solid blue;border-bottom: double blue;text-align:center'>CREATED</td>" \
                                   "<td style='width:7%;border:1px solid blue;border-bottom: double blue;text-align:center'>UPDATED</td>" \
                                   "<td style='width:7%;border:1px solid blue;border-bottom: double blue;text-align:center'>ASSIGNEE</td>" \
                                   "</tr></thead><tbody>"

                    if assignee_flag:

                        table_body += "<tr>" \
                                      "<td style='border:1px solid black;text-align:left'>" + request_subject + "</td>" \
                                      "<td style='border:1px solid black;text-align:left'>" + desc + "</td>" \
                                      "<td style='border:1px solid black;text-align:center'><a href=\"" + (_configDef['zdesk_config']['zdesk_link']) + str(request_id) + "\">" + str(request_id) + "</a></td>" \
                                      "<td style='border:1px solid black;text-align:center'>" + request_status + "</td>" \
                                      "<td style='border:1px solid black;text-align:center'>" + request_priority + "</td>" \
                                      "<td style='border:1px solid black;text-align:center'>" + request_severity + "</td>" \
                                      "<td style='border:1px solid black;text-align:center'><a href=\"" + OrgTicket + "\">" + orgName + "</a></td>" \
                                      "<td style='border:1px solid black;text-align:center'><a href=\"" + requesterTicket + "\">" + str(requesterName) + "</a></td>" \
                                      "<td style='border:1px solid black;text-align:center'>" + request_created + "</td>" \
                                      "<td style='border:1px solid black;text-align:center'>" + request_updated + "</td>" \
                                      "<td style='border:1px solid black;text-align:center'>" + assigneeName + "</td>" \
                                       "</tr>"

                    else:
                        table_body += "<tr>" \
                                      "<td style='border:1px solid black;text-align:left'>" + request_subject + "</td>" \
                                      "<td style='border:1px solid black;text-align:left'>" + desc + "</td>" \
                                      "<td style='border:1px solid black;text-align:center'><a href=\"" + (_configDef['zdesk_config']['zdesk_link']) + str(request_id) + "\">" + str(request_id) + "</a></td>" \
                                      "<td style='border:1px solid black;text-align:center'>" + request_status + "</td>" \
                                      "<td style='border:1px solid black;text-align:center'>" + request_priority + "</td>" \
                                      "<td style='border:1px solid black;text-align:center'>" + request_severity + "</td>" \
                                      "<td style='border:1px solid black;text-align:center'><a href=\"" + OrgTicket + "\">" + orgName + "</a></td>" \
                                      "<td style='border:1px solid black;text-align:center'><a href=\"" + requesterTicket + "\">" + str(requesterName) + "</a></td>" \
                                      "<td style='border:1px solid black;text-align:center'>" + request_created + "</td>" \
                                      "<td style='border:1px solid black;text-align:center'>" + request_updated + "</td>" \
                                      "<td style='border:1px solid black;text-align:center'><a href=\"" + assigneeTicket + "\">" + str(assigneeName) + "</a></td>" \
                                      "</tr>"

                    table_body += "</tbody></table>"
                    reply = table_header + table_body
                    return messageDetail.ReplyToChatV2_noBotLog(reply)

            else:
                botlog.LogSymphonyInfo("User is connected with the bot - Email Address: " + emailZendesk)

                query = "type:user " + emailAddress
                results = zendesk.search(query=query)
                #print(results)

                if str(results).startswith(
                        "{'results': [], 'facets': None, 'next_page': None, 'previous_page': None, 'count': 0}"):
                    return messageDetail.ReplyToChat(
                        "This user, <b>" + firstName + " " + lastName + "</b>, does not exist on Zendesk, the name is misspelled or does not belong to this organisation, <b>" + company + "</b>. Please use this format: /createRequest @mention, subject, description")
                elif str(results).startswith(
                        "{'results': [], 'facets': {'type': {'entry': 0, 'ticket': 0, 'organization': 0, 'user': 0, 'article': 0, 'group': 0}}, 'next_page': None, 'previous_page': None, 'count': 0}"):
                    return messageDetail.ReplyToChat(
                        "This organisation/company, <b>" + company + "</b>, does not exist in Zendesk or name, <b>" + firstName + " " + lastName +"</b>, is misspelled. Only Agents can be assigned ticket to. Please use this format: /assignTicket ticketid| @mention")
                else:

                    data = json.dumps(results, indent=2)
                    d = json.loads(data)

                    for index in range(len(d["results"])):
                        name = d["results"][index]["name"]
                        email = str(d["results"][index]["email"])
                        ZDuserId = str(d["results"][index]["id"])
                        role = str(d["results"][index]["role"])

                        if role == "end-user" or role == "End-user":
                            return messageDetail.ReplyToChatV2("This user, <b>" + name + " (" + email + "</b>), is Not an Agent on this Zendesk instance, please check via <b> /user </b> to find more information about Zendesk users and their role")

    ######           ## This is if the called user is an agent and it will add the user as an assignee and post an internal update

                    ############################

                    conn = http.client.HTTPSConnection(_configDef['zdesk_config']['zdesk_api'])

                    headers = {
                        'username': _configDef['zdesk_config']['zdesk_email'] + "/token",
                        'password': _configDef['zdesk_config']['zdesk_password'],
                        'authorization': _configDef['zdesk_config']['zdesk_auth'],
                        'cache-control': "no-cache",
                        'Content-Type': "application/json"
                    }

                    conn.request("GET", "/api/v2/tickets/" + ticketID + ".json", headers=headers)
                    res = conn.getresponse()
                    data = res.read()
                    request_raw = data.decode("utf-8")

                    ticketDoesNotExist = "{\"error\":\"RecordNotFound", "description\":\"Not found\"}"

                    if request_raw.startswith(ticketDoesNotExist):
                        return messageDetail.ReplyToChatV2(
                            "<b>There is no such Zendesk ticket number: " + str(ticketID) + "</b>")

                    try:
                        data = json.dumps(request_raw, indent=2)
                        data_dict = ast.literal_eval(data)
                        d = json.loads(data_dict)

                        # for index in range(len(request_raw["request"])):
                        # requestid = str(d["request"]["id"])
                        # requestassignee_id = str(d["request"]["assignee_id"])

                        requestid = str(d["ticket"]["id"])
                        requestassignee_id = str(d["ticket"]["assignee_id"])
                    except:
                        return messageDetail.ReplyToChat("Cannot get ticket info for ID " + str(ticketID))

                    try:
                        request_assignee = str(requestassignee_id)

                        # To get the name of the assignee given the assigneeID
                        conn.request("GET", "/api/v2/users/" + request_assignee, headers=headers)
                        res = conn.getresponse()
                        userAssigneeId = res.read()
                        tempUserAssignee = str(userAssigneeId.decode('utf-8'))

                        data = json.dumps(tempUserAssignee, indent=2)
                        data_dict = ast.literal_eval(data)
                        d = json.loads(data_dict)
                        #print(d)

                        assign_name = str(d["user"]["name"])
                        assign_email = str(d["user"]["email"])
                        assigneeName = assign_name
                        #print(assigneeName)
                    except:
                        try:
                            botlog.LogSymphonyInfo("Inside second try for assignee name in assignTicket")
                            request_assignee = str(requestassignee_id)

                            # To get the name of the assignee given the assigneeID
                            conn.request("GET", "/api/v2/users/" + request_assignee, headers=headers)
                            res = conn.getresponse()
                            userAssigneeId = res.read()
                            tempUserAssignee = str(userAssigneeId.decode('utf-8'))

                            data = json.dumps(tempUserAssignee, indent=2)
                            data_dict = ast.literal_eval(data)
                            d = json.loads(data_dict)
                            # print(d)

                            assign_name = str(d["user"]["name"])
                            assign_email = str(d["user"]["email"])
                            assigneeName = assign_name
                            # print(assigneeName)
                        except:
                            assigneeName = "N/A"

                    if str(assign_email) == str(email):
                        return messageDetail.ReplyToChatV2("This Zendesk Agent, <b>" + assigneeName + "</b> is already assigned to Zendesk Ticket : <b>" + str(ticketID) + "</b>")

                    conn = http.client.HTTPSConnection(_configDef['zdesk_config']['zdesk_api'])

                    #payload = "{\r\n  \"ticket\": {\r\n    \"assignee_id\": " + ZDuserId+ "\r\n  }\r\n}"

                    payload = "{\r\n  \"ticket\": {\r\n    \"assignee_id\": " + ZDuserId + ",\r\n    \"comment\":{\r\n    \t\"public\":\"Private\",\r\n    \t\"body\":\"" + callingUser + " assigned this ticket to " + name + "\"\r\n    }\r\n  }\r\n}"
                    #print(payload)

                    ## Using the bot to post an internal comment about the assignment
                    headers = {
                        'username': _configDef['zdesk_config']['zdesk_email'] + "/token",
                        'password': _configDef['zdesk_config']['zdesk_password'],
                        'authorization': _configDef['zdesk_config']['zdesk_auth'],
                        'cache-control': "no-cache",
                        'Content-Type': "application/json"
                    }

                    # base64Encoded = base64.b64encode(bytes((callingUserEMail + "/token:" + _configDef['zdesk_config']['zdesk_password']), 'utf-8'))
                    # base64Enc = (base64Encoded.decode("utf-8"))
                    # print(str(base64Enc))
                    # base = ("Basic " + base64Enc)
                    # print(str(base))
                    #
                    # headers = {
                    #     'email_address': callingUserEMail + "/token",
                    #     'password': (_configDef['zdesk_config']['zdesk_password']),
                    #     'authorization': base,
                    #     'cache-control': "no-cache",
                    #     'content-type': "application/json"
                    # }
                    # print(str(headers))

                    conn.request("PUT", "/api/v2/tickets/" + ticketID, payload, headers)

                    res = conn.getresponse()
                    data = res.read().decode("utf-8")

                    #print(data)

                    invalidTicket = "{\"error\":\"RecordNotFound","description\":\"Not found\"}"

                    if data.startswith(invalidTicket):
                        return messageDetail.ReplyToChatV2("This Zendesk Ticket ID does not exist, please check and try again.")

                messageDetail.ReplyToChatV2("Zendesk Ticket <a href =\"" + (_configDef['zdesk_config']['zdesk_link']) + str(ticketID) + "\">" + str(ticketID) + "</a> is successfully asigned to " + name)

                idt = ticketID

                ##      Will show the Ticket details in a table format.
                conn.request("GET", "/api/v2/tickets/" + idt + ".json", headers=headers)
                res = conn.getresponse()
                data = res.read()
                request_raw = data.decode("utf-8")

                data_raw = json.dumps(request_raw, indent=2)
                data_dict = ast.literal_eval(data_raw)
                d = json.loads(data_dict)

                requestid = str(d["ticket"]["id"])
                requeststatus = str(d["ticket"]["status"])
                requestpriority = str(d["ticket"]["priority"])
                requestseverity = str(d["ticket"]["tags"])

                if (len(d["ticket"]["tags"])) == 0:
                    noTag = True
                else:
                    noTag = False

                notSet = True

                if noTag:
                    sev = "Not set"
                    notSet = False

                for index_tags in range(len(d["ticket"]["tags"])):
                    tags = str((d["ticket"]["tags"][index_tags]))

                    if tags.startswith("severity_1"):
                        sev = "Severity 1"
                        notSet = False
                    elif tags.startswith("severity_2"):
                        sev = "Severity 2"
                        notSet = False
                    elif tags.startswith("severity_3"):
                        sev = "Severity 3"
                        notSet = False
                    elif tags.startswith("severity_4"):
                        sev = "Severity 4"
                        notSet = False

                if notSet:
                    sev = "Not Set"
                    notSet = False

                requestseverity = sev

                requestsubject_temps = str(d["ticket"]["subject"])
                requestsubject = str(requestsubject_temps).replace("<", "&lt;").replace("\"", "&quot;").replace("&", "&amp;").replace("'","&apos;").replace(">","&gt;")
                requestdescription_temps = str(d["ticket"]["description"])
                requestdescription = str(requestdescription_temps).replace("<", "&lt;").replace("\"", "&quot;").replace("&", "&amp;").replace("'","&apos;").replace(">","&gt;")
                requestorganization_id = str(d["ticket"]["organization_id"])
                requestrequester_id = str(d["ticket"]["requester_id"])
                requestcreated_at = str(d["ticket"]["created_at"]).replace("T", " ").replace("Z", "")
                requestupdated_at = str(d["ticket"]["updated_at"]).replace("T", " ").replace("Z", "")
                requestassignee_id = str(d["ticket"]["assignee_id"])

                request_id = str(requestid)
                request_status = str(requeststatus)
                request_priority = str(requestpriority)
                request_severity = str(requestseverity)
                request_subject = str(requestsubject)
                request_desc = str(requestdescription)
                desc = str(request_desc)
                request_org = str(requestorganization_id)
                request_requestor = str(requestrequester_id)
                request_created = str(requestcreated_at)
                request_updated = str(requestupdated_at)

                # To get the name of the requester given the requesterID
                conn.request("GET", "/api/v2/users/" + request_requestor, headers=headers)
                res = conn.getresponse()
                userRequesterId = res.read()
                tempUserRequester = str(userRequesterId.decode('utf-8'))

                data = json.dumps(tempUserRequester, indent=2)
                data_dict = ast.literal_eval(data)
                d = json.loads(data_dict)
                req_name = str(d["user"]["name"])
                requesterName = req_name

                try:
                    request_assignee = str(requestassignee_id)

                    # To get the name of the assignee given the assigneeID
                    conn.request("GET", "/api/v2/users/" + request_assignee, headers=headers)
                    res = conn.getresponse()
                    userAssigneeId = res.read()
                    tempUserAssignee = str(userAssigneeId.decode('utf-8'))

                    data = json.dumps(tempUserAssignee, indent=2)
                    data_dict = ast.literal_eval(data)
                    d = json.loads(data_dict)
                    assign_name = str(d["user"]["name"])
                    assigneeName = assign_name

                except:
                    assigneeName = "Not assigned"
                    assignee_flag = True

                requesterTicket = (_configDef['zdesk_config']['zdesk_link']) + str(request_id) + "/requester/requested_tickets"
                assigneeTicket = (_configDef['zdesk_config']['zdesk_url']) + "/agent/users/" + request_assignee + "/assigned_tickets"
                OrgTicket = (_configDef['zdesk_config']['zdesk_link']) + str(request_id) + "/organization/tickets"

                # Convert the Zendesk ID to company name
                conn.request("GET", "/api/v2/users/" + requestrequester_id + "/organizations.json", headers=headers)
                res = conn.getresponse()
                companyID = res.read()
                compNameRaw = str(companyID.decode("utf-8"))

                data = json.dumps(compNameRaw, indent=2)
                data_dict = ast.literal_eval(data)
                d = json.loads(data_dict)
                org_Name = str(d["organizations"][0]["name"])
                orgName = str(org_Name)

                table_body = ""
                table_header = "<table style='border-collapse:collapse;border:2px solid black;table-layout:auto;width:100%;box-shadow: 5px 5px'><thead><tr style='background-color:#4D94FF;color:#ffffff;font-size:1rem' class=\"tempo-text-color--white tempo-bg-color--black\">" \
                               "<td style='width:20%;border:1px solid blue;border-bottom: double blue;text-align:center'>SUBJECT</td>" \
                               "<td style='width:30%;border:1px solid blue;border-bottom: double blue;text-align:center'>DESCRIPTION</td>" \
                               "<td style='width:2.5%;border:1px solid blue;border-bottom: double blue;text-align:center'>ID</td>" \
                               "<td style='width:3%;border:1px solid blue;border-bottom: double blue;text-align:center'>STATUS</td>" \
                               "<td style='width:3%;border:1px solid blue;border-bottom: double blue;text-align:center'>PRIORITY</td>" \
                               "<td style='width:3.5%;border:1px solid blue;border-bottom: double blue;text-align:center'>SEVERITY</td>" \
                               "<td style='width:5%;border:1px solid blue;border-bottom: double blue;text-align:center'>COMPANY</td>" \
                               "<td style='width:7%;border:1px solid blue;border-bottom: double blue;text-align:center'>REQUESTER</td>" \
                               "<td style='width:7%;border:1px solid blue;border-bottom: double blue;text-align:center'>CREATED</td>" \
                               "<td style='width:7%;border:1px solid blue;border-bottom: double blue;text-align:center'>UPDATED</td>" \
                               "<td style='width:7%;border:1px solid blue;border-bottom: double blue;text-align:center'>ASSIGNEE</td>" \
                               "</tr></thead><tbody>"

                if assignee_flag:

                    table_body += "<tr>" \
                                  "<td style='border:1px solid black;text-align:left'>" + request_subject + "</td>" \
                                  "<td style='border:1px solid black;text-align:left'>" + desc + "</td>" \
                                  "<td style='border:1px solid black;text-align:center'><a href=\"" + (_configDef['zdesk_config']['zdesk_link']) + str(request_id) + "\">" + str(request_id) + "</a></td>" \
                                  "<td style='border:1px solid black;text-align:center'>" + request_status + "</td>" \
                                  "<td style='border:1px solid black;text-align:center'>" + request_priority + "</td>" \
                                  "<td style='border:1px solid black;text-align:center'>" + request_severity + "</td>" \
                                  "<td style='border:1px solid black;text-align:center'><a href=\"" + OrgTicket + "\">" + orgName + "</a></td>" \
                                  "<td style='border:1px solid black;text-align:center'><a href=\"" + requesterTicket + "\">" + str(requesterName) + "</a></td>" \
                                  "<td style='border:1px solid black;text-align:center'>" + request_created + "</td>" \
                                  "<td style='border:1px solid black;text-align:center'>" + request_updated + "</td>" \
                                  "<td style='border:1px solid black;text-align:center'>" + assigneeName + "</td>" \
                                  "</tr>"

                else:
                    table_body += "<tr>" \
                                  "<td style='border:1px solid black;text-align:left'>" + request_subject + "</td>" \
                                  "<td style='border:1px solid black;text-align:left'>" + desc + "</td>" \
                                  "<td style='border:1px solid black;text-align:center'><a href=\"" + (_configDef['zdesk_config']['zdesk_link']) + str(request_id) + "\">" + str(request_id) + "</a></td>" \
                                  "<td style='border:1px solid black;text-align:center'>" + request_status + "</td>" \
                                  "<td style='border:1px solid black;text-align:center'>" + request_priority + "</td>" \
                                  "<td style='border:1px solid black;text-align:center'>" + request_severity + "</td>" \
                                  "<td style='border:1px solid black;text-align:center'><a href=\"" + OrgTicket + "\">" + orgName + "</a></td>" \
                                  "<td style='border:1px solid black;text-align:center'><a href=\"" + requesterTicket + "\">" + str(requesterName) + "</a></td>" \
                                  "<td style='border:1px solid black;text-align:center'>" + request_created + "</td>" \
                                  "<td style='border:1px solid black;text-align:center'>" + request_updated + "</td>" \
                                  "<td style='border:1px solid black;text-align:center'><a href=\"" + assigneeTicket + "\">" + str(assigneeName) + "</a></td>" \
                                  "</tr>"

                table_body += "</tbody></table>"
                reply = table_header + table_body
                return messageDetail.ReplyToChatV2_noBotLog(reply)

        else:
            return messageDetail.ReplyToChat("You aren't authorised to use this command. If required, please review your Zendesk Role with your Zendesk Administrator")
    except:
        return messageDetail.ReplyToChat("I am sorry, I was working on a different task, can you please retry")

def addAccess(messageDetail):
    botlog.LogSymphonyInfo("####################")
    botlog.LogSymphonyInfo("Bot Call: Add Access")
    botlog.LogSymphonyInfo("####################")

    try:
        commandCallerUID = messageDetail.FromUserId

        connComp = http.client.HTTPSConnection(_configDef['symphonyinfo']['pod_hostname'])
        sessionTok = callout.GetSessionToken()

        headersCompany = {
            'sessiontoken': sessionTok,
            'cache-control': "no-cache"
        }

        try:
            connComp.request("GET", "/pod/v3/users?uid=" + commandCallerUID, headers=headersCompany)
        except:
            return messageDetail.ReplyToChat("I am having difficulty to find this user id: " + commandCallerUID)

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

        if callerCheck in (_configDef['AuthUser']['AdminList']):

            company = ""
            addAccessUsers = messageDetail.Command.MessageFlattened
            message_split = addAccessUsers.split()

            if len(message_split) == 1:
                return messageDetail.ReplyToChat("You need to @mention the user or users you want to add to the list of authorised access users")

            if len(message_split) == 2:
                #print("1 user")
                try:
                    detail = messageDetail.Command.MessageFlattened.split("|")
                except:
                    return messageDetail.ReplyToChat("Please use @mention")
                try:
                    flat = messageDetail.Command.MessageFlattened.split("_u_")
                    flat_len = len(flat)
                except:
                    return messageDetail.ReplyToChat("Please use @mention")

                    # removing excess characters to just get the UID
                    ############################################################
                try:
                    UID = flat[1][:int(_configDef['UID'])]
                    #print("UID: " + str(UID))

                    #Calling the API endpoint to get display name
                    connComp = http.client.HTTPSConnection(_configDef['symphonyinfo']['pod_hostname'])
                    sessionTok = callout.GetSessionToken()

                    headersCompany = {
                        'sessiontoken': sessionTok,
                        'cache-control': "no-cache"
                    }

                    try:
                        connComp.request("GET", "/pod/v3/users?uid=" + UID, headers=headersCompany)

                        resComp = connComp.getresponse()
                        dataComp = resComp.read()
                        data_raw = str(dataComp.decode('utf-8'))
                        data_dict = ast.literal_eval(data_raw)

                        dataRender = json.dumps(data_dict, indent=2)
                        d_org = json.loads(dataRender)
                    except:
                        return messageDetail.ReplyToChat(
                            "Please check the UID of the user, also make sure its digit matches the Config's setting.")

                    for index_org in range(len(d_org["users"])):
                        firstName = d_org["users"][index_org]["firstName"]
                        lastName = d_org["users"][index_org]["lastName"]
                        displayName = d_org["users"][index_org]["displayName"]
                        company = d_org["users"][index_org]["company"]
                        userID = str(d_org["users"][index_org]["id"])
                        fullname = (firstName + " " + lastName)

                        botlog.LogSymphonyInfo("Admin: " + messageDetail.Sender.Name + " is giving access to " + fullname + " (" + displayName + ") from: " + company + " with UID: " + str(userID))

                        AccessFile.append(firstName + " " + lastName + " - " + displayName + " - " + company + " - " + str(userID))

                        updatedAccess = 'AccessFile = ' + str(sorted(AccessFile))

                        #file = open("modules/plugins/Zendesk/access.py", "w+")
                        file = open("Data/access.py", "w+")
                        file.write(updatedAccess)
                        file.close()

                    return messageDetail.ReplyToChat("<b>" + firstName + " " + lastName + " (" + displayName + ") </b>, from " + company + " with user ID " + str(userID) + " , was successfully added to the <b>Authorised List</b>")
                except:
                    return messageDetail.ReplyToChat("You need to @mention the user")
            else:
                #print(" more than 1")

                for index in range(len(message_split)-1):
                    index = index + 1

                    try:
                        detail = messageDetail.Command.MessageFlattened.split("|")
                        #print("detail:" + detail)
                    except:
                        return messageDetail.ReplyToChat("Please use @mention")
                        # flat is used for getting the uid from flattened
                    try:
                        flat = messageDetail.Command.MessageFlattened.split("_u_")
                        flat_len = len(flat)
                        #print("flat:" + flat)

                    except:
                        return messageDetail.ReplyToChat("Please use @mention")

                        # removing excess characters to just get the UID
                        ############################################################
                    try:

                        #UID = flat[index][:15]
                        UID = flat[1][:int(_configDef['UID'])]
                        #print("UID: " + UID)

                        # Calling the API endpoint to get display name
                        connComp = http.client.HTTPSConnection(_configDef['symphonyinfo']['pod_hostname'])
                        sessionTok = callout.GetSessionToken()

                        headersCompany = {
                            'sessiontoken': sessionTok,
                            'cache-control': "no-cache"
                        }

                        try:
                            connComp.request("GET", "/pod/v3/users?uid=" + UID, headers=headersCompany)

                            resComp = connComp.getresponse()
                            dataComp = resComp.read()
                            data_raw = str(dataComp.decode('utf-8'))
                            data_dict = ast.literal_eval(data_raw)

                            dataRender = json.dumps(data_dict, indent=2)
                            d_org = json.loads(dataRender)
                        except:
                            return messageDetail.ReplyToChat("Please check the UID of the user, also make sure its digit matches the Config's setting.")

                        for index_org in range(len(d_org["users"])):
                            firstName = d_org["users"][index_org]["firstName"]
                            lastName = d_org["users"][index_org]["lastName"]
                            displayName = d_org["users"][index_org]["displayName"]
                            company = d_org["users"][index_org]["company"]
                            userID = str(d_org["users"][index_org]["id"])
                            fullname = (firstName + " " + lastName)

                            botlog.LogSymphonyInfo("Admin: " + messageDetail.Sender.Name + " is giving access to " + fullname + " (" + displayName + ") from: " + company + " with UID: " + str(userID))

                            AccessFile.append(firstName + " " + lastName + " - " + displayName + " - " + company + " - " + str(userID))


                            updatedAccess = 'AccessFile = ' + str(sorted(AccessFile))

                            #file = open("modules/plugins/Zendesk/access.py", "w+")
                            file = open("Data/access.py", "w+")
                            file.write(updatedAccess)
                            file.close()

                        botlog.LogSymphonyInfo(firstName + " " + lastName + ", from " + company + " with user ID " + str(userID) + " , was successfully added to the Authorised List")
                        alladded = True

                    except:
                        return messageDetail.ReplyToChat("You need to @mention the user(s)")

                if alladded:
                    messageDetail.ReplyToChat("Users were successfully added to the Authorised List")

                    try:

                        table_body = ""
                        table_header = "<table style='max-width:75%'><thead><tr style='background-color:#4D94FF;color:#ffffff;font-size:1rem' class=\"tempo-text-color--white tempo-bg-color--black\">" \
                                       "<td style='max-width:50%'>DISPLAY NAME</td>" \
                                       "</tr></thead><tbody>"

                        for access in sorted(AccessFile):
                            table_body += "<tr>" \
                                          "<td>" + access + "</td>" \
                                                            "</tr>"

                        table_body += "</tbody></table>"

                        reply = table_header + table_body
                        return messageDetail.ReplyToChatV2_noBotLog(
                            "<card iconSrc =\"https://thumb.ibb.co/csXBgU/Symphony2018_App_Icon_Mobile.png\" accent=\"tempo-bg-color--blue\"><header>Access List</header><body>" + reply + "</body></card>")

                    except:
                        return messageDetail.ReplyToChat("Access not found")

        else:
            return messageDetail.ReplyToChat("You aren't authorised to use this command.")
    except:
        return messageDetail.ReplyToChat("I am sorry, I was working on a different task, can you please retry")


def removeAccess(messageDetail):
    botlog.LogSymphonyInfo("#######################")
    botlog.LogSymphonyInfo("Bot Call: Remove Access")
    botlog.LogSymphonyInfo("#######################")

    try:
        commandCallerUID = messageDetail.FromUserId

        connComp = http.client.HTTPSConnection(_configDef['symphonyinfo']['pod_hostname'])
        sessionTok = callout.GetSessionToken()

        headersCompany = {
            'sessiontoken': sessionTok,
            'cache-control': "no-cache"
        }

        try:
            connComp.request("GET", "/pod/v3/users?uid=" + commandCallerUID, headers=headersCompany)
        except:
            return messageDetail.ReplyToChat("I am having difficulty to find this user id: " + commandCallerUID)

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

        if callerCheck in (_configDef['AuthUser']['AdminList']):

            company = ""
            remAccessUsers = messageDetail.Command.MessageFlattened
            message_split = remAccessUsers.split()

            if len(message_split) == 1:
                return messageDetail.ReplyToChat("You need to @mention the user or users you want to remove from the list of authorised access users")

            if len(message_split) == 2:

                try:
                    detail = messageDetail.Command.MessageFlattened.split("|")
                except:
                    return messageDetail.ReplyToChat("Please use @mention")
                try:
                    flat = messageDetail.Command.MessageFlattened.split("_u_")
                    flat_len = len(flat)
                except:
                    return messageDetail.ReplyToChat("Please use @mention")

                    # removing excess characters to just get the UID
                    ############################################################
                try:
                    UID = flat[1][:int(_configDef['UID'])]

                    # Calling the API endpoint to get display name
                    connComp = http.client.HTTPSConnection(_configDef['symphonyinfo']['pod_hostname'])
                    sessionTok = callout.GetSessionToken()

                    headersCompany = {
                        'sessiontoken': sessionTok,
                        'cache-control': "no-cache"
                    }

                    try:
                        connComp.request("GET", "/pod/v3/users?uid=" + UID, headers=headersCompany)

                        resComp = connComp.getresponse()
                        dataComp = resComp.read()
                        data_raw = str(dataComp.decode('utf-8'))
                        data_dict = ast.literal_eval(data_raw)

                        dataRender = json.dumps(data_dict, indent=2)
                        d_org = json.loads(dataRender)
                    except:
                        return messageDetail.ReplyToChat("Please check the UID of the user, also make sure its digit matches the Config's setting.")

                    for index_org in range(len(d_org["users"])):
                        firstName = d_org["users"][index_org]["firstName"]
                        lastName = d_org["users"][index_org]["lastName"]
                        displayName = d_org["users"][index_org]["displayName"]
                        company = d_org["users"][index_org]["company"]
                        userID = str(d_org["users"][index_org]["id"])
                        fullname = (firstName + " " + lastName)

                        botlog.LogSymphonyInfo("Admin: " + messageDetail.Sender.Name + " is removing access to " + fullname + " (" + displayName + ") from: " + company + " with UID: " + str(userID))
                        userTest = firstName + " " + lastName + " - " + displayName + " - " + company + " - " + str(userID)

                        try:
                            AccessFile.remove(firstName + " " + lastName + " - " + displayName + " - " + company + " - " + str(userID))
                        except:
                            return messageDetail.ReplyToChat("This user is not in the Access List")
                        updatedAccess = 'AccessFile = ' + str(sorted(AccessFile))

                        #file = open("modules/plugins/Zendesk/access.py", "w+")
                        file = open("Data/access.py", "w+")
                        file.write(updatedAccess)
                        file.close()

                    return messageDetail.ReplyToChat("<b>" + firstName + " " + lastName + " (" + displayName + ") </b>, from " + company + " with user ID " + str(userID) + " , was successfully removed from the Authorised List")
                except:
                    return messageDetail.ReplyToChat("You need to @mention the user")
            else:

                allremoved = False
                for index in range(len(message_split) - 1):
                    index = index + 1

                    try:
                        detail = messageDetail.Command.MessageFlattened.split("|")
                    except:
                        return messageDetail.ReplyToChat("Please use @mention")
                    try:
                        flat = messageDetail.Command.MessageFlattened.split("_u_")
                        flat_len = len(flat)

                    except:
                        return messageDetail.ReplyToChat("Please use @mention")

                        # removing excess characters to just get the UID
                        ############################################################
                    try:

                        UID = flat[1][:int(_configDef['UID'])]

                        # Calling the API endpoint to get display name
                        connComp = http.client.HTTPSConnection(_configDef['symphonyinfo']['pod_hostname'])
                        sessionTok = callout.GetSessionToken()

                        headersCompany = {
                            'sessiontoken': sessionTok,
                            'cache-control': "no-cache"
                        }

                        try:
                            connComp.request("GET", "/pod/v3/users?uid=" + UID, headers=headersCompany)

                            resComp = connComp.getresponse()
                            dataComp = resComp.read()
                            data_raw = str(dataComp.decode('utf-8'))
                            data_dict = ast.literal_eval(data_raw)

                            dataRender = json.dumps(data_dict, indent=2)
                            d_org = json.loads(dataRender)
                        except:
                            return messageDetail.ReplyToChat("Please check the UID of the user, also make sure its digit matches the Config's setting.")

                        for index_org in range(len(d_org["users"])):
                            firstName = d_org["users"][index_org]["firstName"]
                            lastName = d_org["users"][index_org]["lastName"]
                            displayName = d_org["users"][index_org]["displayName"]
                            company = d_org["users"][index_org]["company"]
                            userID = str(d_org["users"][index_org]["id"])
                            fullname = (firstName + " " + lastName)

                            botlog.LogSymphonyInfo("Admin: " + messageDetail.Sender.Name + " is removing access to " + fullname + " (" + displayName + ") from: " + company + " with UID: " + str(userID))

                            try:
                                AccessFile.remove(firstName + " " + lastName + " - " + displayName + " - " + company + " - " + str(userID))
                            except:
                                messageDetail.ReplyToChatV2("This user, <b>" + displayName + "</b> is not in the Access List")
                            updatedAccess = 'AccessFile = ' + str(sorted(AccessFile))

                            #file = open("modules/plugins/Zendesk/access.py", "w+")
                            file = open("Data/access.py", "w+")
                            file.write(updatedAccess)
                            file.close()

                        botlog.LogSymphonyInfo(firstName + " " + lastName + " (" + displayName + "), from " + company + " with user ID " + str(userID) + " , was successfully removed from the Authorised List")
                        allremoved = True

                    except:
                        return messageDetail.ReplyToChat("You need to @mention the user(s)")

                if allremoved:
                    messageDetail.ReplyToChat("Users were successfully removed from the Authorised List")

                    try:

                        table_body = ""
                        table_header = "<table style='max-width:75%'><thead><tr style='background-color:#4D94FF;color:#ffffff;font-size:1rem' class=\"tempo-text-color--white tempo-bg-color--black\">" \
                                       "<td style='max-width:50%'>DISPLAY NAME</td>" \
                                       "</tr></thead><tbody>"

                        for access in sorted(AccessFile):
                            table_body += "<tr>" \
                                          "<td>" + access + "</td>" \
                                                            "</tr>"

                        table_body += "</tbody></table>"

                        reply = table_header + table_body
                        return messageDetail.ReplyToChatV2_noBotLog(
                            "<card iconSrc =\"https://thumb.ibb.co/csXBgU/Symphony2018_App_Icon_Mobile.png\" accent=\"tempo-bg-color--blue\"><header>Access List</header><body>" + reply + "</body></card>")

                    except:
                        return messageDetail.ReplyToChat("Access not found")

        else:
            return messageDetail.ReplyToChat("You aren't authorised to use this command.")
    except:
        return messageDetail.ReplyToChat("I am sorry, I was working on a different task, can you please retry")


def listAllAccess(messageDetail):
    botlog.LogSymphonyInfo("#########################")
    botlog.LogSymphonyInfo("Bot Call: List All Access")
    botlog.LogSymphonyInfo("#########################")

    try:
        commandCallerUID = messageDetail.FromUserId

        connComp = http.client.HTTPSConnection(_configDef['symphonyinfo']['pod_hostname'])
        sessionTok = callout.GetSessionToken()

        headersCompany = {
            'sessiontoken': sessionTok,
            'cache-control': "no-cache"
        }

        try:
            connComp.request("GET", "/pod/v3/users?uid=" + commandCallerUID, headers=headersCompany)
        except:
            return messageDetail.ReplyToChat("I am having difficulty to find this user id: " + commandCallerUID)

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

        if callerCheck in (_configDef['AuthUser']['AdminList']):

            try:

                table_body = ""
                table_header = "<table style='table-layout:auto;max-width:75%'><thead><tr style='background-color:#4D94FF;color:#ffffff;font-size:1rem' class=\"tempo-text-color--white tempo-bg-color--black\">" \
                               "<td style='max-width:50%'>ZENDESK AGENT ACCESS LIST</td>" \
                               "</tr></thead><tbody>"

                for access in sorted(AccessFile):
                    table_body += "<tr>" \
                                  "<td>" + access +"</td>" \
                                  "</tr>"

                table_body += "</tbody></table>"

                reply = table_header + table_body
                return messageDetail.ReplyToChatV2_noBotLog(
                    "<card iconSrc =\"https://thumb.ibb.co/csXBgU/Symphony2018_App_Icon_Mobile.png\" accent=\"tempo-bg-color--blue\"><header>Zendesk Agent Access List</header><body>" + reply + "</body></card>")

            except:
                return messageDetail.ReplyToChat("Access not found")
        else:
            return messageDetail.ReplyToChat("You aren't authorised to use this command.")
    except:
        return messageDetail.ReplyToChat("I am sorry, I was working on a different task, can you please retry")


def sendBotConnectionRequest(messageDetail):
    botlog.LogSymphonyInfo("Bot Call: Send Bot Connection Request")

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
                firstName + " " + lastName + " (" + displayName + ") from Company/Pod name: " + str(companyName) + " with UID: " + str(
                    userID))
            callerCheck = (firstName + " " + lastName + " - " + displayName + " - " + companyName + " - " + str(userID))

        if callerCheck in (_configDef['AuthUser']['AdminList']):

            conn = http.client.HTTPSConnection(_configDef['symphonyinfo']['pod_hostname'])
            sessionTok = callout.GetSessionToken()

            # flat is used for getting the uid from flattened
            try:
                flat = messageDetail.Command.MessageFlattened.split("_u_")
            except:
                return messageDetail.ReplyToChat("Please use this format: /sendConnection @mention")

            # removing excess characters to just get the UID
            ############################################################
            UID = flat[1][:int(_configDef['UID'])]
            botlog.LogSymphonyInfo("Sending bot Connection Request to User: " + UID)

            payload = "{\n\"userId\": " + UID + " \n}"

            headers = {
                'sessiontoken': sessionTok,
                'content-type': "application/json",
                'cache-control': "no-cache"
            }

            conn.request("POST", "/pod/v1/connection/create", payload, headers)

            res = conn.getresponse()
            data = res.read().decode("utf-8")

            if data.startswith("{\"userId\":" + UID + ",\"status\":\"PENDING_OUTGOING\""):
                return messageDetail.ReplyToChat("The Bot connection request has been sent")
            else:
                return messageDetail.ReplyToChat(str(data))

        else:
            return messageDetail.ReplyToChat("You aren't authorised to use this command.")
    except:
        return messageDetail.ReplyToChat("I am sorry, I was working on a different task, can you please retry")

def removeBotConnectionRequest(messageDetail):
    botlog.LogSymphonyInfo("Bot Call: Remove Connection Request")

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

            botlog.LogSymphonyInfo(firstName + " " + lastName + " (" + displayName + ") from Company/Pod name: " + str(companyName) + " with UID: " + str(userID))
            callerCheck = (firstName + " " + lastName + " - " + displayName + " - " + companyName + " - " + str(userID))

        if callerCheck in (_configDef['AuthUser']['AdminList']):

            conn = http.client.HTTPSConnection(_configDef['symphonyinfo']['pod_hostname'])
            sessionTok = callout.GetSessionToken()

            # flat is used for getting the uid from flattened
            try:
                flat = messageDetail.Command.MessageFlattened.split("_u_")
            except:
                return messageDetail.ReplyToChat("Please use this format: /removeConnection @mention")

            # removing excess characters to just get the UID
            ############################################################
            UID = flat[1][:int(_configDef['UID'])]
            botlog.LogSymphonyInfo("Removing bot Connection from User: " + UID)

            headers = {
                'sessiontoken': sessionTok,
                'content-type': "application/json",
                'cache-control': "no-cache"
            }

            conn.request("POST", "/pod/v1/connection/user/" + UID + "/remove", headers=headers)

            res = conn.getresponse()
            data = res.read().decode("utf-8")

            connectionRemoved = "{\"format\":\"TEXT\",\"message\":\"Connection Removed.\"}"
            connectionNotFound = "{\"code\":404,\"message\":\"Connection not found.\"}"

            if data == connectionRemoved:
                return messageDetail.ReplyToChat("The connection between the Bot and the user as been removed")
            if data == connectionNotFound:
                return messageDetail.ReplyToChat("There is no connection between the bot and this user")
            else:
                return messageDetail.ReplyToChat(str(data))
        else:
            return messageDetail.ReplyToChat("You aren't authorised to use this command.")
    except:
        return messageDetail.ReplyToChat("I am sorry, I was working on a different task, can you please retry")


def listAllBotConnection(messageDetail):
    botlog.LogSymphonyInfo("Bot Call: List All Bot Connection")

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

                botlog.LogSymphonyInfo(firstName + " " + lastName + " (" + displayName + ") from Company/Pod name: " + str(companyName) + " with UID: " + str(userID))

                callerCheck = (firstName + " " + lastName + " - " + displayName + " - " + companyName + " - " + str(userID))

        except:
            return messageDetail.ReplyToChat("Cannot validate user access")

        if callerCheck in (_configDef['AuthUser']['AdminList']):

            messageDetail.ReplyToChat("Gathering all the Bot user connections, please wait.")
            conn = http.client.HTTPSConnection(_configDef['symphonyinfo']['pod_hostname'])
            sessionTok = callout.GetSessionToken()

            headers= {
                'sessiontoken': sessionTok,
                'cache-control': "no-cache"
            }

            try:
                conn.request("GET", "/pod/v1/connection/list?status=all", headers=headers)
                res = conn.getresponse()
                data = res.read().decode("utf-8")
            except:
                return messageDetail.ReplyToChat("I am not able to return the list of all connections.")

            dataList = data.split("},{")

            table_body = ""
            table_header = "<table style='max-width:100%;table-layout:auto'><thead><tr style='background-color:#4D94FF;color:#ffffff;font-size:1rem' class=\"tempo-text-color--white tempo-bg-color--black\">" \
                           "<td style='max-width:20%'>FULL NAME</td>" \
                           "<td style='max-width:20%'>DISPLAY NAME</td>" \
                           "<td style='max-width:20%'>UID</td>" \
                           "<td style='max-width:20%'>EMAIL</td>" \
                           "<td style='max-width:20%'>POD NAME</td>" \
                           "<td style='max-width:20%'>STATUS</td>" \
                           "<td style='max-width:20%'>UPDATED</td>" \
                           "</tr></thead><tbody>"

            bg_color = "purple"
            for index in range(len(dataList)):
                dataListIndexed = dataList[index]
                useridSplit = str(dataListIndexed).split(",")
                try:
                    useridConn = str(useridSplit[0][8:]).replace("\:","").replace(":","").replace("d\"","")
                    print("useridConn: " + str(useridConn))
                except:
                    useridConn = "N/A"
                try:
                    useridStatus = str(useridSplit[1][10:]).replace("\"", "")
                    print("useridStatus: " + str(useridStatus))
                except:
                    useridStatus = "N/A"
                try:
                    useridUpdated_epoch = str(useridSplit[2][12:]).replace("\"", "").replace("}]", "")
                    useridUpdated_epoch = (int(useridUpdated_epoch))
                    print("useridUpdated_epoch: " + str(useridUpdated_epoch))
                except:
                    useridStatus = "N/A"
                try:
                    dt = useridUpdated_epoch / 1000
                    print("dt: " + str(dt))
                    d = datetime.fromtimestamp(dt)
                    print("d: " + str(d))
                    d_split = str(d).split(".")
                    d_time = str(d_split[0])
                    useridUpdated = str(d_time)
                    print("useridUpdated: " + str(useridUpdated))
                except:
                    "N/A"

                try:
                    if useridStatus == "PENDING_INCOMING":
                        bg_color = "yellow"
                    if useridStatus == "PENDING_OUTGOING":
                        bg_color = "blue"
                    if useridStatus == "ACCEPTED":
                        bg_color = "green"
                    if useridStatus == "REJECTED":
                        bg_color = "red"
                except:
                    bg_color = "red"

                try:
                    connComp.request("GET", "/pod/v3/users?uid=" + useridConn, headers=headersCompany)

                    resComp = connComp.getresponse()
                    dataComp = resComp.read()
                    data_raw = str(dataComp.decode('utf-8'))

                    data_dict = ast.literal_eval(data_raw)
                    dataRender = json.dumps(data_dict, indent=2)
                    d_org = json.loads(dataRender)

                    for index_org in range(len(d_org["users"])):
                        firstName = d_org["users"][index_org]["firstName"]
                        lastName = d_org["users"][index_org]["lastName"]
                        displayNameL = d_org["users"][index_org]["displayName"]
                        try:
                            company = str(d_org["users"][index_org]["company"])
                        except:
                            company = "N/A"
                        userID = str(d_org["users"][index_org]["id"])
                        try:
                            emailAddress = str(d_org["users"][index_org]["emailAddress"])
                        except:
                            emailAddress = "N/A"
                        fullname = (firstName + " " + lastName)

                        table_body += "<tr>" \
                                      "<td>" + str(fullname) + "</td>" \
                                      "<td>" + str(displayNameL) + "</td>" \
                                      "<td>" + str(userID) + "</td>" \
                                      "<td>" + str(emailAddress) + "</td>" \
                                      "<td>" + str(company) + "</td>" \
                                      "<td class=\"tempo-bg-color--" + bg_color + " tempo-text-color--white\">" + str(useridStatus) + "</td>" \
                                      "<td>" + str(useridUpdated) + "</td>" \
                                      "</tr>"
                except:
                    messageDetail.ReplyToChat("Cannot lookup UID " + useridConn + "please check if the user is internal or external")

            table_body += "</tbody></table>"

            reply = table_header + table_body
            return messageDetail.ReplyToChatV2_noBotLog("<card iconSrc =\"https://thumb.ibb.co/csXBgU/Symphony2018_App_Icon_Mobile.png\" accent=\"tempo-bg-color--blue\"><header>Bot Connection List</header><body>" + reply + "</body></card>")

        else:
            return messageDetail.ReplyToChat("You aren't authorised to use this command.")
    except:
        return messageDetail.ReplyToChat("There seems to be some connectivity issue. Please try again after after 5 seconds")


def createZendeskUser(messageDetail):
    botlog.LogSymphonyInfo("#################################")
    botlog.LogSymphonyInfo("Bot Call: Create New Zendesk User")
    botlog.LogSymphonyInfo("#################################")

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

            botlog.LogSymphonyInfo(firstName + " " + lastName + " (" + displayName + ") from Company/Pod name: " + str(companyName) + " with UID: " + str(userID))

            callerCheck = (firstName + " " + lastName + " - " + displayName + " - " + companyName + " - " + str(userID))

        if callerCheck in (_configDef['AuthUser']['AdminList']):

            try:
                flat = messageDetail.Command.MessageFlattened.split("_u_")
                UID = flat[1][:int(_configDef['UID'])]
            except:
                return messageDetail.ReplyToChat("Please use @mention")

            connComp = http.client.HTTPSConnection(_configDef['symphonyinfo']['pod_hostname'])
            sessionTok = callout.GetSessionToken()

            headersCompany = {
                'sessiontoken': sessionTok,
                'cache-control': "no-cache"
            }

            try:
                connComp.request("GET", "/pod/v3/users?uid=" + UID + "&local=false", headers=headersCompany)

                resComp = connComp.getresponse()
                dataComp = resComp.read()
                data_raw = str(dataComp.decode('utf-8'))
                data_dict = ast.literal_eval(data_raw)

                dataRender = json.dumps(data_dict, indent=2)
                d_org = json.loads(dataRender)
                #print("User info from Symphony: " + str(d_org))
            except:
                return messageDetail.ReplyToChatV2("Could not get Symphony User Info" + str(d_org))

            for index_org in range(len(d_org["users"])):
                firstName = d_org["users"][index_org]["firstName"]
                lastName = d_org["users"][index_org]["lastName"]
                fullname = firstName + " " + lastName
                try:
                    emailAddress = str(d_org["users"][index_org]["emailAddress"])
                except:
                    return messageDetail.ReplyToChat("This user is not yet connected with the Bot, please send a connection request, user accepts then try again please.")
                    #emailAddress = "N/A"
                try:
                    companyName = d_org["users"][index_org]["company"]
                except:
                    companyName = "N/A"
            try:
                #Test to force Zendesk Org
                #companyName = ""
                payload = "{\n\t\"user\": \n\t{\n\t\t\"name\": \"" + fullname + "\", \n\t\t\"email\": \"" + emailAddress + "\", \n\t\t\"organization\": \n\t\t{\n\t\t\t\"name\": \"" + companyName + "\"\n\t\t}\n\t}\n}"
                #print("payload info for Zendesk " + str(payload))

                conn.request("POST", "/api/v2/users/create_or_update", payload, headers)

                res = conn.getresponse()
                data = res.read().decode("utf-8")
                #print("User Info on Zendesk: " + data)

                data_parser = json.dumps(data, indent=2)
                data_dict = ast.literal_eval(data_parser)
                d_req = json.loads(data_dict)
                ZD_id = str(d_req["user"]["id"])
                ZD_name = str(d_req["user"]["name"])
                ZD_email = str(d_req["user"]["email"])
                ZD_created = str(d_req["user"]["created_at"]).replace("T", " ").replace("Z","")
                ZD_updated = str(d_req["user"]["updated_at"]).replace("T", " ").replace("Z","")
                ZD_role = str(d_req["user"]["role"])

            except:
                return messageDetail.ReplyToChatV2("Could not create a new Zendesk User." + str(data))

            userLink = _configDef['zdesk_config']['zdesk_user'] + str(ZD_id) + "/requested_tickets"

            return messageDetail.ReplyToChatV2("New Zendesk User Created Successfully: <a href=\"" + str(userLink) + "\"><b>" + str(fullname) + "</b></a><br></br>(ID: <b>" + ZD_id + "</b> Name: <b>" + ZD_name + "</b> Email Address: <b>" + ZD_email + "</b> Created at: <b>" + ZD_created + "</b> Updated at: <b>" + ZD_updated + "</b> Zendesk User Role: <b>" + ZD_role + "</b>")
        else:
            return messageDetail.ReplyToChat("You aren't authorised to use this command.")

    except:
        return messageDetail.ReplyToChat("I am sorry, I was working on a different task, can you please retry")


def searchKb(messageDetail):
    botlog.LogSymphonyInfo("#################################")
    botlog.LogSymphonyInfo("Bot Call: Search Knowledge Base")
    botlog.LogSymphonyInfo("#################################")

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


            botlog.LogSymphonyInfo(firstName + " " + lastName + " (" + displayName + ") from Company/Pod name: " + str(companyName) + " with UID: " + str(userID))
            callerCheck = (firstName + " " + lastName + " - " + displayName + " - " + companyName + " - " + str(userID))


        if callerCheck in AccessFile:

            url = (_configDef['zdesk_config']['zdesk_url'] + "api/v2/help_center/articles/search")

            headers = {
                'username': _configDef['zdesk_config']['zdesk_email'] + "/token",
                'password': _configDef['zdesk_config']['zdesk_password'],
                'authorization': _configDef['zdesk_config']['zdesk_auth'],
                'cache-control': "no-cache",
                'Content-Type': "application/json"
            }

            querystring = {"query": "test"}

            response = requests.request("GET", url, headers=headers, params=querystring)

            print(response.text)

        else:
            return messageDetail.ReplyToChat("You aren't authorised to use this command.")

    except:
        return messageDetail.ReplyToChat("I am sorry, I was working on a different task, can you please retry")