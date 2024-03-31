import discord
import pymongo
import os
import json
import urllib.request as urllib2
from discord.ext import commands
from discord import app_commands
from discord.commands import Option
import datetime
from discord.ui import Select, Button, Modal, TextInput, View
from discord.ext import commands
from discord import app_commands
from discord.commands import Option
import numpy as np

guilds = [990445490401341511, 1020927428459241522, 989086863434334279, 494097970208178186, 1028690906901139486]

MONGODB = os.environ['MONGODB']

client = pymongo.MongoClient(MONGODB)
mydb = client["familiardb"]
mycol = mydb["user"]

class Pokepartner(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @app_commands.command(name='pokepartner', description='Check your current pokemon partner to battle and change it if you want')
  async def pokemon_partner(self, ctx):
    userFind = mycol.find_one({"userid": str(ctx.user.id)})
    if userFind == None:
        await ctx.response.send_message(
            f'Neee {ctx.user.name}-nyan, yuk /regist dulu yuk baru liat pokemon..',
            ephemeral=True)
        return

    buttonCH = Button(label='Change Partner',
                      style=discord.ButtonStyle.primary,
                      row=0)
    buttonCO = Button(label='Done', style=discord.ButtonStyle.green, row=0)

    async def change_callback(interaction):
        if interaction.user.id != ctx.user.id:
            await interaction.response.send_message(
                f"Neee {interaction.user.name}-nyan, /pokepartner sendiri gih..",
                ephemeral=True)
            return

        modaler = Modal(title="Change Pokemon Partner", timeout=None)
        modaler.add_item(
            TextInput(label='Pokemon Name',
                      placeholder=
                      '(Must be the exact same as inventory), ex : Pikachu'))

        async def pokecha_callback(minteraction):
            tempFind = mycol.find_one({"userid": str(minteraction.user.id)})
            pokeInven = tempFind["pokeName"]
            name = str(modaler.children[0].value)
            name = name[0].upper() + name[1:].lower()

            if name.lower() == 'porygon-z':
                name = 'Porygon-Z'

            if name in pokeInven:
                pokeIndex = 0
                for x in pokeInven:
                    if x == name:
                        break

                    pokeIndex += 1

                level = int(userFind["pokeLevel"][pokeIndex])
                newvalues = {"$set": {"pokemon": name, "pokemonlv": level}}
                mycol.update_one(tempFind, newvalues)
                tempResponse = urllib2.urlopen(
                    f'https://some-random-api.ml/pokemon/pokedex?pokemon={name.lower()}'
                )
                tempData = json.loads(tempResponse.read())
                eleTemp = ', '.join(tempData["type"])

                embedDit = discord.Embed(
                    title=f'[ Poke Partner ]',
                    description=
                    f"Current : {name} Lv. {str(level)} ({eleTemp})",
                    color=0xee1515)
                embedDit.add_field(
                    name=f"[ Stats ]",
                    value='```' +
                    f'HP       : {str(int(int(tempData["stats"]["hp"])*((((level*2) - 1)+19)/20)))}\n'
                    f'Atk      : {str(int(int(tempData["stats"]["attack"])*((((level*2) - 1)+19)/20)))}\n'
                    +
                    f'Sp. Atk  : {str(int(int(tempData["stats"]["sp_atk"])*((((level*2) - 1)+19)/20)))}\n'
                    +
                    f'Def      : {str(int(int(tempData["stats"]["defense"])*((((level*2) - 1)+19)/20)))}\n'
                    +
                    f'Sp. Def  : {str(int(int(tempData["stats"]["sp_def"])*((((level*2) - 1)+19)/20)))}\n'
                    +
                    f'Speed    : {str(int(int(tempData["stats"]["speed"])*((((level*2) - 1)+19)/20)))}\n'
                    + '```',
                    inline=False)
                embedDit.set_thumbnail(url=tempData['sprites']['animated'])
                await minteraction.response.edit_message(embed=embedDit)
                await minteraction.followup.send(
                    f'{name} berhasil dijadikan partner battle dari {minteraction.user.name}-nyan!',
                    ephemeral=True)

            else:
                await minteraction.response.send_message(
                    f'Neee {minteraction.user.name}-nyan, anata kayanya halu deh, di inventory anata ngga ada yang namanya {name} loh.. Atau salah tulis mungkin, coba deh dicek lagi',
                    ephemeral=True)
                return

        modaler.callback = pokecha_callback
        await interaction.response.send_modal(modaler)

    async def confirm_callback(interaction):
        if interaction.user.id != ctx.user.id:
            await interaction.response.send_message(
                f"Neee {interaction.user.name}-nyan, /pokepartner sendiri gih..",
                ephemeral=True)
            return

        tempFind = mycol.find_one({"userid": str(ctx.user.id)})
        embedEdit = discord.Embed(
            title=f"[ Poke Partner Confirmed! ]",
            description=f"Current : {tempFind['pokemon']}",
            color=0xffff00)
        await interaction.response.edit_message(embed=embedEdit, view=None)
        view.stop()

    buttonCH.callback = change_callback
    buttonCO.callback = confirm_callback
    view = View(timeout=750)
    view.add_item(buttonCH)
    view.add_item(buttonCO)

    partName = userFind["pokemon"]
    partInven = userFind["pokeName"]
    partLevel = userFind["pokemonlv"]
    partIndex = 0

    if partName in partInven:
        for x in partInven:
            if x == partName:
                break

            partIndex += 1

        response = urllib2.urlopen(
            f'https://some-random-api.ml/pokemon/pokedex?pokemon={partName.lower()}')
        data = json.loads(response.read())
        eleString = ', '.join(data["type"])
        embedVar = discord.Embed(
            title=f'[ Poke Partner ]',
            description=
            f"Current : {partName} Lv. {str(partLevel)} ({eleString})",
            color=0xee1515)
        embedVar.add_field(
            name=f"[ Stats ]",
            value='```' +
            f'HP       : {str(int(int(data["stats"]["hp"])*((((partLevel*2) - 1)+19)/20)))}\n'
            f'Atk      : {str(int(int(data["stats"]["attack"])*((((partLevel*2) - 1)+19)/20)))}\n'
            +
            f'Sp. Atk  : {str(int(int(data["stats"]["sp_atk"])*((((partLevel*2) - 1)+19)/20)))}\n'
            +
            f'Def      : {str(int(int(data["stats"]["defense"])*((((partLevel*2) - 1)+19)/20)))}\n'
            +
            f'Sp. Def  : {str(int(int(data["stats"]["sp_def"])*((((partLevel*2) - 1)+19)/20)))}\n'
            +
            f'Speed    : {str(int(int(data["stats"]["speed"])*((((partLevel*2) - 1)+19)/20)))}\n'
            + '```',
            inline=False)
        embedVar.set_thumbnail(url=data['sprites']['animated'])

    else:
        embedVar = discord.Embed(
            title=f'[ Poke Partner ]',
            description=f"Current : None (Change Partner to set)",
            color=0xee1515)

    panelMsg = await ctx.response.send_message(embed=embedVar, view=view, ephemeral=True)
    checkView = await view.wait()

    if checkView:
        tempFind = mycol.find_one({"userid": str(ctx.user.id)})
        embedEdit = discord.Embed(
            title=f"Poke Partner Timed Out...",
            description=f"Partner : {tempFind['pokemon']}",
            color=0xffff00)
        await panelMsg.edit_original_response(embed=embedEdit, view=None)

async def setup(bot):
  await bot.add_cog(Pokepartner(bot))