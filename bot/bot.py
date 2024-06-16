# bot.py
import os

import discord
from dotenv import load_dotenv

import requests
import time, threading


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    channel = discord.utils.get(client.get_all_channels(), name='bot-stuff')
    
    global SERVER_CHECK_URL
    SERVER_CHECK_URL = get_global_from_config('server_check_url')
    
    global BATCH_PATH
    BATCH_PATH = get_global_from_config('bat_file')

    global SERVER_LOGS_PATH
    SERVER_LOGS_PATH = get_global_from_config('server_logs_path')

    global SERVER_DIRECTORY_PATH
    SERVER_DIRECTORY_PATH = get_global_from_config('server_directory_path')
    
    threading.Timer(60 * 20, on_save_timer).start()
    on_save_timer()

    await channel.purge()
    await send_prompt(channel)

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if str(message.channel) == 'bot-stuff':
        print("BEEP BOOP MESSAGE DETECTED")
        print('message author id: ' + str(message.author.id))
        if ('/' in message.content) and (message.author.id == 463869439255904257):
            command = message.content[message.content.index('/')+1::]
            print("Sending command: " + str(command))
            server_command(command)
            time.sleep(0.2)
            output = open(SERVER_LOGS_PATH + 'latest.log').read()
            output = output[output.rindex('[')::]
            await message.channel.purge(limit=1)
            await message.channel.send('```' + output + '```')
        if message.content.lower() == 'clear':
            await message.channel.purge()
            await send_prompt(message.channel)

    
    
async def send_prompt(channel):
    view = discord.ui.View(timeout=None)
    
    status_button = discord.ui.Button(label='Status', custom_id='status-id', style=discord.ButtonStyle.blurple)
    status_button.callback = on_status_button
    view.add_item(status_button)

    logs_button = discord.ui.Button(label='Get logs', custom_id='terminal-id', style=discord.ButtonStyle.secondary)
    logs_button.callback = on_logs_button
    view.add_item(logs_button)

    start_button = discord.ui.Button(label='Start Server', custom_id='start-id', style=discord.ButtonStyle.success)
    start_button.callback = on_start_button
    view.add_item(start_button)
    
    
    await channel.send(content="# Server Status Bot", view=view)

async def on_status_button(interaction : discord.Interaction):
    status_string : str = pull_status()
    emoji = ''
    # channel = discord.utils.get(client.get_all_channels(), name='bot-stuff')
    if status_string == 'Online':
        emoji = ':white_check_mark: '
    else:
        emoji = ':octagonal_sign: '
    text = '# Server Status Bot\n> ## The server is currently: \n> ' + emoji + ' **' + status_string + '**'
    text += '\n> ### **Players Online**: \n' + pull_player_list() + '\n'
    await interaction.response.edit_message(content=text, )

async def on_logs_button(interaction : discord.Interaction):
    output = open(SERVER_LOGS_PATH + 'latest.log').read()
    send = '```'
    output = output.splitlines()
    output = output[::-1]
    output = output[0:10:]
    output = output[::-1]
    for line in output:
        send += line + '\n'
    send = send[-350::]
    send = '```' + send + '```'
    await interaction.channel.purge()
    await send_prompt(interaction.channel)
    time.sleep(0.2)
    await interaction.response.send_message(send)

async def on_start_button(interaction : discord.Interaction):
    if interaction.user.id == 463869439255904257 or interaction.user.id == 2:
        os.chdir(SERVER_DIRECTORY_PATH)
        os.system(BATCH_PATH)
        print(BATCH_PATH)

# Sync functions
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

    if 'sponsored' in text:
        for i in range(text.count('sponsored')):
            text = text[text.index('sponsored') + len('sponsored')::]
            player_list += '> * ' + text[text.index('>') + 1:text.index('<'):] + '\n'
    elif '<div class="hidden" id="players-list">' in text:
        text = text[text.index('<div class="hidden" id="players-list">')::]
        text = text[text.index('<span>')::]
        text = text[:text.index('</pre>'):]

        for line in text.splitlines():
            player_list += '> * ' + get_name_between_spans(line) + '\n'
    
    # print(text)

    
    return player_list

def get_global_from_config(config_string):
    global_element = open('bot.config').read()
    global_element = global_element[global_element.index(config_string+': ')::]
    global_element = global_element[global_element.index(':') + 2:global_element.index('\n'):]

    return global_element

def get_name_between_spans(string):
    original_string = string
    string = string[string.index('>')+1::]
    string = string[string.index('>')+1::]
    string = string[:string.index('<'):]

    return string

def server_command(cmd):
    os.system('screen -S minecraft-server-screen -X stuff "{}\n"'.format(cmd))

def on_save_timer():
    server_command('save-all')

client.run(TOKEN)
