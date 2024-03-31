import discord
import os
import pymongo
from discord.ext import commands
from discord import app_commands

guilds = [990445490401341511, 1020927428459241522, 989086863434334279, 494097970208178186, 1028690906901139486]

MONGODB = os.environ['MONGODB']

client = pymongo.MongoClient(MONGODB)
mydb = client["familiardb"]
mycol = mydb["user"]

class Addxp(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    
  @app_commands.command(name='addxp', description='Add exp for the mentioned user (or to self if without mention)')
  @app_commands.checks.has_any_role('Encoder Magang', 'Owner')
  @app_commands.describe(number="number of XP to add", member="member to give XP")
  async def exp_add(self, ctx: discord.Interaction, number: int = 0, member: discord.Member = None):
    await ctx.response.defer()
    if number <= 0:
        await ctx.followup.send(f'Neee {ctx.user.name}-nyan, ngga jelas deh ih',
                          ephemeral=True)
        return

    if not member:
        userID = ctx.user.id
    else:
        userID = member.id

    userFind = mycol.find_one({"userid": str(userID)})
    mentionUser = '<@' + str(userID) + '>'
    if userFind == None:
        await ctx.followup.send(
            f'{mentionUser}-nyan belum terdaftar nih, /regist dulu yuk')

    else:
        xpCount = userFind["exp"]
        levelCount = userFind["level"]
        if number < ((levelCount * 2) - xpCount):
            xpCount += number
            newvalues = {"$set": {"exp": xpCount}}
            mycol.update_one(userFind, newvalues)
            await ctx.followup.send(
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
            await ctx.followup.send(
                f'Level {mentionUser}-nyan berhasil ditambah menjadi {levelCount} dengan EXP {xpCount}/{levelCount*2}'
            )

async def setup(bot):
  await bot.add_cog(Addxp(bot))