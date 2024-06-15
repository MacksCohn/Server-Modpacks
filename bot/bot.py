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
    
    await channel.purge()
    await send_prompt(channel)


async def on_status_button(interaction : discord.Interaction):
    status_string : str = pull_status()
    emoji = ''
    # channel = discord.utils.get(client.get_all_channels(), name='bot-stuff')
    if status_string == 'Online':
        emoji = ':white_check_mark: '
    else:
        emoji = ':octagonal_sign: '
    text = '# Server Status Bot\n> ## The server is currently: \n> ' + emoji + ' **' + status_string + '**'
    text += '\n> ### **Players Online**: \n> ' + pull_player_list() + '\n'
    await interaction.response.edit_message(content=text, )

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if str(message.channel) == 'bot-stuff':
        print("BEEP BOOP MESSAGE DETECTED")
        await message.channel.purge()
        await send_prompt(message.channel)
        
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

def pull_player_list():
    pull = requests.get(SERVER_CHECK_URL)
    text = pull.text
    player_list = ''

    num_players : int = text.count('sponsored')
    for i in range(num_players):
        text = text[text.index('sponsored') + len('sponsored')::]
        player_list += '* ' + text[text.index('>')+1:text.index('<')] + '\n'
    return player_list

    
    
async def send_prompt(channel):
    view = discord.ui.View()
    
    status_button = discord.ui.Button(label='Status', custom_id='status-id', style=discord.ButtonStyle.blurple)
    status_button.callback = on_status_button
    view.add_item(status_button)

    
    
    await channel.send(content="# Server Status Bot", view=view)

client.run(TOKEN)