import discord
import os
import pymongo
import datetime
from discord.ext import commands
from discord import app_commands

guilds = [990445490401341511, 1020927428459241522, 989086863434334279, 494097970208178186, 1028690906901139486]

MONGODB = os.environ['MONGODB']

client = pymongo.MongoClient(MONGODB)
mydb = client["familiardb"]
mycol = mydb["user"]

class Resethunt(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    
  @app_commands.command(name='resethunt', description='Reset cooldown of /hunt command for chosen user or self (if not choose)')
  @app_commands.checks.has_any_role('Encoder Magang', 'Owner')
  @app_commands.describe(member="The member to reset hunt cd")
  async def reset_hunt(self, ctx: discord.Interaction, member: discord.Member = None):
    await ctx.response.defer()
    if not member:
        member = ctx.user

    userFind = mycol.find_one({"userid": str(member.id)})
    if userFind == None:
        await ctx.followup.send(
            f'{member.name}-nyan belum terdaftar, watashi tidak bisa membuka profilenya',
            ephemeral=True)

    else:
        await ctx.followup.send(
            f"Cooldown command /hunt punya {member.name}-nyan berhasil direset!"
        )
        newvalues = {
            "$set": {
                "hunt": datetime.datetime(2021, 10, 24, 10, 0, 38, 917000)
            }
        }
        mycol.update_one(userFind, newvalues)

async def setup(bot):
  await bot.add_cog(Resethunt(bot))