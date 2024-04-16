import discord
import os
import pymongo
import datetime
from discord.ui import Select, Button, Modal, TextInput, View
from discord.ext import commands
from discord import app_commands
from discord.commands import Option

guilds = [989086863434334279]

MONGODB = os.environ['MONGODB']

client = pymongo.MongoClient(MONGODB)
mydb = client["familiardb"]
mycol = mydb["user"]

class Convert_from_cs(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    
  @app_commands.command(name='convertcstoplat', description='Convert gold in Loraine to platina with the entered number ( 2000 : 1 )')
  async def csconvert_to_plat(self, ctx: discord.Interaction, number: Option(int, "Number of platina to get", required=True)):
    await ctx.defer(ephemeral=True)
    if number <= 0:
        await ctx.response.send_message(f'Neee anata ngga jelas deh, {ctx.user.name}-nyan', ephemeral=True)
        return

    lclient = pymongo.MongoClient(LORENDB)
    lmydb = lclient["LoraineDB"]
    lmycol = lmydb["profilemodels"]
    luserFind = lmycol.find_one({"userID": str(ctx.user.id)})
    userFind = mycol.find_one({"userid": str(ctx.user.id)})
    if userFind == None:
        await ctx.response.send_message(
            f'{ctx.user.name}-nyan belum terdaftar nih, /regist dulu yuk',
            ephemeral=True)

    elif luserFind == None:
        await ctx.response.send_message(
            f'{ctx.user.name}-nyan belum terdaftar di loren nih, /register dulu atau minta role dulu deh..',
            ephemeral=True)

    else:
        goldCount = luserFind["userGold"]
        platCount = userFind["platina"]
        if goldCount < (number * 2000):
            await ctx.response.send_message(
                f'Gold CS {ctx.user.name}-nyan cuma {goldCount}, mana cukup sih buat dijadikan {number} Platina',
                ephemeral=True)
        else:
            goldCount -= (number * 2000)
            platCount += number
            newvalues = {"$set": {"platina": platCount}}
            mycol.update_one(userFind, newvalues)
            newvalues = {"$set": {"userGold": goldCount}}
            lmycol.update_one(luserFind, newvalues)
            await ctx.response.send_message(
                f'Convert berhasil, Platina {ctx.user.name}-nyan menjadi {platCount} dan gold CSnya menjadi {goldCount}',
                ephemeral=True)

async def setup(bot):
  await bot.add_cog(Convert_from_cs(bot))