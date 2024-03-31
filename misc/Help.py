import discord
import os
import datetime
from discord.ui import Select, Button, Modal, TextInput, View
from discord.ext import commands
from discord import app_commands
from discord.commands import Option

guilds = [990445490401341511, 1020927428459241522, 989086863434334279, 494097970208178186, 1028690906901139486]

class Help(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    
  @app_commands.command(name='help', description='Shows the guide to use Setsuna')
  async def show_helpp(self, ctx: discord.Interaction):
    await ctx.defer(ephemeral=True)
    embedVar = discord.Embed(
        title=f"Yoroshiku {ctx.user.name}-nyan, watashi wa Setsuna desu!",
        description=
        "Buat pakai watashi tinggal ketik '/' di chat discord, lalu tekan tab yang ada gambar pfp watashinya, nanti keluar deh command-command yang bisa anata pakai!",
        color=ctx.user.color)
    embedVar.add_field(
        name=f"[ Additional Helps List ]",
        value='```' +
        '/songhelp\n↪ All about song commands and how to utilize them!\n' +
        '/anihelp\n↪ All about anime commands and collecting waifu/husbando!\n'
        + "/pokehelp\n↪ All about pokemon commands and catchin'em all!\n" +
        '/spyhelp\n↪ All about spygame and how to play it with nakama-tachi!\n'
        + '/setsuhelp\n↪ All about AI commands and how to use them!\n'
        + '```',
        inline=False)
    await ctx.response.send_message(embed=embedVar, ephemeral=True)

async def setup(bot):
  await bot.add_cog(Help(bot))