# Kik and Discord Integration Bot

This project integrates a Kik bot with Discord using Redis to facilitate message passing between the two platforms. The Kik bot can respond to messages directly on Kik or relay messages from a Discord channel to Kik and vice versa.

## Prerequisites

Before you start, make sure you have the following installed:
- Python 3.8 or higher
- Redis server

You will also need:
- Kik account credentials (username and password)
- Discord bot token
- OpenAI API key

## Setup

1. **Clone the repository:**
   Ensure you have a copy of the source code on your local machine.

2. **Install dependencies:**
   Install the required Python libraries by running:
```
bash pip install -r requirements.txt
```

   Install the Kik API library:
```
git clone -b new https://github.com/tomer8007/kik-bot-api-unofficial
pip3 install ./kik-bot-api-unofficial
```


4. **Configure the environment:**
   Set up the necessary environment variables or update the configuration directly in the scripts:
   - Kik username and password in `main.py`
   - OpenAI API key in `main.py`
   - Discord bot token in `discft.py`

## Running the Project

1. **Start the Redis Server:**
   Open a terminal and run:
bash redis-server

   This will start the Redis server which is used for message passing between the Discord bot and the Kik bot.

2. **Run the Kik Bot:**
   Open another terminal and execute:
bash python main.py

   This script starts the Kik bot. It will attempt to log in using the credentials provided.

3. **Run the Discord Bot:**
   Open a third terminal and execute:
bash python discft.py

   This script starts the Discord bot, which listens for messages in a specified channel and forwards them to Kik via Redis.

## Handling Captcha During Login

The Kik bot may occasionally require a captcha to be solved during the login process. If this happens, follow these steps:

1. **Inspect the Captcha:**
   When running `main.py`, if a captcha is required, the script will pause, and you will need to manually solve the captcha.
   
2. **Open Developer Tools in the Browser:**
   Press `F12` to open the developer tools where the captcha challenge is displayed.

3. **Solve the Captcha and Copy the Response:**
   Complete the captcha challenge in the browser. Then copy the response into the terminal where the script is running.

## Notes

- Ensure that the Redis server is running before starting the bots as they depend on Redis for message passing.
- The bots must be running simultaneously for the message relay functionality to work correctly between Kik and Discord.

## Troubleshooting

- **Redis Connection Issues:** Ensure that the Redis server is started and listening on the default port (6379).
- **Dependency Errors:** Make sure all dependencies are installed correctly `requirements.txt` file.
- **Captcha Not Loading:** Check your internet connection and browser settings if the captcha does not load in the developer tools.
- **Not Taking the Captcha:** Login again on kik or make a new account if banned from constant 'Responses'.
