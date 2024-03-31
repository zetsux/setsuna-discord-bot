import discord
import os
import pymongo
from discord.ext import commands
from discord import app_commands
from discord.commands import Option

guilds = [990445490401341511, 1020927428459241522, 989086863434334279, 494097970208178186, 1028690906901139486]

MONGODB = os.environ['MONGODB']

client = pymongo.MongoClient(MONGODB)
mydb = client["familiardb"]
mycol = mydb["user"]

class Resetmaze(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    
  @app_commands.command(name='resetmaze', description='Reset cooldown of /dailymaze command for chosen user or self (if not choose)')
  @app_commands.checks.has_any_role('Encoder Magang', 'Owner')
  async def reset_maze(self, ctx: discord.Interaction, member: Option(discord.Member, "The profile you want to check of", required=False, default=None)):
    await ctx.defer()
    if not member:
        member = ctx.user

    userFind = mycol.find_one({"userid": str(member.id)})
    if userFind == None:
        await ctx.response.send_message(
            f'{member.name}-nyan belum terdaftar, watashi tidak bisa membuka profilenya',
            ephemeral=True)

    else:
        await ctx.response.send_message(
            f"Cooldown command /dailymaze punya {member.name}-nyan berhasil direset!"
        )
        newvalues = {"$set": {"daily": "15/9/2022"}}
        mycol.update_one(userFind, newvalues)

async def setup(bot):
  await bot.add_cog(Resetmaze(bot))