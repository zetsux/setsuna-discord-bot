import discord
import os
import pymongo
from discord.ext import commands
from discord import app_commands

MONGODB = os.environ['MONGODB']

client = pymongo.MongoClient(MONGODB)
mydb = client["familiardb"]
mycol = mydb["user"]


class Convert_to_gold(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name='converttogold',
        description='Convert platina to gold with the entered number ( 1 : 100 )'
    )
    @app_commands.describe(number="Number of platina to convert")
    async def convert_to_gold(self, ctx: discord.Interaction, number: int):
        if number <= 0:
            await ctx.response.send_message(
                f'Neee anata ngga jelas deh, {ctx.user.name}-nyan',
                ephemeral=True)
            return

        await ctx.response.defer(ephemeral=True)

        userFind = mycol.find_one({"userid": str(ctx.user.id)})
        if userFind == None:
            await ctx.followup.send(
                f'{ctx.user.name}-nyan belum terdaftar nih, /regist dulu yuk',
                ephemeral=True)

        else:
            goldCount = userFind["gold"]
            platCount = userFind["platina"]
            if platCount < number:
                await ctx.followup.send(
                    f'Platina {ctx.user.name}-nyan tidak cukup buat dijadikan {number*100} Gold',
                    ephemeral=True)
            else:
                goldCount += (number * 100)
                platCount -= number
                newvalues = {"$set": {"platina": platCount, "gold": goldCount}}
                mycol.update_one(userFind, newvalues)
                await ctx.followup.send(
                    f'Convert berhasil, Platina {ctx.user.name}-nyan menjadi {platCount} dan goldnya menjadi {goldCount}',
                    ephemeral=True)


async def setup(bot):
    await bot.add_cog(Convert_to_gold(bot))
