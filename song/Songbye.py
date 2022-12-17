import discord
import os
import wavelink
from wavelink.ext import spotify
from discord.ui import Select, Button, Modal, InputText, View
from discord.ext import commands
from discord.commands import Option
from StaticVars import Songlist

guilds = [990445490401341511, 1020927428459241522, 989086863434334279, 494097970208178186, 1028690906901139486]
SPOTIFYSECRET = os.environ['SPOTIFYSECRET']
SPOTIFYID = os.environ['SPOTIFYID']

class Songbye(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    
  @commands.slash_command(description='Disconnect the bot from the voice channel')
  @commands.has_any_role('Encoder Magang', 'Owner')
  async def songbye(self, ctx):
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

    await vc.disconnect()
    Songlist.songList.clear()
    await ctx.respond(
        f'Hmph, watashi dipaksa keluar sama {ctx.author.name}-nyan, yauda deh sayonara'
    )

def setup(bot):
  bot.add_cog(Songbye(bot))