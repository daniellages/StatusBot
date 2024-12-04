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
    current_start_str = current_month_start.strftime('%d/%m/%Y')
    current_end_str = current_month_end.strftime('%d/%m/%Y')
    previous_start_str = previous_month_start.strftime('%d/%m/%Y')
    previous_end_str = previous_month_end.strftime('%d/%m/%Y')

    # Get messages from both months
    current_month_messages = db.getMessagesDuring(current_start_str, current_end_str)
    previous_month_messages = db.getMessagesDuring(previous_start_str, previous_end_str)

    # Count messages
    current_total = len(current_month_messages)
    previous_total = len(previous_month_messages)

    # Percentage
    if previous_total == 0:
        growth = "infinite" if current_total > 0 else "0"
    else:
        growth = ((current_total - previous_total) / previous_total) * 100
    
    def getTopStats(messages):
        user_stats = {}
        channel_stats = {}

        for msg in messages:
            user_id = msg['user_id']
            channel_id = msg['channel_id']

            user_stats[user_id] = user_stats.get(user_id, 0) + int(msg['count'])
            channel_stats[channel_id] = channel_stats.get(channel_id, 0) + int(msg['count'])
        
        top_user = max(user_stats, key=user_stats.get, default=None)
        top_channel = max(channel_stats, key=channel_stats.get, default=None)

        return top_user, user_stats.get(top_user, 0), top_channel, channel_stats.get(top_channel, 0)

    top_user_current, user_current_count, top_channel_current, channel_current_count = getTopStats(current_month_messages)
    top_user_previous, user_previous_count, top_channel_previous, channel_previous_count = getTopStats(previous_month_messages)

    # Format stats
    stats = {
        "current_total": current_total,
        "previous_total": previous_total,
        "growth": growth,
        "top_user_current": top_user_current,
        "user_current_count": user_current_count,
        "top_channel_current": top_channel_current,
        "channel_current_count": channel_current_count,
        "top_user_previous": top_user_previous,
        "user_previous_count": user_previous_count,
        "top_channel_previous": top_channel_previous,
        "channel_previous_count": channel_previous_count,
    }

    return stats