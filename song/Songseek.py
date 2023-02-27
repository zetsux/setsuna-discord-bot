import discord
import os
import wavelink
from wavelink.ext import spotify
from discord.ui import Select, Button, Modal, InputText, View
from discord.ext import commands
from discord.commands import Option
import datetime
from StaticVars import Songlist

guilds = [990445490401341511, 1020927428459241522, 989086863434334279, 494097970208178186, 1028690906901139486]
SPOTIFYSECRET = os.environ['SPOTIFYSECRET']
SPOTIFYID = os.environ['SPOTIFYID']

class Songseek(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    
  @commands.slash_command(name='songseek', description='Go to the specific duration of the song')
  @commands.has_any_role('Encoder Magang', 'Owner')
  async def song_seek(self, ctx, *, seconds: Option(int, "Second(s) of song duration to seek", required=False, default=0), minutes: Option(int, "Minute(s) of song duration to seek", required=False, default=0), hours: Option(int, "Hour(s) of song duration to seek", required=False, default=0)):
    if not ctx.author.voice:
        await ctx.respond('Etlis join vc dlu la dek..', ephemeral=True)
        return
    elif not ctx.voice_client:
        vc: wavelink.Player = await ctx.author.voice.channel.connect(
            cls=wavelink.Player)
    elif ctx.author.voice.channel != ctx.me.voice.channel:
        await ctx.respond(
            f'Hmph {ctx.author.name}-nyan, watashi ngga mau diatur-atur kalo watashitachi ngga satu vc',
            ephemeral=True)
        return
    elif seconds < 0 or minutes < 0 or hours < 0 :
      await ctx.respond(
            f'Hmph {ctx.author.name}-nyan, gajelas ah masa waktunya minus gitu',
            ephemeral=True)
      return
    
    else:
      vc: wavelink.Player = ctx.voice_client
      totalSec = seconds + (minutes*60) + (hours*3600)
      await ctx.respond(
        f'`{vc.track.title}` berhasil dipindahkan ke detik ke-{totalSec} oleh {ctx.author.name}-nyan'
      )
      await vc.seek(totalSec*1000)

def setup(bot):
  bot.add_cog(Songseek(bot))