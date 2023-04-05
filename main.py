from webserver import keep_alive
import os
import random
import discord
from discord.ui import Select, Button, Modal, InputText, View
from discord.ext import commands
from discord.commands import Option
import pymongo
import json
import urllib.request as urllib2
import wavelink
from wavelink.ext import spotify
import datetime
import pytz
import numpy as np
import asyncio
import time
import requests
from StaticVars import Songlist

TOKEN = os.environ['TOKEN']
ROLECLAIM = int(os.environ['ROLEMSGID'])
MONGODB = os.environ['MONGODB']
LORENDB = os.environ['LORENDB']
LVLINKHOST = os.environ['LVLINKHOST']
LVLINKPORT = int(os.environ['LVLINKPORT'])
LVLINKPASS = os.environ['LVLINKPASS']
SPOTIFYSECRET = os.environ['SPOTIFYSECRET']
SPOTIFYID = os.environ['SPOTIFYID']
SONGCH = int(os.environ['SONGCHID'])
GUILDID = int(os.environ['GUILDID'])
CSGUILDID = int(os.environ['CSGUILDID'])
CSSONGCH = int(os.environ['SONGCSID'])
LOGCH = int(os.environ['LOGCHID'])
SPBGUILDID = int(os.environ['SPBGUILDID'])
SPBSONGCH = int(os.environ['SPBCHID'])
NGGUILDID = int(os.environ['NGGUILDID'])
NGSONGCH = int(os.environ['NGCHID'])
ZSGUILDID = int(os.environ['ZSGUILDID'])
ZSSONGCH = int(os.environ['ZSCHID'])

guildList = []
guildList.append(GUILDID)
guildList.append(CSGUILDID)
guildList.append(SPBGUILDID)
guildList.append(NGGUILDID)
guildList.append(ZSGUILDID)

songchList = []
songchList.append(SONGCH)
songchList.append(CSSONGCH)
songchList.append(SPBSONGCH)
songchList.append(NGSONGCH)
songchList.append(ZSSONGCH)

client = pymongo.MongoClient(MONGODB)
mydb = client["familiardb"]
mycol = mydb["user"]

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!$', intents=intents)

@bot.event
async def on_ready():
  print(f'{bot.user.name} has connected to Discord!')
  await bot.change_presence(activity=discord.Activity(
      type=discord.ActivityType.watching, name="u from afar | /help"))
        
  bot.loop.create_task(connect_nodes())
    # change_bot_task.start()


@bot.event
async def on_wavelink_node_ready(node: wavelink.Node):
    print(f'The Node {node.identifier} has also connected to Discord!')


# @tasks.loop(seconds=1800)
# async def change_bot_task():
#   await bot.wait_until_ready()
#   statuses = ["commands | !help", "cues | !help", "orders | !help", "instructions | !help", "directions | !help", "requests | !help", "demands | !help", "mandates | !help", "decrees | !help", "prompts | !help", "signals | !help", "ur bs | !help"]
#   while not bot.is_closed() :
#     status = random.choice(statuses)
#     await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=status))


async def connect_nodes():
    await bot.wait_until_ready()
    await wavelink.NodePool.create_node(bot=bot, host=LVLINKHOST, port=LVLINKPORT, password=LVLINKPASS, https=True, spotify_client=spotify.SpotifyClient(client_id=SPOTIFYID, client_secret=SPOTIFYSECRET))

def getThumbnail(url):
  request = requests.get(url)
  if request.status_code == 200 :
    return url
  else :
    return 'https://cdn.discordapp.com/attachments/995337235211763722/1033079306143940709/milk-and-mocha-cute.gif'

