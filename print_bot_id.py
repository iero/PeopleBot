import os, sys
from slackclient import SlackClient

import xml.etree.ElementTree as ET

BOT_NAME = 'peopledev'

if __name__ == "__main__":

    if len(sys.argv) != 2 :
        print("Please use # python peoplebot.py settings.xml")
        sys.exit(1)

    auth_tree = ET.parse(sys.argv[1])
    auth_root = auth_tree.getroot()

    for service in auth_root.findall('service') :
        if service.get("name") == "slack" :
            bot_token = service.find("bot_token").text

    print("using token : "+bot_token)
    slack_client = SlackClient(bot_token)

    api_call = slack_client.api_call("users.list")
    if api_call.get('ok'):
        # retrieve all users so we can find our bot
        users = api_call.get('members')
        for user in users:
            profil = user.get('profile')
            print(profil['email'])
            if 'name' in user and user.get('name') == BOT_NAME:
                print("Bot ID for '" + user['name'] + "' is " + user.get('id'))
    else:
        print("could not find bot user with the name " + BOT_NAME)
