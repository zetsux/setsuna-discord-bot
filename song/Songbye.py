import discord
import os
import wavelink
from discord.ext import commands
from discord import app_commands
from StaticVars import Songlist

guilds = [990445490401341511, 1020927428459241522, 989086863434334279, 494097970208178186, 1028690906901139486]
SPOTIFYSECRET = os.environ['SPOTIFYSECRET']
SPOTIFYID = os.environ['SPOTIFYID']

class Songbye(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    
  @app_commands.command(description='Disconnect the bot from the voice channel')
  @app_commands.checks.has_any_role('Encoder Magang', 'Owner')
  async def songbye(self, ctx: discord.Interaction):
    if not ctx.guild.voice_client:
        await ctx.response.send_message(
            f'Ihh aneh deh {ctx.user.name}-nyan, watashi aja ngga di vc',
            ephemeral=True)
        return
    elif not ctx.user.voice:
        await ctx.response.send_message('Etlis join vc dlu la dek..', ephemeral=True)
        return
    elif ctx.user.voice.channel != ctx.guild.me.voice.channel:
        await ctx.response.send_message(
            f'Hmph {ctx.user.name}-nyan, watashi ngga mau diatur-atur kalo watashitachi ngga satu vc',
            ephemeral=True)
        return
    else:
        vc: wavelink.Player = ctx.guild.voice_client

    await vc.disconnect()
    Songlist.songList.clear()
    await ctx.response.send_message(
        f'Hmph, watashi dipaksa keluar sama {ctx.user.name}-nyan, yauda deh sayonara'
    )

async def setup(bot):
  await bot.add_cog(Songbye(bot))