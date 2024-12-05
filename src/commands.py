from datetime import datetime, timedelta
import database as db
from stats import getMonthStats
from logger import logger

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
                        date_str = msg.created_at.strftime('%Y-%m-%d')
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
    growth = stats['growth']

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

# Voice
async def voiceStateUpdate(member, before, after):
    now = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    user_id = member.id

    # User joins voice channel
    if before.channel is None and after.channel is not None:
        channel_id = after.channel.id
        joined_at = now
        db.upsertVoiceState(user_id, channel_id, joined_at=joined_at)
        logger.info(f"User {member} joined voice channel {after.channel.name}.")
    
    # User changes voice channel
    elif before.channel is not None and after.channel is not None:
        # Update old entry
        old_channel_id = before.channel.id
        left_at = now
        db.upsertVoiceState(user_id, old_channel_id, left_at=left_at)
        
        # Insert new entry
        new_channel_id = after.channel.id
        joined_at = now
        db.upsertVoiceState(user_id, new_channel_id, joined_at=joined_at)
        logger.info(f"User {member} changed voice channel from {before.channel.name} to {after.channel.name}.")

    # User leaves voice channel
    elif before.channel is not None and after.channel is None:
        channel_id = before.channel.id
        left_at = now
        db.upsertVoiceState(user_id, channel_id, left_at=left_at)
        logger.info(f"User {member} left voice channel {before.channel.name}.")

# Clear all data from messages table
async def resetMessagesTable(message):
    async with message.channel.typing():
        try:
            db.resetData('messages')
            await message.channel.send(f"The 'messages' table has been successfully reset!")
        except:
            await message.channel.send(f"An error occurred while resetting the 'messages' table.")

# Clear all data from voices table
async def resetVoicesTable(message):
    if message.author.id == 236169317706629130:
        async with message.channel.typing():
            try:
                db.resetData('voices')
                await message.channel.send(f"The 'voices' table has been successfully reset!")
            except:
                await message.channel.send(f"An error occurred while resetting the 'voices' table.")
    else:
        await message.channel.send("You don't have permission for that.")