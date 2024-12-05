import discord
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
    top_messages_user_current = f"<@{stats['top_messages_users_current'][0]['user_id']}>" if stats['top_messages_users_current'] else "Unkown"
    top_messages_user_previous = f"<@{stats['top_messages_users_previous'][0]['user_id']}>" if stats['top_messages_users_previous'] else "Unkown"

    # Get channel link
    top_messages_channel_current = f"<#{stats['top_messages_channels_current'][0]['channel_id']}>" if stats['top_messages_channels_current'] else "Unkown"
    top_messages_channel_previous = f"<#{stats['top_messages_channels_previous'][0]['channel_id']}>" if stats['top_messages_channels_previous'] else "Unkown"

    # Create embed
    embed = discord.Embed(
        title="📊 Server Monthly Stats",
        description="Here are the stats for this month compared with last month!",
        color=discord.Color.blurple(),
        timestamp=discord.utils.utcnow())
    
    # Message Activity
    embed.add_field(
        name="📩 **Message Activity (This month)**",
        value=(f"**Messages:** {stats['current_total']}\n"
               f"**Top User:** {top_messages_user_current} ({stats['top_messages_users_current'][0]['count']} messages)\n"
               f"**Top Channel:** {top_messages_channel_current} ({stats['top_messages_channels_current'][0]['count']} messages)"),
        inline=False)
    embed.add_field(
        name="📩 **Message Activity (Last Month)**",
        value=(f"**Messages:** {stats['previous_total']}\n"
               f"**Top User:** {top_messages_user_previous} ({stats['top_messages_users_previous'][0]['count']} messages)\n"
               f"**Top Channel:** {top_messages_channel_previous} ({stats['top_messages_channels_previous'][0]['count']} messages)"),
        inline=False)
    embed.add_field(
        name="📈 Growth",
        value=f"{growth}%",
        inline=False)
    
    ranking_messages_str = ""
    for idx, user in enumerate(stats['top_messages_users_current']):
        user_mention = f"<@{user['user_id']}>"
        count = user['count']
        rank_emoji = "🥇" if idx == 0 else "🥈" if idx == 1 else "🥉" if idx == 2 else "🔝"

        ranking_messages_str += f"{rank_emoji} **{idx + 1}.** {user_mention} - {count} messages\n"

    embed.add_field(
        name="🏆 Top Message Users, this month",
        value=ranking_messages_str,
        inline=False)

    # Voice Activity
    embed.add_field(
        name="🎙️ **Voice Activity (This Month)**",
        value=(f"**Top User:** <@{stats['top_voices_users_current'][0]['user_id']}>"
               f"({int(stats['top_voices_users_current'][0]['duration']) / 60} minutes)"
               if stats['top_voices_users_current'] else "No data available."),
        inline=False)
    embed.add_field(
        name="🎙️ **Voice Activity (Last Month)**",
        value=(f"**Top User:** <@{stats['top_voices_users_previous'][0]['user_id']}> "
               f"({int(stats['top_voices_users_previous'][0]['duration']) / 60} minutes)"
               if stats['top_voices_users_previous'] else "No data available."),
        inline=False)

    voice_data = db.getVoicesDuring(stats['previous_start_str'], stats['current_end_str'])
    ranking_voices_str = ""
    for idx, user in enumerate(stats['top_voices_users_current']):
        user_mention = f"<@{user['user_id']}>"
        total_minutes = getTotalMinutes(user['user_id'], voice_data)
        rank_emoji = "🥇" if idx == 0 else "🥈" if idx == 1 else "🥉" if idx == 2 else "🔝"

        ranking_voices_str += f"{rank_emoji} **{idx + 1}.** {user_mention} - {total_minutes} minutes\n"

    embed.add_field(
        name="🗣️ Top Voice Users, this month",
        value=ranking_voices_str,
        inline=False)

    if message.guild.icon:
        embed.set_thumbnail(url=message.guild.icon.url)
    embed.set_footer(text="Created by tedisntfat")

    logger.info("Stats successfully sent.")
    await message.channel.send(embed=embed)

async def help(message):
    await message.channel.send("You can visit commands here: https://github.com/daniellages/StatusBot")

# Voice
async def voiceStateUpdate(member, before, after):
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    user_id = member.id

    # Ignore events where the user only changes mute, deaf, or similar states
    if before.channel == after.channel:
        return

    # User joins voice channel
    if before.channel is None and after.channel is not None:
        channel_id = after.channel.id
        db.upsertVoiceState(user_id, channel_id, joined_at=now)
        logger.info(f"User {member} joined voice channel {after.channel.name}.")
    
    # User changes voice channel
    elif before.channel is not None and after.channel is not None:
        # Update old entry
        db.upsertVoiceState(user_id, before.channel.id, left_at=now)
        # Insert new entry
        db.upsertVoiceState(user_id, after.channel.id, joined_at=now)
        logger.info(f"User {member} changed voice channel from {before.channel.name} to {after.channel.name}.")

    # User leaves voice channel
    elif before.channel is not None and after.channel is None:
        db.upsertVoiceState(user_id, before.channel.id, left_at=now)
        logger.info(f"User {member} left voice channel {before.channel.name}.")

# Clear all data from messages table
async def resetMessagesTable(message):
    if message.author.id == 236169317706629130:
        async with message.channel.typing():
            try:
                db.resetData('messages')
                await message.channel.send(f"The 'messages' table has been successfully reset!")
            except:
                await message.channel.send(f"An error occurred while resetting the 'messages' table.")
    else:
        await message.channel.send("You don't have permission for that.")

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

# Calculate the total minutes spent in voice sessons for a specific user
def getTotalMinutes(user_id, voice_data):
    total_seconds = 0

    for entry in voice_data:
        if entry['user_id'] == user_id:
            joined_at = datetime.strptime(entry['joined_at'], '%Y-%m-%d %H:%M:%S')
            left_at = datetime.strptime(entry['left_at'], '%Y-%m-%d %H:%M:%S') if entry['left_at'] else datetime.now()
            session_duration = (left_at - joined_at).total_seconds()
            total_seconds += session_duration
    
    # Convert total seconds to minutes
    total_minutes = total_seconds / 60
    return round(total_minutes, 2)
