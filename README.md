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
