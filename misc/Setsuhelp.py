import discord
import os
import datetime
from discord.ui import Select, Button, Modal, TextInput, View
from discord.ext import commands
from discord import app_commands
from discord.commands import Option

guilds = [990445490401341511, 1020927428459241522, 989086863434334279, 494097970208178186, 1028690906901139486]

class Setsuhelp(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    
  @app_commands.command(name='setsuhelp', description='Explains how to use AI commands')
  async def setsu_helpp(self, ctx: discord.Interaction):
    await ctx.defer(ephemeral=True)
    embedVar = discord.Embed(
        title=f"[ Setsuna's AI Commands Help ]",
        description=
        'Seluruh AI commands yang terdapat pada watashi diawali dengan kata "setsu" dan dapat digunakan untuk membantu keperluan kalian!\n',
        color=0x9457EB)
    embedVar.add_field(
        name=f"[ AI Commands List ]",
        value='```' +
        '/setsuchat\n  ↪ Digunakan untuk berkomunikasi dengan AI melalui Setsuna, dapat menanyakan suatu pertanyaan, meminta Setsuna melakukan sesuatu, meminta Setsuna membuatkan sesuatu, dan masih banyak lagi!\n'
        +
        '/setsualter\n  ↪ Digunakan untuk melakukan perubahan terhadap teks yang dimasukkan sesuai dengan instruksi yang diberikan oleh user. Dapat digunakan untuk memperbaiki kesalahan dalam teks, grammar-fixing, memperbaiki code, dan lain-lain!\n'
        +
        '/setsuimgl\n  ↪ Digunakan untuk melakukan generate terhadap gambar sesuai dengan prompt yang diberikan oleh user dalam jumlah tertentu!\n'
        + '```',
        inline=False)
    await ctx.response.send_message(embed=embedVar, ephemeral=True)

async def setup(bot):
  await bot.add_cog(Setsuhelp(bot))