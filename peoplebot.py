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


def getAuth(authorization_url, people_username, people_password) :
    """
    get authentication fron the authentication URL.
    The people api, at the first authentication, request a user/password over
    a login page. This function below go through the login page and play the give
    user/password.
    """
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
    authorization_response=oauth.get(people_url_req+'/statistics')
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


def retrieve_people(url,ID):
    """
    retrieve person profile from ID in people database
    simple function to retrieve the profile of a person from people database,
    using its ID in the database.
    retrieve_people(ID), where ID is a digits. Example: retrieve_people(1)
    """
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
    my_dict["author_link"]=url+"/p/" + json_decode["slugged_id"]
    my_dict["attachment_type"]="default"
    my_dict["short"]="true"
    #check if 'the' jobs section in people database is populate for the given person.
    #if not, retrive only its 'title'

    # if json_decode["jobs"]:
    #     my_dict["text"]=json_decode["job_title"] + " - " + json_decode["jobs"][0]["description"]
    # else:
    #     my_dict["text"]=json_decode["job_title"]
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

def getHelp(url) :
    textresponse="Commands available (examples) : \n"

    result=[]

    my_dict={}
    my_dict["color"]="#3AA3E3"
    my_dict["attachment_type"]="default"
    my_dict["title"]="@people who is greg"
    my_dict["text"]="I'm lucky"
    result.append(my_dict)

    my_dict={}
    my_dict["color"]="#3AA3E3"
    my_dict["attachment_type"]="default"
    my_dict["title"]="@people search david"
    my_dict["text"]="Look for all david"
    result.append(my_dict)

    my_dict={}
    my_dict["color"]="#3AA3E3"
    my_dict["attachment_type"]="default"
    my_dict["title"]="@people What's the phone of John Snow?"
    my_dict["text"]="Ask a natural question about a person.\n Look for phone number, office, skills and languages."
    result.append(my_dict)

    my_dict={}
    my_dict["color"]="#3AA3E3"
    my_dict["attachment_type"]="default"
    my_dict["title"]="@people give me names of people who worked in angola and have drilling skills."
    my_dict["text"]="Ask a natural question to find people..."
    result.append(my_dict)
    attachments=json.dumps(result)

    return textresponse, attachments

def search_slack_user(user) :
        if (search_string.startswith('@')) :
            print('look for user '+search_string)
            api_call = slack_client.api_call("users.list")


def search_people(url, search_string):
    """
    Retrieve a list of people through a search in people
    The command action is remove from the search string
    returns back a text, an attachment per person, and the id of the first one.
    """
    search_string.replace(' ','+')
    authorization_response=oauth.get(url+'/users/search/{'+ search_string + '}')
    response = authorization_response.content
    response = response.decode("utf-8")
    json_decode=json.loads(response)

    #print(len(json_decode))
    if len(json_decode) == 0 :
        textresponse="Nobody found"
    else :
        textresponse="I found {} people for your search *{}*\n".format(len(json_decode),search_string)
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

    #print(result)
    attachments=json.dumps(result)
    if (len(json_decode) > 0) :
        first_id = json_decode[0]["id"]
    else :
        first_id = None

    return textresponse, attachments, first_id

def get_item(ID, item):
    """
    Retrieve item from a person, when its ID is known.
    returns back a text, an attachment per person.
    """
    authorization_response=oauth.get(people_url_req+'/users/'+str(ID))
    response = authorization_response.content
    #print(response)
    response = response.decode("utf-8")
    json_decode=json.loads(response)

    #create the text of the slackbot response.
    if item == "phone_get":
        phone_string = "unknown" if json_decode["phone"] is None else json_decode["phone"]
        textresponse = "The phone number of %s is *%s*" %(json_decode['first_name'],phone_string)
    elif item == "office_get":
        office_string = "unknown" if json_decode["office_address"] is None else json_decode["office_address"]
        textresponse = "The office of %s is *%s*" %(json_decode['first_name'],office_string)
    elif item == "entity_get":
        entity_string = "unknown" if json_decode["entity"] is None else json_decode["entity"]
        textresponse = "The entity name of %s is *%s*" %(json_decode['first_name'],entity_string)
    elif item == "skills_get":
        #create the string for the answer
        nb_skills = len(json_decode["skills"])
        skills_string = ""
        i = 0
        for skill in json_decode["skills"]:
            i += 1
            if i == nb_skills:
                skills_string += "*" + skill["name"] + "*."
            elif i == nb_skills - 1:
                skills_string += "*" + skill["name"] + "* and "
            else:
                skills_string += "*" + skill["name"] + "*, "
        #build finale sentence:
        string_s = "" if nb_skills == 1 else "s"
        textresponse="%s has *%s* skill%s: %s" %(json_decode['first_name'],str(nb_skills), string_s, skills_string)

    elif item == "languages_get":
        #create the string for the response
        nb_languages = len(json_decode["languages"])
        languages_string = ""
        i = 0
        for language in json_decode["languages"]:
            i += 1
            if i == nb_languages:
                languages_string += "*" + language["name"] + "*."
            elif i == nb_languages - 1:
                languages_string += "*" + language["name"] + "* and "
            else:
                languages_string += "*" + language["name"] + "*, "
        #build finale sentence:
        string_s = "" if nb_languages == 1 else "s"
        textresponse="%s speaks *%s* language%s: %s" %(json_decode['first_name'], str(nb_languages), string_s, languages_string)

    #create attachements in the slackbot response.
    result=[]
    my_dict={}
    my_dict["author_name"]=json_decode['first_name'] + " " + json_decode["last_name"]
    my_dict["author_link"]=site+"/p/" + json_decode["slugged_id"]
    my_dict["attachment_type"]="default"
    my_dict["color"]="#3AA3E3"
    my_dict["thumb_url"]=json_decode['picture_url']
    my_dict["footer"]="people.total"
    my_dict["ts"]=time.time()
    result.append(my_dict)

    attachments=json.dumps(result)

    return textresponse, attachments


