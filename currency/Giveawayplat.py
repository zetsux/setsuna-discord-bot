import discord
import os
import pymongo
import datetime
from discord.ui import Select, Button, Modal, TextInput, View
from discord.ext import commands
from discord import app_commands
from discord.commands import Option
import numpy as np
import time
import random

guilds = [990445490401341511, 1020927428459241522, 989086863434334279, 494097970208178186, 1028690906901139486]

MONGODB = os.environ['MONGODB']

client = pymongo.MongoClient(MONGODB)
mydb = client["familiardb"]
mycol = mydb["user"]

class Giveawayplat(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    
  @app_commands.command(name='giveawayplat', description='Giveaway the entered number of platina to the fastest claimer'
)
  async def platina_giveaway(self, ctx, number: Option(int, "Number to giveaway", required=True)):
    await ctx.defer()
    if number <= 0:
        await ctx.response.send_message(f'Neee anata ngga jelas deh, {ctx.user.name}-nyan', ephemeral=True)
        return

    userFind = mycol.find_one({"userid": str(ctx.user.id)})
    if userFind == None:
        await ctx.response.send_message(
            f'Neee {ctx.user.name}-nyan, yuk bisa yuk /regist dulu~',
            ephemeral=True)

    else:
        platinaCount = userFind["platina"]
        if number > platinaCount:
            await ctx.response.send_message(
                f'Platina anata ngga cukup, {ctx.user.name}-nyan...',
                ephemeral=True)

        else:
            flag = True
            platinaCount = userFind["platina"] - number
            newvalues = {"$set": {"platina": platinaCount}}
            mycol.update_one(userFind, newvalues)
            buttons = Button(label="Claim Platina",
                             style=discord.ButtonStyle.success,
                             emoji="🤑")

            async def button_callback(interaction):
                userFind = mycol.find_one({"userid": str(interaction.user.id)})
                if userFind == None:
                    await interaction.response.send_message(
                        f'Neee {interaction.user.name}-nyan, yuk /regist dulu baru ikut giveaway',
                        ephemeral=True)
                else:
                    embedEdit = discord.Embed(
                        title=str(number) + " Platina Giveaway by " +
                        ctx.user.name + "-nyan",
                        description=
                        f">> Claimed by {interaction.user.name}-nyan",
                        color=0xffd700)
                    await interaction.response.edit_message(embed=embedEdit,
                                                            view=None)

                    nonlocal flag
                    if flag:
                        flag = False
                        platinaCount = userFind["platina"] + number
                        newvalues = {"$set": {"platina": platinaCount}}
                        mycol.update_one(userFind, newvalues)

            buttons.callback = button_callback
            view = View()
            view.add_item(buttons)

            embedVar = discord.Embed(
                title=str(number) + " Platina Giveaway by " + ctx.user.name +
                "-nyan",
                description="Penekan tombol tercepat akan mendapatkannya!",
                color=0xe5e4e2)
            embedVar.set_thumbnail(
                url=
                "https://i.ibb.co/F3rgw7r/kisspng-junk-silver-silver-coin-coin-collecting-5b2ecbbdd0c336-2118554315297934698551.png"
            )
            await ctx.response.send_message(embed=embedVar, view=view)

async def setup(bot):
  await bot.add_cog(Giveawayplat(bot))