@bot.event
async def on_wavelink_track_end(player: wavelink.Player, track: wavelink.Track, reason):
    ctx = player.ctx
    vc: player = ctx.voice_client

    if vc.loop:
        await vc.play(track)
        return

    try:
        next_track = vc.queue.get()
        await vc.play(next_track)
        embedVar = discord.Embed(
                    title=f'Now Playing :',
                    description=f"{next_track.title}",
                    color=0xf2bc00)
        songL = Songlist.songList.pop(0)
        embedVar.set_footer(text=f"Requested by : {songL[1].name}", icon_url=songL[1].avatar.url)
        embedVar.set_thumbnail(url=getThumbnail(next_track.thumb))
        await ctx.channel.send(embed=embedVar)
    except:
        await vc.stop()


@bot.event
async def on_voice_state_update(member, before, after):
    if member.id == bot.user.id:
        if before.channel is None:
          voice = after.channel.guild.voice_client
          time = 0
          while True:
              await asyncio.sleep(1)
              time = time + 1
              if voice.is_playing() and not voice.is_paused():
                  time = 0
              if time >= 180 and not voice.is_paused():
                  if after.channel.guild.id in guildList :
                      idx = guildList.index(after.channel.guild.id)
                      channel = after.channel.guild.get_channel(songchList[idx])
                      embedVar = discord.Embed(
                        description=f"Watashi leave dari {after.channel.name} dulu deh ya, bosen nich udah 3 menit ga ngapa-ngapain, nanti /songinsert lagi ajah kalo mau manggil lagi yaa~",
                        color=0x800000)
                      await channel.send(embed=embedVar)
                
                  return await voice.disconnect()

              elif time >= 1200:
                  if after.channel.guild.id in guildList :
                      idx = guildList.index(after.channel.guild.id)
                      channel = after.channel.guild.get_channel(songchList[idx])
                      embedVar = discord.Embed(
                        description=f"Watashi leave dari {after.channel.name} dulu deh ya, udah 20 menit kena pause bah, nanti /songinsert lagi ajah kalo mau manggil lagi yaa~",
                        color=0x800000)
                      await channel.send(embed=embedVar)
                
                  return await voice.disconnect()
                
              if not voice.is_connected():
                  break

    elif after.channel is None or before.channel is not None:
        voice = before.channel.guild.voice_client
        if len(before.channel.members) >= 1:
            setexist = False
            for mem in before.channel.members:
                if mem.id == bot.user.id:
                    setexist = True

                if not mem.bot:
                    return

            if not setexist:
                return

            memlen = len(before.channel.members)
            time = 0
            while True:
                await asyncio.sleep(1)
                time = time + 1
                # print(time)
                if voice.is_playing() and not voice.is_paused():
                    if time >= 300:
                        if before.channel.guild.id in guildList :
                          idx = guildList.index(before.channel.guild.id)
                          channel = before.channel.guild.get_channel(songchList[idx])
                          embedVar = discord.Embed(
                            description=f"Watashi leave dari {before.channel.name} dulu deh ya, mendokusai ah muter lagu gada yg dengerin, parah banget ga di-disconnect, nanti /songinsert lagi ajah kalo mau manggil lagi yaa~",
                            color=0x800000)
                          await channel.send(embed=embedVar)
                          
                        return await voice.disconnect()

                else:
                    if time >= 120:                        
                        if before.channel.guild.id in guildList :
                          idx = guildList.index(before.channel.guild.id)
                          channel = before.channel.guild.get_channel(songchList[idx])
                          embedVar = discord.Embed(
                            description=f"Watashi leave dari {before.channel.name} dulu deh ya, sabishii ditinggal sendiri, mana ngga di-disconnect pula, nanti /songinsert lagi ajah kalo mau manggil lagi yaa~",
                            color=0x800000)
                          await channel.send(embed=embedVar)

                        return await voice.disconnect()

                if not voice.is_connected():
                    break

                if len(before.channel.members) != memlen:
                    for mem in before.channel.members:
                        if not mem.bot:
                            return

                    memlen = len(before.channel.members)


