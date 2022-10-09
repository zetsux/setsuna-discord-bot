import discord
import os
import pymongo
import datetime
from discord.ui import Select, Button, Modal, InputText, View
from discord.ext import commands
from discord.commands import Option
import numpy as np

guilds = [990445490401341511, 1020927428459241522, 989086863434334279, 494097970208178186, 1028690906901139486]

MONGODB = os.environ['MONGODB']

client = pymongo.MongoClient(MONGODB)
mydb = client["familiardb"]
mycol = mydb["user"]

class Anifav(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    
  @commands.slash_command(name='anifav', description='Set an owned anime character as favorite')
  async def anime_favorite(self, ctx, name: Option(str, "Name of anime to set as favorite", required=True)):
    userFind = mycol.find_one({"userid": str(ctx.author.id)})
    if userFind == None:
        await ctx.respond(
            f'Neee {ctx.author.name}-nyan, yuk /regist dulu yuk baru pasang favorite..',
            ephemeral=True)
        return

    animeInven = userFind["animeName"]
    animeIndex = 0
    if name in animeInven:
        for char in animeInven:
            if char == name:
                break

            animeIndex += 1

        if userFind["animeCount"][animeIndex] <= 0:
            await ctx.respond(
                f'Neee {ctx.author.name}-nyan, anata kayanya halu deh, di inventory anata ngga ada yang namanya {name} loh.. Coba deh dicek lagi',
                ephemeral=True)
            return

        newvalues = {"$set": {"favani": name}}
        mycol.update_one(userFind, newvalues)
        await ctx.respond(
            f'{name} berhasil dijadikan favorite anime dari {ctx.author.name}-nyan!',
            ephemeral=True)

    else:
        await ctx.respond(
            f'Neee {ctx.author.name}-nyan, anata kayanya halu deh, di inventory anata ngga ada yang namanya {name} loh.. Atau salah tulis mungkin, coba deh dicek lagi',
            ephemeral=True)
        return

def setup(bot):
  bot.add_cog(Anifav(bot))