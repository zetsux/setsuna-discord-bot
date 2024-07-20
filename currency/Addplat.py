import discord
import os
import pymongo
from discord.ext import commands
from discord import app_commands

MONGODB = os.environ['MONGODB']

client = pymongo.MongoClient(MONGODB)
mydb = client["familiardb"]
mycol = mydb["user"]


class Addplat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name='addplat',
        description=
        'Add platina for the mentioned user (or to self if without mention)')
    @app_commands.checks.has_any_role('Encoder Magang', 'Owner')
    @app_commands.describe(
        number="Number of platina to add",
        member="The member to add platina to (or self if empty)")
    async def platina_add(self,
                          ctx: discord.Interaction,
                          number: int,
                          member: discord.Member = None):
        if number <= 0:
            await ctx.response.send_message(
                f'Neee anata ngga jelas deh, {ctx.user.name}-nyan',
                ephemeral=True)
            return

        await ctx.response.defer()

        if not member:
            userID = ctx.user.id
        else:
            userID = member.id

        userFind = mycol.find_one({"userid": str(userID)})
        mentionUser = '<@' + str(userID) + '>'
        if userFind == None:
            await ctx.followup.send(
                f'{mentionUser}-nyan belum terdaftar nih, /regist dulu yuk')

        else:
            platCount = userFind["platina"] + number
            newvalues = {"$set": {"platina": platCount}}
            mycol.update_one(userFind, newvalues)
            await ctx.followup.send(
                f'Platinanya {mentionUser}-nyan berhasil ditambah menjadi {platCount}'
            )


async def setup(bot):
    await bot.add_cog(Addplat(bot))
