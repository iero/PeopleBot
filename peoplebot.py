import os
import time
import sys
import json

from slackclient import SlackClient

import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup

from requests_oauthlib import OAuth2Session, requests

import urllib.parse
from urllib.request import Request, urlopen
from urllib.parse import urlparse

#get authentication fron the authentication URL.
#The people api, at the first authentication, request a user/password over
#a login page. This function below go through the login page and play the give
# user/password.

def getAuth(authorization_url, people_username, people_password) :
    #print(entry_domain)
    client = requests.session()
    r = client.get(authorization_url)

    soup = BeautifulSoup(r.content, "html.parser")
    desc = soup.find("meta", {"name":"csrf-token"})
    csrftoken = desc['content']

    #print("+-[token] : {}".format(csrftoken))
    entry_parsed = urlparse(authorization_url)
    entry_domain = '{uri.scheme}://{uri.netloc}'.format(uri=entry_parsed)
    soup = BeautifulSoup(r.content, "html.parser")
    desc = soup.find("form", {"class":"new_user"})
    url = entry_domain+desc['action']
    #print("+-[url] : {}".format(url))

    payload = urllib.parse.urlencode({
        'utf8':'✓',
        'authenticity_token':csrftoken,
        'user[email]':people_username,
        'user[password]':people_password,
        'user[remember_me]':'0',
        'commit':'Log in'
        })

    r = client.post(url, data=payload, headers=dict(Referer=url))

    soup = BeautifulSoup(r.content, "html.parser")
    desc = soup.find("code", {"id":"authorization_code"})
    code = desc.text
    #print("+-[auth code] : {}".format(code))

    return code

def getStats() :
    authorization_response=oauth.get('https://people.total/api/v1/statistics')
    response = authorization_response.content
    print(response)
    response = response.decode("utf-8")
    json_decode=json.loads(response)

    result=[]
    my_dict={}
    my_dict["users"]=json_decode['users']['total_count']
    # for u in json_decode['users'] :
    #     for s in u :
    #         print("+-[{}] {}".format(s,u[s]))

    result.append(my_dict)
    attachments=json.dumps(result)

    textresponse="Tada :"

    return textresponse, attachments

#retrieve person profile from ID in people database

#simple function to retrieve the profile of a person from people database,
#using its ID in the database.
# retrieve_people(ID), where ID is a digits. Example: retrieve_people(1)

def retrieve_people(url,ID):
    #"""
    #        Retrieve the profile of a person from its ID
    #        returns back a text, and attachment for the person.
    #"""
    authorization_response=oauth.get(url+"/users/"+str(ID))
    response = authorization_response.content
    #print(response)
    response = response.decode("utf-8")
    json_decode=json.loads(response)

    #create the text of the slackbot response.
    textresponse="I gess you are looking for (best match):"
    #print(json_decode['first_name'])

    #create attachements in the slackbot response.
    #print(json_decode["jobs"])
    result=[]
    my_dict={}
    my_dict["author_name"]=json_decode['first_name'] + " " + json_decode["last_name"]
    my_dict["author_link"]="https://people.total/p/" + json_decode["slugged_id"]
    my_dict["attachment_type"]="default"
    my_dict["short"]="true"
    #check if 'the' jobs section in people database is populate for the given person.
    #if not, retrive only its 'title'
    if json_decode["jobs"]:
        my_dict["text"]=json_decode["job_title"] + " - " + json_decode["jobs"][0]["description"]
    else:
        my_dict["text"]=json_decode["job_title"]

    my_dict["color"]="#3AA3E3"
    my_dict["attachment_type"]="default"
    my_dict["fields"]=[{"title": "phone","value": json_decode["phone"],"short": "true" }, \
        {"title": "entity","value": json_decode["entity"],"short": "true" }, \
        {"title": "office address","value": json_decode["office_address"],"short": "true" }]
    my_dict["thumb_url"]=json_decode['picture_url']
    my_dict["footer"]="people.total"
    my_dict["ts"]=time.time()
    #print(my_dict)

    result.append(my_dict)
    #print(result)
    attachments=json.dumps(result)

    return textresponse, attachments


#retrieve list of people

#simple function to retrieve a list of people from people database,
#using the search api of the application.
# retrieve_people(url, search_string, action), where :
#       - 'url' is the url of the api,
#       - 'search' string is the message ask to the bot by the end user over the slack interface
#       - 'action' is a word of the sentence. It will be removed from the search string.


