# bot.py
import os

import discord
from dotenv import load_dotenv

import requests

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.Client(intents=discord.Intents.default())
SERVER_CHECK_URL = 'https://mcstatus.io/status/java/108.49.248.157:25565'

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    channel = discord.utils.get(client.get_all_channels(), name='bot-stuff')
    
    view = discord.ui.View()
    test_button = discord.ui.Button(label='Status', custom_id='status-id', style=discord.ButtonStyle.blurple)
    test_button.callback = on_status_button
    view.add_item(test_button)
    await channel.send("Server Status Bot", view=view)


async def on_status_button(interaction : discord.Interaction):
    status_string : str = pull_status()
    emoji = ''
    # channel = discord.utils.get(client.get_all_channels(), name='bot-stuff')
    if status_string == 'Online':
        emoji = ':white_check_mark: '
    else:
        emoji = ':octagonal_sign: '
    await interaction.response.edit_message(content='Server Status Bot\nThe server is currently: ' + emoji + status_string)

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
        
def pull_status():
    pull = requests.get(SERVER_CHECK_URL)
    text = pull.text
    from_status = text[text.index('Status</span>'):text.index('Status</span>') + 200:]
    first_bracket = from_status[from_status.index('>')+1::]
    second_bracket = first_bracket[first_bracket.index('>')+1::]
    third_bracket = second_bracket[second_bracket.index('>')+1::]
    final_string = third_bracket[:third_bracket.index('<'):]
    #print(from_status)
    return final_string
    
    

client.run(TOKEN)