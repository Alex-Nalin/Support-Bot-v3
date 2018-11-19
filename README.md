Bot written from the Symphony-Ares bot base.

# Symphony Zendesk Bot
A multi-function bot for use with the Symphony communications platform

Symphony Zendesk Bot is an example of a multi-function command and chat-bot for the Symphony communications platform. It was written using Python 3.5.

The main purpose of Symphony Zendesk Bot is to assist the Support team with their daily work

These are the functions added for this to integrate to Zendesk Support Ticket Management:

* searchMyTickets (`/searchMyTickets <open/new/pending/solved/closed/unresolved/all> (optional)`) to search for your own Zendesk ticket or (`/searchMyTickets <open/new/pending/solved/closed/unresolved/all> @mention`) to search for a colleague's Zendesk ticket by status.
* Show Zendesk Comments (`/showComments <ticket_id>`) will show the updates made to a ticket and its author. This will show attachments and their respective size
* Create Zendesk Ticket (`/createTicket subject| description`) as an agent and, this will use the agent as the ticket requester with default values.
* Create Zendesk Request (`/createRequest <@mention user>| <subject>| <description>`) by @mentioning a Symphony user, the bot will cross check the user on Zendesk and once validated, it will create a Zendesk ticket with the provided title and description of the issue/problem.
* Recent Zendesk ticket (`/recentZD`), this will show all the recent ticket the agents have reviewed.
* User (`/user alex| Symphony`) will return all the users named Alex on the Symphony Zendesk account. (`/user alex nalin| symphony`) will return all users name Alex Nalin on the Symphony Zendesk account. If you want to get the full list of users on a given account use this method (`/user | symphony`) (to look for all users on the Symphony Zendesk account)
* Show Zendesk  (`/show <ticketid>`) is a call to display a given Zendesk ticket by its ID.
* Today call (`/today`) will show all the tickets raised today, you can also specify how many days back to go (`/today 5`) to get a bigger list of recently raised support issue from 5 days ago.
* Ticket Update (`/ticketUpdate <ticketID>| comment| status| public/private`) will allow the caller to add a public or private update to an existing Support Ticket.
* Assign Ticket (`assignTicket` <ticketID> <@mention user>) will assign the Zendesk ticket to the @mentioned Zendesk Agent who is also a Symphony user.
* Whois Symphony User (`/whois @mentioned user`) allow to look up a user and get profile information
* UIDcheck (`/uidCheck <UID>`) allows the caller to retrieve details from a given Symphony UID
* streamCheck (`/streamCheck <streamID>`) allows the caller to retrieve details from a given Symphony StreamID also known as ConversationID


* Add Access (`/addAccess <@mention user(s)>`) to the list of authorised users to communicate with the Bot to execute commands. It will also sort the list when adding new user. This is an Admin restricted function
* Remove Access (`/removeAccess <@mention user>`) of the user to remove from the list of authorised users. This is an Admin restricted function
* List All Access (`/listallaccess`) as its function states, this will return all the authorised user list. This is an Admin restricted function
* Sends a Bot connection request (`/sendConnection @mention user`) to a Symphony user /sendConnection @mention(required) (the bot will auto send connection request). This is an Admin restricted function
* Remove the Bot connection (`/removeConnection @mention user`) from a Symphony user. This is an Admin restricted function
* List all the Bot connections (`/botConnection`) with their status. This is an Admin restricted function
* Give a list of all the Bot Symphnony streams (`/botStream`) that exist with users, this include IM, MIM and ROOMs
* Send Bot message (`/botMessage IM/ROOM/ALL <message>`) to IM/MIM/ROOMs where the bot is a member of to inform or an update or else.
* Shutdown bot (`/shutdown IM/ROOM/ALL <message>(optional)`) with or without a message to IM/MIM or Rooms
* Create a Zendesk user (`/createZendeskUser @mention`) by @mentioning the Symphony User, the user needs to be connected with the bot in order to do this a it requires the email address.


## Requirements

The bot was built using Pycharm on Ubuntu 17.04 and runs against Python 3.5, though it likely will run against Python 2.7 with minor modifications. 

* Python 3.5 

    * requests - http://docs.python-requests.org/en/master/
    * lxml - http://lxml.de/
    * cryptography.io - https://cryptography.io/en/latest/
    * Redis - https://pypi.python.org/pypi/redis
    * RQ - http://python-rq.org/

* Redis 2.6.0 or better

    * https://redis.io/
    * Sample Docker config: https://github.com/sameersbn/docker-redis

