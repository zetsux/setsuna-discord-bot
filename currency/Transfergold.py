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

class Transfergold(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    
  @commands.slash_command(name='transfergold', description='Transfer the entered number of gold to a user')
  async def gold_transfer(self, ctx, number: Option(int, "Number of gold to transfer", required=True), member: Option(discord.Member, "Who to transfer gold to", required=True)):
    await ctx.defer()
    if number <= 0:
        await ctx.respond(f'Neee anata ngga jelas deh, {ctx.author.name}-nyan',
                          ephemeral=True)
        return

    userFind = mycol.find_one({"userid": str(ctx.author.id)})
    if userFind == None:
        await ctx.respond(
            f'Neee {ctx.author.name}-nyan, yuk bisa yuk /regist dulu~',
            ephemeral=True)

    targetFind = mycol.find_one({"userid": str(member.id)})
    if targetFind == None:
        await ctx.respond(
            f'Neee {ctx.author.name}-nyan, {member.name}-nyan tuh blom regist, bisa yuk disuruh /regist dulu~',
            ephemeral=True)

    if ctx.user.id == member.id:
        await ctx.respond(
            f'Neee {ctx.author.name}-nyan, masa transfer ke diri sendiri sih {member.name}-nyan...',
            ephemeral=True)

    else:
        goldCount = userFind["gold"]
        if number > goldCount:
            await ctx.respond(
                f'Gold anata ngga cukup, {ctx.author.name}-nyan...',
                ephemeral=True)

        else:
            goldCount = userFind["gold"] - number
            newvalues = {"$set": {"gold": goldCount}}
            mycol.update_one(userFind, newvalues)
            goldCount = targetFind["gold"] + number
            newvalues = {"$set": {"gold": goldCount}}
            mycol.update_one(targetFind, newvalues)
            await ctx.respond(
                f'{ctx.author.name}-nyan berhasil memberikan {number} gold kepada {member.name}-nyan!')

def setup(bot):
  bot.add_cog(Transfergold(bot))