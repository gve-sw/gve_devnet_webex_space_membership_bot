#!/usr/bin/env python3
""" Copyright (c) 2023 Cisco and/or its affiliates.
This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at
           https://developer.cisco.com/docs/licenses
All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.
"""

# Import Section
from flask import Flask, render_template, request, session, redirect, url_for, jsonify, make_response
from requests_oauthlib import OAuth2Session
import json
import csv
import os
import requests
import datetime
import time
from webexteamssdk import WebexTeamsAPI
from dotenv import load_dotenv
from collections import defaultdict
from webex_api import get_groups, get_group_members, get_rooms, get_room_membership, add_room_membership, remove_room_membership

# load all environment variables
load_dotenv()

AUTHORIZATION_BASE_URL = 'https://api.ciscospark.com/v1/authorize'
TOKEN_URL = 'https://api.ciscospark.com/v1/access_token'
SCOPE = "spark:memberships_read spark:memberships_write spark:rooms_read spark:rooms_write spark:team_memberships_read spark:team_memberships_write identity:groups_read"

#initialize variabes for URLs
#REDIRECT_URL must match what is in the integration, but we will construct it below in __main__
# so no need to hard code it here
PUBLIC_URL='http://localhost:5000'
#REDIRECT_URI will be set in admin() if it needs to trigger the oAuth flow
REDIRECT_URI=""


os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

app = Flask(__name__)

app.secret_key = '123456789012345678901234'

#Methods
#Returns location and time of accessing device
def getSystemTime():
    #request user ip
    userIPRequest = requests.get('https://get.geojs.io/v1/ip.json')
    userIP = userIPRequest.json()['ip']

    #request geo information based on ip
    geoRequestURL = 'https://get.geojs.io/v1/ip/geo/' + userIP + '.json'
    geoRequest = requests.get(geoRequestURL)
    geoData = geoRequest.json()

    #create info string
    timezone = geoData['timezone']
    current_time=datetime.datetime.now().strftime("%d %b %Y, %I:%M %p")
    time = "{} {}".format(current_time, timezone)

    return time

# Returns a dictionary that maps the group name to the room name whose members should match
def getRoomsAndGroups(filename):
    group_to_room = {}

    # open the CSV file that has the group and room names structured together
    with open(filename) as csv_file:
        csv_reader = csv.DictReader(csv_file)

        # the file has two columns - the first is the group name and the second is the room name
        for line in csv_reader:
            # for each line in in the CSV file, get the group and room. Then add the group name as a key in the dictionary with the value as the room name
            group = line["group"]
            room = line["room"]

            group_to_room[group] = room

    return group_to_room