@bot.slash_command(name='reloadcogs', description='Reload Cogs')
@commands.has_any_role('Encoder Magang', 'Owner')
async def reload(ctx):
  await ctx.defer()
  str = ""
  for folder in os.listdir("./") :
    path = f"./{folder}"
    
    if not os.path.isdir(path) :
      continue
      
    for filename in os.listdir(f"./{folder}") :
      if filename.endswith(".py") :
        try : 
          bot.load_extension(f"{folder}.{filename[:-3]}")
          str += f"{folder}.{filename[:-3]}\n"
        except Exception as error :
          print(error)

  await ctx.respond(f"{str}")

@bot.event
async def on_member_join(member):
    if member.bot:
        return

    await member.create_dm()
    await member.dm_channel.send(
        f'Halo {member.name}-nyan, watashi Setsuna yang akan mengurus anata di server baru, yoroshiku~'
    )


# @bot.event
# async def on_message(message):
#     if message.author == bot.user:
#       return

#     if "ajg" in message.content.lower() or "bgst" in message.content.lower():
#       await message.add_reaction('\U0001F974')
#       await message.channel.send(f'Kasar yaa, {message.author.name}-nyan')

#     await bot.process_commands(message)

# @bot.event
# async def on_message_edit(before, after):
#     if before.author == bot.user:
#         return

#     await before.add_reaction('\U0001F9D0')
#     await before.channel.send(
#         f'{before.author} abis edit msg nich di {before.channel.name}!\n\n'
#         f'Jadi awalnya gini :\n[ {before.content} ]\n\n'
#         f'Eh trus jadi gini :\n[ {after.content} ]'
#     )


@bot.event
async def on_raw_reaction_add(payload):
    if payload.member == bot.user:
        return

    guild = bot.get_guild(payload.guild_id)
    channel = guild.get_channel(payload.channel_id)
    if payload.message_id == ROLECLAIM:
        if payload.emoji.name == '🗿':
            role = discord.utils.get(guild.roles, name='Player')
            await payload.member.add_roles(role)
        elif payload.emoji.name == '💀':
            role = discord.utils.get(guild.roles, name='Hunter')
            await payload.member.add_roles(role)
        elif payload.emoji.name == '🤑':
            role = discord.utils.get(guild.roles, name='Shopkeeper')
            await payload.member.add_roles(role)
        elif payload.emoji.name == '🧑‍🌾':
            role = discord.utils.get(guild.roles, name='Villager')
            await payload.member.add_roles(role)
        elif payload.emoji.name == '👨‍🍳':
            role = discord.utils.get(guild.roles, name='Cook')
            await payload.member.add_roles(role)


@bot.event
async def on_raw_reaction_remove(payload):
    if payload.message_id != ROLECLAIM:
        return

    guild = bot.get_guild(payload.guild_id)
    member = guild.get_member(payload.user_id)

    if payload.emoji.name == '🗿':
        role = discord.utils.get(guild.roles, name='Player')
        await member.remove_roles(role)
    elif payload.emoji.name == '💀':
        role = discord.utils.get(guild.roles, name='Hunter')
        await member.remove_roles(role)
    elif payload.emoji.name == '🤑':
        role = discord.utils.get(guild.roles, name='Shopkeeper')
        await member.remove_roles(role)
    elif payload.emoji.name == '🧑‍🌾':
        role = discord.utils.get(guild.roles, name='Villager')
        await member.remove_roles(role)
    elif payload.emoji.name == '👨‍🍳':
        role = discord.utils.get(guild.roles, name='Cook')
        await member.remove_roles(role)


