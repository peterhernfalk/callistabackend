
# import hashlib
import json
# from time import time
# from datetime import datetime
# from urllib.parse import urlparse
# from uuid import uuid4
# import requests
from flask import Flask, request    # jsonify
# import random
# import uuid
# import seccure
import re

"""
#curl -X POST -H "Content-Type: application/json" -d '{"requestNumber": "0", "responseTo": "0", "value": "hej", "botId": "1", "language": "sv"}' "http://localhost:4001/request"
#curl -X POST -H "Content-Type: application/json" -d '{"requestNumber": "0", "responseTo": "0", "value": "microservice", "botId": "1", "language": "sv"}' "http://localhost:4001/request"
#curl -X POST -H "Content-Type: application/json" -d '{"requestNumber": "0", "responseTo": "0", "value": "om callista", "botId": "1", "language": "sv"}' "http://localhost:400/request"

##curl -X POST -H "Content-Type: application/json" -d '{"requestNumber": "0", "responseTo": "0", "value": "microservice", "botId": "1", "language": "sv"}' "https://callistabackend.herokuapp.com:4001/request"



# Chatbot examples, including stories: https://www.chatbot.com/docs/talk-with-bot/
# https://chatterbot.readthedocs.io/en/stable/
# Code sample: https://codepen.io/lilgreenland/pen/pyVvqB

Chatbot API:s
https://docs.microsoft.com/en-us/azure/bot-service/rest-api/bot-framework-rest-connector-api-reference?view=azure-bot-service-4.0
https://core.telegram.org/bots/api
https://www.livezilla.net/chatbotapi/en/
https://developers.viber.com/docs/api/rest-bot-api/
"""

##############################
# API Definition (Initially based on selected parts from LiveZilla Chat Bot API, and later modified to suit the purposes)
##############################


class Message:
    def __init__(self):
        # self.objectType = "Message"
        self.objectVersion = "1.0"
        self.label = ""
        self.link = ""
        self.linkcategory = ""      # presently: cadec, callista, notiser, presentationer, teknik
        self.publisheddate = ""


class RequestMessage:
    def __init__(self):
        # self.objectType = "ChatRequest"
        self.objectVersion = "1.0"
        self.requestNumber = "0"      # Requests serial number starting with 0
        self.responseTo = "0"         # Last response.id
        self.value = ""             # Visitors input
        self.botId = "0"              # In case we plan to use more than one bot
        # self.visitorName = ""
        self.language = ""


class ResponseMessage:
    def __init__(self):
        # self.objectType = "ChatResponse"
        self.objectVersion = "1.0"
        self.id = 0                 # Id, which can be used in next request
        self.action = ""            # chat | message. Start chat with human or leave a message
        # self.reply = ""             # Answer to the request. General response text (HTML)
        self.messages = []
        self.teasers = []

    def tojson(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)


class Teaser:
    def __init__(self):
        # self.objectType = "Teaser"
        self.objectVersion = "1.0"
        self.id = 0                 # Id, which can be used in next request
        self.teaserCategory = ""
        self.teaserTitle = ""
        self.teaserURL = ""


