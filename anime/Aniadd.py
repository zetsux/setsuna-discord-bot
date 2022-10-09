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

class Aniadd(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    
  @commands.slash_command(name='aniadd', description='Add the entered number of anime to the mentioned user')
  @commands.has_any_role('Encoder Magang', 'Owner')
  async def anime_add(self, ctx, name: Option(str, "Name of anime to give", required=True), number: Option(int, "Number to give", required=True), member: Option(discord.Member,"Give target", required=True)):
    targetFind = mycol.find_one({"userid": str(member.id)})
    mentionTarget = '<@' + str(member.id) + '>'
    if targetFind == None:
        await ctx.respond(
            f'Neee {mentionTarget}-nyan, yuk /regist yuk, ada yang mau ngegift anata tuhh'
        )

    else:
        await ctx.respond(
            f'Omedetou {mentionTarget}-nyan! Anata mendapatkan {number} {name}!!'
        )
        animeInven = targetFind["animeName"]
        if name in animeInven:
            animeIndex = 0

            for x in animeInven:
                if x == name:
                    break
                animeIndex += 1

            stringIndex = "animeCount." + str(animeIndex)
            newvalues = {
                "$set": {
                    stringIndex: targetFind["animeCount"][animeIndex] + number
                }
            }
            mycol.update_one(targetFind, newvalues)

        else:
            newvalues = {"$push": {"animeName": name, "animeCount": number}}
            mycol.update_one(targetFind, newvalues)

def setup(bot):
  bot.add_cog(Aniadd(bot))