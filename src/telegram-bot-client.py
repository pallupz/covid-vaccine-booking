import os
import pprint
import sys

from telegram.client import Telegram

from utils import get_saved_user_info, save_user_info


def create_tg_client_config(tg_config_file: str = "tg-config.json"):
    api_id = input("Enter the Telegram API ID: ")
    api_hash = input("Enter the Telegram API hash: ")
    phone = input("Enter your mobile number registered with Telegram: ")
    encryption_key = input("Enter database secret key: ")
    cowin_mobile = input("Enter registered CoWIN mobile number:")
    tg_config = {
        'api_id': api_id,
        'api_hash': api_hash,
        'phone': phone,
        'encryption_key': encryption_key,
        'cowin-mobile': cowin_mobile
    }
    save_user_info(tg_config_file, tg_config)
    return tg_config


def read_tg_client_config(tg_config_file: str = "tg-config.json"):
    client_details = None
    if os.path.exists(tg_config_file):
        client_details = get_saved_user_info(tg_config_file)
    else:
        client_details = create_tg_client_config()
    return client_details


def initialize_tg_client(tg_config_file: str = "tg-config.json") -> Telegram:
    client_config = read_tg_client_config(tg_config_file)
    client = Telegram(
        api_id=client_config.get("api_id"),
        api_hash=client_config.get("api_hash"),
        phone=client_config.get("phone"),
        database_encryption_key=client_config.get("encryption_key")
    )
    return client


def new_message_handler(update):
    # we want to process only text messages
    pprint.pprint(update)
    message_content = update['message']['content'].get('text', {})
    message_text = message_content.get('text', '').lower()
    chat_id = update['message']['chat_id'] # Either use this if you know the chat_id
    search_string = 'Vaccination centers for 18-44 group' # Replace this with the message of the notification
    if search_string.lower() in message_text:
        os.system('python3 src/covid-vaccine-slot-booking.py')
    return


def signal_term_handler():
    sys.exit(0)


def main():
    tg_client = initialize_tg_client()
    tg_client.login()
    tg_client.add_message_handler(new_message_handler)
    result = tg_client.get_chats()
    result.wait()
    tg_client.idle()
    return


if __name__ == '__main__':
    main()
