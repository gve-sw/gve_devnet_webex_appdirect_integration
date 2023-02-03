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


import os
from dotenv import load_dotenv
import json
import requests
import time
import random

load_dotenv()

#Global Variables
WEBEX_TOKEN = os.environ['WEBEX_TOKEN']
BASE_URL = "https://webexapis.com/v1"
HEADERS = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'Authorization': 'Bearer ' + WEBEX_TOKEN
}


## CUSTOMER ORGANIZATION CREATION
'''
Checks if a Wholesale customer associated to the AppDirect Company is present and return boolean or customer.
'''
def wholesale_customer_exists(app_direct_company_uuid):

    url = BASE_URL + '/wholesale/customers'

    response = requests.get(url, headers=HEADERS)
    
    if(response.status_code == 200):
        response = response.json()
        for customer in response['items']:

                external_id = customer['externalId']

                if external_id == app_direct_company_uuid:
                    
                    customer_id = customer['id']
                    customer_url = f"{BASE_URL}/wholesale/customers/{customer_id}"
                    
                    customer = wait_for_customer_successfully_provisioned(customer_url)
                    
                    print("Organization/Customer in Wholesale present and ready provisioned")

                    return customer 
        
        print("Organization/Customer in Wholesale not present.")
        return False
    else: 
        print(f'Status code: {response.status_code}, Response: {response.text}')


'''
Creates a new wholesale meetings customer/organization and returns its
'''
def create_wholesale_meetings_customer(event_details, app_direct_company_uuid):
    
    customer_name = event_details['payload']['company']['name']
    customer_email = event_details['payload']['company']['email'] 
    language = event_details['creator']['locale'].replace("-", "_") 
    phone_number = event_details['payload']['company']['phoneNumber']  

    ADDRESS=os.environ['ADDRESS']
    ZIP_CODE=os.environ['ZIP_CODE']
    CITY=os.environ['CITY']
    COUNTRY=os.environ['COUNTRY']
    STATE=os.environ['STATE']
    TIMEZONE=os.environ['TIMEZONE']
    CUSTOMER_PACKAGES=json.loads(os.environ['CUSTOMER_PACKAGES'])
    PROVISIONING_ID = os.environ['PROVISIONING_ID']

    data = {
        "provisioningId": PROVISIONING_ID,
        "packages": CUSTOMER_PACKAGES,
        "externalId": app_direct_company_uuid,
        "address": {
            "addressLine1": ADDRESS,
            "addressLine2": "",
            "city": CITY,
            "stateOrProvince": STATE,
            "zipOrPostalCode": ZIP_CODE,
            "country": COUNTRY
        },
        "customerInfo": {
            "name": customer_name + " AppDirect Test", 
            "primaryEmail": customer_email, 
            "language": language 
        },
        "provisioningParameters": {
            "calling": {
                "location": {
                    "name": customer_name + " Location",
                    "address": {
                        "addressLine1": ADDRESS,
                        "addressLine2": "",
                        "city": CITY,
                        "stateOrProvince": STATE,
                        "zipOrPostalCode": ZIP_CODE,
                        "country": COUNTRY
                    },
                    "timezone": TIMEZONE,
                    "language": language,
                    "emergencyLocationIdentifier": "",
                    "numbers": [phone_number],
                    "mainNumber": phone_number
                }
            },
            "meetings": {
                "timezone": TIMEZONE 
            }
        }
    }

    url = BASE_URL + '/wholesale/customers'

    response = requests.post(url, headers=HEADERS, data=json.dumps(data))

    if response.status_code == 202:
        print("Setup process for new customer started. Provisioning can take some time.")
        return False, 'Your company is using our service for the first time thereby further preparations are required. We will setup everything for you, but this takes around 5 minutes. Please try to subscribe again in 5 minutes.', "CONFIGURATION_ERROR" , None 
    
    else: 
        print(f"Wholesale Customer wasn't created - Status code: {response.status_code}, Response: {response.text}")
        return False, 'Error during customer creation. Please contact your administrator.', 'UNKNOWN_ERROR', None 


'''
Checks if the customer is successfully provisioned and returns customer.
'''
def wait_for_customer_successfully_provisioned(customer_url):

    provisioned = False
    
    while not provisioned:
        print("Waiting for provisioning to finish...")
        
        customer_info = requests.get(customer_url, headers=HEADERS).json()

        if customer_info['status'] == "provisioned":
            return customer_info
    
        time.sleep(15)


## SUBSCRIBING
'''
Executes pre-provisioning check and returns boolean
'''
def wholesale_pre_provision_check_successful(wholesale_customer_id, subscriber_email):
    
    print('Precheck potential subscriber')

    data = {
            "customerId": wholesale_customer_id,
            "email": subscriber_email
        }
    
    url = BASE_URL + '/wholesale/subscribers/validate'

    response = requests.post(url, data=json.dumps(data), headers=HEADERS).json()
    
    if response['message'] == 'success':
        print(f"Precheck potential for subscriber {subscriber_email} successful")
        return True
    else:
        print(f"Precheck potential for subscriber {subscriber_email} not successful: {response}")
        return False