##############################
# Chat Bot
##############################
class ChatBot:
    def __init__(self):
        self.botId = "Botten"
        self.keywordfile = "keywords.txt"
        self.keywords = ""
        self.about_keywords = ['callista']
        self.event_keywords = ['cadec', 'event', 'aktuellt', 'konferens']
        self.offer_keywords = ['erbjudande']
        self.recruit_keywords = ['jobb', 'rekrytering']

    def loadkeywords(self):
        print("loadkeywords:", len(self.keywords))
        self.keywords = open(self.keywordfile, 'r').read().lower()

    def loadblogdata(self):
        self.blogdata = open(blogdatafile, 'r').read().lower()
        self.blogdata_links = open(blogdatafile, 'r').readlines()
        self.blogdata_nolinks = open(blogdatafile_titles, 'r').read().lower()
        print("loadblogdata:", len(self.blogdata))

    def find_blogposts(self, keyword):
        line_number = 0
        resultlist = []
        for line in chatbot.blogdata_nolinks.split("\n"):
            line_number += 1
            if keyword in line.split():
                resultlist.append((keyword, line_number, chatbot.blogdata_links[line_number - 1]))

        return resultlist

    def get_bot_reply(self, request):
        response = ResponseMessage()
        response.id = request.botId   # str(int(requestmessage.botId) + 1)
        response.action = "chat"

        requestmessagelowercase = request.value.lower()

        requestwords = re.findall(r'\w+', requestmessagelowercase)
        keywordlist = []
        for word in requestwords:
            label = ""
            link = ""
            publisheddate = ""

            if word in self.keywords:
                if debugExecution == True:
                    print("keyword: " + word)

                keywordlist.append(word)
                matched_lines = self.find_blogposts(word)

                if debugExecution == True:
                    print("Keyword: " + word + '. Total Matched blog posts: ', len(matched_lines))
                if len(matched_lines) == 0:
                    # This can only happen if "word in self.keywords" doesn't work properly
                    label = "Vår sökfunktion kan tyvärr inte hitta några bloggar som motsvarar det du frågade efter."
                elif len(matched_lines) == 1:
                    label = "Varsågod, här är en länk om " + word  # + "<br>"
                elif len(matched_lines) > 1:
                    label = "Varsågod, här är " + str(len(matched_lines)) + " länkar om " + word

                response.messages.append(self.add_message(label, link))

                for line_element in matched_lines:
                    label = ""
                    link = line_element[2]
                    response.messages.append(self.add_message(label, link))

                    if debugExecution == True:
                        print('Word = ', line_element[0], ' :: Line Number = ', line_element[1], ' :: Line = ', line_element[2])
                keywordlist.clear()

        if len(response.messages) == 0:
            label = self.get_chitchat_reply(requestmessagelowercase)
            response.messages.append(self.add_message(label, link))

        response = self.add_teasers(requestwords, response)

        return response.tojson()

    def add_message(self, label, link):
        message = Message()
        message.label = label
        message.link = link
        if len(link) > 0:
            message.publisheddate = self.get_date_from_link(link)
            message.linkcategory = self.get_category_from_link(link)

        return message

    def get_date_from_link(self, link):
        trimmeddate = re.search('\d{4}/\d{2}/\d{2}', link).group()
        formatteddate = trimmeddate.replace('/', '-')

        return formatteddate

    def get_category_from_link(self, link):
        linkcategory = ""

        # Rather ugly code, but it works
        match = re.search('blogg/(.*)/', link).group()
        match = match[6:]
        end_of_category = match.find('/')
        linkcategory = match[0:end_of_category]

        return linkcategory

    def add_teasers(self, requestwords, response):
        teaserCategory = "None"

        for word in requestwords:
            if word in chatbot.about_keywords:
                label = "Om du är intresserad av " + word + " så kan du följa länken om Callista"
                link = ""
                response.messages.append(self.add_message(label, link))
                teaser2 = Teaser()
                teaser2.id = 1
                teaser2.teaserCategory = "About"
                teaser2.teaserTitle = "Om Callista"
                teaser2.teaserURL = "https://callistaenterprise.se/om/"
                response.teasers.append(teaser2)

            if word in chatbot.event_keywords:
                label = "Nästa Cadec är i Stockholm 2022-01-26"
                link = ""
                response.messages.append(self.add_message(label, link))
                teaser1 = Teaser()
                teaser1.id = 2
                teaser1.teaserCategory = "Event"
                teaser1.teaserTitle = "Cadec"
                teaser1.teaserURL = "https://callistaenterprise.se/event/cadec/"
                response.teasers.append(teaser1)

            if word in chatbot.offer_keywords:
                label = "Om du är intresserad av " + word + " så kan du följa länken om erbjudanden"
                link = ""
                response.messages.append(self.add_message(label, link))
                teaser2 = Teaser()
                teaser2.id = 3
                teaser2.teaserCategory = "Link"
                teaser2.teaserTitle = "Erbjudanden"
                teaser2.teaserURL = "https://callistaenterprise.se/erbjudanden/"
                response.teasers.append(teaser2)

            if word in chatbot.recruit_keywords:
                label = "Om du är intresserad av " + word + " så kan du följa länken om jobb hos oss"
                link = ""
                response.messages.append(self.add_message(label, link))
                teaser2 = Teaser()
                teaser2.id = 3
                teaser2.teaserCategory = "Link"
                teaser2.teaserTitle = "Jobba hos oss"
                teaser2.teaserURL = "https://callistaenterprise.se/om/jobb/"
                response.teasers.append(teaser2)

        return response

    def get_chitchat_reply(self, requestmessagelowercase):
        # https://lionbridge.ai/datasets/15-best-chatbot-datasets-for-machine-learning/
        # https://github.com/Microsoft/BotBuilder-PersonalityChat/tree/master/CSharp/Datasets
        # https://docs.microsoft.com/sv-se/azure/cognitive-services/qnamaker/how-to/chit-chat-knowledge-base
        # https://webscope.sandbox.yahoo.com/catalog.php?datatype=l&guccounter=1

        chitchatReply = ""
        if requestmessagelowercase == "hej":
            chitchatReply = "Hej!"
        elif requestmessagelowercase == "help":
            chitchatReply = "Fråga gärna om sådant som intresserar dig. Vi har för närvarande " + str(
                len(self.blogdata_links)) + " bloggartiklar, främst om teknik."
        else:
            chitchatReply = "Vi har tyvärr inga bloggar som motsvarar det du frågade efter."

        return chitchatReply


