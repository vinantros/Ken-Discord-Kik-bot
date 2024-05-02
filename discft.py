import discord
import os
import sqlite3
from discord.ext import commands
import asyncio
import redis
import json
from concurrent.futures import ThreadPoolExecutor

# set up Discord bot intents
intents = discord.Intents.default()
intents.message_content = True


# define custom Discord bot class
class SpiralBot(discord.Client):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__class__._instance = self
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
        self.executor = ThreadPoolExecutor(max_workers=2)


    async def on_ready(self):
        print(f'Logged on as {self.user}!')
        self.loop.create_task(self.redis_subscriber())
        

    async def on_message(self, message):

        print(f"Message received: {message.content}")
     
        if message.author == self.user:
            return
        print(message.content)
        
        if message.channel.id == 1091389971715342409:  # Replace with your specific channel ID
            print(f"Captured message: {message.content} from {message.author.name}")
            message_data = {
                "content": message.content,
                "sender": message.author.name  # or any other sender identifier you prefer
            }
            message_to_send = json.dumps(message_data)  # Convert the dictionary to a JSON string
            self.redis_client.publish('discord_to_kik_channel', message_to_send)  # Use a different Redis channel for Discord to Kik
        
    async def redis_subscriber(self):
        pubsub = self.redis_client.pubsub()
        pubsub.subscribe('discord_channel')
        print("Subscribed to Redis channel 'discord_channel'")
        
        while True:
            message = await self.loop.run_in_executor(self.executor, pubsub.get_message, True, 1.0)
            if message and message['type'] == 'message':
                channel = bot.get_channel(1091389971715342409)  # Replace with your channel ID
                message_data = json.loads(message['data'].decode())  # Decode and load JSON data
                message_content = message_data['content']
                message_sender = message_data['sender']
                formatted_message = f"{message_sender}: {message_content}"  # Format the message as you like
                await channel.send(formatted_message)

            
bot = SpiralBot(intents=intents)
bot.run("discord bot token")