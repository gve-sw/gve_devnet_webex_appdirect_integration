# Webex AppDirect Integration

This demo shows three basic integration workflows between the AppDirect Marketplace and the Webex Partner Hub (Webex Wholesale API). The mentioned workflows are the creation, update and deletion of Webex subscriptions based on the users' interaction with AppDirect. Furthermore, it covers the creation of a new Webex organization, if it doesn’t already exist.

## Contacts
* Ramona Renner
* Jordan Coaten

## Solution Components
* Webex Partner Hub
* AppDirect Marketplace
* Ngrok (Optionally)

## Prerequisites
* AppDirect Marketplace (admin account - based on email address, which is not associated to any Webex organization)
* Access to Webex Partner Hub (Webex Wholesale API)

## Demo Workflow
![/IMAGES/Workflow.png](/IMAGES/Workflow.png)

## High Level Design 
![/IMAGES/High_Level_Design.png](/IMAGES/High_Level_Design.png)


## Prepare AppDirect
Navigate to your AppDirect Marketplace URL,    

1. Login as admin and with an account, which is not yet assigned to a Webex organization.    

**Add Information of Company in AppDirect:**  

2. Click **[your username]** > **My Company** 
3. Make sure the following information is defined:   
  * Company Name 
  * Company Phone
  * Company Email (which is not yet assigned to a Webex organization)
  * Address (e.g. 771 Alder Drive, Cisco Site 5, Milpitas, CA, 95035)
4. Click **Save**   


**Add Information of User in AppDirect:**  

5. Click **[your username]** > **My Profile** > Click the **Pencil Icon** (on hover) next to the **Email Address** field
6. Enter an **Email Address** value: It can be the same email as in step 3, but needs to be an email address which is not yet assigned to a Webex organization. 
7. Click **Save**  
> Furthermore, make sure the name of the user is set.

**Create a Product:**  
 
8. Go to **Manage** (in header menu) > **Developer** > **Products** > **Add Products**    
9. Enter the following information:
  * Product Name: e.g. Webex
  * Service Type: Standalone Product
  * Product Type: Web App
  * Integration Type: Full Integration
  * Usage Model: Single User
  * Revenue Model: Recurring
  * Terms and Conditions: checked
10. Click **Create Product**   


**Add Three Editions:**   

11. In the left menu or the product view, click **Editions** > **Add New Edition** in the **EDITIONS AND PRICING** sections
12. Enter a **Name** and **Edition Code**
13. Click **Save Plan**   
> Use the following data and repeat step 11.-13. three times: Name: Webex Meetings, Editon code: webex_meetings; Name: Webex Calling, Editon code: webex_calling; Name: Webex Suite, Editon code: webex_suite;    
14. Delete the default **Recurring Edition**   


**Create Authorization Credentials:**  

15. In the left menu, click **Credentials** in the **INTEGRATION** sections  
16. In the **INBOUND CREDENTIALS (OAUTH 2.0)** box, click **Generate ID and Secret** and copy and save the credentials for a later step.    
17. In the **OUTBOUND CREDENTIALS** box, enter the following:   
  * Type: Basic Authentication
  * Username: choose preferred username
  * Password: choose preferred password
18. Note the entered information for a later step and click **Save**    


**Get Public Url for the Demo Application Tunnel:**   

