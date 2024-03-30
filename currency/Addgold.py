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

class Addgold(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    
  @commands.slash_command(name='addgold', description='Add gold for the mentioned user (or to self if without mention)')
  @commands.has_any_role('Encoder Magang', 'Owner')
  async def gold_add(self, ctx, number: Option(int, "Number to add", required=True), member: Option(discord.Member, "Who to add gold or self if empty", required=False, default=None)):
    await ctx.defer()
    if number <= 0:
        await ctx.respond(f'Neee anata ngga jelas deh, {ctx.author.name}-nyan',
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
            f'{mentionUser}-nyan, /regist dulu yuk biar bisa ditambah goldnya')

    else:
        goldCount = userFind["gold"] + number
        newvalues = {"$set": {"gold": goldCount}}
        mycol.update_one(userFind, newvalues)
        await ctx.respond(
            f'Goldnya {mentionUser}-nyan berhasil ditambah menjadi {goldCount}'
        )

def setup(bot):
  bot.add_cog(Addgold(bot))