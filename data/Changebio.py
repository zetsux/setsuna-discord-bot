import discord
import os
import pymongo
import datetime
from discord.ext import commands

guilds = [990445490401341511, 1020927428459241522, 989086863434334279, 494097970208178186, 1028690906901139486]

MONGODB = os.environ['MONGODB']

client = pymongo.MongoClient(MONGODB)
mydb = client["familiardb"]
mycol = mydb["user"]

class Regist(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    
  @commands.slash_command(name='changebio', description='Change profile bio', guild_ids=guilds)
  async def bio_adding(self, ctx, bio: Option(str, "New bio", required=True)):
      userFind = mycol.find_one({"userid": str(ctx.author.id)})
      if userFind == None:
          await ctx.respond(
              f'Neee {ctx.author.name}-nyan, /regist dulu gih baru pasang bio yaa~',
              ephemeral=True)
          return
  
      newValues = {"$set": {"bio": bio}}
      mycol.update_one(userFind, newValues)
      await ctx.respond(
          f'Berhasil mengganti bio pada profile {ctx.author.name}-nyan menjadi\n[{bio}]',
          ephemeral=True)

def setup(bot):
  bot.add_cog(Regist(bot))