import discord
import os
import pymongo
import datetime
from discord.ext import commands
from discord import app_commands

guilds = [
    990445490401341511, 1020927428459241522, 989086863434334279,
    494097970208178186, 1028690906901139486
]

MONGODB = os.environ['MONGODB']

client = pymongo.MongoClient(MONGODB)
mydb = client["familiardb"]
mycol = mydb["user"]


class Registfor(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name='registfor',
        description='Register account and create profile for someone')
    @app_commands.checks.has_any_role('Encoder Magang', 'Owner')
    @app_commands.describe(member='The member to register')
    async def registfor(self, ctx : discord.Interaction, member: discord.Member):
        if not member:
            userID = ctx.user.id
        else:
            userID = member.id

        checkRegist = mycol.find_one({"userid": str(userID)})

        if checkRegist != None:
            await ctx.response.send_message(
                f'Neee {ctx.user.name}-nyan, orang yang mau anata daftarin udah kedaftar',
                ephemeral=True)

        else:
            mentionUser = '<@' + str(userID) + '>'
            await ctx.response.send_message(
                f'{ctx.user.name}-nyan berhasil mendaftarkan {mentionUser}!\nSilahkan tulis /help untuk mengetahui cara menggunakan Setsuna~'
            )
            d = datetime.datetime.strptime(
                str(datetime.datetime.now().isoformat()),
                "%Y-%m-%dT%H:%M:%S.%f")
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
                "epicpity": 0,
                "legendpity": 0,
                "allAni": 0,
                "uniAni": 0
            }
            mycol.insert_one(newMem)
            userCounterFind = {"func": "counter"}
            y = mycol.find_one(userCounterFind)
            count = y["usercount"]
            newvalues = {"$set": {"usercount": count + 1}}
            mycol.update_one(userCounterFind, newvalues)


async def setup(bot):
    await bot.add_cog(Registfor(bot))
