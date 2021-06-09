# load the necessary packages
import pandas as pd
import requests
from requests.auth import HTTPBasicAuth
import time
from datetime import datetime
import os
import logging
import json 
import time
from urllib.parse import urljoin
from datetime import datetime, timedelta

#CIVIS enviro variables
van_key = os.environ['VAN_PASSWORD']
strive_key = os.environ['STRIVE_PASSWORD']
campaign_id = os.environ['STRIVE_CAMPAIGN_ID']

# EA API credentials
username = 'brittany'
dbMode = '1'
password = van_key + '|' + dbMode
auth = HTTPBasicAuth(username, password)
headers = {"headers" : "application/json"}

##### Set up logger #####
logger = logging.getLogger(__name__)
_handler = logging.StreamHandler()
_formatter = logging.Formatter('%(levelname)s %(message)s')
_handler.setFormatter(_formatter)
logger.addHandler(_handler)
logger.setLevel('INFO')

##### SET TIME #####

max_time = datetime.now()
delta  = timedelta(minutes=30)
min_time = max_time - delta

max_time_string = max_time.strftime("%Y-%m-%dT%H:%M:%SZ")
min_time_string = min_time.strftime("%Y-%m-%dT%H:%M:%SZ")


##### REQUEST EXPORT JOB #####

logger.info('Starting Script!')
base_url = 'https://api.securevan.com/v4/'
job = "changedEntityExportJobs"
url = urljoin(base_url, job)

recent_contacts = {
  "dateChangedFrom": 		min_time_string,
  "dateChangedTo" : 		max_time_string,
  "resourceType": 			"Contacts",
  "requestedFields": 		["VanID", "FirstName", "LastName", "Phone", "PhoneOptInStatus", "DateCreated"],
  "excludeChangesFromSelf": "true"

}

##### REQUEST EXPORT JOB #####

logger.info("Initiate Export Job")
response = requests.post(url, json = recent_contacts, headers = headers, auth = auth, stream = True)
jobId = str(response.json().get('exportJobId'))

##### GET EXPORT JOB ##### 

url = url + '/' + jobId
logger.info("Waiting for export")
timeout = 1000   # [seconds]
timeout_start = time.time()

while time.time() < timeout_start + timeout:
	time.sleep(20) # twenty second delay
	try:
		response = requests.get(url, headers = headers, auth = auth)
		downloadLink = response.json().get('files')[0].get('downloadUrl')
		break
	except:
		logger.info("File not ready, trying again in 20 seconds")

else:
	logger.info("Export Job Complete")

##### CLEAN DATA #####
# Read in the data
df = pd.read_csv(downloadLink)
logger.info(f"Found, {len(df)}, modified contacts. Checking if created today.")

# Filter for contacts that were created today
# EveryAction returns a date, not a datetime, for DateCreated
# Relying on Strive's dedupe upsert logic to not text people twice
df['DateCreated']= pd.to_datetime(df['DateCreated'], format='%Y-%m-%d')
df_filtered = df.loc[df['DateCreated'] ==  pd.to_datetime(datetime.now().date())]

logger.info(f"Found, {len(df_filtered)}, new contacts. Checking if they are opted in.")

# Check for SMS opt in
df_for_strive = df_filtered.loc[df_filtered['PhoneOptInStatus'] == 1.0]
df_for_strive = df_for_strive[["VanID", "FirstName", "LastName", "Phone"]]

logger.info(f"Found, {len(df_for_strive)}, opted in contacts. Sending to Strive.")

##### SEND TO STRIVE #####

url = "https://api.strivedigital.org/"

headers = {
  'Content-Type': 'application/json',
  'Authorization': 'Bearer ' + strive_key
}

if len(df_for_strive) != 0:
	print("New folk to welcome! Let's send to Strive. They'll handle any deduping.")
	
	for index, row in df_for_strive.iterrows():
			phone_number = row['Phone']
			
			first_name = row['FirstName']
			# Assign Friend as first name if missing
			if pd.isnull(first_name):
				first_name = "Friend"
			
			last_name = row['LastName']
			# Assign Friend as last name if missing
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

			response = requests.request("POST", 'https://api.strivedigital.org/members', headers=headers, data=json.dumps(payload))
			if response.status_code == 201:
				logger.info(f"Successfully added: {first_name} {last_name}")
			else:
				logger.info(f"Was not able to add {first_name} {last_name} to Stive. Error {response.status_code}")
	
else:
	logger.info("No contacts to send to Strive.")

