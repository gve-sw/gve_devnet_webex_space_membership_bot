# GVE DevNet Webex Space Membership App
This repository contains the code for a Flask app that will add and delete members to a Webex space according to their membership to Webex groups. The Flask app will run the code to add/delete members every 12 hours that the webpage is open. The Flask app then displays the members added and deleted from the spaces. 

![/IMAGES/webex_space_membership_workflow.png](/IMAGES/webex_space_membership_workflow.png)

## Contacts
* Danielle Stacy

## Solution Components
* Python 3.10
* Flask
* Webex APIs

## Prerequisites
- **OAuth Integrations**: Integrations are how you request permission to invoke the Webex REST API on behalf of another Webex Teams user. To do this in a secure way, the API supports the OAuth2 standard which allows third-party integrations to get a temporary access token for authenticating API calls instead of asking users for their password. To register an integration with Webex Teams:
1. Log in to `developer.webex.com`.
2. Click on your avatar at the top of the page and then select `My Webex Apps`.
3. Click `Create a New App`.
4. Click `Create an Integration` to start the wizard.
5. Follow the instructions of the wizard and provide your integration's name, description, and logo. Additionally, you will need to provide a redirect URI for the user to be redirected to when completing an OAuth grant flow. When running this app on your local machine (which these instructions assume), the redirect URI should be `http://localhost:5000/callback`.
6. After successful registration, you'll be taken to a different screen containing your integration's newly created Client ID and Client Secret.
7. Copy the secret and store it safely. Please note that the Client Secret will only be shown once for security purposes.
8. Note that access token may not include all the scopes necessary for this prototype by default. To include the necessary scopes, select `My Webex Apps` under your avatar once again. Then click on the name of the integration you just created. Scroll down to the `Scopes` section. From there, select all the scopes needed for this integration. The scopes needed for this integration are spark:memberships_read, spark:memberships_write, spark:rooms_read, spark:rooms_write, spark:team_memberships_read, spark:team_memberships_write, and identity:groups_read.

> To read more about Webex Integrations & Authorization and to find information about the different scopes, you can find information [here](https://developer.webex.com/docs/integrations)

## Installation/Configuration
1. Clone this repository with `git clone https://github.com/gve-sw/gve_devnet_webex_space_membership_bot.git`
2. Set up a Python virtual environment. Make sure Python 3 is installed in your environment, and if not, you may download Python [here](https://www.python.org/downloads/). Once Python 3 is installed in your environment, you can activate the virtual environment with the instructions found [here](https://docs.python.org/3/tutorial/venv.html).
3. Install the requirements with `pip3 install -r requirements.txt`.
4. Add the Client ID and Client Secret that you collected when creating the Webex Inegration in the Prerequisites section to the envirnoment variables in the `.env` file.
```
CLIENT_ID = "enter Client ID obtained from Webex Integration here"
CLIENT_SECRET = "enter Client secret obtained from Webex Integration here"
```
5. In the `group_room.csv` file, add the groups and rooms that you want the script to check memberships of. Each row represents the group/room pair that you would like to monitor. The first column should be the name of the group that you would like to add to a Webex space, and the second column should be the name of the space. Be sure to not add a space after the comma separating the group and space names.
```
group,room
first_group,first_room
second_group,second_room
third_group,third_room
```

## Usage
To start the web app that is written in the file `app.py`, use the command:
```
$ flask run
```
Then access the app in your browser of choice at the address `http:localhost:5000`. From here, you will be asked to login to the web app with your Webex account that you created the Webex integration with.

![/IMAGES/login_prompt.png](/IMAGES/login_prompt.png)

![/IMAGES/webex_login.png](/IMAGES/webex_login.png)

Once you have gone through the login process, you will be redirected to the page where the status of the Webex space memberships is displayed. There are two sections: Added Members and Removed Members. Under the Added Members is a list of the people who have been added to which space - it will display the people's names and the names of the rooms they were added to. Similarly, under the Removed Members is a list of the people who have been removed from which space - it will display the people's names and the names of the rooms they were removed from. Under these lists is the date and time the room memberships were updated. As the code is written, if the web page is left open, the room memberships will update every 12 hours according to the groups they're associated with in `group_room.csv`.

![/IMAGES/membership_status.png](/IMAGES/membership_status.png)

The console will also print out similar information about which users were added and removed from which spaces. In addition to the information that is displayed on the web page, the console will print out the membership id that is associated with the members and the room they were added or removed from.

![/IMAGES/terminal_output.png](/IMAGES/terminal_output.png)

![/IMAGES/0image.png](/IMAGES/0image.png)

### LICENSE

Provided under Cisco Sample Code License, for details see [LICENSE](LICENSE.md)

### CODE_OF_CONDUCT

Our code of conduct is available [here](CODE_OF_CONDUCT.md)

### CONTRIBUTING

See our contributing guidelines [here](CONTRIBUTING.md)

#### DISCLAIMER:
<b>Please note:</b> This script is meant for demo purposes only. All tools/ scripts in this repo are released for use "AS IS" without any warranties of any kind, including, but not limited to their installation, use, or performance. Any use of these scripts and tools is at your own risk. There is no guarantee that they have been through thorough testing in a comparable environment and we are not responsible for any damage or data loss incurred with their use.
You are responsible for reviewing and testing any scripts you run thoroughly before use in any non-testing environment.
