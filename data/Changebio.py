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


class ChangeBio(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='changebio', description='Change profile bio')
    @app_commands.describe(bio='Your new bio')
    async def bio_change(self, ctx: discord.Interaction, bio: str):
        userFind = mycol.find_one({"userid": str(ctx.user.id)})
        if userFind == None:
            await ctx.response.send_message(
                f'Neee {ctx.user.name}-nyan, /regist dulu gih baru pasang bio yaa~',
                ephemeral=True)
            return

        newValues = {"$set": {"bio": bio}}
        mycol.update_one(userFind, newValues)
        await ctx.response.send_message(
            f'Berhasil mengganti bio pada profile {ctx.user.name}-nyan menjadi\n[{bio}]',
            ephemeral=True)


async def setup(bot):
    await bot.add_cog(ChangeBio(bot))
