import discord
import os
import datetime
import random
from discord.ui import Select, Button, Modal, TextInput, View
from discord.ext import commands
from discord.commands import Option

guilds = [990445490401341511, 1020927428459241522, 989086863434334279, 494097970208178186, 1028690906901139486]

class RNG(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    
  @commands.slash_command(name='rng', description='Generates a random number from 1 to the entered number')
  async def random_number_generate(self, ctx, max: Option(int, "Max range of rng", required=True), count: Option(int, "Number of rolls wanted", required=False, default=1)):
    await ctx.defer()
    if max > 1 and count >= 1:
        rngStr = ""

        for n in range(count):
            randValue = random.randint(1, max)
            if n % 2 == 0:
                rngStr = rngStr + f"➳ {n+1}) [{randValue}]\n"

            else:
                rngStr = rngStr + f"➸ {n+1}) [{randValue}]\n"

        embedVar = discord.Embed(
            title=f"[ RNG Result ( 1 - {max} | {count}x ) ]",
            description=f"```{rngStr}```",
            color=ctx.user.color)
        embedVar.set_author(name=ctx.author.name,
                            icon_url=ctx.author.avatar.url)
        await ctx.respond(embed=embedVar)

    elif max <= 1:
        await ctx.respond(
            f'Neee {ctx.author.name}-nyan, yang bener dong masukkin angka maxnya. Masa maxnya {max} sih..',
            ephemeral=True)

    elif count < 1:
        await ctx.respond(
            f'Neee {ctx.author.name}-nyan, yang bener dong masukkin countnya. Masa countnya {count} sih..',
            ephemeral=True)

def setup(bot):
  bot.add_cog(RNG(bot))