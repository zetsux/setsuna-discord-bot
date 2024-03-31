import discord
import os
import datetime
from discord.ui import Select, Button, Modal, TextInput, View
from discord.ext import commands
from discord import app_commands
from discord.commands import Option

guilds = [990445490401341511, 1020927428459241522, 989086863434334279, 494097970208178186, 1028690906901139486]

class Songhelp(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    
  @app_commands.command(name='songhelp', description='Explains how to use song commands')
  async def song_helpp(self, ctx: discord.Interaction):
    await ctx.defer(ephemeral=True)
    embedVar = discord.Embed(
        title=f"[ Setsuna's Song Commands Help ]",
        description=
        'Seluruh song commands yang terdapat pada watashi diawali dengan kata "song" dan dapat digunakan untuk mendengarkan lagu melalui discord voice channel maupun voice stage!\n',
        color=0x9acd32)
    embedVar.add_field(
        name=f"[ Song Commands List ]",
        value='```' +
        '/songinsert\n  ↪ Digunakan untuk memutar lagu atau menambahkan lagu ke dalam antrian. Masukkan dapat berupa link spotify album, spotify playlist, spotify song, youtube playlist, maupun youtube video. Bila bukan berupa link, maka Setsuna akan mengambil video pertama dari Youtube Search menggunakan keyword masukkan (Setsuna akan masuk ke voice channel pengguna command secara otomatis bila tidak sedang berada di vc)!\n'
        +
        '/songpanel\n  ↪ Berisi berbagai tombol yang dapat digunakan untuk membantu dalam mendengarkan lagu, yakni Resume, Pause, Skip, Loop, Shuffle, dan Disconnect (hanya bila ada satu orang saja di dalam VC atau Setsuna tidak sedang melakukan apa-apa). Selain itu, juga bisa digunakan untuk mengecek lagu yang sedang diputar serta antrian yang menunggu!\n'
        + '```',
        inline=False)
    await ctx.response.send_message(embed=embedVar, ephemeral=True)

async def setup(bot):
  await bot.add_cog(Songhelp(bot))