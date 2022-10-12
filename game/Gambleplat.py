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

class Gambleplat(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    
  @commands.slash_command(name='gambleplat', description='Gamble your platina with approximately 50/50 odds of getting double or losing all'
)
  async def platina_gamble(self, ctx, number: Option(int, "Number to gamble", required=True)):
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
        platinaCount = userFind["platina"]
        if number > platinaCount:
            await ctx.respond(
                f'Platina anata ngga cukup, {ctx.author.name}-nyan...',
                ephemeral=True)

        else:
            randValue = random.randint(0, 100)
            if randValue % 2 == 1:
                platinaCount += number
                newvalues = {"$set": {"platina": platinaCount}}
                mycol.update_one(userFind, newvalues)
                await ctx.respond(
                    f'Omedetou! platina {ctx.author.name}-nyan menjadi {platinaCount}',
                    ephemeral=True)

            else:
                platinaCount -= number
                newvalues = {"$set": {"platina": platinaCount}}
                mycol.update_one(userFind, newvalues)
                await ctx.respond(
                    f'Yahh kalah, platina {ctx.author.name}-nyan menjadi {platinaCount}',
                    ephemeral=True)

def setup(bot):
  bot.add_cog(Gambleplat(bot))