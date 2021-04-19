# A Faster Welcome Text

Text new people to your list within 15 minutes of them joining!

## Requirements
This project assumes that:

* You're using EveryAction
* The person has opted in to your SMS list
* You've set up an Automation in Strive 

## Notes

[Welcome Text Local](https://github.com/sunrisedatadept/a-faster-welcome-text/blob/main/welcome_text_local.py)  
This is a local version of the script. You can use this to test the script and ensure you're successfuly sending contacts to Strive.   

[Welcome Text Container](https://github.com/sunrisedatadept/a-faster-welcome-text/blob/main/welcome_text_container.py)  
This is the container version of the script. This is what you want to point your Civic Container script to. It will not run locally. 

## Usage

1. Clone this Github repository -- you'll need to specify your new url in the civis interface
2. Create a new Container Script in Civis
3. The following parameters must be set in the script for this to work:

| PARAMETER NAME     | DISPLAY NAME       | DEFAULT            | TYPE              | MAKE REQUIRED |
|--------------------|--------------------|--------------------|-------------------|---------------|
| VAN                | VAN                | N/A                | Custom Credential | Yes           |
| STRIVE             | STRIVE             | N/A                | Custom Credential | Yes           |
| STRIVE_CAMPAIGN_ID | STRIVE_CAMPAIGN_ID | {Your campaign ID} | INTEGER           | Yes           |

4. Connect civis to your github repository and point it appropriately.

5. Put the following in the command lines COMMAND section:

```
pip install pandas
python welcome_text_container.py

```
## Strive Set Up

This script works by sending contacts to an Automation flow we've set up in Strive. **You must first send at least 1 contact to Strive via the API for this feature to be available**. We are taking advantage of the fact that Strive never sends a welcome text to the same person. 

1. Navigate to the Automation section on the left sidebar in your campaign.
2. Automations > API > Create API automation 
3. Name your automation 
4. Set the trigger to "New member is added via API"
5. Choose the Flow
6. Create your automation 


