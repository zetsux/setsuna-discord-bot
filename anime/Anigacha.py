import discord
import os
import pymongo
import datetime
from discord.ui import Select, Button, Modal, InputText, View
from discord.ext import commands
from discord.commands import Option
import numpy as np
import time
import random

guilds = [990445490401341511, 1020927428459241522, 989086863434334279, 494097970208178186, 1028690906901139486]

MONGODB = os.environ['MONGODB']

client = pymongo.MongoClient(MONGODB)
mydb = client["familiardb"]
mycol = mydb["user"]

class Anigacha(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    
  @commands.slash_command(name='anigacha', description='Play anime gacha for 1 Platina each')
  async def anime_gacha(self, ctx):
    userFind = mycol.find_one({"userid": str(ctx.author.id)})
    if userFind == None:
        await ctx.respond(
            f'Neee {ctx.author.name}-nyan, yuk bisa yuk /regist dulu~',
            ephemeral=True)

    else:
        animeFind = mycol.find_one({"func": "animedb"})
        gashaGif = 'https://cdn.discordapp.com/attachments/995337235211763722/1016230324792995930/gashap.gif'
        button1 = Button(label="Male 1x", style=discord.ButtonStyle.primary)

        async def button1_callback(interaction):
            userFind = mycol.find_one({"userid": str(interaction.user.id)})
            if userFind == None:
                await interaction.response.send_message(
                    f'Neee {interaction.user.name}-nyan, \regist dulu baru main gachanya nanti yaa',
                    ephemeral=True)
            else:
                await interaction.response.defer()
                time.sleep(2)
                platFind = mycol.find_one({"userid": str(interaction.user.id)})
                platinaCount = platFind["platina"]
                if platinaCount < 1:
                    await interaction.followup.send(
                        f'Platina anata kurang, {interaction.user.name}-nyan...',
                        ephemeral=True)
                else:
                    randomValue = random.randint(0, len(animeFind["male"]) - 1)
                    result = animeFind["male"][randomValue]
                    animeInven = platFind["animeName"]

                    if result in animeInven:
                        animeIndex = 0

                        for x in animeInven:
                            if x == result:
                                break
                            animeIndex += 1

                        aniCount = platFind["animeCount"][animeIndex] + 1
                        stringIndex = "animeCount." + str(animeIndex)
                        newvalues = {
                            "$set": {
                                "platina": platinaCount - 1,
                                stringIndex: aniCount
                            }
                        }
                        mycol.update_one(platFind, newvalues)

                        embedVar = discord.Embed(
                            title=
                            f"【 {interaction.user.name}-nyan's AniGacha Result 】",
                            description=
                            f"*sfx : klink klank*\n**{result}**\n ↳ Count : [{aniCount}]",
                            color=0x2E99A5)
                        embedVar.set_thumbnail(url=gashaGif)
                        await interaction.followup.send(embed=embedVar)

                    else:
                        newvalues = {
                            "$set": {
                                "platina": platinaCount - 1
                            },
                            "$push": {
                                "animeName": result,
                                "animeCount": 1
                            }
                        }
                        mycol.update_one(platFind, newvalues)
                        embedVar = discord.Embed(
                            title=
                            f"【 {interaction.user.name}-nyan's AniGacha Result 】",
                            description=
                            f"*sfx : klink klank*\n**{result}**\n ↳ Count : [1]",
                            color=0x2E99A5)
                        embedVar.set_thumbnail(url=gashaGif)
                        await interaction.followup.send(embed=embedVar)

        button2 = Button(label="Female 1x", style=discord.ButtonStyle.danger)

        async def button2_callback(interaction):
            userFind = mycol.find_one({"userid": str(interaction.user.id)})
            if userFind == None:
                await interaction.response.send_message(
                    f'Neee {interaction.user.name}-nyan, \regist dulu baru main gachanya nanti yaa',
                    ephemeral=True)
            else:
                await interaction.response.defer()
                time.sleep(2)
                platFind = mycol.find_one({"userid": str(interaction.user.id)})
                platinaCount = platFind["platina"]
                if platinaCount < 1:
                    await interaction.followup.send(
                        f'Platina anata kurang, {interaction.user.name}-nyan...',
                        ephemeral=True)
                else:
                    animeInven = platFind["animeName"]
                    randomValue = random.randint(0,
                                                 len(animeFind["female"]) - 1)
                    result = animeFind["female"][randomValue]

                    if result in animeInven:
                        animeIndex = 0

                        for x in animeInven:
                            if x == result:
                                break
                            animeIndex += 1

                        aniCount = platFind["animeCount"][animeIndex] + 1
                        stringIndex = "animeCount." + str(animeIndex)
                        newvalues = {
                            "$set": {
                                "platina": platinaCount - 1,
                                stringIndex: aniCount
                            }
                        }
                        mycol.update_one(platFind, newvalues)

                        embedVar = discord.Embed(
                            title=
                            f"【 {interaction.user.name}-nyan's AniGacha Result 】",
                            description=
                            f"*sfx : klink klank*\n**{result}**\n ↳ Count : [{aniCount}]",
                            color=0xee1515)
                        embedVar.set_thumbnail(url=gashaGif)
                        await interaction.followup.send(embed=embedVar)

                    else:
                        newvalues = {
                            "$set": {
                                "platina": platinaCount - 1
                            },
                            "$push": {
                                "animeName": result,
                                "animeCount": 1
                            }
                        }
                        mycol.update_one(platFind, newvalues)
                        embedVar = discord.Embed(
                            title=
                            f"【 {interaction.user.name}-nyan's AniGacha Result 】",
                            description=
                            f"*sfx : klink klank*\n**{result}**\n ↳ Count : [1]",
                            color=0xee1515)
                        embedVar.set_thumbnail(url=gashaGif)
                        await interaction.followup.send(embed=embedVar)

        button1.callback = button1_callback
        button2.callback = button2_callback
        view = View(timeout=600)
        view.add_item(button1)
        view.add_item(button2)

        embedVar = discord.Embed(
            title="— AniGacha! —",
            description=
            "Cost per Gacha : 1 Platina\n━━━━━━━━━━━\nNewly Added : \n➲ Summer 2021 - Spring 2022 Characters\n➲ Isekai Quartet Characters\n➲ **Ensemble Stars! (Rate UP!!)**\n➲ **Hololive Talents (Rate UP!!)**",
            color=0xff69b4)
        embedVar.set_image(
            url=
            "https://cdn.discordapp.com/attachments/995337235211763722/1013753097807482911/imgonline-com-ua-twotoone-bC3frXSwfPCEo0S.jpg"
        )
        gachaMsg = await ctx.respond(embed=embedVar, view=view)
        checkView = await view.wait()

        if checkView:
            embedEdit = discord.Embed(
                title=f"Thank you for using anigacha!",
                description="You can type /anigacha to do more gachas",
                color=0xff69b4)
            await gachaMsg.edit_original_message(embed=embedEdit, view=None)

def setup(bot):
  bot.add_cog(Anigacha(bot))