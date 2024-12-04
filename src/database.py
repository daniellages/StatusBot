import csv
from datetime import datetime
from logger import logger

# Variables
messages_path = '../tables/messages.csv'

# Read all data from csv
def readData():
    try:
        with open(messages_path, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            return list(reader)
    except FileNotFoundError:   
        logger.warning("Messages CSV file not found.")    
        return []  # If file doesn't exist, return empty list

# Write data to csv
def writeData(messages):
    try:
        with open(messages_path, mode='w', newline='', encoding='utf-8') as file:
            fieldnames = ['date', 'user_id', 'channel_id', 'count']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(messages)
    except Exception as e:
        logger.error(f"Error writing to CSV file: {e}")

# Upsert Message function -> Update or Insert
def upsertMessageCount(date, user_id, channel_id):  # count is automatic
    # Read existing messages
    messages = readData()

    # Check if message entry exists
    entry_found = False
    for message in messages:
        if message['date'] == date and message['user_id'] == str(user_id) and message['channel_id'] == str(channel_id):
            # If entry exists, increment count
            message['count'] = str(int(message['count']) + 1)
            entry_found = True
            break
    
    if not entry_found:
        # If entry doesn't exist, create new message
        new_message = {
            'date': date,
            'user_id': str(user_id),
            'channel_id': str(channel_id),
            'count': '1'  # Starting point for count
        }
        messages.append(new_message)
    
    # Update data
    writeData(messages)

# Get messages during a time range
def getMessagesDuring(start_date, end_date):
    # Read existing messages
    messages = readData()

    # Ensure datetime type dd/mm/YYYY
    start_date = datetime.strptime(start_date, '%d/%m/%Y')
    end_date = datetime.strptime(end_date, '%d/%m/%Y')

    # Get the messages that are in the range
    filtered_messages = []
    for message in messages:
        message_date = datetime.strptime(message['date'], '%d/%m/%Y')
        if start_date <= message_date <= end_date:
            filtered_messages.append(message)
 
    return filtered_messages