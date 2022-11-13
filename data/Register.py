import discord
import os
import pymongo
import datetime
from discord.ext import commands

MONGODB = os.environ['MONGODB']

client = pymongo.MongoClient(MONGODB)
mydb = client["familiardb"]
mycol = mydb["user"]

class Register(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    
  @commands.slash_command(name='regist', description='Register your account and create a profile')
  async def register_account(self, ctx):
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
            "legendpity" : 0,
            "allAni" : 0,
            "uniAni" : 0
        }
        mycol.insert_one(newMem)
        userCounterFind = {"func": "counter"}
        y = mycol.find_one(userCounterFind)
        count = y["usercount"]
        newvalues = {"$set": {"usercount": count + 1}}
        mycol.update_one(userCounterFind, newvalues)

def setup(bot):
  bot.add_cog(Register(bot))