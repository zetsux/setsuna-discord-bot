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

class Giveawaygold(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    
  @app_commands.command(name='giveawaygold', description='Giveaway the entered number of gold to the fastest claimer')
  async def gold_giveaway(self, ctx, number: Option(int, "Number to giveaway",required=True)):
    await ctx.defer()
    if number <= 0:
        await ctx.response.send_message(f'Neee anata ngga jelas deh, {ctx.user.name}-nyan',
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
            flag = True
            goldCount = userFind["gold"] - number
            newvalues = {"$set": {"gold": goldCount}}
            mycol.update_one(userFind, newvalues)
            buttons = Button(label="Claim Gold",
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
                        title=str(number) + " Gold Giveaway by " +
                        ctx.user.name + "-nyan",
                        description=
                        f">> Claimed by {interaction.user.name}-nyan",
                        color=0xffd700)
                    await interaction.response.edit_message(embed=embedEdit,
                                                            view=None)

                    nonlocal flag
                    if flag:
                        flag = False
                        goldCount = userFind["gold"] + number
                        newvalues = {"$set": {"gold": goldCount}}
                        mycol.update_one(userFind, newvalues)

            buttons.callback = button_callback
            view = View()
            view.add_item(buttons)

            embedVar = discord.Embed(
                title=str(number) + " Gold Giveaway by " + ctx.user.name +
                "-nyan",
                description="Penekan tombol tercepat akan mendapatkannya!",
                color=0xffd700)
            embedVar.set_thumbnail(
                url=
                "https://i.ibb.co/BZPbJ6W/pngfind-com-gold-coins-png-37408.png"
            )
            await ctx.response.send_message(embed=embedVar, view=view)

async def setup(bot):
  await bot.add_cog(Giveawaygold(bot))