import discord
import os
import pymongo
from discord.ext import commands
from discord import app_commands
import random

MONGODB = os.environ['MONGODB']

client = pymongo.MongoClient(MONGODB)
mydb = client["familiardb"]
mycol = mydb["user"]


class Gamblegold(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name='gamblegold',
        description='Gamble your gold with approximately 50/50 odds of getting double or losing all'
    )
    @app_commands.describe(number="Number of gold to gamble")
    async def gold_gamble(self, ctx: discord.Interaction, number: int):
        if number <= 0:
            await ctx.response.send_message(
                f'Neee anata ngga jelas deh, {ctx.user.name}-nyan',
                ephemeral=True)
            return

        userFind = mycol.find_one({"userid": str(ctx.user.id)})
        if userFind == None:
            await ctx.response.send_message(
                f'Neee {ctx.user.name}-nyan, yuk bisa yuk /regist dulu~',
                ephemeral=True)

        else:
            goldCount = userFind["gold"]
            if number > goldCount:
                await ctx.response.send_message(
                    f'Gold anata ngga cukup, {ctx.user.name}-nyan...',
                    ephemeral=True)

            else:
                randValue = random.randint(0, 100)
                if randValue % 2 == 1:
                    goldCount += number
                    newvalues = {"$set": {"gold": goldCount}}
                    mycol.update_one(userFind, newvalues)
                    await ctx.response.send_message(
                        f'Omedetou! Gold {ctx.user.name}-nyan menjadi {goldCount}',
                        ephemeral=True)

                else:
                    goldCount -= number
                    newvalues = {"$set": {"gold": goldCount}}
                    mycol.update_one(userFind, newvalues)
                    await ctx.response.send_message(
                        f'Yahh kalah, gold {ctx.user.name}-nyan menjadi {goldCount}',
                        ephemeral=True)


async def setup(bot):
    await bot.add_cog(Gamblegold(bot))
