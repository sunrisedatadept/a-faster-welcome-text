# load the necessary packages
import pandas as pd
import requests
from requests.auth import HTTPBasicAuth
import time
from datetime import datetime
import os
import json
import time
from urllib.parse import urljoin
from datetime import datetime, timedelta
import sys

# Set parameters
delta  = timedelta(hours =  4) ## Set this to the frequency of your Container Script

# Set local environmental variables
van_key = os.environ['VAN_API_KEY']
strive_key = os.environ['STRIVE_KEY']
campaign_id = os.environ['STRIVE_CAMPAIGN_ID']

# Set EA API credentials
username = 'welcometext'  ## This can be anything
db_mode = '1'    ## Specifying the NGP side of VAN
password = f'{van_key}|{db_mode}' ## Create the password from the key and the mode combined
everyaction_auth = HTTPBasicAuth(username, password)
everyaction_headers = {"headers" : "application/json"}

# Strive parameters
strive_url = "https://api.strivedigital.org/"

#### Functions
def get_every_action_contacts(everyaction_headers, everyaction_auth):
    """
    Prepares the time strings for the EA API end point, creates the URL end point
    and sends a request to the endpoint for a Contacts record, with VanID, first name,
    last name, phone, SMS opt in status, and the date the contact was created.

    Returns endpoint with the jobId for the download job to access the requested contacts.
    """

    # Prepare vstrings for Changed Entites API
    max_time = datetime.now()
    min_time = max_time - delta
    max_time_string = max_time.strftime("%Y-%m-%dT%H:%M:%SZ")
    min_time_string = min_time.strftime("%Y-%m-%dT%H:%M:%SZ")

    # EveryAction Changed Entities parameters
    base_everyaction_url = 'https://api.securevan.com/v4/'
    everyaction_job = "changedEntityExportJobs"
    changed_entities_url = urljoin(base_everyaction_url, everyaction_job)

    recent_contacts = {
      "dateChangedFrom": 		min_time_string,
      "dateChangedTo" : 		max_time_string,
      "resourceType": 			"Contacts",
      "requestedFields": 		["VanID", "FirstName", "LastName", "Phone", "PhoneOptInStatus", "DateCreated" ],
      "excludeChangesFromSelf": "true"
    }

    response = requests.post(changed_entities_url, json = recent_contacts, headers = everyaction_headers, auth = everyaction_auth, stream = True)
    jobId = str(response.json().get('exportJobId'))
    everyaction_download_url = f'{changed_entities_url}/{jobId}'
    return everyaction_download_url


def get_export_job(everyaction_download_url, everyaction_headers, everyaction_auth):
    """
    Takes the endpoint for the download job and checks if the downlink is available every 20 seconds. Once the download link is available,
    downloads the data into a data frame. If 1000 seconds have passed and the download link is not available, assume the API has stalled out and
    exit the program to try again the next run.
    """

    timeout = 1000   # [seconds]
    timeout_start = time.time()

    while time.time() < timeout_start + timeout:
    	time.sleep(20) # twenty second delay
    	try:
    		response = requests.get(everyaction_download_url, headers = everyaction_headers, auth = everyaction_auth)
    		downloadLink = response.json().get('files')[0].get('downloadUrl')
    		break
    	except:
    		print("File not ready, trying again in 20 seconds")

    if time.time() == timeout_start + timeout:
    	sys.exit("Export Job failed to download!")
    else:
    	print("Export Job Complete")
    return downloadLink

def prepare_data(downloadLink):
    """
    Takes the downloaded dataframe of contacts and
    - Checks if contacts were created today
    - Checks if contacts are opted in to SMS list

    Then returns the final data frame that will be send to Strive.
    """

    df = pd.read_csv(downloadLink)
    # Save a csv for troubleshooting
    if len(df) > 0:
        print(f"Found {len(df)} modified contacts. Checking if created today.")
    else:
        sys.exit("No new contacts. Exiting.")

    # Filter for contacts that were created today
    # EveryAction returns a date, not a datetime, for DateCreated
    # Relying on Strive's dedupe upsert logic to not text people twice
    df['DateCreated']= pd.to_datetime(df['DateCreated'], format='%Y-%m-%d')
    df_filtered = df.loc[df['DateCreated'] ==  pd.to_datetime(datetime.now().date())]

    if len(df_filtered) > 0:
        print(f"Found {len(df_filtered)} new contacts. Checking if they are opted in.")
    else:
        sys.exit("No contacts that were created today. Exiting.")


    # Filter for contacts that have opted in. Opted in = 1
    print(df_filtered['PhoneOptInStatus'])
    df_for_strive = df_filtered.loc[df_filtered['PhoneOptInStatus'] == 1.0]
    df_for_strive = df_for_strive[["VanID", "FirstName", "LastName", "Phone"]]

    if len(df_for_strive) != 0:
        print("New folk to welcome! Let's send to Strive. They'll handle any deduping.")
    else:
        print("No opted in contacts. No contacts to send to Strive. Exiting.")


    return df_for_strive

def send_contacts_to_strive(df_for_strive):
    """
    Takes the data frame from the `prepare_data` function and sends each contact
    to Strive and adds them to the "EA API member" group.
    """

    if len(df_for_strive) != 0:
        print("New folk to welcome! Let's send to Strive. They'll handle any deduping.")

        strive_headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + strive_key}

        for index, row in df_for_strive.iterrows():
            phone_number = row['Phone']
            first_name = row['FirstName']
            if pd.isnull(first_name):
                first_name = "Friend"
            last_name = row['LastName']
            if pd.isnull(last_name):
                last_name = "Friend"
            payload = {
				    "phone_number": phone_number,
				    "campaign_id": campaign_id,
				    "first_name": first_name,
				    "last_name": last_name,
				    "opt_in": True,
				      "groups": [
				        {
				          "name": "EA API Member"
				        }
       				]
                    }
            response = requests.request("POST", 'https://api.strivedigital.org/members', headers = strive_headers, data = json.dumps(payload))
            if response.status_code == 201:
            	print(f"Successfully added: {first_name} {last_name}")
            else:
            	print(f"Was not able to add {first_name} {last_name} to Stive. Error: {response.status_code}")

    else:
    	print("No contacts to send to Strive.")

if __name__ == "__main__":
    print("Initiate Export Job")
    everyaction_download_url = get_every_action_contacts(everyaction_headers, everyaction_auth)
    downloadLink = get_export_job(everyaction_download_url, everyaction_headers, everyaction_auth)
    df_for_strive = prepare_data(downloadLink)
    send_contacts_to_strive(df_for_strive)
