import discord
import os
import wavelink
from wavelink.ext import spotify
from discord.ui import Select, Button, Modal, TextInput, View
from discord.ext import commands
from discord.commands import Option
from StaticVars import Songlist

guilds = [990445490401341511, 1020927428459241522, 989086863434334279, 494097970208178186, 1028690906901139486]
SPOTIFYSECRET = os.environ['SPOTIFYSECRET']
SPOTIFYID = os.environ['SPOTIFYID']

class Songremove(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    
  @commands.slash_command(description='Force remove a song from queue')
  @commands.has_any_role('Encoder Magang', 'Owner')
  async def songremove(self, ctx, remove: Option(int, "The position of song in queue", required=True)):
    if not ctx.voice_client:
        await ctx.respond(
            f'Ihh aneh deh {ctx.author.name}-nyan, watashi aja ngga di vc',
            ephemeral=True)
        return
    elif not ctx.author.voice:
        await ctx.respond('Etlis join vc dlu la dek..', ephemeral=True)
        return
    elif ctx.author.voice.channel != ctx.me.voice.channel:
        await ctx.respond(
            f'Hmph {ctx.author.name}-nyan, watashi ngga mau diatur-atur kalo watashitachi ngga satu vc',
            ephemeral=True)
        return
    else:
        vc: wavelink.Player = ctx.voice_client

    if vc.queue.count >= remove :
      
      arr = []
      i = 1
      for song in vc.queue :
        if i == remove :
          await ctx.respond(
              f'`{song.title}` di urutan ke-{remove} pada antrian berhasil diskip paksa oleh {ctx.author.name}-nyan')
          Songlist.songList.pop(remove - 1)
        else :
          arr.append(song)
      
        i += 1

      vc.queue.clear()
      vc.queue.extend(arr)
        
    else :
      await ctx.respond(
          f'Lagu di queue aja cuma {vc.queue.count}, masa mau hapus lagu ke-{remove} sih, {ctx.user}-nyan..'
      )
      
def setup(bot):
  bot.add_cog(Songremove(bot))