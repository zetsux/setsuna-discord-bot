import discord
import os
import pymongo
import datetime
from discord.ui import Select, Button, Modal, TextInput, View
from discord.ext import commands
from discord import app_commands
from discord.commands import Option
import numpy as np

guilds = [990445490401341511, 1020927428459241522, 989086863434334279, 494097970208178186, 1028690906901139486]

MONGODB = os.environ['MONGODB']

client = pymongo.MongoClient(MONGODB)
mydb = client["familiardb"]
mycol = mydb["user"]

class Transfergold(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    
  @app_commands.command(name='transfergold', description='Transfer the entered number of gold to a user')
  async def gold_transfer(self, ctx : discord.Interaction, number: Option(int, "Number of gold to transfer", required=True), member: Option(discord.Member, "Who to transfer gold to", required=True)):
    await ctx.defer()
    if number <= 0:
        await ctx.response.send_message(f'Neee anata ngga jelas deh, {ctx.user.name}-nyan',
                          ephemeral=True)
        return

    userFind = mycol.find_one({"userid": str(ctx.user.id)})
    if userFind == None:
        await ctx.response.send_message(
            f'Neee {ctx.user.name}-nyan, yuk bisa yuk /regist dulu~',
            ephemeral=True)

    targetFind = mycol.find_one({"userid": str(member.id)})
    if targetFind == None:
        await ctx.response.send_message(
            f'Neee {ctx.user.name}-nyan, {member.name}-nyan tuh blom regist, bisa yuk disuruh /regist dulu~',
            ephemeral=True)

    if ctx.user.id == member.id:
        await ctx.response.send_message(
            f'Neee {ctx.user.name}-nyan, masa transfer ke diri sendiri sih {member.name}-nyan...',
            ephemeral=True)

    else:
        goldCount = userFind["gold"]
        if number > goldCount:
            await ctx.response.send_message(
                f'Gold anata ngga cukup, {ctx.user.name}-nyan...',
                ephemeral=True)

        else:
            goldCount = userFind["gold"] - number
            newvalues = {"$set": {"gold": goldCount}}
            mycol.update_one(userFind, newvalues)
            goldCount = targetFind["gold"] + number
            newvalues = {"$set": {"gold": goldCount}}
            mycol.update_one(targetFind, newvalues)
            await ctx.response.send_message(
                f'{ctx.user.name}-nyan berhasil memberikan {number} gold kepada {member.name}-nyan!')

async def setup(bot):
  await bot.add_cog(Transfergold(bot))