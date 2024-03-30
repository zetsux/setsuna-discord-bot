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

class Reduceplat(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    
  @commands.slash_command(name='reduceplat', description='Reduce platina for the mentioned user (or to self if without mention)')
  @commands.has_any_role('Encoder Magang', 'Owner')
  async def platina_reduce(self, ctx, number: Option(int, "Number to reduce", required=True), member: Option(discord.Member, "Who to reduce platina or self if empty", required=False, default=None)):
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
            f'{mentionUser}-nyan belum terdaftar nih, /regist dulu yuk')

    else:
        platCount = userFind["platina"]
        if platCount == 0:
            await ctx.respond(
                f'Platinanya {mentionUser}-nyan sudah habis nih, apalagi yang mau dikurangi'
            )
        else:
            platCount -= number
            if platCount < 0:
                platCount = 0
            newvalues = {"$set": {"platina": platCount}}
            mycol.update_one(userFind, newvalues)
            await ctx.respond(
                f'Platinanya {mentionUser}-nyan berhasil dikurangi menjadi {platCount}')

def setup(bot):
  bot.add_cog(Reduceplat(bot))