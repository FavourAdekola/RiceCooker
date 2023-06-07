import discord
import responses
import datetime
import random
from asyncio import run_coroutine_threadsafe
from discord.ext import commands
import json
import re
from urllib import parse, request
import os
import asyncio
from youtube_dl import YoutubeDL
from music_cog import music_cog

async def send_message(message, user_message, is_private):
    try:
        response = responses.handle_response(user_message)
        await message.author.send(response)  if is_private else await message.channel.send(response)
    except Exception as e:
        print(e)


def run_discord_bot():
    TOKEN = 'OTkxNDU0MDAzOTE5NjAxNzI0.GiPuX5.WSA1BhKx2Qbbuuc2et4PH3Fv0YWs51p7auUrM8'
    intents = discord.Intents.all()
    intents.message_content = True
    client = discord.Client(intents = intents)

    bot = commands.Bot(command_prefix='?', intents = intents)

    

    @client.event
    async def on_ready():
        print(f'{client.user} is now running!')
        await client.change_presence(activity=discord.Game("Cooking Rice"))
        await bot.add_cog(music_cog(bot))

        # It's The First Of The Month
        day = datetime.datetime.now()
        if day.strftime("%d") == "01":
            print("It's the first of the month")
            await client.get_channel(698008492526665780).send("https://cdn.discordapp.com/attachments/1046948327767412816/1048005776318414919/263521927_1036371346932224_1220958437198197236_n.mp4")
        if day.strftime("%A") == "Friday":
            print("It's Friday")
            choice = random.choice([1,2])
            if choice == 1:
                await client.get_channel(698008492526665780).send("https://cdn.discordapp.com/attachments/1046948327767412816/1048347906706513930/yt5s.com-ITS_YAKUZA_FRIDAY360p.mp4")
            if choice == 2:
                await client.get_channel(698008492526665780).send("https://cdn.discordapp.com/attachments/1046948327767412816/1048349749679501424/yt5s.com-Today_is_Friday_in_California360p.mp4")

    @client.event
    async def on_message(message):
        if message.author == client.user:
            return

        username = str(message.author)
        user_message = str(message.content)
        channel = str(message.channel)

        await send_message(message,user_message, is_private=False )
        await bot.process_commands(message)
        
    client.run(TOKEN)