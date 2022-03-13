from flask import Flask
import configparser
import json
import asyncio
from datetime import date, datetime,timedelta
from time import time

from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from telethon.tl.functions.messages import (GetHistoryRequest)
from telethon.tl.types import (
    PeerChannel
)

app = Flask(__name__)


# some functions to parse json date
class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()

        if isinstance(o, bytes):
            return list(o)

        return json.JSONEncoder.default(self, o)


# Reading Configs
config = configparser.ConfigParser()
config.read("config.ini")

# Setting configuration values
api_id = config['Telegram']['api_id']
api_hash = config['Telegram']['api_hash']

print(api_id)
print(api_hash)

api_hash = str(api_hash)

phone = config['Telegram']['phone']
username = config['Telegram']['username']

keywords = ["maleta", "tv", "stadia", "pelo", "olaplex"]

# Create the client and connect
client = TelegramClient(username, api_id, api_hash)

async def main(phone):
    await client.start()
    print("Client Created")
    # Ensure you're authorized
    if await client.is_user_authorized() == False:
        await client.send_code_request(phone)
        try:
            await client.sign_in(phone, input('Enter the code: '))
        except SessionPasswordNeededError:
            await client.sign_in(password=input('Password: '))

    me = await client.get_me()

    # user_input_channel = input('enter entity(telegram URL or entity id):')
    user_input_channel = "https://t.me/chollometro"


    if user_input_channel.isdigit():
        entity = PeerChannel(int(user_input_channel))
    else:
        entity = user_input_channel

    my_channel = await client.get_entity(entity)

    offset_id = 0
    limit = 100
    all_messages = []
    total_messages = 0
    total_count_limit = 1000

    while True:
        # print("Current Offset ID is:", offset_id, "; Total Messages:", total_messages)
        history = await client(GetHistoryRequest(
            peer=my_channel,
            offset_id=offset_id,
            offset_date=None,
            add_offset=0,
            limit=limit,
            max_id=0,
            min_id=0,
            hash=0
        ))
        if not history.messages:
            break
        messages = history.messages
        for message in messages:
            message_str = message.to_dict()["message"]
            message_date = message.to_dict()["date"].replace(tzinfo=None)
            
            hours_passed = int((datetime.utcnow() - message_date).total_seconds()/3600)
            # print(hours_passed)
            for keyword in keywords:
                if keyword in message_str.lower() and "TOP 10 CHOLLOS DE HOY" not in message_str and hours_passed <= 1:
                    # print(f"Woohoo! Found {keyword} in a Chollo!:")
                    # print(message_str)
                    message_str = f"Woohoo! Found {keyword} in a Chollo!:\n" + message_str
                    print(message_str)
                    await client.send_message(entity="https://t.me/chollometro_alerts",message=message_str)
            all_messages.append(message.to_dict())

        offset_id = messages[len(messages) - 1].id
        # print(all_messages)
        total_messages = len(all_messages)
        if total_count_limit != 0 and total_messages >= total_count_limit:
            break
        

    # with open('channel_messages.json', 'w') as outfile:
    #     json.dump(all_messages, outfile, cls=DateTimeEncoder)


    
@app.route("/")
def home_view():
    with client:
        client.loop.run_until_complete(main(phone))