import wavelink
from wavelink.ext import spotify
import asyncio
import discord
import requests
from StaticVars import Songlist

def getThumbnail(url):
  request = requests.get(url)
  if request.status_code == 200 :
    return url
  else :
    return 'https://cdn.discordapp.com/attachments/995337235211763722/1033079306143940709/milk-and-mocha-cute.gif'

async def get_next_song(player: wavelink.Player, track: wavelink.Track, reason):
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

async def auto_leave(member, before, after, bot_id, guildList, songchList):
  if member.id == bot_id:
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
            if mem.id == bot_id:
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