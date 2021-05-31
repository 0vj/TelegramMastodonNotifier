from pymongo import collation
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import os
import pymongo 
import requests
import json

myclient = pymongo.MongoClient("mongodb://"+os.environ['MONOG_DATABASE_USERNAME']+":"+os.environ['MONOG_DATABASE_PASSWORD']+"@"+os.environ['MONOG_DATABASE_ADDRESS'])
DB = myclient[os.environ['MONGO_DATABASE_NAME']]
mastodon_connections_collation = DB["mastodon_connections"]

def get_last_mastodon_notification_id(mastodon_server_address, access_token) -> dict:
    endpoint_url = mastodon_server_address + os.environ['MASToDON_API_NOTIFICATION_ADDRESS']
    headers = {"Authorization": "Bearer " + access_token}
    response = requests.get(endpoint_url, headers=headers)
    notifications = json.loads(response.text)
    last_notification_id = notifications[-1]["id"]
    return last_notification_id

def start(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    first_name = update.message.from_user.first_name
    update.message.bot.send_message(chat_id=chat_id, text=f"Hello {first_name}. Welcome to the Mastodon notifier bot!")

def add_mastodon_account_help(update: Update, context: CallbackContext) -> None:
        text = "To add your Mastodon account, you must send your server address and password (with read notification) as the next message."
        update.message.bot.send_message(chat_id=update.message.chat_id, text=text)
        message_example = """https://mas.to
        bx9soFfZFSh2WhJZ_NY287Dh-hI04UJyP8uFSPn0iSY
        """
        update.message.bot.send_message(chat_id=update.message.chat_id, text=message_example)



def add_mastodon_account(update: Update, context: CallbackContext) -> None:
    mastodon_server_address, access_token= update.message.text.splitlines()
    last_notification_id = get_last_mastodon_notification_id(mastodon_server_address, access_token)
    mastodon_connections_collation.insert_one({"first_name": update.message.from_user.first_name, 
                                               "chat_id": update.message.chat_id,
                                               "mastodon_server_address": mastodon_server_address, 
                                               "access_token": access_token,
                                               "last_notification_id": last_notification_id,})
    update.message.bot.send_message(chat_id=update.message.chat_id, text="Your account has been successfully added.")



def echo(update: Update, context: CallbackContext) -> None:
    text = "Please use bot commands"
    update.message.bot.send_message(chat_id=update.message.chat_id, text=text)

def main():
    updater = Updater(os.environ['TELEGRAM_BOT_TOKEN'])
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("add_mastodon_account", add_mastodon_account_help))
    dispatcher.add_handler(MessageHandler(Filters.text, add_mastodon_account))
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()