@bot.event
async def on_command_error(ctx, error):
    userFind = mycol.find_one({"userid": str(ctx.author.id)})
    if userFind == None:
        await ctx.channel.send(
            f'Neee {ctx.author.name}-nyan, yuk bisa yuk /regist dulu~')
        return

    if isinstance(error, commands.errors.CheckFailure):
        await ctx.channel.send(
            f'Gomenasai {ctx.message.author}-nyan, anata ngga punya hak buat nyuruh watashi pakai command itu...'
        )

    elif isinstance(error, commands.CommandOnCooldown):
        if error.retry_after > 3600:
            hourLeft = error.retry_after / 3600
            minLeft = (error.retry_after % 3600) / 60
            secLeft = (error.retry_after % 3600) % 60
            await ctx.channel.send(
                f'Command !{ctx.invoked_with} is still on cooldown...\nDuration Left : {int(hourLeft)} hour(s), {int(minLeft)} minute(s), and {int(secLeft)} second(s)'
            )

        elif error.retry_after > 60:
            minLeft = error.retry_after / 60
            secLeft = error.retry_after % 60
            await ctx.channel.send(
                f'Command !{ctx.invoked_with} is still on cooldown...\nDuration Left : {int(minLeft)} minute(s) and {int(secLeft)} second(s)'
            )

        else:
            await ctx.channel.send(
                f'Command !{ctx.invoked_with} is still on cooldown...\nDuration Left : {int(error.retry_after)} second(s)'
            )

    else:
        print(error)
        guild = bot.get_guild(GUILDID)
        channel = guild.get_channel(LOGCH)
        try:
            await channel.send(error)
        except:
            await channel.send('Error tapi kepanjangan bro...')


@bot.event
async def on_application_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.respond(
            f'Gomenasai {ctx.author.name}-nyan, anata ngga punya hak buat nyuruh watashi pakai command itu...'
        )
        return

    userFind = mycol.find_one({"userid": str(ctx.author.id)})
    if userFind == None:
        await ctx.respond(
            f'Neee {ctx.author.name}-nyan, yuk bisa yuk /regist dulu~',
            ephemeral=True)
        return

    elif isinstance(error, commands.CommandOnCooldown):
        if error.retry_after > 3600:
            hourLeft = error.retry_after / 3600
            minLeft = (error.retry_after % 3600) / 60
            secLeft = (error.retry_after % 3600) % 60
            await ctx.respond(
                f'Command is still on cooldown...\nDuration Left : {int(hourLeft)} hour(s), {int(minLeft)} minute(s), and {int(secLeft)} second(s)',
                ephemeral=True)

        elif error.retry_after > 60:
            minLeft = error.retry_after / 60
            secLeft = error.retry_after % 60
            await ctx.respond(
                f'Command is still on cooldown...\nDuration Left : {int(minLeft)} minute(s) and {int(secLeft)} second(s)',
                ephemeral=True)

        else:
            await ctx.respond(
                f'Command is still on cooldown...\nDuration Left : {int(error.retry_after)} second(s)',
                ephemeral=True)

    else:
        print(error)
        guild = bot.get_guild(GUILDID)
        channel = guild.get_channel(LOGCH)
        try:
            await channel.send(error)
        except:
            await channel.send('Error tapi kepanjangan bro...')


# @bot.slash_command(name='resetcd', description='Reset cooldown of a command for self')
# @commands.has_any_role('Encoder Magang', 'Owner')
# async def reset_cd(ctx, command: Option(str, "Name of command to reset", required=True)):
#   await ctx.defer(ephemeral=True)
#   bot.get_application_command(command).reset_cooldown(ctx)
#   await ctx.respond(f'Cooldown command /{command} pada {ctx.author.name}-nyan berhasil direset!', ephemeral=True)


for folder in os.listdir("./") :
  path = f"./{folder}"
  
  if not os.path.isdir(path) :
    continue
    
  for filename in os.listdir(f"./{folder}") :
    if filename.endswith(".py") :
      try : 
        print(f"{folder}.{filename[:-3]}")
        bot.load_extension(f"{folder}.{filename[:-3]}")
      except Exception as error :
        print(error)

keep_alive()
try:
  bot.run(TOKEN)
except discord.errors.HTTPException :
  print("Kena rate limit nih, bentar restart duls..")
  os.system('kill 1')
  os.system('python restart.py')