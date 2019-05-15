import json

data = {
    'token': 'YOUR_TOKEN',
    'mantainer': 0, #REPLACE "0" WITH ACTUAL TELEGRAM USER ID (maintainer)
    'room': 0, #REPLACE "0" WITH ACTUAL TELEGRAM CHAT ID (Testing Room)
    'testers': [] #LIST OF TESTERS (Telegram user IDs)
}


with open('security.json', 'w', encoding='utf-8') as fo:
    json.dump(data, fo)
