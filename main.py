# Creators: Nathan Bonetto and True Sarmiento
# Date last edited: 5/28/21
# This is a discord bot that manages a server's elo system
# Functions:
# - Have an admin register people in the bot
# - Have it know Person A vs Person B is fighting
# - Have a moderator role declare a winner
# - Give/take elo relative to the elo difference between the two players
# - Store the players elo
# - Give roles based on a player's elo "bracket"
# - Create a channel displaying player's elo in descending order
# - Update said channel everytime a player's elo is updated
# - Every two weeks take away X amount of elo if someone's name has not been used within the bot
# - Allow moderators to unregister people from the bot

import discord

from discord.ext import commands
from db import create_table
from db import addMember
from db import removeMember
from db import printStandings
from db import updateRank

DISCORD_TOKEN = ""
bot = commands.Bot(command_prefix="$")

@bot.event
async def on_ready():
    print("------------------------------------")
    print("Bot Name: " + bot.user.name)
    print("Bot ID: " + str(bot.user.id))
    print("Discord Version: " + str(discord.__version__))
    print("------------------------------------")

@bot.command()
async def setup(ctx):
    x = 0
    for guild in bot.guilds:
      for channel in guild.text_channels:
        if channel.name == 'current-standings':
          x = 1
    guild = ctx.guild
    if x == 0:
      create_table(guild.name)
      # comment out create_role code - True 5/25/21
      await guild.create_role(name="Bot Moderator")
      await guild.create_role(name="Beginner")
      await guild.create_role(name="Intermidiate", colour=discord.Colour(0x001BFF))
      await guild.create_role(name="Advanced", colour=discord.Colour(0x00FF1B))
      await guild.create_role(name="Master", colour=discord.Colour(0xFF0000))
      await guild.create_role(name="Grandmaster", colour=discord.Colour(0xF7FF00))
      role = discord.utils.get(ctx.guild.roles, name="Simple Elo Bot")
      role2 = discord.utils.get(ctx.guild.roles, name="Bot Moderator")

      await guild.create_text_channel('current-standings')
      channel = discord.utils.get(ctx.guild.channels, name="current-standings")
      await channel.set_permissions(role, send_messages=True)
      await channel.set_permissions(role2, send_messages=True)
      await channel.set_permissions(ctx.guild.default_role, send_messages=False)

      await guild.create_text_channel('match-history')
      channel = discord.utils.get(ctx.guild.channels, name="match-history")
      await channel.set_permissions(role, send_messages=True)
      await channel.set_permissions(role2, send_messages=True)
      await channel.set_permissions(ctx.guild.default_role, send_messages=False)

      await guild.create_text_channel('bot-commands')
      channel = discord.utils.get(ctx.guild.channels, name="bot-commands")
      await channel.set_permissions(role, send_messages=True, view_channel=True)
      await channel.set_permissions(role2, send_messages=True, view_channel=True)
      await channel.set_permissions(ctx.guild.default_role, view_channel=False)

      await channel.send("Please make sure that I have 0 permissions in any channels EXCEPT the ones I created. Also make sure that the (@Bot Moderator) role is given to moderators only!")
    elif x == 1:
      channel = discord.utils.get(ctx.guild.channels, name="bot-commands")
      await channel.send('This server has already been setup!')

@bot.command()
async def register(ctx, name):
    reply = addMember(name, ctx.guild.name)
    await ctx.channel.send(reply)

@bot.command()
async def resign(ctx, name):
    reply = removeMember(name, ctx.guild.name)
    await ctx.channel.send(reply)

@bot.command()
async def update(ctx):
    channel = discord.utils.get(ctx.guild.channels, name="current-standings")
    result = printStandings(ctx.guild.name)
    await channel.purge(limit=100)
    for i in result:
        string = str(i)
        string = string.replace("(", "").replace("'", "").replace("'", "").replace(",", " ").replace(")", "")
        await channel.send(string)

@bot.command()
async def score(ctx, name1, name2, scored, lost):
    channel = discord.utils.get(ctx.guild.channels, name="match-history")
    update = updateRank(name1, name2, scored, lost, ctx.guild.name)
    await ctx.channel.send("Scores have been update!")
    await channel.send(update)

    # Updates the server's standings after updating
    channel = discord.utils.get(ctx.guild.channels, name="current-standings")
    result = printStandings(ctx.guild.name)
    await channel.purge(limit=100)
    for i in result:
        string = str(i)
        string = string.replace("(", "").replace("'", "").replace("'", "").replace(",", " ").replace(")", "")
        await channel.send(string)

bot.run(DISCORD_TOKEN)