# Edit the memberships of Webex Rooms according to the memberships of a Webex Group
def editMemberships(webex_key):
    # Set variables need for API requests
    base_url = "https://webexapis.com/v1"
    headers = {
        "Authorization": "Bearer " + webex_key,
        "Content-Type": "application/json; charset=utf-8"
    }

    group_to_room = getRoomsAndGroups("group_room.csv")

    # Get groups and rooms in the Webex organization
    groups = get_groups(base_url, headers)
    rooms = get_rooms(base_url, headers)

    # These variables will be used to keep track of room and person information from the JSON response
    room_memberships = defaultdict(list)
    person_to_member_id = defaultdict(dict)
    room_name_to_id = {}
    person_id_to_name = {}

    affected_groups = set()
    affected_rooms = set()
    for group, room in group_to_room.items():
        affected_groups.add(group)
        affected_rooms.add(room)

    # Iterate through rooms
    for room in rooms:
        room_id = room["id"]
        room_name = room["title"]

        if room_name in affected_rooms:
            # Map the room name to the room id
            room_name_to_id[room_name] = room_id

            # Get the room members for each room
            room_members = get_room_membership(base_url, headers, room_id)
            # Iterate through each member in the room and record the person id and membership id of each person
            for member in room_members:
                person_id = member["personId"]
                room_memberships[room_id].append(member["personId"])
                person_to_member_id[member["personId"]][room_id] = member["id"]
                person_id_to_name[person_id] = member["personDisplayName"]

    # These variables will be used to keep track of group information from the JSON response
    group_memberships = defaultdict(list)
    group_name_to_id = {}
    group_member_id_to_name = {}
    # Iterate through groups
    for group in groups:
        group_id = group["id"]
        group_name = group["displayName"]

        if group_name in affected_groups:
            # Map the group names to the group ids
            group_name_to_id[group_name] = group_id

            # Get the group members for each group
            group_members = get_group_members(base_url, headers, group_id)
            # Iterate through each member in the group and record the person id of each person
            for member in group_members:
                group_memberships[group_id].append(member["id"])
                group_member_id_to_name[member["id"]] = member["displayName"]

    # Create a struct that stores the members added to the room and the members removed
    member_struct = {
        "added": [],
        "removed": []
    }

    for group in affected_groups:
        # Get the group id of the group that the bot is monitoring
        affected_group_id = group_name_to_id[group]
        # Get room associated with the group
        affected_room = group_to_room[group]
        # Get room id of the room the bot is modifying
        affected_room_id = room_name_to_id[affected_room]

        # Get the group members of the group the bot is monitoring
        affected_group_members = group_memberships[affected_group_id]
        # Get the room members of the room the bot is modifying
        affected_room_members = room_memberships[affected_room_id]

        # Check if each member in group is in the room
        for member in affected_group_members:
            if member not in affected_room_members:
                # Add the group member to the room if they are not a part of it
                membership_id = add_room_membership(base_url, headers, affected_room_id, member) # a successful add operation will return a membership id
                member_name = group_member_id_to_name[member] # to print a meaningful status statement, we need the name of the member who we added to the room
                # to print a status message to the web page, pass a structure with the name, room, and membership id of the added member
                new_member = {
                    "name": member_name,
                    "room": affected_room,
                    "membership": membership_id
                }
                member_struct["added"].append(new_member)

                print("Added " + member_name + " to " + affected_room + " with membership id " + membership_id)

        # Check if each member in room is in the group
        for member in affected_room_members:
            if member not in affected_group_members:
                # Remove the room member from the room if they are not a part of the group
                membership_id = person_to_member_id[member][affected_room_id] # we need the person id to remove the person from the room
                delete_status = remove_room_membership(base_url, headers,
                                                       membership_id)
                member_name = person_id_to_name[member] # to print a meaningful status statement, we need the name of the member who we tried to delete
                # if the delete operation was successful, it will have a status of 204
                if delete_status["status"] == 204:
                    # to print the web page, pass a structure with the name, room, and membership id of the removed member
                    removed_member = {
                        "name": member_name,
                        "room": affected_room,
                        "membership": membership_id
                    }

                    member_struct["removed"].append(removed_member)
                    print("Removed " + member_name + " from " + affected_room + " with membership id " + membership_id)
                else:
                    print("Error: {}".format(delete_status["status"]))
                    print("There was an error trying to remove " + member_name + " from " + affected_room)

    return member_struct

##Routes
@app.route('/')
def login():
    return render_template('login.html')

@app.route("/callback", methods=["GET"])
def callback():
    """
    Retrieving an access token.
    The user has been redirected back from the provider to your registered
    callback URL. With this redirection comes an authorization code included
    in the redirect URL. We will use that to obtain an access token.
    """
    global REDIRECT_URI

    print(session)
    print("Came back to the redirect URI, trying to fetch token....")
    print("redirect URI should still be: ",REDIRECT_URI)
    print("Calling OAuth2SEssion with CLIENT_ID ",os.getenv('CLIENT_ID')," state ",session['oauth_state']," and REDIRECT_URI as above...")
    auth_code = OAuth2Session(os.getenv('CLIENT_ID'), state=session['oauth_state'], redirect_uri=REDIRECT_URI)
    print("Obtained auth_code: ",auth_code)
    print("fetching token with TOKEN_URL ",TOKEN_URL," and client secret ",os.getenv('CLIENT_SECRET')," and auth response ",request.url)
    token = auth_code.fetch_token(token_url=TOKEN_URL, client_secret=os.getenv('CLIENT_SECRET'),
                                  authorization_response=request.url)

    print("Token: ",token)
    print("should have grabbed the token by now!")
    session['oauth_token'] = token
    with open('tokens.json', 'w') as json_file:
        json.dump(token, json_file)
    return redirect(url_for('.spacememberships'))


