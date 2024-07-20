import discord
import os
import pymongo
from discord.ext import commands
from discord import app_commands

MONGODB = os.environ['MONGODB']

client = pymongo.MongoClient(MONGODB)
mydb = client["familiardb"]
mycol = mydb["user"]


class Anifav(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name='anifav', description='Set an owned anime character as favorite')
    @app_commands.describe(
        name="The name of anime character to set as favorite")
    async def anime_favorite(self, ctx: discord.Interaction, name: str):
        await ctx.response.defer()

        userFind = mycol.find_one({"userid": str(ctx.user.id)})
        if userFind == None:
            await ctx.followup.send(
                f'Neee {ctx.user.name}-nyan, yuk /regist dulu yuk baru pasang favorite..',
                ephemeral=True)
            return

        animeInven = userFind["animeName"]
        animeIndex = 0
        if name in animeInven:
            for char in animeInven:
                if char == name:
                    break

                animeIndex += 1

            if userFind["animeCount"][animeIndex] <= 0:
                await ctx.followup.send(
                    f'Neee {ctx.user.name}-nyan, anata kayanya halu deh, di inventory anata ngga ada yang namanya {name} loh.. Coba deh dicek lagi',
                    ephemeral=True)
                return

            newvalues = {"$set": {"favani": name}}
            mycol.update_one(userFind, newvalues)
            await ctx.followup.send(
                f'{name} berhasil dijadikan favorite anime dari {ctx.user.name}-nyan!',
                ephemeral=True)

        else:
            await ctx.followup.send(
                f'Neee {ctx.user.name}-nyan, anata kayanya halu deh, di inventory anata ngga ada yang namanya {name} loh.. Atau salah tulis mungkin, coba deh dicek lagi',
                ephemeral=True)
            return


async def setup(bot):
    await bot.add_cog(Anifav(bot))
