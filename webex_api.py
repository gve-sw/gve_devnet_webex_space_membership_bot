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
import requests, json


# Get Webex groups
def get_groups(base_url, headers):
    groups_endpoint = "/groups"
    groups_response = requests.get(base_url+groups_endpoint, headers=headers)
    groups = json.loads(groups_response.text)["groups"]

    return groups

# Get members from Webex group
def get_group_members(base_url, headers, group_id):
    members_endpoint = "/groups/" + group_id + "/members"
    members_response = requests.get(base_url+members_endpoint, headers=headers)
    members = json.loads(members_response.text)["members"]

    return members

# Get Webex rooms
def get_rooms(base_url, headers):
    rooms_endpoint = "/rooms"
    rooms_response = requests.get(base_url+rooms_endpoint, headers=headers)
    rooms = json.loads(rooms_response.text)["items"]

    return rooms

# Get Webex room membership
def get_room_membership(base_url, headers, room_id):
    room_membership_endpoint = "/memberships?roomId=" + room_id
    room_membership_response = requests.get(base_url+room_membership_endpoint,
                                            headers=headers)
    room_membership = json.loads(room_membership_response.text)["items"]

    return room_membership

# Add member to Webex room
def add_room_membership(base_url, headers, room_id, person_id):
    membership_endpoint = "/memberships"
    membership_body = {
        "roomId": room_id,
        "isModerator": False,
        "personId": person_id
    }
    membership_response = requests.post(base_url+membership_endpoint,
                                        headers=headers,
                                        data=json.dumps(membership_body))
    membership_id = json.loads(membership_response.text)["id"]

    return membership_id

# Remove member from Webex room
def remove_room_membership(base_url, headers, membership_id):
    remove_membership_endpoint = "/memberships/" + membership_id
    remove_response = requests.delete(base_url+remove_membership_endpoint,
                                      headers=headers)

    remove_status = {
        "status": remove_response.status_code,
        "removed_membership": membership_id
    }

    return remove_status
