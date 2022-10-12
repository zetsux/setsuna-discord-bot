import discord
import os
import pymongo
import datetime
from discord.ui import Select, Button, Modal, InputText, View
from discord.ext import commands
from discord.commands import Option
import numpy as np
import time
import asyncio
import random

guilds = [990445490401341511, 1020927428459241522, 989086863434334279, 494097970208178186, 1028690906901139486]

MONGODB = os.environ['MONGODB']

client = pymongo.MongoClient(MONGODB)
mydb = client["familiardb"]
mycol = mydb["user"]

class Timer(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    
  @commands.slash_command(
    name='timer',
    description='Create a button that auto end after a set period of time')
  async def timer_test(self, ctx, timer: Option(int, "Seconds to wait", required=True)):
    if timer <= 0:
        await ctx.respond(
            f"Neeee {ctx.user.name}-nyan, ngga jelas banget ah, ngapain coba timer kurang dari 0 detik",
            ephemeral=True)
        return

    buttonTime = Button(label='End', style=discord.ButtonStyle.danger, row=0)
    buttonCheck = Button(label='Check Time',
                         style=discord.ButtonStyle.gray,
                         row=0)
    flag = False

    async def end_callback(interaction):
        if interaction.user.id != ctx.user.id:
            await interaction.response.send_message(
                f"Neee {interaction.user.name}-nyan, mending /timer sendiri deh, jangan pake punya orang lain ih",
                ephemeral=True)
            return

        nonlocal flag
        flag = True
        embedEdit = discord.Embed(
            title=f"Timer ditutup secara paksa dengan button",
            description="Sudah abis kak",
            color=0xffff00)
        await interaction.response.edit_message(embed=embedEdit, view=None)

    async def check_callback(interaction):
        await interaction.response.send_message(
            f"Sabar yah {interaction.user.name}-nyan, waktu tersisa {timer - time} detik lagi..",
            ephemeral=True)

    buttonTime.callback = end_callback
    buttonCheck.callback = check_callback
    view = View(timeout=None)
    view.add_item(buttonTime)
    view.add_item(buttonCheck)

    embedVar = discord.Embed(title=f'[ Timer ]',
                             description=f"for {timer} seconds",
                             color=0x8b0000)
    timerMsg = await ctx.respond(embed=embedVar, view=view)

    time = 0
    while True:
        await asyncio.sleep(1)
        time += 1
        # print(time)
        if time == timer:
            embedEnd = discord.Embed(title=f"Timer ditutup karena waktu habis",
                                     description="Sudah abis kak",
                                     color=0xffff00)
            await timerMsg.edit_original_message(embed=embedEnd, view=None)
            break
        if flag:
            break

def setup(bot):
  bot.add_cog(Timer(bot))