import discord
import pymongo
import os
import requests
from discord.ext import commands
from discord import app_commands
from discord.ui import Button, Modal, TextInput, View

GUILDID = int(os.environ['GUILDID'])
LOGCH = int(os.environ['LOGCHID'])
MONGODB = os.environ['MONGODB']

client = pymongo.MongoClient(MONGODB)
mydb = client["familiardb"]
mycol = mydb["user"]


class Pokepartner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name='pokepartner',
        description=
        'Check your current pokemon partner to battle and change it if you want'
    )
    async def pokemon_partner(self, ctx: discord.Interaction):
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
                TextInput(
                    label='Pokemon Name',
                    placeholder=
                    '(Must be the exact same as inventory), ex : Pikachu'))

            async def pokecha_callback(minteraction):
                tempFind = mycol.find_one(
                    {"userid": str(minteraction.user.id)})
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

                    try:
                        tempResponse = requests.get(
                            f'https://pokeapi.co/api/v2/pokemon/{name.lower()}'
                        )
                        tempData = tempResponse.json()
                        newvalues = {
                            "$set": {
                                "pokemon": name,
                                "pokemonlv": level
                            }
                        }
                        mycol.update_one(tempFind, newvalues)
                    except:
                        guild = self.bot.get_guild(GUILDID)
                        channel = guild.get_channel(LOGCH)
                        await channel.send(f"Pokemon not found in API : {name}"
                                           )

                    eleTemp = ', '.join([
                        t['type']['name'].capitalize()
                        for t in tempData['types']
                    ])

                    embedDit = discord.Embed(
                        title=f'[ Poke Partner ]',
                        description=
                        f"Current : {name} Lv. {str(level)} ({eleTemp})",
                        color=0xee1515)
                    embedDit.add_field(
                        name="[ Stats ]",
                        value='```'
                        f'HP       : {str(int(int(tempData["stats"][0]["base_stat"]) * ((((level * 2) - 1) + 19) / 20)))}\n'
                        f'Atk      : {str(int(int(tempData["stats"][1]["base_stat"]) * ((((level * 2) - 1) + 19) / 20)))}\n'
                        f'Sp. Atk  : {str(int(int(tempData["stats"][3]["base_stat"]) * ((((level * 2) - 1) + 19) / 20)))}\n'
                        f'Def      : {str(int(int(tempData["stats"][2]["base_stat"]) * ((((level * 2) - 1) + 19) / 20)))}\n'
                        f'Sp. Def  : {str(int(int(tempData["stats"][4]["base_stat"]) * ((((level * 2) - 1) + 19) / 20)))}\n'
                        f'Speed    : {str(int(int(tempData["stats"][5]["base_stat"]) * ((((level * 2) - 1) + 19) / 20)))}\n'
                        '```',
                        inline=False)

                    embedDit.set_thumbnail(url=tempData['sprites']['other']
                                           ['showdown']['front_default'])
                    await minteraction.response.edit_message(embed=embedDit)
                    await minteraction.followup.send(
                        f'{name} berhasil dijadikan partner battle dari {minteraction.user.name}-nyan!',
                        ephemeral=True)

                else:
                    await minteraction.response.send_message(
                        f'Neee {minteraction.user.name}-nyan, anata kayanya halu deh, di inventory anata ngga ada yang namanya {name} loh.. Atau salah tulis mungkin, coba deh dicek lagi',
                        ephemeral=True)
                    return

            modaler.on_submit = pokecha_callback
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

            try:
                response = requests.get(
                    f'https://pokeapi.co/api/v2/pokemon/{partName.lower()}')
                data = response.json()
            except:
                guild = self.bot.get_guild(GUILDID)
                channel = guild.get_channel(LOGCH)
                await channel.send(f"Pokemon not found in API : {partName}")

            eleString = ', '.join(
                [t['type']['name'].capitalize() for t in data['types']])
            embedVar = discord.Embed(
                title=f'[ Poke Partner ]',
                description=
                f"Current : {partName} Lv. {str(partLevel)} ({eleString})",
                color=0xee1515)
            embedVar.add_field(
                name="[ Stats ]",
                value='```'
                f'HP       : {int(int(data["stats"][0]["base_stat"]) * ((((partLevel * 2) - 1) + 19) / 20))}\n'
                f'Atk      : {int(int(data["stats"][1]["base_stat"]) * ((((partLevel * 2) - 1) + 19) / 20))}\n'
                f'Sp. Atk  : {int(int(data["stats"][3]["base_stat"]) * ((((partLevel * 2) - 1) + 19) / 20))}\n'
                f'Def      : {int(int(data["stats"][2]["base_stat"]) * ((((partLevel * 2) - 1) + 19) / 20))}\n'
                f'Sp. Def  : {int(int(data["stats"][4]["base_stat"]) * ((((partLevel * 2) - 1) + 19) / 20))}\n'
                f'Speed    : {int(int(data["stats"][5]["base_stat"]) * ((((partLevel * 2) - 1) + 19) / 20))}\n'
                '```',
                inline=False)
            embedVar.set_thumbnail(
                url=data['sprites']['other']['showdown']['front_default'])

        else:
            embedVar = discord.Embed(
                title=f'[ Poke Partner ]',
                description=f"Current : None (Change Partner to set)",
                color=0xee1515)

        await ctx.response.send_message(embed=embedVar,
                                        view=view,
                                        ephemeral=True)
        checkView = await view.wait()

        if checkView:
            tempFind = mycol.find_one({"userid": str(ctx.user.id)})
            embedEdit = discord.Embed(
                title=f"Poke Partner Timed Out...",
                description=f"Partner : {tempFind['pokemon']}",
                color=0xffff00)
            await ctx.edit_original_response(embed=embedEdit, view=None)


async def setup(bot):
    await bot.add_cog(Pokepartner(bot))
