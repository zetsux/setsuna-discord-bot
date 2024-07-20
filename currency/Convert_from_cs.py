import discord
import os
import pymongo
from discord.ext import commands
from discord import app_commands

guilds = [discord.Object(id=989086863434334279)]

MONGODB = os.environ['MONGODB']
LORENDB = os.environ['LORENDB']

client = pymongo.MongoClient(MONGODB)
mydb = client["familiardb"]
mycol = mydb["user"]


class Convert_from_cs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name='convertcstoplat',
        description=
        'Convert gold in Loraine to platina with the entered number ( 2000 : 1 )'
    )
    @app_commands.guilds(*guilds)
    @app_commands.describe(number="Number of platina to get")
    async def csconvert_to_plat(self, ctx: discord.Interaction, number: int):
        if number <= 0:
            await ctx.response.send_message(
                f'Neee anata ngga jelas deh, {ctx.user.name}-nyan',
                ephemeral=True)
            return

        await ctx.response.defer(ephemeral=True)

        lclient = pymongo.MongoClient(LORENDB)
        lmydb = lclient["LoraineDB"]
        lmycol = lmydb["profilemodels"]
        luserFind = lmycol.find_one({"userID": str(ctx.user.id)})
        userFind = mycol.find_one({"userid": str(ctx.user.id)})
        if userFind == None:
            await ctx.followup.send(
                f'{ctx.user.name}-nyan belum terdaftar nih, /regist dulu yuk',
                ephemeral=True)

        elif luserFind == None:
            await ctx.followup.send(
                f'{ctx.user.name}-nyan belum terdaftar di loren nih, /register dulu atau minta role dulu deh..',
                ephemeral=True)

        else:
            goldCount = luserFind["userGold"]
            platCount = userFind["platina"]
            if goldCount < (number * 2000):
                await ctx.followup.send(
                    f'Gold CS {ctx.user.name}-nyan cuma {goldCount}, mana cukup sih buat dijadikan {number} Platina',
                    ephemeral=True)
            else:
                goldCount -= (number * 2000)
                platCount += number
                newvalues = {"$set": {"platina": platCount}}
                mycol.update_one(userFind, newvalues)
                newvalues = {"$set": {"userGold": goldCount}}
                lmycol.update_one(luserFind, newvalues)
                await ctx.followup.send(
                    f'Convert berhasil, Platina {ctx.user.name}-nyan menjadi {platCount} dan gold CSnya menjadi {goldCount}',
                    ephemeral=True)


async def setup(bot):
    await bot.add_cog(Convert_from_cs(bot))
