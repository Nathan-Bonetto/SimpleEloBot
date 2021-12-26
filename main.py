# Creators: Nathan Bonetto and True Sarmiento
# Date last edited: 12/25/21

import discord
import threading
import asyncio

from discord.ext import commands
from db import create_table
from db import addMember
from db import removeMember
from db import printStandings
from db import updateRank
from db import decay
from db import delete_table

DISCORD_TOKEN = ""
bot = commands.Bot(command_prefix="$", help_command=None)

def decayTimer():
  threading.Timer((3600 * 24), decayTimer).start()
  decay()

decayTimer()


@bot.event
async def on_ready():
    print("------------------------------------")
    print("Bot Name: " + bot.user.name)
    print("Bot ID: " + str(bot.user.id))
    print("Discord Version: " + str(discord.__version__))
    print("------------------------------------")

async def check_roles(ctx, message):
    for i in message.author.roles:
        if i == discord.utils.get(ctx.guild.roles, name="Bot Moderator"):
            return True
    return False

@bot.command()
async def help(ctx):
    if ctx.author.guild_permissions.administrator:
        await ctx.channel.send("```"
            "help     - Shows this message\n"
            "register - this followed by a name registers a name (no spaces, max 20 characters)\n" 
            "resign   - this followed by a player's name removes the player and deletes their data\n"   
            "score    - to submit a score, MUST BE SUBMITED IN THIS ORDER(no commas): winner's name, winner's score, loser's name, loser's score\n"    
            "setup    - Setsup the server with channels and roles (needs to be done once)\n"    
            "tearDown - Deletes everything, nothing is recoverable once this command is executed\n" 
            "update   - Updates the current-standings channel manually"
            "```")


@bot.command()
async def setup(ctx):
    if ctx.author.guild_permissions.administrator:
        x = 0
        for channel in ctx.guild.text_channels:
            if channel.name == 'current-standings':
              x = 1
        guild = ctx.guild
        if x == 0:
          create_table(guild.name)
          await guild.create_role(name="Bot Moderator")
          await guild.create_role(name="Grandmaster", colour=discord.Colour(0xF7FF00), hoist=True)
          await guild.create_role(name="Master", colour=discord.Colour(0xFF0000), hoist=True)
          await guild.create_role(name="Advanced", colour=discord.Colour(0x00FF1B), hoist=True)
          await guild.create_role(name="Intermediate", colour=discord.Colour(0x001BFF), hoist=True)
          await guild.create_role(name="Beginner", hoist=True)
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

          await channel.send("Please make sure that I have 0 permissions in any channels EXCEPT the ones I created. Only people with admin privileges AND the  "+ role2.mention + " will be able to use my commands!")

        elif x == 1:
          channel = discord.utils.get(ctx.guild.channels, name="bot-commands")
          await channel.send('This server has already been setup!')

@bot.command()
async def tearDown(ctx):
    def check(msg):
        return msg.content == "Yes"
    if await check_roles(ctx, ctx.message) and ctx.author.guild_permissions.administrator:
        await ctx.channel.send("Are you sure? This command means I delete everything I made inside this server including the database, there is no "
                               "recovering information once I delete it. Would you still like me to delete everything? "
                               "(type \"Yes\" exactly for me to do it, or wait 5 seconds for the request to expire)")
        try:
            msg = await bot.wait_for("message", check=check, timeout=5)
        except asyncio.TimeoutError:
            await ctx.channel.send("Request has timed out, your information is still here!")
        if msg:
            role = discord.utils.get(ctx.guild.roles, name="Bot Moderator")
            await role.delete()
            role = discord.utils.get(ctx.guild.roles, name="Beginner")
            await role.delete()
            role = discord.utils.get(ctx.guild.roles, name="Intermediate")
            await role.delete()
            role = discord.utils.get(ctx.guild.roles, name="Advanced")
            await role.delete()
            role = discord.utils.get(ctx.guild.roles, name="Master")
            await role.delete()
            role = discord.utils.get(ctx.guild.roles, name="Grandmaster")
            await role.delete()


            channel = discord.utils.get(ctx.guild.channels, name="current-standings")
            await channel.delete()

            channel = discord.utils.get(ctx.guild.channels, name="match-history")
            await channel.delete()

            channel = discord.utils.get(ctx.guild.channels, name="bot-commands")
            await channel.delete()

            delete_table(ctx.guild.name)

@bot.command()
async def register(ctx, name):
    if await check_roles(ctx, ctx.message) and ctx.author.guild_permissions.administrator:
        reply = addMember(name, ctx.guild.name)
        await ctx.channel.send(reply)
        await update(ctx)

@bot.command()
async def resign(ctx, name):
    if await check_roles(ctx, ctx.message) and ctx.author.guild_permissions.administrator:
        reply = removeMember(name, ctx.guild.name)
        await ctx.channel.send(reply)
        await update(ctx)

@bot.command()
async def update(ctx):
    if await check_roles(ctx, ctx.message) and ctx.author.guild_permissions.administrator:
        channel = discord.utils.get(ctx.guild.channels, name="current-standings")
        result = printStandings(ctx.guild.name)
        await channel.purge(limit=1000)
        await channel.send("```Name                 Rank```")
        for i in result:
            string = str(i)
            string = string.replace("(", "").replace("'", "").replace("'", "").replace(",", "").replace(")", "")

            temp = string.find(" ")
            name = string[0 : temp]
            space1 = ""
            for j in range(40 - len(name)):
                space1 +=  " "

            string = string[temp + 1 : len(string)]
            rank = string[0 : temp]

            await channel.send(" " + name + space1 + rank)

@bot.command()
async def score(ctx, name1, scored, name2, lost):
    if await check_roles(ctx, ctx.message) and ctx.author.guild_permissions.administrator:
        channel = discord.utils.get(ctx.guild.channels, name="match-history")
        rankUpdate = updateRank(name1, scored, name2, lost, ctx.guild.name)
        await ctx.channel.send("Scores have been update!")
        await channel.send(rankUpdate)
        await update(ctx)

bot.run(DISCORD_TOKEN)