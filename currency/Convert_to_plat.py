import discord
import os
import pymongo
import datetime
from discord.ui import Select, Button, Modal, InputText, View
from discord.ext import commands
from discord.commands import Option

guilds = [990445490401341511, 1020927428459241522, 989086863434334279, 494097970208178186, 1028690906901139486]

MONGODB = os.environ['MONGODB']

client = pymongo.MongoClient(MONGODB)
mydb = client["familiardb"]
mycol = mydb["user"]

class Convert_to_plat(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    
  @commands.slash_command(name='converttoplat', description='Convert gold to platina with the entered number ( 100 : 1 )')
  async def convert_to_plat(self, ctx, number: Option(int, "Number of platina to get", required=True)):
    await ctx.defer(ephemeral=True)
    if number <= 0:
        await ctx.respond(f'Neee anata ngga jelas deh, {ctx.author.name}-nyan',
                          ephemeral=True)
        return

    userFind = mycol.find_one({"userid": str(ctx.author.id)})
    if userFind == None:
        await ctx.respond(
            f'{ctx.author.name}-nyan belum terdaftar nih, /regist dulu yuk',
            ephemeral=True)

    else:
        goldCount = userFind["gold"]
        platCount = userFind["platina"]
        if goldCount < (number * 100):
            await ctx.respond(
                f'Gold {ctx.author.name}-nyan tidak cukup buat dijadikan {number} Platina',
                ephemeral=True)
        else:
            goldCount -= (number * 100)
            platCount += number
            newvalues = {"$set": {"platina": platCount, "gold": goldCount}}
            mycol.update_one(userFind, newvalues)
            await ctx.respond(
                f'Convert berhasil, Platina {ctx.author.name}-nyan menjadi {platCount} dan goldnya menjadi {goldCount}',
                ephemeral=True)

def setup(bot):
  bot.add_cog(Convert_to_plat(bot))