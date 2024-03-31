import discord
import os
import datetime
from discord.ui import Select, Button, Modal, TextInput, View
from discord.ext import commands
from discord import app_commands
from discord.commands import Option

guilds = [990445490401341511, 1020927428459241522, 989086863434334279, 494097970208178186, 1028690906901139486]

class Anihelp(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    
  @app_commands.command(name='anihelp', description='Explains how to use anicommands')
  async def ani_helpp(self, ctx : discord.Interaction):
    await ctx.defer(ephemeral=True)
    embedVar = discord.Embed(
        title=f"[ Setsuna's AniCommands Help ]",
        description=
        'AniCommands pada Setsuna digunakan untuk anata-tachi para manusia yang ingin mengoleksi karakter anime 2D!\n',
        color=0xff69b4)
    embedVar.add_field(
        name=f"[ AniCommands List ]",
        value='```' +
        '/anigacha\n  ↪ Dimana semuanya bermula, tempat anata mendapatkan waifu/husbando dengan mengorbankan 1 Platina saja. Terdiri dari pilihan Male dan Female, dengan hanya satu sentuhan pada tombol, anata akan mendapatkannya!\n'
        +
        '/anifav\n  ↪ Memasangkan karakter anime yang dimiliki pada kolom "Favorite Anime Character" untuk membanggakannya!\n'
        +
        '/anidel\n  ↪ Menghapus sejumlah karakter anime yang dimiliki dari inventory jika diinginkan.\n'
        +
        '/anigive\n  ↪ Memberikan sejumlah karakter anime yang dimiliki dari inventory kepada orang yang dimention secara cuma-cuma.\n'
        +
        '/anitrade\n  ↪ Membuka trading board dengan orang yang dimention untuk saling bertukar koleksi anime.\n'
        + '```',
        inline=False)
    await ctx.response.send_message(embed=embedVar, ephemeral=True)

async def setup(bot):
  await bot.add_cog(Anihelp(bot))