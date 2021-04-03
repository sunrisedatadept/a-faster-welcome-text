# A Faster Welcome Text

Text new people to your list within 15 minutes of them joining!

## Requirements
This project assumes that:

* You're using EveryAction
* The person has opted in to your SMS list
* You've set up an Automation in Strive 

## Usage

1. Clone this Github repository -- you'll need to specify your new url in the civis interface
2. Create a new Container Script in Civis
3. The following parameters must be set in the script for this to work:

| PARAMETER NAME | DISPLAY NAME | DEFAULT | TYPE              | MAKE REQUIRED |
|----------------|--------------|---------|-------------------|---------------|
| VAN            | VAN          | N/A     | Custom Credential | Yes           |
| STRIVE         | STRIVE       | N/A     | Custom Credential | Yes           |

Connect civis to your github repository and point it appropriately.

Put the following in the command lines COMMAND section:

```
pip install pandas
python welcome_text_container.py

```
## Strive Set Up

Strive has a wonderful Automation feature that we're taking advantage of. **You must first send at least 1 contact to Strive via the API for this feature to be available**. 

1. Navigate to the Automation section
![image](https://user-images.githubusercontent.com/28691023/113482997-2b14db80-946f-11eb-9924-022f8509532c.png)

2. 


## Notes

[Welcome Text Local](https://github.com/sunrisedatadept/a-faster-welcome-text/blob/main/welcome_text_local.py)  
This is a local version of the script. You can use this to test the script and ensure you're successfuly sending contacts to Strive.   

[Welcome Text Container](https://github.com/sunrisedatadept/a-faster-welcome-text/blob/main/welcome_text_container.py)  
This is the container version of the script. This is what you want to point your Civic Container script to. It will not run locally. 
