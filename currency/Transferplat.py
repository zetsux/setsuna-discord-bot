import discord
import os
import pymongo
from discord.ext import commands
from discord import app_commands

MONGODB = os.environ['MONGODB']

client = pymongo.MongoClient(MONGODB)
mydb = client["familiardb"]
mycol = mydb["user"]


class Transferplat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name='transferplat',
        description='Transfer the entered number of plat to a user')
    @app_commands.describe(number="Number of platina to transfer",
                           member="The member to transfer platina to")
    async def plat_transfer(self, ctx: discord.Interaction, number: int,
                            member: discord.Member):
        if number <= 0:
            await ctx.response.send_message(
                f'Neee anata ngga jelas deh, {ctx.user.name}-nyan',
                ephemeral=True)
            return

        await ctx.response.defer()

        userFind = mycol.find_one({"userid": str(ctx.user.id)})
        if userFind == None:
            await ctx.followup.send(
                f'Neee {ctx.user.name}-nyan, yuk bisa yuk /regist dulu~',
                ephemeral=True)

        targetFind = mycol.find_one({"userid": str(member.id)})
        if targetFind == None:
            await ctx.followup.send(
                f'Neee {ctx.user.name}-nyan, {member.name}-nyan tuh blom regist, bisa yuk disuruh /regist dulu~',
                ephemeral=True)

        if ctx.user.id == member.id:
            await ctx.followup.send(
                f'Neee {ctx.user.name}-nyan, masa transfer ke diri sendiri sih {member.name}-nyan...',
                ephemeral=True)

        else:
            platinaCount = userFind["platina"]
            if number > platinaCount:
                await ctx.followup.send(
                    f'Platina anata ngga cukup, {ctx.user.name}-nyan...',
                    ephemeral=True)

            else:
                platinaCount = userFind["platina"] - number
                newvalues = {"$set": {"platina": platinaCount}}
                mycol.update_one(userFind, newvalues)
                platinaCount = targetFind["platina"] + number
                newvalues = {"$set": {"platina": platinaCount}}
                mycol.update_one(targetFind, newvalues)
                await ctx.followup.send(
                    f'{ctx.user.name}-nyan berhasil memberikan {number} platina kepada {member.name}-nyan!'
                )


async def setup(bot):
    await bot.add_cog(Transferplat(bot))
