import discord
import os
import pymongo
import datetime
from discord.ui import Select, Button, Modal, TextInput, View
from discord.ext import commands
from discord.commands import Option

guilds = [990445490401341511, 1020927428459241522, 989086863434334279, 494097970208178186, 1028690906901139486]

MONGODB = os.environ['MONGODB']

client = pymongo.MongoClient(MONGODB)
mydb = client["familiardb"]
mycol = mydb["user"]

class Addxp(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    
  @commands.slash_command(name='addxp', description='Add exp for the mentioned user (or to self if without mention)')
  @commands.has_any_role('Encoder Magang', 'Owner')
  async def exp_add(self, ctx, number: Option(int, "Number to add", required=True), member: Option(discord.Member, "Who to give xp or self if empty", required=False, default=None)):
    await ctx.defer()
    if number <= 0:
        await ctx.respond(f'Neee {ctx.author.name}-nyan, ngga jelas deh ih',
                          ephemeral=True)
        return

    if not member:
        userID = ctx.author.id
    else:
        userID = member.id

    userFind = mycol.find_one({"userid": str(userID)})
    mentionUser = '<@' + str(userID) + '>'
    if userFind == None:
        await ctx.respond(
            f'{mentionUser}-nyan belum terdaftar nih, /regist dulu yuk')

    else:
        xpCount = userFind["exp"]
        levelCount = userFind["level"]
        if number < ((levelCount * 2) - xpCount):
            xpCount += number
            newvalues = {"$set": {"exp": xpCount}}
            mycol.update_one(userFind, newvalues)
            await ctx.respond(
                f'Level {mentionUser}-nyan berhasil ditambah menjadi {levelCount} dengan EXP {xpCount}/{levelCount*2}'
            )

        else:
            number -= ((levelCount * 2) - xpCount)
            levelCount += 1

            while number >= (levelCount * 2):
                number -= (levelCount * 2)
                levelCount += 1

            xpCount = number
            newvalues = {"$set": {"level": levelCount, "exp": xpCount}}
            mycol.update_one(userFind, newvalues)
            await ctx.respond(
                f'Level {mentionUser}-nyan berhasil ditambah menjadi {levelCount} dengan EXP {xpCount}/{levelCount*2}'
            )

def setup(bot):
  bot.add_cog(Addxp(bot))