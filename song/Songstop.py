import discord
import os
import wavelink
from wavelink.ext import spotify
from discord.ui import Select, Button, Modal, InputText, View
from discord.ext import commands
from discord.commands import Option

guilds = [990445490401341511, 1020927428459241522, 989086863434334279, 494097970208178186, 1028690906901139486]
SPOTIFYSECRET = os.environ['SPOTIFYSECRET']
SPOTIFYID = os.environ['SPOTIFYID']

class Songstop(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    
  @commands.slash_command(description='Force stop current song and clear all song in queue')
  @commands.has_any_role('Encoder Magang', 'Owner')
  async def songstop(self, ctx):
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

    setattr(vc, "loop", False)
    await ctx.respond(
        f'Seluruh musik berhasil dihentikan dan dikosongkan secara paksa oleh {ctx.author.name}-nyan')
    await vc.stop()
    await vc.queue.clear()

def setup(bot):
  bot.add_cog(Songstop(bot))