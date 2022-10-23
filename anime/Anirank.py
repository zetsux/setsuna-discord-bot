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

class Anirank(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    
  @commands.slash_command(name='anirank', description='Check the leaderboard to see who is the best anime collector')
  async def anime_rank(self, ctx):
    targetFind = mycol.find_one({"userid": str(ctx.author.id)})
    mentionTarget = '<@' + str(ctx.author.id) + '>'
    if targetFind == None:
      await ctx.respond(f'Neee {mentionTarget}-nyan, yuk /regist yuk, ada yang mau ngegift anata tuhh')

    else:
      await ctx.defer()
      aniLB = mycol.find_one({"func" : "anilb"})
      aniBoard = aniLB["board"]

      lbString = "```"

      rank = 1
      noSelf = True
      for id in aniBoard :
        try :
          user = self.bot.get_user(int(id))
          username = user.name
        except :
          continue
          
        if rank <= 15 :
          if id == str(ctx.author.id) :
            uniUser = targetFind["uniAni"]
            allUser = targetFind["allAni"]
            lbString += f"{rank}) {username} (You) [{uniUser}/{allUser}]\n"
            noSelf = False
  
          else :
            userFind = mycol.find_one({"userid": id})
            uniUser = userFind["uniAni"]
            allUser = userFind["allAni"]
            lbString += f"{rank}) {username} [{uniUser}/{allUser}]\n"

        elif noSelf :
          if id == str(ctx.author.id) :
            uniUser = targetFind["uniAni"]
            allUser = targetFind["allAni"]

            if rank == 17 :
              lbString += ".\n"

            elif rank == 18 :
              lbString += ".\n.\n"

            else : 
              lbString += ".\n.\n.\n"
              
            lbString += f"{rank}) {username} (You) [{uniUser}/{allUser}]\n"
            noSelf = False

        else :
          break

        rank += 1
        
      embedVar = discord.Embed(
          title="「 Anime Collector Leaderboard 」",
          description=
          f"{lbString}```\n",
          color=0xFFD700)
      embedVar.set_thumbnail(url='https://cdn.discordapp.com/attachments/995337235211763722/1033605605484662874/hoho-omoshiroi_1.gif')
      embedVar.set_footer(text="Note :\n[Unique Owned Anime Count/All Owned Anime Count]", icon_url=ctx.author.avatar.url)
      await ctx.respond(embed=embedVar)

def setup(bot):
  bot.add_cog(Anirank(bot))