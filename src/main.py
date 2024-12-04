import os
from dotenv import load_dotenv
import discord
import commands as cmd
from logger import logger

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
    logger.info(f"{client.user} is Ready!")

# Command dispatcher
async def handle_command(message):
    commands = {
        "record this message": cmd.recordMessage,
        "get messages": cmd.getMessages,
        "load messages": cmd.loadMessages,
        "get stats": cmd.stats,
        "help": cmd.help,
    }
    content = message.content.strip()

    if content in commands:
        await commands[content](message)

# Comando simples: responder ao !ping
@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    try:
        await handle_command(message)
    except Exception as e:
        logger.error(f"Error in command: {e}")
        await message.channel.send("An error has occurred while handling your command.")

# Start bot
if __name__ == "__main__":
    try:
        client.run(TOKEN)
    except Exception as e:
        logger.critical(f"Statify failed to start: {e}")