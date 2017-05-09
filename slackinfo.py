import os, sys
from slackclient import SlackClient

import xml.etree.ElementTree as ET

if __name__ == "__main__":

    if len(sys.argv) != 2 :
        print("Please use # python peoplebot.py settings.xml")
        sys.exit(1)

    auth_tree = ET.parse(sys.argv[1])
    auth_root = auth_tree.getroot()

    for service in auth_root.findall('service') :
        if service.get("name") == "slack" :
            bot_token = service.find("bot_token").text

    print("+-[Connected] using {} token".format(bot_token))
    slack_client = SlackClient(bot_token)

    api_call = slack_client.api_call("users.list")
    if api_call.get('ok'):
        # retrieve all users so we can find our bot
        users = api_call.get('members')
        print("+-[{} users]".format(len(users)))
        for user in users:
            profil = user.get('profile')
            if 'email' in profil :
                print("+-[{}] {}".format(user.get('id'),profil['email']))
            else :
                print("+-[{}] Bot : {}".format(user.get('id'),user['name']))

    api_call = slack_client.api_call("channels.list")
    if api_call.get('ok'):
        channels = api_call.get('channels')
        print("+-[{} channels]".format(len(channels)))
        for chan in channels:
            print("+-[{}] {} with {} members".format(chan.get('id'),chan.get('name'),chan.get('num_members')))

    api_call = slack_client.api_call("im.list")
    if api_call.get('ok'):
        ims = api_call.get('ims')
        print("+-[{} IM]".format(len(ims)))
        for im in ims:
            print("+-[{}] with {}".format(im.get('id'),im.get('user')))
