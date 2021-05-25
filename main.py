# Creators: Nathan Bonetto and True Sarmiento
# Date last edited: 5/21/21
# This is a discord bot that manages a server's elo system
# Functions:
# - Have people register within the bot
# - Have it know Person A vs Person B is fighting
# - Have a moderator role declare a winner
# - Give/take elo relative to the elo difference between the two players
# - Store the players elo
# - Give roles based on a player's elo "bracket"
# - Create a channel displaying player's elo in descending order
# - Update said channel everytime a player's elo is updated
# - Every two weeks take away X amount of elo if someone's name has not been used within the bot
# - Allows players to unregister from the bot

import discord
import os

import null as null
from discord.ext import commands
from db import create_table
from db import addMember
from db import removeMember
from db import printStandings

DISCORD_TOKEN = ""
bot = commands.Bot(command_prefix="$")

@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))

@bot.command()
async def setup(ctx):
    x = 0
    for guild in bot.guilds:
      for channel in guild.text_channels:
        if channel.name == 'current-standings':
          x = 1
    guild = ctx.guild
    if x == 0:
      # comment out create_role code - True 5/25/21
      await guild.create_role(name="Beginner")
      await guild.create_role(name="Intermidiate", colour=discord.Colour(0x001BFF))
      await guild.create_role(name="Advanced", colour=discord.Colour(0x00FF1B))
      await guild.create_role(name="Master", colour=discord.Colour(0xFF0000))
      await guild.create_role(name="Grandmaster", colour=discord.Colour(0xF7FF00))
      await guild.create_text_channel('current-standings')
      create_table(guild.name)
      await ctx.channel.send('Channels and roles have been made!')
    elif x == 1:
      await ctx.channel.send('This server has already been setup!')

@bot.command()
async def register(ctx):
    new_name = str(ctx.message.author)
    reply = addMember(new_name, ctx.guild.name)
    await ctx.channel.send(reply)

@bot.command()
async def resign(ctx):
    new_name = str(ctx.message.author)
    reply = removeMember(new_name, ctx.guild.name)
    await ctx.channel.send(reply)

@bot.command()
async def update(ctx):
    channel = discord.utils.get(ctx.guild.channels, name="current-standings")
    channel_id = channel.id
    result = printStandings(ctx.guild.name)
    for i in result:
        for z in i:
            await ctx.channel.send(z)

bot.run(DISCORD_TOKEN)
