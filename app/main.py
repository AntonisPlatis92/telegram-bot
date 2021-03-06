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


# Reading Configs
config = configparser.ConfigParser()
config.read("app/config.ini")
# Setting configuration values
api_id = config['Telegram']['api_id']
api_hash = config['Telegram']['api_hash']


api_hash = str(api_hash)

phone = config['Telegram']['phone']
username = config['Telegram']['username']

keywords = ["maleta", "tv", "stadia", "pelo", "olaplex", "switch"]

# Create the client and connect
client = TelegramClient(username, api_id, api_hash)

async def raise_alerts(phone):

    await client.start()

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
    total_count_limit = 100

    chollos_found = 0
    print("Starting")
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
        i=1
        for message in messages:
            print(f"Checking message {i}")
            message_str = message.to_dict()["message"]
            message_date = message.to_dict()["date"].replace(tzinfo=None)
            
            mins_passed = int((datetime.utcnow() - message_date).total_seconds()/60)
            hours_passed = int((datetime.utcnow() - message_date).total_seconds()/3600)
            # print(hours_passed)
            for keyword in keywords:
                if keyword in message_str.lower() and "TOP 10 CHOLLOS DE HOY" not in message_str and hours_passed < 1:
                    chollos_found += 1
                    message_str = f"Woohoo! Found {keyword} in a Chollo!\nPublished at: {message_date} ({mins_passed} mins ago)\n" + message_str
                    print(message_str)
                    await client.send_message(entity="https://t.me/chollometro_alerts",message=message_str)
            all_messages.append(message.to_dict())
            i += 1

        offset_id = messages[len(messages) - 1].id
        # print(all_messages)
        total_messages = len(all_messages)
        if total_count_limit != 0 and total_messages >= total_count_limit:
            break

    print("Finished")

    return chollos_found



    
@app.route("/")
async def home_view() -> str:
    async with client:
        chollos_found = await raise_alerts(phone)
    return f"Found {chollos_found} Chollos"