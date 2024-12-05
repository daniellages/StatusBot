from datetime import datetime, timedelta
import database as db
import calendar

def getMonthStats():
    # Define dates for both months
    today = datetime.now()
    current_month_start = today.replace(day=1)
    _, last_day_current_month = calendar.monthrange(today.year, today.month)
    current_month_end = today.replace(day=last_day_current_month)
    previous_month_end = current_month_start - timedelta(days=1)
    previous_month_start = previous_month_end.replace(day=1)

    # Format dates to strings
    current_start_str = current_month_start.strftime('%Y-%m-%d')
    current_end_str = current_month_end.strftime('%Y-%m-%d')
    previous_start_str = previous_month_start.strftime('%Y-%m-%d')
    previous_end_str = previous_month_end.strftime('%Y-%m-%d')

    # Get messages from both months
    current_month_messages = db.getMessagesDuring(current_start_str, current_end_str)
    previous_month_messages = db.getMessagesDuring(previous_start_str, previous_end_str)
    current_month_voices = db.getVoicesDuring(current_start_str, current_end_str)
    previous_month_voices = db.getVoicesDuring(previous_start_str, previous_end_str)

    # Count messages
    current_messages_total = int(len(current_month_messages))
    previous_messages_total = int(len(previous_month_messages))

    # Percentage
    if previous_messages_total == 0:
        growth = "infinite" if current_messages_total > 0 else "0"
    else:
        growth = round(((current_messages_total - previous_messages_total) / previous_messages_total) * 100, 2)
    
    # Helper function
    def calculateTopStats(data, key, duration=False, top_n = 5):
        stats = {}

        for entry in data:
            identifier = entry[key]
            # Calculate voice duration
            if duration:
                joined_at = datetime.strptime(entry['joined_at'], '%Y-%m-%d %H:%M:%S')
                left_at = datetime.strptime(entry['left_at'], '%Y-%m-%d %H:%M:%S') if entry['left_at'] else today
                time_spent = (left_at - joined_at).total_seconds()
                stats[identifier] = stats.get(identifier, 0) + time_spent
            # Count occorrences for messages
            else:
                stats[identifier] = stats.get(identifier, 0) + int(entry['count'])
        
        # Sort and return the top N items
        return sorted(stats.items(), key=lambda x: x[1], reverse=True)[:top_n]

    # Calculate message stats
    top_messages_users_current = calculateTopStats(current_month_messages, key='user_id')
    top_messages_channels_current = calculateTopStats(current_month_messages, key='channel_id')
    top_messages_users_previous = calculateTopStats(previous_month_messages, key='user_id')
    top_messages_channels_previous = calculateTopStats(previous_month_messages, key='channel_id')

    # Calculate voice stats
    top_voices_users_current = calculateTopStats(current_month_voices, key='user_id', duration=True)
    top_voices_channels_current = calculateTopStats(current_month_voices, key='channel_id', duration=True)
    top_voices_users_previous = calculateTopStats(previous_month_voices, key='user_id', duration=True)
    top_voices_channels_previous = calculateTopStats(previous_month_voices, key='channel_id', duration=True)

    # Format stats
    stats = {
        "previous_start_str": previous_start_str,
        "current_end_str": current_end_str,
        "current_total": current_messages_total,
        "previous_total": previous_messages_total,
        "growth": growth,
        "top_messages_users_current": [{"user_id": user_id, "count": count} for user_id, count in top_messages_users_current],
        "top_messages_channels_current": [{"channel_id": channel_id, "count": count} for channel_id, count in top_messages_channels_current],
        "top_messages_users_previous": [{"user_id": user_id, "count": count} for user_id, count in top_messages_users_previous],
        "top_messages_channels_previous": [{"channel_id": channel_id, "count": count} for channel_id, count in top_messages_channels_previous],
        "top_voices_users_current": [{"user_id": user_id, "duration": round(duration, 2)} for user_id, duration in top_voices_users_current],
        "top_voices_channels_current": [{"channel_id": channel_id, "duration": round(duration, 2)} for channel_id, duration in top_voices_channels_current],
        "top_voices_users_previous": [{"user_id": user_id, "duration": round(duration, 2)} for user_id, duration in top_voices_users_previous],
        "top_voices_channels_previous": [{"channel_id": channel_id, "duration": round(duration, 2)} for channel_id, duration in top_voices_channels_previous],
    }

    return stats