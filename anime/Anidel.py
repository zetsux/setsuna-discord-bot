import discord
import os
import pymongo
import datetime
from discord.ui import Select, Button, Modal, TextInput, View
from discord.ext import commands
from discord.commands import Option
import numpy as np

guilds = [990445490401341511, 1020927428459241522, 989086863434334279, 494097970208178186, 1028690906901139486]

MONGODB = os.environ['MONGODB']

client = pymongo.MongoClient(MONGODB)
mydb = client["familiardb"]
mycol = mydb["user"]

def arrangelb(idUser) :
  inFind = mycol.find_one({'userid' : str(idUser)})

  lbFind = mycol.find_one({'func' : "anilb"})
  newvalues = {'$pull': {'board': str(idUser)}}
  mycol.update_one(lbFind, newvalues)
  
  index = 0
  lbFind = mycol.find_one({'func' : "anilb"})
  lbBoard = lbFind['board']
  dUni = inFind["uniAni"]
  dAll = inFind["allAni"]
  
  for i in lbBoard:
    iUser = mycol.find_one({"userid": i})
    iUni = iUser["uniAni"]
    iAll = iUser["allAni"]

    if dUni > iUni or (dUni == iUni and dAll > iAll):
        break

    index += 1
  
  lbFind = mycol.find_one({'func' : "anilb"})
  newvalues = {"$push": {'board' : {'$each': [str(idUser)], "$position": index}}}
  mycol.update_one(lbFind, newvalues)

class Anidel(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    
  @commands.slash_command(name='anidel', description='Delete anime from your inventory with count is entered number')
  async def anime_remove(self, ctx, name: Option(str, "Name to delete", required=True), number: Option(int, "Number to delete", required=True)):
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
        animeInven = userFind["animeName"]
        mUni = userFind["uniAni"]
        mAll = userFind["allAni"]
        if name in animeInven:
            animeIndex = 0

            for x in animeInven:
                if x == name:
                    break
                animeIndex += 1

            if userFind["animeCount"][animeIndex] < number:
                await ctx.respond(
                    f'Neee {ctx.author.name}-nyan, anata cuma punya {userFind["animeCount"][animeIndex]} {name}',
                    ephemeral=True)

            elif userFind["animeCount"][animeIndex] == number:
                await ctx.respond(
                    f'Omedetou {ctx.author.name}-nyan, penghapusan {number} {name} berhasil. Menghapuskan seluruh koleksi {name} anata'
                )
                stringIndex = "animeCount." + str(animeIndex)
                mycol.update_one(userFind, {"$set": {"uniAni" : mUni - 1, "allAni" : mAll - 1, stringIndex: 0}})
                arrangelb(ctx.author.id)

            elif userFind["animeCount"][animeIndex] > number:
                await ctx.respond(
                    f'Omedetou {ctx.author.name}-nyan, penghapusan {number} {name} berhasil. Membuat jumlah koleksi {name} anata tersisa {userFind["animeCount"][animeIndex] - number}')
              
                stringIndex = "animeCount." + str(animeIndex)
                newvalues = {"$set": {"allAni" : mAll - 1, stringIndex : userFind["animeCount"][animeIndex] - number}}
                mycol.update_one(userFind, newvalues)
                arrangelb(ctx.author.id)

        else:
            await ctx.respond(
                f'Neee {ctx.author.name}-nyan, jangan halu yaa, anata ngga punya yang namanya {name}...\natau salah tulis nama mungkin, coba dicek lagi deh.',
                ephemeral=True)

def setup(bot):
  bot.add_cog(Anidel(bot))