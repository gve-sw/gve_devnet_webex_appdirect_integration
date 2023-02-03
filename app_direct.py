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
import requests
import json
import os
from dotenv import load_dotenv
from pprint import pprint
import base64


load_dotenv()
#Appdirect
base_url_market_place = os.environ['BASE_URL_MARKETPLACE']
OAUTH_CLIENT_ID = os.environ['OAUTH_CLIENT_ID']
OAUTH_CLIENT_SECRET = os.environ['OAUTH_CLIENT_SECRET']
BASIC_USERNAME = os.environ['BASIC_USERNAME']
BASIC_PASSWORD = os.environ['BASIC_PASSWORD']


'''
Helper: Converts basic username and password to base64 auth string
'''
def base_cred_to_base64(BASIC_USERNAME, BASIC_PASSWORD):
    usrPass = BASIC_USERNAME+":"+BASIC_PASSWORD
    calculated_base64_auth_value = base64.b64encode(usrPass.encode()).decode()
    return calculated_base64_auth_value


'''
Validates Webhook credentials based on basic username and password
See also: https://help.appdirect.com/products/Default.htm#AppDistribution/Validate-Outbound-Event-Notifications.htm
''' 
def outbound_basic_auth_creds_matching(response_header):
    
    global basic64_outbound_creds, BASIC_USERNAME, BASIC_PASSWORD

    print('Validate received basic outbound creds')

    response_base64_auth_value = response_header.get('Authorization')
    calculated_base64_auth_value = base_cred_to_base64(BASIC_USERNAME, BASIC_PASSWORD)

    return (response_base64_auth_value == f'Basic {calculated_base64_auth_value}')



'''
Gets token based on basic auth with BASIC_USERNAME and BASIC_PASSWORD and then uses token for more inbound requests
See also: https://help.appdirect.com/products/Default.htm#AppDistribution/Authorize-Inbound-API-requests.htm
'''
def request_inbound_access_token_via_basic_auth():
    global base_url_market_place, OAUTH_CLIENT_ID, OAUTH_CLIENT_SECRET
    
    token_url = base_url_market_place +"/oauth2/token"

    headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
    }
    
    data = {
        'grant_type': 'client_credentials',
        'scope': 'ROLE_APPLICATION', 
    }

    response = requests.post(token_url, headers=headers, data=data, auth=(OAUTH_CLIENT_ID, OAUTH_CLIENT_SECRET))

    return json.loads(response.text)['access_token']



'''
Executes an inbound call to request event details based on the event_url provided via the webhook event
See also: https://help.appdirect.com/products/Content/DevCenter/eventURL-parameter.htm
'''
def inbound_event_details_request(event_url):

    token = request_inbound_access_token_via_basic_auth()

    print(f'Request event details based on event_url: {event_url}')

    headers = {
        'Authorization': f'Bearer {token}',
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    event_details = requests.get(url=event_url, headers=headers)
    pprint(event_details) 

    return event_details.json(), event_details.status_code



'''
Creates response for AppDirect. This will define the feedback (green or red prompt) the user will see in the UI.
See also:
https://help.appdirect.com/products/Content/Dev-DistributionGuide/en-notif-urls-and-responses.html
https://help.appdirect.com/products/Content/Dev-DistributionGuide/en-error-codes.html
'''
def respond_to_appdirect(success, message, errorCode, accountIdentifier):

    webhook_callback = {}
    webhook_callback['success'] = success
    webhook_callback['message'] = message
    webhook_callback['errorCode'] = errorCode

    if accountIdentifier != None:
        webhook_callback['accountIdentifier'] = accountIdentifier
    
    print(f'Responds for AppDirect: {webhook_callback}')

    return webhook_callback

