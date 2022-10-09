import discord
import os
import pymongo
import datetime
from discord.ext import commands
from discord.commands import Option

guilds = [990445490401341511, 1020927428459241522, 989086863434334279, 494097970208178186, 1028690906901139486]

MONGODB = os.environ['MONGODB']

client = pymongo.MongoClient(MONGODB)
mydb = client["familiardb"]
mycol = mydb["user"]

class Registfor(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    
  @commands.slash_command(name='registfor', description='Register account and create profile for someone')
  @commands.has_any_role('Encoder Magang', 'Owner')
  async def registfor(self, ctx, member: Option(discord.Member, "Member to register for", required=True)):
    if not member:
        userID = ctx.author.id
    else:
        userID = member.id

    checkRegist = mycol.find_one({"userid": str(userID)})

    if checkRegist != None:
        await ctx.respond(
            f'Neee {ctx.author.name}-nyan, orang yang mau anata daftarin udah kedaftar',
            ephemeral=True)

    else:
        mentionUser = '<@' + str(userID) + '>'
        await ctx.respond(
            f'{ctx.author.name}-nyan berhasil mendaftarkan {mentionUser}!\nSilahkan tulis /help untuk mengetahui cara menggunakan Setsuna~'
        )
        d = datetime.datetime.strptime(
            str(datetime.datetime.now().isoformat()), "%Y-%m-%dT%H:%M:%S.%f")
        newMem = {
            "userid": str(userID),
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
  bot.add_cog(Registfor(bot))