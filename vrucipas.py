import discord
from discord.ext import commands
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
    client = commands.Bot(command_prefix='.', intents=intents)

    queues = {}
    voice_clients = {}
    yt_dl_options ={'format': 'bestaudio/best'}
    ytdl = yt_dlp.YoutubeDL(yt_dl_options)

    ffmpeg_options = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5','options': '-vn -filter:a "volume=0.25"'}

    @client.event
    async def on_ready():
        print(f'{client.user} is now jamming')

    async def play_next(ctx):
        if queues[ctx.guild.id] != []:
            link = queues[ctx.guild.id].pop(0)
            await play(ctx, link)

    @client.command(name='play')
    async def play(ctx, link):
        try:
            voice_client = await ctx.author.voice.channel.connect()
            voice_clients[voice_client.guild.id] = voice_client
        except Exception as error:
            print(error)

        try:
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, lambda: ytdl.extract_info(link, download=False))
                
            song = data['url']
            player = discord.FFmpegOpusAudio(song, **ffmpeg_options)

            # lambda is one line func
            voice_clients[ctx.guild.id].play(player, after=lambda e: asyncio.run_coroutine_threadsafe(play_next(ctx), client.loop))
        except Exception as error:
            print(error)

        @client.command(name='pause')
        async def pause(ctx):
            try:
                voice_clients[ctx.guild.id].pause()
            except Exception as e:
                print(e)
        
        @client.command(name='resume')
        async def resume(ctx):
            try:
                voice_clients[ctx.guild.id].resume()
            except Exception as e:
                print(e)

        @client.command(name='stop')
        async def stop(ctx):
            try:
                voice_clients[ctx.guild.id].stop()
                await voice_clients[ctx.guild.id].disconnect()
                del voice_clients[ctx.guild.id]
            except Exception as e:
                print(e)

        @client.command(name='queue')
        async def queue(ctx, url):
            if ctx.guild.id not in queues:
                queues[ctx.guild.id] = []
            queues[ctx.guild.id].append(url)
            await ctx.send('Song added to queue!')

        @client.command(name='clear_queue')
        async def clear_queue(ctx):
            if ctx.guild.id in queues:
                queues[ctx.guild.id].clear()
                await ctx.send('Queue cleared!')
            else:
                ctx.send("There is no queue to clear!")

        @client.command(name='help')
        async def help(ctx):
            try:
                help_message = dedent('''
                    General commands:
                    **?help** - displays all the available commands
                    **?play** url - start playing music from url you send
                    **?pause** - pause the current song
                    **?resume** - resume the current song
                    **?stop** - stop the current song and disconnect the bot
                ''')
                await ctx.channel.send(help_message)
            except Exception as e:
                print(e)
            

    client.run(TOKEN)