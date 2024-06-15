# bot.py
import os

import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.Client(intents=discord.Intents.default())
server = None

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')


async def on_status_button(interaction : discord.Interaction):
    status_string : str = await pull_status()
    channel = discord.utils.get(client.get_all_channels(), name='bot-stuff')
    print (str(channel))

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if str(message.channel) == 'bot-stuff':
        print("BEEP BOOP MESSAGE DETECTED")
        view = discord.ui.View()
        test_button = discord.ui.Button(label='Status', custom_id='status-id', style=discord.ButtonStyle.blurple)
        test_button.callback = on_status_button
        view.add_item(test_button)
        await message.channel.send("TEST BUTTON", view=view)
        
async def pull_status():
    pass
    

client.run(TOKEN)