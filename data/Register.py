import discord
import os
import pymongo
import datetime
from discord.ext import commands
from discord import app_commands

MONGODB = os.environ['MONGODB']

client = pymongo.MongoClient(MONGODB)
mydb = client["familiardb"]
mycol = mydb["user"]


class Register(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name='regist',
        description='Register your account and create a profile')
    async def register_account(self, ctx: discord.Interaction):
        checkRegist = mycol.find_one({"userid": str(ctx.user.id)})
        if checkRegist != None:
            await ctx.response.send_message(
                f'Neee {ctx.user.name}-nyan, anata udah kedaftar ih',
                ephemeral=True)

        else:
            mentionUser = '<@' + str(ctx.user.id) + '>'
            await ctx.response.send_message(
                f'{mentionUser} berhasil terdaftar!\nSilahkan tulis /help untuk mengetahui cara menggunakan Setsuna~'
            )
            d = datetime.datetime.strptime(
                str(datetime.datetime.now().isoformat()),
                "%Y-%m-%dT%H:%M:%S.%f")
            newMem = {
                "userid": str(ctx.user.id),
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
    await bot.add_cog(Register(bot))
