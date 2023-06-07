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


class music_cog(commands.Cog):
    def __init__(self,bot):
        self.bot = bot

        self.is_playing = {}
        self.is_paused = {}
        self.musicQueue = {}
        self.queueIndex = {}

        self.YTDL_OPTIONS = {'format': 'bestaudio', 'nonplaylist': 'True'}
        self.FFMPEG_OPTIONS = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'
        }

        self.embedBlue  = 0x2c76dd
        self.embedRed   = 0xdf1141
        self.embedGreen = 0x0eaa51

        self.vc = {}

    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            id = int(guild.id)
            self.musicQueue[id] = []
            self.queueIndex[id] = 0
            self.vc[id] = None
            self.is_paused[id] = self.is_playing[id] = False

    def now_playing_embed(self, ctx, song):
        title = song['title']
        link = song['link']
        thumbnail = song['thumbnail']
        author = ctx.author
        avatar = author.avatar_url

        embed = discord.Embed(
            title = "Now Playing",
            description=f'[{title}]({link})',
            colour  = self.embedBlue
        )
        embed.set_thumbnail(url=thumbnail)
        embed.set_footer(text=f'Song addded by: {str(author)}', icon_url=avatar)
        return embed

    async def join_VC(self,ctx,channel):
        id = int(ctx.guild.id)
        if self.vc[id] == None or not self.vc[id].is_connected():
            self.vc[id] = await channel.connect()

            if self.vc[id] == None:
                await ctx.send("Could not connect to the voice channel.")
                return
        else:
            await self.vc[id].move_to(channel)


    def search_YT(self, search):
        queryString = parse.urlencode({'search_query': search}) 
        htmContent = request.urlopen( 'http://www.youtube.com/results?' + queryString)
        searchResults = re.findall( '/watch\?v-(.{11})', htmContent.read().decode())
        return searchResults[0:10]

    def extract_YT(self, url):
        with YoutubeDL(self.YTDL_OPTIONS) as ydl:
            try:
                info = ydl.extract_info(url, download=False)
            except: 
                return False

        return {
            'link': 'https://www.youtube.com/watch?v=' + url,
            'thumbnail': 'https://i.ytimg.com/vi/' + url + '/hqdefault.jpg?sqp=-oaymwEcCOADEI4CSFXyq4qpAw4IARUAAIhCGAFwAcABBg==&rs=AOn4CLD5uL4xKN-IUfez6KIW_j5y70mlig',
            'source': info['formats'][0]['url'],
            'title': info['title']
        }

    def play_next(self,ctx):
        id = int(ctx.guild.id)

        if not self.is_playing[id]:
            return
        if self.queueIndex[id] + 1 < len(self.musicQueue[id]):
            self.is_playing[id] = True
            self.queueIndex[id] += 1

            song = self.musicQueue[id][self.queueIndex[id]][0]
            message = self.now_playing_embed(ctx,song)
            coro = ctx.send(embed=message)
            fut = run_coroutine_threadsafe(coro, self.bot.loop)
            try:
                fut.result()
            except:
                pass

            self.vc[id].play(discord.FFmpegPCMAudio(
                song['source'], **self.FFMPEG_OPTIONS), after=lambda e: self.play_next(ctx)) 
        else:
            self.queueIndex[id] += 1
            self.is_playing[id] = False

    async def play_music(self, ctx):
        id = int(ctx.guild.id)

        if self.queueIndex[id] < len(self.musicQueue[id]):
            self.is_playing[id]= True
            self.is_paused[id] = False

            await self.join_VC(ctx, self.musicQueue[id][self.queueIndex[id]][1])
            
            song = self.musicQueue[id][self.queueIndex[id]][0]
            message = self.now_playing_embed(ctx,song)
            await ctx.send(embed=message)

            self.vc[id].play(discord.FFmpegPCMAudio(
                song['source'], **self.FFMPEG_OPTIONS), after=lambda e: self.play_next(ctx)) 
        else:
            await ctx.send("There are no songs in the queue to be played.")
            self.queueIndex[id] += 1
            self.is_playing[id] = False

    @ commands.command(
        name ="join"
    )
    async def join(self, ctx):
        if ctx.author.voice:
            userChannel = ctx.author.voice.channel
            await self.join_VC(ctx,userChannel)
            await ctx.send(f'Rice Cooker has joined {userChannel}')

        else:
            await ctx.send("You are not connected to a voice channel.")

    @ commands.command(
        name ="leave"
    )
    async def leave(self,ctx):
        id = int(ctx.guild.id)
        self.is_playing[id] = self.is_paused[id] = False
        self.musicQueue[id] = []
        self.queueIndex[id] = 0

        if self.vc[id] != None:
            await ctx.send("Rice Cooker has left the voice channel")
            await self.vc[id].disconnect()