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

from flask import Flask, request, render_template
from pprint import pprint
from urllib.error import HTTPError
from dotenv import load_dotenv
import app_direct
import wholesale

load_dotenv()
app = Flask(__name__)


#Routes 
#Webhook receiver route
#https://help.appdirect.com/products/Content/DevCenter/Dev-Edit-integration.htm 
#https://help.appdirect.com/products/Content/DevCenter/eventURL-parameter.htm
#https://help.appdirect.com/products/Content/Dev-DistributionGuide/en-ue-attributes.html
@app.route('/subscription_receiver', methods=['GET' ,'POST'])
@app.route('/subscription_receiver?eventUrl=<eventUrl>&eventType=<eventType>', methods=['GET' ,'POST'])
def respond():

    try:
        print('Webhook event identified')

        if(app_direct.outbound_basic_auth_creds_matching(request.headers)): 

            event_url = request.args.get("eventUrl")
            event_type = request.args.get("eventType")

            #request event details based on the eventURL
            event_details, event_status = app_direct.inbound_event_details_request(event_url)
            pprint(event_details)

            if event_status == 200:  

                if(event_type == 'create'):
                    
                    print('Create subscription event in AppDirect triggered...')

                    app_direct_company_uuid = event_details['payload']['company']['uuid']

                    associated_wholesale_customer = wholesale.wholesale_customer_exists(app_direct_company_uuid)
                    
                    if not associated_wholesale_customer:

                        print('Wholesale Customer for AppDirect Company not present. Creating customer...')                   
                        
                        success, message, errorCode, accountIdentifier = wholesale.create_wholesale_meetings_customer(event_details, app_direct_company_uuid)

                        return app_direct.respond_to_appdirect(success, message, errorCode, accountIdentifier)
                    
                    else:
                        print('Creating subscriber...')
                        
                        success, message, errorCode, accountIdentifier = wholesale.create_wholesale_meetings_subscriber_if_not_existing(event_details, associated_wholesale_customer, app_direct_company_uuid)
                                                
                        return app_direct.respond_to_appdirect(success, message, errorCode, accountIdentifier)
                
                elif(event_type == 'update'):

                    print('Update subscription event in AppDirect triggered ...')
                    
                    app_direct_company_uuid = event_details['payload']['account']['accountIdentifier']

                    associated_wholesale_customer = wholesale.wholesale_customer_exists(app_direct_company_uuid)

                    success, message, errorCode, accountIdentifier = wholesale.update_webex_subscriber_if_existing(event_details, associated_wholesale_customer, app_direct_company_uuid)
                    
                    return app_direct.respond_to_appdirect(success, message, errorCode, accountIdentifier) 

                elif(event_type == 'cancel'):
                    
                    print('Cancel subscription event in AppDirectin triggered ...')
                    
                    app_direct_company_uuid = event_details['payload']['account']['accountIdentifier']

                    associated_wholesale_customer = wholesale.wholesale_customer_exists(app_direct_company_uuid)

                    success, message, errorCode, accountIdentifier = wholesale.remove_wholesale_meetings_subscriber_if_existing(event_details, app_direct_company_uuid)
                    
                    if success:
                        success, message, errorCode, accountIdentifier = wholesale.remove_Webex_person(event_details, associated_wholesale_customer)
                    
                    return app_direct.respond_to_appdirect(success, message, errorCode, accountIdentifier)
                                        
                else:
                    return app_direct.respond_to_appdirect(False, 'No associated action implemented in the backend.', 'CONFIGURATION_ERROR', None)  
            else:
                print("Waiting...")
                return app_direct.respond_to_appdirect(True, 'This takes a bit longer than expected. Please wait ...', 'PENDING', None)

        else:
            return app_direct.respond_to_appdirect(False, 'The AppDirect outbound credentials are wrong', 'UNAUTHORIZED', None)

    except HTTPError as err:
        print(err)
        status_code = err.response.status_code
        return app_direct.respond_to_appdirect(False, f'An HTTP error occured. Status code: {status_code}', 'UNKNOWN_ERROR', None)
    except Exception as err: 
        print(err)
        return app_direct.respond_to_appdirect(False, 'An unknown error occured', 'UNKNOWN ERROR', None)


@app.route('/auth', methods=['GET' ,'POST'])
def auth():

    response = app_direct.request_inbound_access_token_via_basic_auth()
    return render_template('auth.html', response = response)


if __name__ == "__main__":
    app.run(host='localhost', port=5002, debug=True, use_reloader=False)