def search_people(url, search_string, action):
    """
    Retrieve a list of people through a search in people
    The command action is remove from the search string
    returns back a text, an attachment per person, and the id of the first one.
    """
    authorization_response=oauth.get(url+'/users/search/{'+ search_string.replace(action,'') + '}')
    response = authorization_response.content
    response = response.decode("utf-8")
    json_decode=json.loads(response)


    #response creation
    textresponse="Here are the people for your search: *" + search_string.replace('search','') + "*\n"
    #print(textresponse)

    #create attachements
    result=[]
    for item in json_decode:
        my_dict={}
        my_dict["title"]=item.get('first_name') + " " + item.get("last_name")
        my_dict["text"]=item.get("job_title")
        #y_dict["fallback"]="You did not want more info..."
        #my_dict["callback_id"]="people_userid"
        my_dict["color"]="#3AA3E3"
        my_dict["attachment_type"]="default"
        #pour ajouter un bouton, mais seul les app slack le permettent
        #my_dict["actions"]=[{"name": "user","text": "More info...","type": "button","value":  str(item.get("id")) }]
        #print(my_dict)
        result.append(my_dict)

    print(result)
    attachments=json.dumps(result)

    first_id = json_decode[0]["id"]

    return textresponse, attachments, first_id


def handle_command(url, command, channel):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    EXAMPLE_COMMAND = "search"

    response = "Not sure what you mean. Use the *" + EXAMPLE_COMMAND + \
               "* command with numbers, delimited by spaces."

    if command.startswith("help"):
        response = "Sure... Use *search* or *who is* commands, and I will look for you!"
        attachement = ""

    elif command.startswith("who is") or command.startswith("whois"):
        response, attachement, first_id = search_people(url,command, "who is")
        response, attachement = retrieve_people(url,first_id)

    elif command.startswith("search"):
        print(command)
        response, attachement, first_id = search_people(url,command, "search")

    else:
        response = "I don't know... Use *search* or *who is* commands, and I will look for you!"
        attachement = ""

    slack_client.api_call("chat.postMessage", channel=channel,
                          text=response, attachments=attachement, as_user=True)


def parse_slack_output(bot_id, slack_rtm_output):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """
    AT_BOT = "<@" + bot_id + ">"

    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                # return text after the @ mention, whitespace removed
                return output['text'].split(AT_BOT)[1].strip().lower(), \
                       output['channel']
    return None, None


if __name__ == "__main__":

    if len(sys.argv) != 2 :
        print("Please use # python peoplebot.py settings.xml")
        sys.exit(1)

    auth_tree = ET.parse(sys.argv[1])
    auth_root = auth_tree.getroot()

    for service in auth_root.findall('service') :
        if service.get("name") == "slack" :
            bot_token = service.find("bot_token").text
                #bot_name = service.find("bot_name").text
            bot_id = service.find("bot_id").text
        elif service.get("name") == "people" :
            client_id = service.find("api_id").text
            client_secret = service.find("api_secret").text

            site = service.find("url_site").text
            redirect_uri = service.find("url_redir").text
            people_url_auth = service.find("url_auth").text
            people_url_token = service.find("url_token").text
            people_refresh_url=people_url_token
            people_url_req=service.find("url_req").text

            people_username = service.find("api_username").text
            people_password = service.find("api_pwd").text

    # instantiate Slack & Twilio clients
    slack_client = SlackClient(bot_token)

    #authentication creation and url
    oauth = OAuth2Session(client_id, redirect_uri=redirect_uri)
    authorization_url, state = oauth.authorization_url(people_url_auth)

    redirect_response = getAuth(authorization_url, people_username, people_password)

    #token fetching
    token = oauth.fetch_token(people_url_token, client_secret=client_secret,code=redirect_response)

    READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
    if slack_client.rtm_connect():
        print("PeopleBot connected and running!")
        while True:
            try :
                command, channel = parse_slack_output(bot_id, slack_client.rtm_read())
                line = parse_slack_output(bot_id, slack_client.rtm_read())
                if command and channel:
                    handle_command(people_url_req, command, channel)
                time.sleep(READ_WEBSOCKET_DELAY)
            except :
                print("Hang")
    else:
        print("Connection failed. Invalid Slack token or bot ID?")
