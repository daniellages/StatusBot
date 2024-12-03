# StatusBot

**StatusBot** is a Discord bot that has management functions to display stats and curiosities.

## Setup

### 1. Clone the Repository
```bash
git clone https://github.com/daniellages/StatusBot
cd StatusBot
```

### 2. Setup Virtual Environment

- **On Windows**
```bash
python -m venv venv
.\venv\bin\activate
```

- **On macOS/Linux**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
python -m pip install -r requirements.txt
```

### 4. Setup `.env` File
Create the `.env` file in the root of the project.
```makefile
TOKEN=discord_bot_token_here
```

### 5. Run the Bot
```bash
cd src
python main.py
```

## Structure of database tables
- `messages`
    - `date`: The date the message was sent, `dd/mm/YYYY` format.
    - `user_id`: The Discord user ID of the author.
    - `channel_id`: The Discord channel ID where the message was sent.
    - `count`: The number of messages sent by `user_id` in a specific `channel_id` and `date`

**Example:**
```csv
date,user_id,channel_id,count
03/12/2024,236169317706629130,1312483397851021493,6
03/12/2024,236169317706629130,747480205299286087,1
03/12/2024,236169317706629130,864440262939115531,1
```

## Functions

### 1. `upsertMessageCount(date, user_id, channel_id)`

This function updates or inserts the message count for a specific `date`, `user_id` and `channel_id`
- If an entry already exists: Increment the counter
- If no entry exists: Create a new entry with counter starting at 1

### 2. `getMessagesDuring(start_date, end_date)`

This function retrieves all messages that were recorded durint the specified date range
- Returns: A list of dictionaries containing the message data withing the specified date range

## Notes
- **CSV File is temporary:** a database will be used in the future
- **Date Format:** should always be converted to `dd/mm/YYYY` for consistency

## Author

* **Daniel Lages** - [daniellages](https://github.com/daniellages)