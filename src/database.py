import os
import sqlite3
from dotenv import load_dotenv
from datetime import datetime
from logger import logger

# Variables
load_dotenv()
database_path = os.getenv('DB_PATH')

def resetData(table):
    # Connect database
    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()

    try:
        sql = f"DELETE FROM {table}"
        cursor.execute(sql)
        connection.commit()
        logger.info(f"Table {table} has been successfully reset!")
    except Exception as e:
        logger.error(f"Error resetting {table}: {e}")
        raise
    finally:
        connection.close()

# Upsert Message function -> Update or Insert
def upsertMessageCount(date, user_id, channel_id):  # count is automatic
    # Connect database
    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()

    try:
        # Check if entry exists
        cursor.execute("SELECT count FROM messages WHERE date = ? and user_id = ? AND channel_id = ?",
                       (date, user_id, channel_id))
        result = cursor.fetchone()

        if result:
            # Update count if entry exists
            current_count = result[0]
            cursor.execute("UPDATE messages SET count = ? WHERE date = ? AND user_id = ? AND channel_id = ?",
                           (current_count + 1, date, user_id, channel_id))
        else:
            # Inser new entry if entry doesn't exist
            cursor.execute("INSERT INTO messages (date, user_id, channel_id, count) VALUES (?, ?, ?, ?)",
                           (date, user_id, channel_id, 1))
        
        # Execute commands in database
        connection.commit()
        logger.info(f"Message count upserted for user {user_id} in channel {channel_id} on {date}.")
    except Exception as e:
        logger.error(f"Error upserting message count: {e}")
    finally:
        # Close database
        connection.close()

# Get messages during a time range
def getMessagesDuring(start_date, end_date):
    # Connect database
    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    try:
        cursor.execute("SELECT * FROM messages WHERE date BETWEEN ? AND ?",
                       (start_date, end_date))
        messages = cursor.fetchall()
        logger.info(f"Retrieved {len(messages)} messages between {start_date} and {end_date}.")
        return [dict(message) for message in messages]
    except Exception as e:
        logger.error(f"Error retrieving messages: {e}")
        return []
    finally:
        # Close database
        connection.close()

# Upsert voice function
def upsertVoiceState(user_id, channel_id, joined_at=None, left_at=None):
    # Connect database
    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()

    try:
        if left_at:
            # Update the left_at time for the user in the specified channel
            cursor.execute("UPDATE voices SET left_at = ? WHERE user_id = ? AND channel_id = ? AND left_at IS NULL",
                           (left_at, user_id, channel_id))
            logger.info(f"Updated left_at for user {user_id} in channel {channel_id} at {left_at}.")
        
        elif joined_at:
            # Insert a new entry for the user's voice state
            cursor.execute("INSERT INTO voices (user_id, channel_id, joined_at, left_at) VALUES (?, ?, ?, ?)",
                           (user_id, channel_id, joined_at, None))
            logger.info(f"Added new voice state for user {user_id} in channel {channel_id} at {joined_at}.")

        # Execute commands in database
        connection.commit()
    except Exception as e:
        logger.error(f"Error upserting voice state: {e}")
    finally:
        # Close database
        connection.close()

# Get voices during a time range
def getVoicesDuring(start_date, end_date):
    # Connect database
    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    try:
        cursor.execute("SELECT * FROM voices WHERE joined_at BETWEEN ? AND ?",
                       (start_date, end_date))
        voices = cursor.fetchall()
        logger.info(f"Retrieved {len(voices)} voice states between {start_date} and {end_date}.")
        return [dict(voice) for voice in voices]
    except Exception as e:
        logger.error(f"Error retrieving voice state: {e}")
        return []
    finally:
        # Close database
        connection.close()