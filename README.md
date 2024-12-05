# Statify

**Statify** is a Discord bot that has management functions to display stats and curiosities.

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
DB_PATH=path_to_databases_folder
```

### 5. Run the Bot
```bash
cd src
python main.py
```

## Commands

### - `load messages`
Loads every messages from the past 2 months to the messages table, this may take a while

### - `get stats`
Get current month stats compared with the previous month

### - `help`
Get link to this repository, inception

## Events

### - User joins channel
Creates new entry in voices table with empty left_at value

### - User leaves channel
Updates entry in voices table with the correct left_at value

## Structure of database tables
- `messages`
    - `date`: The date the message was sent, `YYYY-MM-DD` format.
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

- `voices`
    - `user_id`: The Discord user ID of the author.
    - `channel_id`: The Discord channel ID where the message was sent.
    - `joined_at`: The datetime that the user joined the voice channel, `YYYY-MM-DD HH:MM:SS` format.
    - `left_at`: The datetime that the user left the voice channel, `YYYY-MM-DD HH:MM:SS` format.

**Example:**
```csv
user_id, channel_id, joined_at, left_at
```

## Logging System
The Statify bot includes a comprehensive logging system to track events, errors and general activity

## Notes
- **Date Format:** should always be converted to `YYYY-MM-DD` (ISO 8601)

## Author

* **Daniel Lages** - [daniellages](https://github.com/daniellages)