'''
Creates new subscriber if it doesn't already exist
'''
def create_wholesale_meetings_subscriber_if_not_existing(event_details, wholesale_customer, app_direct_company_uuid):

    wholesale_customer_id = wholesale_customer['id']
    subscriber_email = event_details['creator']['email']

    pre_check_successful = wholesale_pre_provision_check_successful(wholesale_customer_id, subscriber_email)

    if pre_check_successful:
        
        subscriber_first_name = event_details['creator']['address']['firstName']
        subscriber_last_name = event_details['creator']['address']['lastName']
        subscriber_package_choice = event_details['payload']['order']['editionCode']
        location_id = get_wholesale_location_id_of_wholesale_customer(wholesale_customer)
        random_extention = provide_free_extention(location_id, wholesale_customer)
        #Potential alternative AppDirect fields for phone:
        #phone_number = event_details['payload']['company']['phoneNumber']
        #subscriberPrimaryPhoneNumber = event_details['creator']['address']['phone']
        #subscriberPhoneExtension = event_details['creator']['address']['phoneExtension']
        #wholesale_customer_org_id = wholesale_customer['orgId']
        #adding_phone_number_to_Webex(wholesale_customer_org_id, location_id, phone_number)

        url = BASE_URL + '/wholesale/subscribers'
    
        data = {
            "customerId": wholesale_customer_id,
            "email": subscriber_email,
            "package": subscriber_package_choice,
            "provisioningParameters": {
                "firstName": subscriber_first_name,
                "lastName": subscriber_last_name,
                #"primaryPhoneNumber": phone_number, 
                "extension": str(random_extention),
                "locationId": location_id
                }
            }
        #For using other a phone number, first add the number to the location before using it via:https://developer.webex.com/docs/api/v1/webex-calling-organization-settings/add-phone-numbers-to-a-location 
        #or use available number (not yet used): https://developer.webex.com/docs/api/v1/webex-calling-organization-settings/get-phone-numbers-for-an-organization-with-given-criterias

        response = requests.post(url, headers=HEADERS, data=json.dumps(data)) 
                 
        if response.status_code == 200:
            print("Webex subscription has been created.")
            return True, 'Webex subscription has been created.', None , app_direct_company_uuid 
        
        else: 
            print(f"Wholesale Subscribers was not created - Status code: {response.status_code}, Response: {response.json()}")
            return False, 'Error during subscriber creation.', 'UNKNOWN_ERROR', None 

    else:

        print(f"Wholesale Subscribers was not created - Pre-Check failed.")
        return False, 'Wholesale PreCheck Failed', 'UNKNOWN_ERROR', None


'''
Adds a phone number to a Webex organization and location
'''
def adding_phone_number_to_Webex(wholesale_customer_org_id, location_id, number_to_add):
    
    print("Phone number does not yet exist in Webex. Adding phone number to location ...")
    url = BASE_URL + '/telephony/config/locations/'+location_id+'/numbers?orgId='+wholesale_customer_org_id

    data = {
            "phoneNumbers": [number_to_add],
            "state": "ACTIVE"
        }
        
    response = requests.post(url, headers=HEADERS, data=json.dumps(data)) 
    print(f'Status code {response.status_code}), Response: {response.text}')
    
    return response


'''
Provides valid random extention
see also: https://developer.webex.com/docs/api/v1/webex-calling-organization-settings/read-the-list-of-call-park-extensions
'''
def provide_free_extention(locationId, wholesale_customer):

    wholesale_orga_id = wholesale_customer['orgId']
    status_success = False

    url =  f"{BASE_URL}/telephony/config/locations/{locationId}/actions/validateExtensions/invoke?orgId={wholesale_orga_id}"
    
    while not status_success:
        random_extention = random.randint(1000,9999)
        data = {
                "extensions": [random_extention]
            }

        response = requests.post(url, headers=HEADERS, data=json.dumps(data)).json() 
        status_success = response['status'] == "OK"

    print(f"Assign random extention: {random_extention}")  
    return random_extention


## UPDATE SUBSCRIBER
'''
Updates a subscription
'''
def update_webex_subscriber_if_existing(event_details, wholesale_customer, app_direct_company_uuid):
    
    subscriber_email = event_details['creator']['email']
    webex_subscriber = wholesale_subscriber_exists(app_direct_company_uuid, subscriber_email)

    if webex_subscriber:
        
        print('Associated Webex user found. Updating ...')
        
        subscriber_id = webex_subscriber['id']
        subscriberPackageChoice = event_details['payload']['order']['editionCode']

        url = BASE_URL + '/wholesale/subscribers/' + subscriber_id
    
        data = {
                "package": subscriberPackageChoice,
                "provisioningParameters": { 
                    #"primaryPhoneNumber": "", 
                    #"extension": "",
                    #"locationId": location_id
                }
                
            }
        #The commented attributes should only be supplied when changing from the Meetings Package to a package that requires calling-specific attributes.

        if subscriberPackageChoice != "webex_meetings" and "extension" not in webex_subscriber:
            location_id = get_wholesale_location_id_of_wholesale_customer(wholesale_customer)
            random_available_extention = str(provide_free_extention(location_id, wholesale_customer))
            data['provisioningParameters']['extension'] = random_available_extention
            data['provisioningParameters']['locationId'] = location_id

        response = requests.put(url, headers=HEADERS, data=json.dumps(data)) 
        
        if response.status_code == 200:
            return True, 'Subscription to Webex has been updated.', None, None 
        
        else: 
            print(f"Error during subscriber creation. Status code:{response.status_code} - Response: {response.text}")
            return False, 'Error during subscriber creation.', 'UNKNOWN_ERROR', None 
    
    else:
        return False, 'No associated subscriber found. Nothing to update', 'USER_NOT_FOUND', None  



