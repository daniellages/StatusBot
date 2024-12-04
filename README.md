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

## Commands

### - `record this message`
It forcefully load the message to the messages table

### - `get messages`
Loads every messsage and displays only the total count

### - `load messages`
Loads every messages from the past 2 months to the messages table, this may take a while

### - `get stats`
Get current month stats compared with the previous month

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

## Notes
- **CSV File is temporary:** a database will be used in the future
- **Date Format:** should always be converted to `dd/mm/YYYY` for consistency

## Author

* **Daniel Lages** - [daniellages](https://github.com/daniellages)