import discord
import os
import pymongo
import datetime
from discord.ext import commands
from discord.commands import Option
import random

guilds = [990445490401341511, 1020927428459241522, 989086863434334279, 494097970208178186, 1028690906901139486]

MONGODB = os.environ['MONGODB']

client = pymongo.MongoClient(MONGODB)
mydb = client["familiardb"]
mycol = mydb["user"]

class Gamblegold(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    
  @commands.slash_command(name='gamblegold', description='Gamble your gold with approximately 50/50 odds of getting double or losing all')
  async def gold_gamble(self, ctx, number: Option(int, "Number to add", required=True)):
    if number <= 0:
        await ctx.respond(f'Neee anata ngga jelas deh, {ctx.author.name}-nyan',
                          ephemeral=True)
        return

    userFind = mycol.find_one({"userid": str(ctx.author.id)})
    if userFind == None:
        await ctx.respond(
            f'Neee {ctx.author.name}-nyan, yuk bisa yuk /regist dulu~',
            ephemeral=True)

    else:
        goldCount = userFind["gold"]
        if number > goldCount:
            await ctx.respond(
                f'Gold anata ngga cukup, {ctx.author.name}-nyan...',
                ephemeral=True)

        else:
            randValue = random.randint(0, 100)
            if randValue % 2 == 1:
                goldCount += number
                newvalues = {"$set": {"gold": goldCount}}
                mycol.update_one(userFind, newvalues)
                await ctx.respond(
                    f'Omedetou! Gold {ctx.author.name}-nyan menjadi {goldCount}',
                    ephemeral=True)

            else:
                goldCount -= number
                newvalues = {"$set": {"gold": goldCount}}
                mycol.update_one(userFind, newvalues)
                await ctx.respond(
                    f'Yahh kalah, gold {ctx.author.name}-nyan menjadi {goldCount}',
                    ephemeral=True)

def setup(bot):
  bot.add_cog(Gamblegold(bot))