'''
Receives and maps a Wholesale customer address to a location id
see also: https://developer.webex.com/docs/api/v1/locations
'''
def get_wholesale_location_id_of_wholesale_customer(wholesale_customer):
    
    location_id = None

    org_id = wholesale_customer['orgId']
    comparison_address = wholesale_customer['address']['addressLine1']
    comparison_zip = wholesale_customer['address']['zipOrPostalCode']

    url = BASE_URL + '/locations?orgId=' + org_id

    locations = requests.get(url, headers=HEADERS).json()

    for location in locations['items']:
        street = location['address']['address1']
        zip = location['address']['postalCode']
        location_id = location['id']
        
        if street == comparison_address and zip == comparison_zip:
            return location_id

    #if no mapping possible we take the last location in the list for this customer   
    return location_id



## UNSUBSCRIBING
'''
Removes Wholesale subscriber if existing
'''
def remove_wholesale_meetings_subscriber_if_existing(event_details, app_direct_company_uuid):
    
    subscriber_email = event_details['creator']['email']
    wholesale_subscriber = wholesale_subscriber_exists(app_direct_company_uuid, subscriber_email)
    
    if wholesale_subscriber:
        
        print('Associated Wholesale subscriber found. Deleting ...')
        
        subscriber_id = wholesale_subscriber['id']

        url = BASE_URL + '/wholesale/subscribers/' + subscriber_id

        response = requests.delete(url, headers=HEADERS)

        if response.status_code == 204:
            print("Webex subscription has been cancelled.")
            return True, 'Subscription to Webex has been cancelled.', None, None 
        else: 
            print(f"Wholesale Subscribers was not cancelled - Status code: {response.status_code}, Response: {response.json()}")
            return False, 'Error during unsubscribing.', 'UNKNOWN_ERROR', None  
    else:
        print(f"No associated Wholesale subscriber found. Nothing to delete.")
        return False, 'No associated subscriber found. Nothing to delete', 'USER_NOT_FOUND', None  


'''
Executes check if subscriber already exists and return bool or subscriber.
'''
def wholesale_subscriber_exists(app_direct_company_uuid, subscriber_email):
    
    url = BASE_URL + '/wholesale/subscribers?externalCustomerId=' + app_direct_company_uuid
    
    wholesale_subscribers = requests.get(url, headers=HEADERS).json()

    for subscriber in wholesale_subscribers['items']:

        wholesaleSubscriberEmail = subscriber['email']
        wholesaleExternalCustomerID = subscriber['externalCustomerId']

        if subscriber_email == wholesaleSubscriberEmail and wholesaleExternalCustomerID == app_direct_company_uuid:
            print("Subscriber existing.")
            return subscriber 
    
    return False


'''
Remove Subscriber as Webex person. Webex only allows an email address to be part of one organization/customer. 
Thereby it is important not only to unsubscribe but also delete the person for future reassignments to another organization. 
'''
def remove_Webex_person(event_details, associated_wholesale_customer): 
    
    subscriber_email = event_details['creator']['email']
    orga_id = associated_wholesale_customer['orgId']

    person = get_webex_person(subscriber_email, orga_id).json()
    person_id = person['items'][0]['id'] #Webex only allows an email address to be part of one organization and we filtered based on the email, thereby we just use the first element

    response = delete_webex_person(person_id)

    if response.status_code == 204:
        print("Subscription has been removed.")
        return True, 'Subscription has been removed.', None, None
    
    else:
        print(f"Error during Webex person deleting. - Status code: {response.status_code}, Response: {response.json()}")
        return False, 'Error during Webex person deleting.', 'UNKNOWN_ERROR', None
    

'''
Gets a Webex person with a specific email address and for an specific organization
'''
def get_webex_person(email, org_id):
    
    url = BASE_URL + '/people?orgId='+org_id+'&email='+email

    response = requests.request("GET", url, headers=HEADERS)

    return response


'''
Deletes a Webex person with a specific ID
'''
def delete_webex_person(person_id):

    url = BASE_URL + '/people/' + person_id

    response = requests.request("DELETE", url, headers=HEADERS) 

    print(f"Status code for people delete {response.status_code}")

    return response

