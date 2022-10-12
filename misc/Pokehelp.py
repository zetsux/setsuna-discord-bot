import discord
import os
import datetime
from discord.ui import Select, Button, Modal, InputText, View
from discord.ext import commands
from discord.commands import Option

guilds = [990445490401341511, 1020927428459241522, 989086863434334279, 494097970208178186, 1028690906901139486]

class Pokehelp(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    
  @commands.slash_command(name='pokehelp', description='Explains how to use pokecommands')
  async def poke_helpp(self, ctx):
    await ctx.defer(ephemeral=True)
    embedVar = discord.Embed(
        title=f"[ Setsuna's PokeCommands Help ]",
        description=
        'PokeCommands hadir di Setsuna bagi anata-tachi para penggemar pokemon yang ingin menangkap, mengoleksi, mempelajari, melatih, dan juga berduel dengan pokemon kalian\n',
        color=0xee1515)
    embedVar.add_field(
        name=f"[ PokeCommands List ]",
        value='```' +
        '/pokecatch\n  ↪ Awal dari perjalanan pokemon anata, tempat anata menangkap pokemon dengan bermodalkan 1 platina. Terdiri dari Rarity Basic dengan chance 67%, Advanced dengan chance 25%, Epic dengan chance 7%, dan Legendary dengan chance 1% (Gen 1 - 5)\n'
        +
        '/pokeinfo\n  ↪ Digunakan untuk mengecek atau mempelajari tentang suatu pokemon yang sudah tersedia di /pokecatch!\n'
        +
        '/pokepartner\n  ↪ Digunakan untuk mengecek atau mengganti partner pokemon battle anata secara diam-diam.\n'
        +
        '/pokeduel\n  ↪ Melakukan matchmaking dan mencari lawan untuk berduel menggunakan pokemon satu sama lain. Pokemon Duel pada bot Setsuna agak berbeda dimana terdapat 6 tipe Move yang dapat dilakukan dalam setiap turn player\n'
        + '```',
        inline=False)
    embedVar.add_field(
        name=f"[ PokeDuel Move List ]",
        value='```' +
        '➤ Attack : Menyerang pokemon lawan dengan 100% status Atk dan dikurangi oleh status Def lawan ( Terpengaruh oleh Type Effectivity )\n'
        +
        '➤ Special : Menyerang pokemon lawan dengan 100% status Sp. Atk dan dikurangi oleh status Sp. Def lawan ( Terpengaruh oleh Type Effectivity )\n'
        +
        '➤ Alt. Attack : Menyerang pokemon lawan dengan 65% status Atk dan dikurangi oleh status Def lawan ( Tidak terpengaruh oleh Type Effectivity )\n'
        +
        '➤ Alt. Special : Menyerang pokemon lawan dengan 65% status Sp. Atk dan dikurangi oleh status Sp. Def lawan ( Tidak terpengaruh oleh Type Effectivity )\n'
        + '➤ Boost Atk : Meningkatkan status Atk pokemon sebanyak 1 stage\n'
        '➤ Boost Atk : Meningkatkan status Sp. Atk pokemon sebanyak 1 stage\n'
        + '```',
        inline=False)
    await ctx.respond(embed=embedVar, ephemeral=True)

def setup(bot):
  bot.add_cog(Pokehelp(bot))