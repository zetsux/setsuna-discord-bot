import discord
import os
import datetime
from discord.ui import Select, Button, Modal, TextInput, View
from discord.ext import commands
from discord import app_commands
from discord.commands import Option

guilds = [990445490401341511, 1020927428459241522, 989086863434334279, 494097970208178186, 1028690906901139486]

class Spyhelp(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    
  @app_commands.command(name='spyhelp', description='Explains how to play SpyGame')
  async def spy_helpp(self, ctx : discord.Interaction):
    await ctx.defer(ephemeral=True)
    embedVar = discord.Embed(
        title=f"[ Setsuna's SpyGame Help ]",
        description=
        'SpyGame merupakan adaptasi dari SpyFall yang di bawa ke Setsuna untuk dimainkan oleh minimal 3 orang! Dapat dimainkan dengan menggunakan command /spygame\n',
        color=0x330066)
    embedVar.add_field(
        name=f"[ How To Play ]",
        value='```' +
        '1) Setelah permainan dimulai, para pemain akan mendapatkan rolenya masing-masing secara random. 1 Pemain akan menjadi Spy dan sisanya menjadi Citizen\n2) Akan diberikan durasi waktu tergantung dari jumlah pemain dan para pemain dapat saling bertanya jawab sesuai dengan giliran yang diberikan. Pemain akan bergantian sesuai giliran menunjuk satu orang lain dan memberikannya satu pertanyaan yang berhubungan dengan lokasi. Ini akan dilakukan hingga waktu habis atau voting dimulai secara paksa\n3) Tombol "Start Vote" dapat ditekan apabila sudah merasa yakin dan apabila kuota tercukupi maka permainan akan langsung memasuki babak Voting\n4) Pada babak voting, setiap pemain diberi kesempatan untuk memasang satu vote terhadap satu orang pilihannya secara anonymous dan menebak siapa spynya berdasarkan tanya jawab\n5) Kemudian Spy akan diberi kesempatan untuk memilih lokasi dari pilihan yang ada dan barulah diumumkan hasil permainannya.'
        + '```',
        inline=False)
    embedVar.add_field(
        name=f"[ Roles ]",
        value='```' +
        '➤ Citizen : Seluruh citizen dalam satu game akan mendapatkan lokasi pertemuan yang sama dan harus melindunginya dari Spy. Tugas dari Citizen adalah mencari tahu siapa Spynya tanpa membongkar lokasi pertemuan mereka melalui serangkaian tanya jawab dengan hati-hati.\n'
        +
        '➤ Spy : Hanya ada 1 Spy dalam suatu game yang tidak mendapatkan lokasi. Tugasnya adalah mencari tahu lokasi pertemuan para Citizen melalui serangkaian tanya jawab sambil membaur dengan mereka tanpa membongkar kedoknya sendiri\n'
        + '```',
        inline=True)
    embedVar.add_field(
        name=f"[ Outcomes ]",
        value='```' +
        '➤ Citizens Win\n  ↪ Spy tertangkap dan lokasi gagal ditebak oleh Spy\n'
        +
        '➤ Spy Win\n  ↪ Lokasi berhasil ditebak oleh spy dan spy tidak tertangkap\n'
        +
        '➤ Draw\n  ↪ Lokasi berhasil ditebak oleh spy namun spy tertangkap / Lokasi gagal ditebak oleh spy dan spy tidak tertangkap\n'
        + '```',
        inline=True)
    await ctx.response.send_message(embed=embedVar, ephemeral=True)

async def setup(bot):
  await bot.add_cog(Spyhelp(bot))