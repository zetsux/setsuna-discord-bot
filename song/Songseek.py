import discord
import os
import wavelink
from discord.ext import commands
from discord import app_commands

guilds = [990445490401341511, 1020927428459241522, 989086863434334279, 494097970208178186, 1028690906901139486]
SPOTIFYSECRET = os.environ['SPOTIFYSECRET']
SPOTIFYID = os.environ['SPOTIFYID']

class Songseek(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    
  @app_commands.command(name='songseek', description='Go to the specific duration of the song')
  @app_commands.checks.has_any_role('Encoder Magang', 'Owner')
  @app_commands.describe(seconds="The second(s) of song duration to seek", minutes="The minute(s) of song duration to seek", hours= "The hour(s) of song duration to seek")
  async def song_seek(self, ctx: discord.Interaction, *, seconds: int = 0, minutes: int = 0, hours: int = 0):
    if not ctx.user.voice:
        await ctx.response.send_message('Etlis join vc dlu la dek..', ephemeral=True)
        return
    elif not ctx.guild.voice_client:
        vc: wavelink.Player = await ctx.user.voice.channel.connect(
            cls=wavelink.Player)
    elif ctx.user.voice.channel != ctx.guild.me.voice.channel:
        await ctx.response.send_message(
            f'Hmph {ctx.user.name}-nyan, watashi ngga mau diatur-atur kalo watashitachi ngga satu vc',
            ephemeral=True)
        return
    elif seconds < 0 or minutes < 0 or hours < 0 :
      await ctx.response.send_message(
            f'Hmph {ctx.user.name}-nyan, gajelas ah masa waktunya minus gitu',
            ephemeral=True)
      return
    
    else:
      vc: wavelink.Player = ctx.guild.voice_client
      totalSec = seconds + (minutes*60) + (hours*3600)
      await ctx.response.send_message(
        f'`{vc.track.title}` berhasil dipindahkan ke detik ke-{totalSec} oleh {ctx.user.name}-nyan'
      )
      await vc.seek(totalSec*1000)

async def setup(bot):
  await bot.add_cog(Songseek(bot))