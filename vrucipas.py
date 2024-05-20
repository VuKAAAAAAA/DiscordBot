import discord
import os
import asyncio
import yt_dlp
from dotenv import load_dotenv
from textwrap import dedent

def run_bot():
    # load .env file
    load_dotenv('.env')
    # put discord token in a variable
    TOKEN = os.getenv('discord_token')
    # define default intents
    intents = discord.Intents.default()
    # message_content is not enable by default
    intents.message_content = True
    # define client object
    client = discord.Client(intents=intents)

    queues = {}
    voice_clients = {}
    yt_dl_options ={'format': 'bestaudio/best'}
    ytdl = yt_dlp.YoutubeDL(yt_dl_options)

    ffmpeg_options = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5','options': '-vn -filter:a "volume=0.25"'}

    @client.event
    async def on_ready():
        print(f'{client.user} is now jamming')

    @client.event
    async def on_message(message):
        if message.author == client.user:
            return

        if message.content.startswith('?help'):
            try:
                help_message = dedent('''
                    General commands:
                    **?help** - displays all the available commands
                    **?play** url - start playing music from url you send
                    **?pause** - pause the current song
                    **?resume** - resume the current song
                    **?stop** - stop the current song and disconnect the bot
                ''')
                await message.channel.send(help_message)
            except Exception as e:
                print(e)

        if message.content.startswith('?play'):
            try:
                voice_client = await message.author.voice.channel.connect()
                voice_clients[voice_client.guild.id] = voice_client
            except Exception as e:
                print(e)
            try:
                # ?play link, 0 index, 1 index
                url = message.content.split()[1]

                loop = asyncio.get_event_loop()
                data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))
                
                song = data['url']
                player = discord.FFmpegOpusAudio(song, **ffmpeg_options)

                voice_clients[message.guild.id].play(player)
            except Exception as e:
                print(e)
            
        if message.content.startswith('?pause'):
            try:
                voice_clients[message.guild.id].pause()
            except Exception as e:
                print(e)

        if message.content.startswith('?resume'):
            try:
                voice_clients[message.guild.id].resume()
            except Exception as e:
                print(e)

        if message.content.startswith('?stop'):
            try:
                voice_clients[message.guild.id].stop()
                await voice_clients[message.guild.id].disconnect()
            except Exception as e:
                print(e)

    client.run(TOKEN)