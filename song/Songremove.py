import discord
import os
import wavelink
from wavelink.ext import spotify
from discord.ui import Select, Button, Modal, TextInput, View
from discord.ext import commands
from discord import app_commands
from discord.commands import Option
from StaticVars import Songlist

guilds = [990445490401341511, 1020927428459241522, 989086863434334279, 494097970208178186, 1028690906901139486]
SPOTIFYSECRET = os.environ['SPOTIFYSECRET']
SPOTIFYID = os.environ['SPOTIFYID']

class Songremove(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    
  @app_commands.command(description='Force remove a song from queue')
  @app_commands.checks.has_any_role('Encoder Magang', 'Owner')
  async def songremove(self, ctx: discord.Interaction, remove: Option(int, "The position of song in queue", required=True)):
    if not ctx.voice_client:
        await ctx.response.send_message(
            f'Ihh aneh deh {ctx.user.name}-nyan, watashi aja ngga di vc',
            ephemeral=True)
        return
    elif not ctx.user.voice:
        await ctx.response.send_message('Etlis join vc dlu la dek..', ephemeral=True)
        return
    elif ctx.user.voice.channel != ctx.me.voice.channel:
        await ctx.response.send_message(
            f'Hmph {ctx.user.name}-nyan, watashi ngga mau diatur-atur kalo watashitachi ngga satu vc',
            ephemeral=True)
        return
    else:
        vc: wavelink.Player = ctx.voice_client

    if vc.queue.count >= remove :
      
      arr = []
      i = 1
      for song in vc.queue :
        if i == remove :
          await ctx.response.send_message(
              f'`{song.title}` di urutan ke-{remove} pada antrian berhasil diskip paksa oleh {ctx.user.name}-nyan')
          Songlist.songList.pop(remove - 1)
        else :
          arr.append(song)
      
        i += 1

      vc.queue.clear()
      vc.queue.extend(arr)
        
    else :
      await ctx.response.send_message(
          f'Lagu di queue aja cuma {vc.queue.count}, masa mau hapus lagu ke-{remove} sih, {ctx.user}-nyan..'
      )
      
async def setup(bot):
  await bot.add_cog(Songremove(bot))