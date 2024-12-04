from datetime import datetime, timedelta
import discord
import database as db
from stats import getMonthStats
from logger import logger

async def recordMessage(message):
    date_str = message.created_at.strftime('%d/%m/%Y')
    try:
        db.upsertMessageCount(date_str, message.author.id, message.channel.id)
        logger.info(f"Recorded message from user {message.author.name} in channel {message.channel.name}")
        await message.channel.send('Message recorded!')
    except Exception as e:
        logger.error(f"Error recording message: {e}")
        await message.channel.send("Failed to record the message.")

async def getMessages(message):
    # Example date range
    start_date = '03/11/2024'
    end_date = '04/12/2024'

    try:
        messages = db.getMessagesDuring(start_date, end_date)

        count = len(messages)
        response = f"Number of entries from {start_date} to {end_date}: {count}"
        
        logger.info(f"Retrieved {count} messages from {start_date} to {end_date}")
        await message.channel.send(response)
    except Exception as e:
        logger.error(f"Error fetching messages: {e}")
        await message.channel.send("Failed to fetch messages.")

async def loadMessages(message):
    two_months_ago = datetime.now() - timedelta(days=60)
    loaded_messages = set()
    logger.info(f"Starting to load messages from the last two months: {message.guild.name}")

    # Appear as typing
    async with message.channel.typing():
        for channel in message.guild.text_channels:
            try:
                # Go through channel's history
                async for msg in channel.history(limit=None, after=two_months_ago):
                    # Use unique key to avoid duplicates
                    unique_key = f"{msg.id}-{msg.channel.id}"
                    if unique_key not in loaded_messages:
                        date_str = msg.created_at.strftime('%d/%m/%Y')
                        db.upsertMessageCount(date_str, msg.author.id, channel.id)
                        loaded_messages.add(unique_key)
                logger.info(f"Messages loaded successfully from channel: {channel.name}")
            except Exception as e:
                logger.error(f"Error loading messages from channel {channel.name}: {e}")
                await message.channel.send("Failed to load messages from past two months.")
                return

    logger.info(f"Completed loading messages from server: {message.guild.name}")
    await message.channel.send('Messages from the last two months have been loaded!')

async def stats(message):
    logger.info(f"Fetching stats for server: {message.guild.name}")

    async with message.channel.typing():
        try:
            stats = getMonthStats()
            logger.debug("Successufully retrieved stats")
        except Exception as e:
            logger.error(f"Error retrieving stats: {e}")
            await message.channel.send("Failed to retrieve stats.")
            return

    # Round growth
    growth = round(stats['growth'])

    # Use mentions
    top_user_current = f"<@{stats['top_user_current']}>" if stats['top_user_current'] else "Unkown"
    top_user_previous = f"<@{stats['top_user_previous']}>" if stats['top_user_previous'] else "Unkown"

    # Get channel link
    guild = message.guild
    top_channel_current = f"<#{stats['top_channel_current']}>" if stats['top_channel_current'] else "Unkown"
    top_channel_previous = f"<#{stats['top_channel_previous']}>" if stats['top_channel_previous'] else "Unkown"

    response = (
        f"**Monthly Stats:**\n"
        f"Messages this month: {stats['current_total']}\n"
        f"Messages last month: {stats['previous_total']}\n"
        f"Growth: {growth}%\n\n"
        f"**Top User This Month:** {top_user_current} with {stats['user_current_count']} messages\n"
        f"**Top Channel This Month:** {top_channel_current} with {stats['channel_current_count']} messages\n\n"
        f"**Top User Last Month:** {top_user_previous} with {stats['user_previous_count']} messages\n"
        f"**Top Channel Last Month:** {top_channel_previous} with {stats['channel_previous_count']} messages"
    )

    logger.info("Stats successfully sent.")
    await message.channel.send(response)

async def help(message):
    await message.channel.send("You can visit commands here: https://github.com/daniellages/StatusBot")