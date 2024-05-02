from kik_unofficial.client import KikClient
from kik_unofficial.callbacks import KikClientCallback
import kik_unofficial.datatypes.xmpp.chatting as chatting
from kik_unofficial.datatypes.xmpp.errors import LoginError
from kik_unofficial.datatypes.xmpp.roster import FetchRosterResponse
from openai import OpenAI
from threading import Lock
from kik_unofficial.datatypes.xmpp.roster import FetchRosterResponse, PeersInfoResponse
import redis
import json
import asyncio


# Your kik login credentials (username and password)
username = "kik username"
password = "kik password"
openaikey = "openai key"
friends = {}


client = OpenAI(
    
    api_key="openai key here just in case",
)

#calls redis client started from your terminal
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# This bot class handles all the callbacks from the kik client
class EchoBot(KikClientCallback):
    message_counter_lock = Lock()
    message_counter = 0
    debate_mode = False
    global users
    users = {}
    def __init__(self):
        super().__init__()
        self.client = KikClient(self, username, password)
        self.discord_mode_active = False
        self.loop = asyncio.get_event_loop()
        self.loop.create_task(self.discord_to_kik_subscriber())
        self.client.wait_for_messages()
    # This method is called when the bot is fully logged in and setup
    def on_authenticated(self):
        self.client.request_roster() # request list of chat partners
        
        
    def chatbot(self, input, messages, firstName):
        if input:
            formatted_input = f"{firstName} has said: {input}"  # Format the input with the user's first name
            print(f"Sending message to chatbot: {formatted_input}")
            messages.append({"role": "user", "content": formatted_input})
            chat = client.chat.completions.create(
                model="gpt-3.5-turbo", messages=messages
            )
            reply = chat.choices[0].message.content
            messages.append({"role": "assistant", "content": reply})
            return reply
        
    def chatbot_debate(self, input_text):
        try:
            messages = [
                {"role": "system", "content": "Your name is ken"},
                {"role": "user", "content": input_text}
            ]
            # Define a prompt that instructs the AI to use specific phrases
        
            chat = client.chat.completions.create(
                model="gpt-3.5-turbo", messages=messages
            )
            reply = chat.choices[0].message.content
            return reply
        except Exception as e:
            print(f"An error occurred while processing the message: {e}")
            return None
        

        

    # This method is called when the bot receives a direct message (chat message)
    def on_chat_message_received(self, chat_message: chatting.IncomingChatMessage):
        
        def jid_to_username(jid):
            print(jid)
            return jid.split("@")[0][:-4]
    
        TheirUsername = jid_to_username(chat_message.from_jid)
        
        print(self.client.request_info_of_users(TheirUsername))
              
        print(chat_message.body)
        messages = [
            {"role": "system", "content": "You are a bot programmed by a python script in a group chat on kik."},
        ]
        
        reply = self.chatbot(chat_message.body, messages, TheirUsername)
        self.client.send_chat_message(chat_message.from_jid, reply)
        
    
    # This method is called when the bot receives a chat message in a group
    
    def on_peer_info_received(self, response: PeersInfoResponse):
                users[response.users[0].jid] = response.users[0]
                
    def on_group_message_received(self, chat_message: chatting.IncomingGroupChatMessage):
        print(chat_message.body)
        global sender_identifier
        sender_identifier = chat_message.group_jid  # Adjust as needed for your use case
        

        def query_user(jid):
            if jid in users:
                return users[jid]
            else:
                self.client.request_info_of_users(jid)
                while jid not in users:
                    pass
                return users[jid]

        def jid_to_group_display_name(jid):
            return query_user(jid).display_name
        
        def remove_last_name(full_name):
            # Split the name by spaces
            parts = full_name.split()
            
            # Check if the name has more than one part
            if len(parts) > 1:
                # Join all parts except the last one
                return ' '.join(parts[:-1])
            else:
                # If there's only one part, return it as is
                return full_name

        
        theirFullDisplayName = jid_to_group_display_name(chat_message.from_jid)
        global firstName
        firstName = remove_last_name(theirFullDisplayName)
        
        
    
            
        messages = [
            {"role": "system", "content": "You are a bot programmed by a python script in a group chat on kik. You are named Ken and the # is #PsychologyAndPhilosphy. The creator of this bot is Saul. You sometimes like to tease and troll back in a rude way but about 50 percent of the time. You do not mention openai or anything AT ALL. It's forbidden that you are created by them, only by Saul. You are not friendly, you are sarcastic but clever"},
        ]
        with self.message_counter_lock:  # Use the lock when accessing the message counter
            self.message_counter += 1  # Increment the counter each time a message is received
        if "Ken" in chat_message.body:
            reply = self.chatbot(chat_message.body, messages, firstName)
            self.client.send_chat_message(chat_message.group_jid, reply)
            self.message_counter = 0  # Reset the counter if "Ken" is in the message
        elif self.message_counter == 10:  # If this is the 10th message and "Ken" is not in it, respond and reset the counter
            reply = self.chatbot(chat_message.body, messages, firstName)
            self.client.send_chat_message(chat_message.group_jid, reply)
            self.message_counter = 0
            
            
            
        if "/discord" in chat_message.body:
            self.discord_mode_active = True
            print("Discord mode set to True")
            self.client.send_chat_message(chat_message.group_jid, "Discord channel activated. Messages will now be sent to Discord.")
            return
        elif "/discordoff" in chat_message.body:
            self.discord_mode_active = False
            print("Discord mode set to False")
            self.client.send_chat_message(chat_message.group_jid, "Discord channel deactivated.")
            return
        if self.discord_mode_active:
            print("Publishing message to Redis")
            # If Discord mode is active, publish messages to Redis
            message_data = {
                "content": chat_message.body,
                "sender": theirFullDisplayName
            }
            message_to_send = json.dumps(message_data)
            redis_client.publish('discord_channel', message_to_send)
        
            
            
        if "debate mode on" in chat_message.body.lower():
            self.debate_mode = True
            self.client.send_chat_message(chat_message.group_jid, "Debate mode is now on.")
            return
        elif "debate mode off" in chat_message.body.lower():
            self.debate_mode = False
            self.client.send_chat_message(chat_message.group_jid, "Debate mode is now off.")
            return

        if self.debate_mode:
            potential_reply = self.chatbot_debate(chat_message.body)
            if potential_reply:
                # Check if the response contains the specific phrases
                if 'bias detected:' in potential_reply.lower() or 'misinformation detected:' in potential_reply.lower():
                    # Send the explanation provided by the AI
                    self.client.send_chat_message(chat_message.group_jid, potential_reply)
                
    async def discord_to_kik_subscriber(self):
        pubsub = redis_client.pubsub()
        pubsub.subscribe('discord_to_kik_channel')
        print("Subscribed to Redis channel 'discord_to_kik_channel'")
        
        while True:
            message = pubsub.get_message()
            if message and message['type'] == 'message' and self.discord_mode_active:
                message_data = json.loads(message['data'].decode())  # Decode and load JSON data
                message_content = message_data['content']
                message_sender = message_data['sender']
                reply = f"{message_sender}: {message_content}"
                
                kik_group_jid = sender_identifier  # Use the sender_identifier to get the JID
            
                if kik_group_jid:
                    reply = f"{message_sender}: {message_content}"
                    self.client.send_chat_message(kik_group_jid, reply)
                else:
                    print(f"No active group JID found for sender: {message_sender}")
                
            await asyncio.sleep(1)
        
    # This method is called if a captcha is required to login
    def on_login_error(self, login_error: LoginError):
        if login_error.is_captcha():
            login_error.solve_captcha_wizard(self.client)


if __name__ == '__main__':
    # Creates the bot and start listening for incoming chat messages
    callback = EchoBot()