* A Symphony bot account with client certificate files

    * Client certificates are generally provided as .p12 files. The code asks for .pem files in /certificates
    * You will need the certificate password to extract the .pem files
    * crt.pem: openssl pkcs12 -in path.p12 -out bot.crt.pem -clcerts -nokeys
    * key.pem: openssl pkcs12 -in path.p12 -out bot.key.pem -nocerts -nodes

* Access to your POD's REST endpoints

## Installation

Installation of the bot is somewhat manual today. 

1. Clone the repo to your local environment 

    * `git clone https://github.com/Alex-Nalin/Symphony-Zendesk-bot`

2. Install and configure your Redis server. 
3. Create new config file by copying the *.sample.json to *.json (e.g. config.sample.json -> config.json)
4. Modify the main config files:

    * ./SymphonyZendeskBot/config.json - Contains general config details, including information about your Symphony configuration

5. Use access.sample.py to create -> `access.py` file and use dictionary.sample.py to create -> `dictionary.py`

## Starting the Bot

1. Ensure your Redis server is running
2. Start the Redis worker process

    * Open a new terminal session
    * Change to the bot folder, e.g. `cd /bots/symphony/SymphonyZendeskBot/`
    * Run the worker script: `python3 startWorker.py`

3. Start the bot

    * Open a new terminal session
    * Change to the bot folder
    * Run the bot script: `python3 startBot.py`

## Logging

SymphonyZendeskBot does not log messages, but will log other activity, including commands that are issued. Various logs can be found in ./SymphonyZendeskBot/logging

## Usage

Several functions are included by default with the bot. 

**Note**: The bot user _must_ be in the room in which a command is issued. Symphony does not support global commands at this time. 

### Google Translate:

Autodetects and translates the provided sentence into English

* Command: /translate "Hola. Como estas?"
* Reply: I think you said "Hello how are you?" (es)
* The two-letter language code for the auto-identified source language is included at the end of the reply

### Stock Quotes (AlphaVantage)

Pulls the most recent Open and Close prices for the given ticker symbol

* Command: `/quote AAPL`
* Reply: 

    Quote for: AAPL
    Date: 2017-09-04
    Open: 164.7600
    Close: 164.0400

* Note: An AlphaVantage API token is required. This can be obtained for free: https://www.alphavantage.co/documentation/

### Giphy

Searches for and returns a gif

* Command: `/gif Search Text`
* Reply: [link to gif]
* Note 1: /gif with no parameters produces a random gif
* Note 2: Requires an API token for Giphy: https://developers.giphy.com/

### Echo

A simple test to verify the bot is working and Symphony's APIs are responding

* Command: `/echo` [echo text]
* Reply: [echo text]

### Quote of the day

`/quote`

Retrieves the Quote of the day from quotes.rest and displays the author and the message in a card formatted text.

### Weather forecast

`/weather london 5`

Give the weather forecast (from api.apixu.com) by location (city/postcode/zipcode) and for up to 7 days with various attributes such as average temperature, sunrise, moonset and with image.

### Random Famous Quotes

`/funQuote`

Will return some movies or famous peoples Quote via the api.andrux.net

### Random Jokes

`/joke`

Will return a funny joke from icanhazdadjoke.com

### Add/Remove(sort), Search and List Acronyms (Jelena Kolomijec)

`/addAcronym`
`/removeAcronym`
`/findAcronym`
/`ListAllAcronym`

Allows to add, remove and search for acroyms added to a custom dictionary

### Wiki Search (Jelena Kolomijec)

`/wikiSearch`

Give the top three results from Wikipedia

## Plugins

This initial python distribution includes a nascent framework for creating plugins for the bot. A plugin must contain several files:

* config.json - this file must be valid json and must contain a `"commands": []` array that will tell the plugin parser what commands you have provided for the users

    Each command must have the following attributes:

    * "triggers": [] -> An array of strings - each string will act as a command alias for this command

        E.g. "triggers": ["quote", "$", "qt"] => the /quote command will also trigger with /qt or /$

    * "function": FunctionName -> The method name in your commands.py that the triggers will execute
    * "description": [text] -> Description of your command. Returned with /[command] help
    * "helptext": [text] -> Help info for your command. Returned with /[command] help

* commands.py - Contains the method definitions specified in config.json
* __init__.py -> A blank file that python uses to correctly identify packages

Any additional files required for processing your command are ignored by the plugin parser