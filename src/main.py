import os
from dotenv import load_dotenv
import discord
import database as db

# Load token
load_dotenv()
TOKEN = os.getenv('TOKEN')

# Intents
intents = discord.Intents.default()
intents.message_content = True

# Init Bot
client = discord.Client(intents=intents)

# ONLINE
@client.event
async def on_ready():
    print(f'{client.user} is Ready!')

# Comando simples: responder ao !ping
@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    if message.content.startswith('record this message'):
        date_str = message.created_at.strftime('%d/%m/%Y')
        db.upsertMessageCount(date_str, message.author.id, message.channel.id)
        await message.channel.send('Done!')
    
    elif message.content.startswith('get messages'):
        # Get messages during a specific date range
        messages = db.getMessagesDuring('03/12/2024', '04/12/2024')
        
        # Send the messages to the Discord channel
        if messages:
            response = "\n".join([f"{msg['date']} | {msg['user_id']} | {msg['channel_id']} | {msg['count']}" for msg in messages])
        else:
            response = "No messages found in this date range."
        
        await message.channel.send(response)

# Start bot
client.run(TOKEN)