This app requires being reachable over an internet accessible URL, so that AppDirect can send events to it. Therefore, it can be deployed on different IaaS platforms like Heroku, Amazon Web Services Lambda, Google Cloud Platform (GCP) and more. For simplicity, we will use [Ngrok](https://ngrok.com/download) here to create a tunnel to our local app. Please be aware that ngrok can be blocked in some corporate networks.  

19. Download and install [Ngrok](https://ngrok.com/download)   
20. Execute the following command in the terminal:   
  ```
  ngrok http 5002
  ```   
> This demo app is running on http://localhost:5002 by default      
21. Copy and save the **Forwarding** URL with the format **https://[xxx].ngrok.io** from the output for the next step   
![/IMAGES/ngrok.png](/IMAGES/ngrok.png)   


**Define the Integration Endpoints:** 

22. On the AppDirect product edit page, click **Edit Integration** in the **INTEGRATION** sections of the left menu 
23. Fill in the following integration endpoints based on the URL from step 21:   
  * Subscription Create Notification URL: https://[xxx].ngrok.io/subscription_receiver?eventUrl={eventUrl}&eventType=create
  * Subscription Change Notification URL: https://[xxx].ngrok.io/subscription_receiver?eventUrl={eventUrl}&eventType=update
  * Subscription Cancel Notification URL https://[xxx].ngrok.io/subscription_receiver?eventUrl={eventUrl}&eventType=cancel
  > Note: Adapt the [xxx] section accordingly 
24. Click **Save**   


## Prepare the Webex Partner Hub 

**Create a Configuration Template:**   

Go to the Webex Partner Hub (https://admin.webex.com/),   
25. Click **Customers** in left menu > **Templates** Tab > **Create template**      
26. Provide the following information:
  * Template name
  * Country or region (e.g. United States of America)
  * Service provider admin
  * Cloud Connected PSTN provider (requirement for the provisioning of Webex Calling)
  * You do not need to select a wholesale subscription    
27. Click **Next**
28. Choose the applicable authentication and click **Next**
29. Define the **Brand name for emails** and click **Next**
30. Review the provided information and click **Submit**
31. Click the name of the template that you just created in the list > copy the **Provisioning ID** for a later step as shown below:   
![/IMAGES/template_008_provisionId.png](/IMAGES/template_008_provisionId.png)   


## Get a Webex Token
  
32. Navigate to https://developer.webex.com   
33. Log in with the same account you used with the Webex Partner Hub.   
34. Navigate to an API endpoint such as https://developer.webex.com/docs/api/v1/wholesale-subscribers/list-wholesale-subscribers   
35. In the **Try It** Tab > select **Use personal access token** > copy the bearer token and save it for a later step.  
![/IMAGES/webex_api_bearer.png](/IMAGES/webex_api_bearer.png) 

> **Note:** A personal access token is a short-lived access token you can use to make Webex API calls on your own behalf. Any actions taken through the API will be done as you. Personal access tokens expire 12 hours after you sign in to the Developer Portal and should not be used in production environments. A production app should instead create an [integration](https://developer.webex.com/docs/integrations) to obtain an access token from an authenticating user using OAuth.  


## Installation/Configuration of the Sample App

36. Make sure you have [Python 3.8.9](https://www.python.org/downloads/) and [Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) installed.

37. (Optional) Create and activate a virtual environment for the project ([Instructions](https://docs.python.org/3/tutorial/venv.html))   

38. Access the created virtual environment folder
    ```
    cd [add name of virtual environment here] 
    ```

39. Clone this Github repository into the local folder:  
    ```
    git clone [add github link here]
    ```
    * For Github link: 
      In Github, click on the **Clone or download** button in the upper part of the page > click the **copy icon**  
      ![/IMAGES/giturl.png](/IMAGES/giturl.png)
  * Or simply download the repository as zip file using 'Download ZIP' button and extract it

40. Access the downloaded folder:  
    ```
    cd gve_devnet_webex_appdirect_integration
    ```

41. Install all dependencies:
    ```
    pip3 install -r requirements.txt
    ```

42. Fill in your variables in the .env file. Feel free to leave the address data as it is (for testing purpose): 

  ```python
  BASE_URL_MARKETPLACE=[Add base url of your AppDirect Marketplace, e.g https://marketplace.appdirect.com]

  OAUTH_CLIENT_ID=[Add client ID from step 16]
  OAUTH_CLIENT_SECRET=[Add client secret from step 16]
  BASIC_USERNAME=[Add username from step 18]
  BASIC_PASSWORD=[Add password from step 18]

  WEBEX_TOKEN=[Add bearer token from step 35]
  PROVISIONING_ID=[Add provisioning ID from step 31]

  CUSTOMER_PACKAGES='["webex_calling", "webex_meetings", "webex_suite", "common_area_calling", "webex_voice"]'
  ADDRESS="771 Alder Drive"
  ZIP_CODE="95035"
  CITY="Milpitas"
  COUNTRY="US"
  STATE="CA"
  TIMEZONE="America/Los_Angeles"
  ```
> Note: Mac OS hides the .env file in the finder by default. View the demo folder for example with your preferred IDE to make the file visible.

43. Start the flask application:   

```python3 app.py```


## Usage

**Create a Subscription**   

Start your integration tests in AppDirect by creating a subscription,  

44. Go to **Manage** > **Developer** > click **Edit** next to the previously created product > click **Integration Report** (in the **INTEGRATION** section) > click **Run Test** in the **Subscribe to your product** section.      
45. Choose a subscription and click **Create Subscription**      
46. If the Webex organization associated to the users' AppDirect company doesn't exist already, it will be automatically created as part of the process. This provisioning process can take up to 5 minutes. Thereby, the user will be notified that a set-up process was triggered, and asked to wait for around 5 minutes. **This only happens once for each company in AppDirect, when the first user buys a subscription. For every following user of the company, step 46 will be skipped.**     
47. After 5 minutes, the user can click **Create Subscription** again. This time the Webex organization is present and the subscriber will be added to the available organization.       


**Updating a Subscription.**  

48. Click **Continue to Change**   
49. Choose another subscription and click **Change Subscription**   


**Cancelling a Subscription.** 

50. Click **Continue to Cancel**   
51. Choose another subscription and click **Cancel Subscription**   


## Screenshot

![/IMAGES/screenshot.png](/IMAGES/screenshot.png)


## Limitations

This sample code only shows some basic integration workflows for the packages: Webex Meetings, Webex Calling, Webex Suite. It is not meant to cover all possible workflows or configurations. Some of the information required for the creation of the Webex organization and subscribers is static, since we assume that the information is provided by an additional external system, which is not part of this demo.
For simplicity, this demo assigns random phone extensions when adding a Webex Calling or Suite subscription instead of a phone number. 

### LICENSE

Provided under Cisco Sample Code License, for details see [LICENSE](LICENSE.md)

### CODE_OF_CONDUCT

Our code of conduct is available [here](CODE_OF_CONDUCT.md)

### CONTRIBUTING

See our contributing guidelines [here](CONTRIBUTING.md)

#### DISCLAIMER:
<b>Please note:</b> 
This script is meant for demo purposes only. All tools/ scripts in this repo are released for use "AS IS" without any warranties of any kind, including, but not limited to their installation, use, or performance. Any use of these scripts and tools is at your own risk. There is no guarantee that they have been through thorough testing in a comparable environment and we are not responsible for any damage or data loss incurred with their use.
You are responsible for reviewing and testing any scripts you run thoroughly before use in any non-testing environment.
