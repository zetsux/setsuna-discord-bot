import discord
import os
import pymongo
import datetime
from discord.ui import Select, Button, Modal, TextInput, View
from discord.ext import commands
from discord import app_commands
from discord.commands import Option

guilds = [990445490401341511, 1020927428459241522, 989086863434334279, 494097970208178186, 1028690906901139486]

MONGODB = os.environ['MONGODB']

client = pymongo.MongoClient(MONGODB)
mydb = client["familiardb"]
mycol = mydb["user"]

class Convert_to_plat(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    
  @app_commands.command(name='converttoplat', description='Convert gold to platina with the entered number ( 100 : 1 )')
  async def convert_to_plat(self, ctx : discord.Interaction, number: Option(int, "Number of platina to get", required=True)):
    await ctx.defer(ephemeral=True)
    if number <= 0:
        await ctx.response.send_message(f'Neee anata ngga jelas deh, {ctx.user.name}-nyan',
                          ephemeral=True)
        return

    userFind = mycol.find_one({"userid": str(ctx.user.id)})
    if userFind == None:
        await ctx.response.send_message(
            f'{ctx.user.name}-nyan belum terdaftar nih, /regist dulu yuk',
            ephemeral=True)

    else:
        goldCount = userFind["gold"]
        platCount = userFind["platina"]
        if goldCount < (number * 100):
            await ctx.response.send_message(
                f'Gold {ctx.user.name}-nyan tidak cukup buat dijadikan {number} Platina',
                ephemeral=True)
        else:
            goldCount -= (number * 100)
            platCount += number
            newvalues = {"$set": {"platina": platCount, "gold": goldCount}}
            mycol.update_one(userFind, newvalues)
            await ctx.response.send_message(
                f'Convert berhasil, Platina {ctx.user.name}-nyan menjadi {platCount} dan goldnya menjadi {goldCount}',
                ephemeral=True)

async def setup(bot):
  await bot.add_cog(Convert_to_plat(bot))