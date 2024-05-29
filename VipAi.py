import random
from pymongo import MongoClient
from pyrogram import Client, filters
from config import MONGO_DB_URI as MONGO_URL
from pyrogram.enums import ChatAction

# Initialize MongoDB connection once
mongo_client = MongoClient(MONGO_URL)
chatdb = mongo_client["Word"]["WordDb"]
vipdb = mongo_client["VipDb"]["Vip"]

# Helper function to handle sending messages or stickers
async def send_reply(client, message, text_or_sticker):
    if text_or_sticker["check"] == "sticker":
        await message.reply_sticker(text_or_sticker["text"])
    else:
        await message.reply_text(text_or_sticker["text"])

# Handler for the "alive" command
@Client.on_message(filters.command("alive", prefixes=["/", ".", "?", "-"]))
async def start(client, message):
    await message.reply_text("**ᴀʟᴇxᴀ ᴀɪ ᴜsᴇʀʙᴏᴛ ғᴏʀ ᴄʜᴀᴛᴛɪɴɢ ɪs ᴡᴏʀᴋɪɴɢ**")

# General handler for text and sticker messages in groups
@Client.on_message((filters.text | filters.sticker) & ~filters.private & ~filters.me & ~filters.bot)
async def handle_group_message(client, message):
    is_vip = vipdb.find_one({"chat_id": message.chat.id})
    if is_vip:
        return

    await client.send_chat_action(message.chat.id, "typing")

    if not message.reply_to_message:
        word = message.text if message.text else message.sticker.file_unique_id
        responses = list(chatdb.find({"word": word}))
        if responses:
            response = random.choice(responses)
            await send_reply(client, message, response)
    else:
        user_id = (await client.get_me()).id
        if message.reply_to_message.from_user.id == user_id:
            responses = list(chatdb.find({"word": message.text}))
            if responses:
                response = random.choice(responses)
                await send_reply(client, message, response)
        else:
            if message.text:
                chatdb.update_one(
                    {"word": message.reply_to_message.text, "text": message.text},
                    {"$set": {"check": "none"}},
                    upsert=True,
                )
            if message.sticker:
                chatdb.update_one(
                    {"word": message.reply_to_message.text, "text": message.sticker.file_id},
                    {"$set": {"check": "sticker", "id": message.sticker.file_unique_id}},
                    upsert=True,
                )

# Handler for text and sticker messages in private chats
@Client.on_message((filters.text | filters.sticker) & filters.private & ~filters.me & ~filters.bot)
async def handle_private_message(client, message):
    await client.send_chat_action(message.chat.id, "typing")

    if not message.reply_to_message:
        responses = list(chatdb.find({"word": message.text}))
        if responses:
            response = random.choice(responses)
            await send_reply(client, message, response)
    else:
        user_id = (await client.get_me()).id
        if message.reply_to_message.from_user.id == user_id:
            responses = list(chatdb.find({"word": message.text}))
            if responses:
                response = random.choice(responses)
                await send_reply(client, message, response)

# Start the client with your API ID and hash (replace with actual values)
