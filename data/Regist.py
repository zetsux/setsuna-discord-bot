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
    
  @commands.slash_command(name='regist', description='Register your account and create a profile', guild_ids=guilds)
  async def regist(self, ctx):
    checkRegist = mycol.find_one({"userid": str(ctx.author.id)})
    if checkRegist != None:
        await ctx.respond(
            f'Neee {ctx.author.name}-nyan, anata udah kedaftar ih',
            ephemeral=True)

    else:
        mentionUser = '<@' + str(ctx.author.id) + '>'
        await ctx.respond(f'{mentionUser} berhasil terdaftar!\nSilahkan tulis /help untuk mengetahui cara menggunakan Setsuna~')
        d = datetime.datetime.strptime(str(datetime.datetime.now().isoformat()), "%Y-%m-%dT%H:%M:%S.%f")
        newMem = {
            "userid": str(ctx.author.id),
            "level": 1,
            "gold": 500,
            "platina": 0,
            "exp": 0,
            "bio": "None (do /changebio to fill)",
            "daily": '-',
            "pokemon": '-',
            "pokemonlv": -1,
            "gift": False,
            "win": 0,
            "lose": 0,
            "draw": 0,
            "latest": "Never Battled",
            "favani": "None (/anifav to set)",
            "animeName": [],
            "animeCount": [],
            "pokeName": [],
            "pokeLevel": [],
            "hunt": d,
            "epicpity" : 0,
            "legendpity" : 0
        }
        mycol.insert_one(newMem)
        userCounterFind = {"func": "counter"}
        y = mycol.find_one(userCounterFind)
        count = y["usercount"]
        newvalues = {"$set": {"usercount": count + 1}}
        mycol.update_one(userCounterFind, newvalues)

def setup(bot):
  bot.add_cog(Regist(bot))