def getWit(wit_bearer, text):
    """
        interact with the wit api.
        send the message from the user, and retrieve its interpretation

        if the intent of the user is to look for someone, the function extract
        locations and skills and build a search string with that.

        If the intent of the user is to retrieve a specif info for someone known, the
        function extract its name.

        Then, the function return : name of the person, confidence of wit regarding
        the name extraction, intent of the user's message and wit confidence about it, and the
        created search string.
    """
    headers = {
        'Authorization': 'Bearer ' + wit_bearer,
    }

    params = (
        ('v', '20170505'),
        ('q', text),
    )

    #create request and retrieve info from wit
    resp = requests.get(wit_url, headers=headers, params=params)
    content=resp.content
    content = content.decode("utf-8")
    json_decode=json.loads(content)
    print(json_decode)

    #retrieve intent of the user
    try:
        if 'thanks' in json_decode["entities"] :
            action_confidence = json_decode["entities"]["thanks"][0]["confidence"]
            search_string = ""
            return "", 0, "thanks", action_confidence, ""

        if 'greetings' in json_decode["entities"] :
            action_confidence = json_decode["entities"]["greetings"][0]["confidence"]
            search_string = ""
            return "", 0, "greetings", action_confidence, ""


        action = json_decode["entities"]["intent"][0]["value"]
        action_confidence = json_decode["entities"]["intent"][0]["confidence"]

        # if json_decode["entities"][0]=="greetings":


        #if the user is looking for people, retrieve entities from wit.
        if json_decode["entities"]["intent"][0]["value"]=="search_get":
            search_string = ""
            for entity in json_decode["entities"]:
                if entity != "intent" :
                    for item in json_decode["entities"][entity]:
                        #check if the contact item is a stopwords
                        if entity == 'contact' and item['value'] in contact_stopwords:
                            del item["value"]
                        else:
                            search_string += " " + item["value"]
            person = ""
            person_confidence = ""
        else:
            #retrieve people name from the user request
            person = json_decode["entities"]["contact"][0]["value"]
            person_confidence = json_decode["entities"]["contact"][0]["confidence"]
            search_string = ""
        #print(person, person_confidence, action, action_confidence, search_string)

        return person, person_confidence, action, action_confidence, search_string
    except KeyError as e:
        print("I got an KeyError - reason {}".format(str(e)))
        return "",0,"",0,""
    except IndexError as e:
        print("I got an IndexError - reason {}".format(str(e)))
        return "",0,"",0,""

def handle_command(url, slack_client, command, channel, wit_bearer):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """

    if command.startswith("help"):
        response, attachement = getHelp(url)

    elif command.startswith("who is"):
        arg = command.replace("who is ",'')
        response, attachement, first_id = search_people(url,arg)
        if first_id != None:
            response, attachement = retrieve_people(url,first_id)


    elif command.startswith("search"):
        arg = command.replace("search ",'')
        # if arg.startswith('@') :
        #     api_call = slack_client.api_call("users.list")
        response, attachement, first_id = search_people(url,arg)

    else:
        person, person_confidence, action, action_confidence, search_string = getWit(wit_bearer, command)
        # print(action)
        # print(action_confidence)

        #If the intent is to retrieve the profile of a person:
        if action == "profile_get" and action_confidence > 0.7:
            response, attachement, first_id = search_people(url,person)
            response, attachement = retrieve_people(url,first_id)
        #If the intent is to search someone
        elif action == "search_get" and action_confidence > 0.7:
            response, attachement, first_id = search_people(url,search_string)
            #check of there is a single result. In this case, retrieve the complete profile.
            if len(json.loads(attachement)) == 1:
                response, attachement = retrieve_people(url,first_id)
        elif action == "thanks" and action_confidence > 0.7:
            response = "your're welcome !"
            attachement = ""
        elif action == "greetings" and action_confidence > 0.7:
            response = "hello !"
            attachement = ""
        #If the intent is to retrieve a specific info for a specific person:
        #TODO : A ameliorer, catch trop de choses
        elif action != "profile_get" and action != "search_get" and action_confidence > 0.7:
            response, attachement, first_id = search_people(url,person)
            #check if the person in the request is known in the Database.
            if first_id != None:
                response, attachement = get_item(first_id, action)

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
            if output and 'text' in output and bot_id not in output['user']:
                # return text after if not sent by the bot, whitespace removed
                return output['text'].strip().lower(), \
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

        elif service.get("name") == "wit" :
            wit_bearer = service.find("app_id").text
            wit_url = service.find("url_req").text

        elif service.get("name") == "stopwords" :
            contact_stopwords = service.find("contact").text.split(',')

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
            command, channel = parse_slack_output(bot_id, slack_client.rtm_read())
            if command and channel:
                print("+-[{}] {}".format(command,channel))
                handle_command(people_url_req, slack_client, command, channel, wit_bearer)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")