##############################
# Startup settings
##############################
# Instantiate the App
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# Instantiate Classes
chatbot = ChatBot()
requestmessage = RequestMessage()
responsemessage = ResponseMessage()


##############################
# App Endpoints
##############################
@app.route('/request', methods=['POST'])
def reponse2request():

    # Session Settings
    global blogdatafile
    global blogdatafile_titles
    global debugExecution
    blogdatafile = "blogdata_links.txt"
    blogdatafile_titles = "blogdata_titles.txt"
    debugExecution = True
    # Execute_after_startup()
    chatbot.loadkeywords()
    chatbot.loadblogdata()


    values = request.get_json()
    requestmessage.requestNumber = values.get('requestNumber')
    requestmessage.responseTo = values.get('responseTo')
    requestmessage.value = values.get('value')
    # requestmessage.botId = values.get('botId')
    requestmessage.language = values.get('language')

    responsemessage = chatbot.get_bot_reply(requestmessage)
    print("reponse2request:", values, responsemessage)

    response = {
        'message': 'response',
        'reply': responsemessage,
    }

    #if debugExecution == True:
    #    print("request: \n" + str(values))
    #    print("response: \n" + responsemessage)
    #print("request: \n" + str(values))

    return responsemessage


##############################
# Main
##############################
if __name__ == '__main__':
    from argparse import ArgumentParser

    # Session Settings
    blogdatafile = "blogdata_links.txt"
    blogdatafile_titles = "blogdata_titles.txt"
    # ##blogdatafile_titles = "blogdata/blogdata_shorttitles.txt"
    debugExecution = True

    # Execute_after_startup()
    print("Execute_after_startup()")
    chatbot.loadkeywords()
    chatbot.loadblogdata()

    ########## development
    search_phrase1 = 'machine learning'
    search_phrase2 = '"machine learning"'
    search_phrase3 = 'machine+learning'
    # keyword1 = "machine"
    # keyword2 = "learning"
    blog_title_list1 = "['machine', 'learning', 'på', 'javaplattformen']"
    blog_title_list2 = "['gdpr-aspekter', 'på', 'machine', 'learning', 'och', 'hur', 'automatiska', 'beslut', 'kan', 'förklaras', 'med', 'hjälp', 'av', 'visualisering']"

    """for line in chatbot.blogdata_nolinks.split("\n"):
        line_number += 1
        if keyword in line.split():"""

    # print(chatbot.get_category_from_link('<a href="https://callistaenterprise.se/blogg/presentationer/cadec/2019/01/30/ark/" target="_blank">Macro, mini, micro, … – hur väljer du rätt tjänstebaserad arkitektur?</a>'))
    ##########

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=4001, type=int, help='port to listen on')
    args = parser.parse_args()
    #port = args.port
    #port = 4001
    #usedHost = 'https://callistabackend.herokuapp.com'
    #instance_address = "http://" + usedHost + ":" + str(port)
    #instance_address = usedHost
    #app.run(host=usedHost, port=port)

    usedHost = 'https://callistabackend.herokuapp.com'
    app.run(host=usedHost)