#manual refresh of the token
@app.route('/refresh', methods=['GET'])
def webex_teams_webhook_refresh():

    r_api=None

    teams_token = session['oauth_token']

    # use the refresh token to
    # generate and store a new one
    access_token_expires_at=teams_token['expires_at']

    print("Manual refresh invoked!")
    print("Current time: ",time.time()," Token expires at: ",access_token_expires_at)
    refresh_token=teams_token['refresh_token']
    #make the calls to get new token
    extra = {
        'client_id': os.getenv('CLIENT_ID'),
        'client_secret': os.getenv('CLIENT_SECRET'),
        'refresh_token': refresh_token,
    }
    auth_code = OAuth2Session(os.getenv('CLIENT_ID'), token=teams_token)
    new_teams_token=auth_code.refresh_token(TOKEN_URL, **extra)
    print("Obtained new_teams_token: ", new_teams_token)
    #store new token

    teams_token=new_teams_token
    session['oauth_token'] = teams_token
    #store away the new token
    with open('tokens.json', 'w') as json_file:
        json.dump(teams_token, json_file)

    #test that we have a valid access token
    r_api = WebexTeamsAPI(access_token=teams_token['access_token'])

    return ("""<!DOCTYPE html>
                   <html lang="en">
                       <head>
                           <meta charset="UTF-8">
                           <title>Webex Teams Bot served via Flask</title>
                       </head>
                   <body>
                   <p>
                   <strong>The token has been refreshed!!</strong>
                   </p>
                   </body>
                   </html>
                """)



@app.route('/spacememberships')
def spacememberships():

    global REDIRECT_URI
    global PUBLIC_URL
    global ACCESS_TOKEN

    if os.path.exists('tokens.json'):
        with open('tokens.json') as f:
            tokens = json.load(f)
    else:
        tokens = None

    if tokens == None or time.time()>(tokens['expires_at']+(tokens['refresh_token_expires_in']-tokens['expires_in'])):
        # We could not read the token from file or it is so old that even the refresh token is invalid, so we have to
        # trigger a full oAuth flow with user intervention
        REDIRECT_URI = PUBLIC_URL + '/callback'  # Copy your active  URI + /callback
        print("Using PUBLIC_URL: ",PUBLIC_URL)
        print("Using redirect URI: ",REDIRECT_URI)
        teams = OAuth2Session(os.getenv('CLIENT_ID'), scope=SCOPE, redirect_uri=REDIRECT_URI)
        authorization_url, state = teams.authorization_url(AUTHORIZATION_BASE_URL)

        # State is used to prevent CSRF, keep this for later.
        print("Storing state: ",state)
        session['oauth_state'] = state
        print("root route is re-directing to ",authorization_url," and had sent redirect uri: ",REDIRECT_URI)
        return redirect(authorization_url)
    else:
        # We read a token from file that is at least younger than the expiration of the refresh token, so let's
        # check and see if it is still current or needs refreshing without user intervention
        print("Existing token on file, checking if expired....")
        access_token_expires_at = tokens['expires_at']
        if time.time() > access_token_expires_at:
            print("expired!")
            refresh_token = tokens['refresh_token']
            # make the calls to get new token
            extra = {
                'client_id': os.getenv('CLIENT_ID'),
                'client_secret': os.getenv('CLIENT_SECRET'),
                'refresh_token': refresh_token,
            }
            auth_code = OAuth2Session(os.getenv('CLIENT_ID'), token=tokens)
            new_teams_token = auth_code.refresh_token(TOKEN_URL, **extra)
            print("Obtained new_teams_token: ", new_teams_token)
            # assign new token
            tokens = new_teams_token
            # store away the new token
            with open('tokens.json', 'w') as json_file:
                json.dump(tokens, json_file)


        session['oauth_token'] = tokens
        print("Using stored or refreshed token....")
        ACCESS_TOKEN=tokens['access_token']

        member_struct = editMemberships(ACCESS_TOKEN) # this function returns a structure that displays all the members added and removed from the rooms according to their Webex group membership
        current_time = getSystemTime() # get the current time to display the update time of the rooms on the page

        return render_template("spacememberships.html", member_struct=member_struct, update_time=current_time)

#Main Function
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
