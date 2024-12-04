import os
from dotenv import load_dotenv
import discord
import commands as cmd

# Load token
load_dotenv()
TOKEN = os.getenv('TOKEN')

# Intents
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
intents.messages = True

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
        await cmd.recordMessage(message)
    
    elif message.content.startswith('get messages'):
        await cmd.getMessages(message)

    elif message.content.startswith('load messages'):
        await cmd.loadMessages(message)

    elif message.content.startswith('get stats'):
        await cmd.stats(message)
# Start bot
if __name__ == "__main__":
    client.run(TOKEN)