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
import time
import asyncio
import random

guilds = [990445490401341511, 1020927428459241522, 989086863434334279, 494097970208178186, 1028690906901139486]

GUILDID = int(os.environ['GUILDID'])
LOGCH = int(os.environ['LOGCHID'])
MONGODB = os.environ['MONGODB']

client = pymongo.MongoClient(MONGODB)
mydb = client["familiardb"]
mycol = mydb["user"]

class Pokecatch(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @app_commands.command(name='pokecatch', description='Catch a random pokemon from the wild for 1 Platina')
  async def poke_gacha(self, ctx: discord.Interaction):
    firstFind = mycol.find_one({"userid": str(ctx.user.id)})
    if firstFind == None:
        await ctx.response.send_message(
            f'Neee {ctx.user.name}-nyan, yuk bisa yuk /regist dulu~',
            ephemeral=True)

    else:
        pokeFind = mycol.find_one({"func": "pokedb"})
        pokeBasic = pokeFind["basic"]
        pokeElite = pokeFind["elite"]
        pokeEpic = pokeFind["epic"]
        pokeLegend = pokeFind["legend"]
        pokeList = pokeBasic + pokeElite + pokeEpic + pokeLegend

        pokeNot = ["Darmanitan"]
        button1 = Button(label="Catch!", style=discord.ButtonStyle.green)

        async def button1_callback(interaction):
            upFind = mycol.find_one({"userid": str(interaction.user.id)})
            if upFind == None:
                await interaction.response.send_message(
                    f'Neee {interaction.user.name}-nyan, \regist dulu baru main gachanya nanti yaa',
                    ephemeral=True)
            else:
                await interaction.response.defer()
                time.sleep(2)
                platFind = mycol.find_one({"userid": str(interaction.user.id)})
                platinaCount = platFind["platina"]
                # print(platinaCount)
                if platinaCount < 1:
                    await interaction.followup.send(
                        f'Platina anata kurang, {interaction.user.name}-nyan...',
                        ephemeral=True)
                else:
                    numpitye = platFind["epicpity"]
                    numpityl = platFind["legendpity"]

                    if numpityl >= 99:
                        rarityVal = 100

                    elif numpitye >= 29:
                        rarityVal = 99

                    else:
                        rarityVal = random.randint(1, 100)

                    if rarityVal <= 67:
                        pokeArr = pokeFind["basic"]
                        randomValue = random.randint(0, len(pokeArr) - 1)
                        rarity = 'Basic'
                        newvalues = {
                            "$set": {
                                "platina": platinaCount - 1,
                                "epicpity": numpitye + 1,
                                "legendpity": numpityl + 1
                            }
                        }
                        mycol.update_one(platFind, newvalues)

                    elif rarityVal <= 92:
                        pokeArr = pokeFind["elite"]
                        randomValue = random.randint(0, len(pokeArr) - 1)
                        rarity = 'Advanced'
                        newvalues = {
                            "$set": {
                                "platina": platinaCount - 1,
                                "epicpity": numpitye + 1,
                                "legendpity": numpityl + 1
                            }
                        }
                        mycol.update_one(platFind, newvalues)

                    elif rarityVal <= 99:
                        pokeArr = pokeFind["epic"]
                        randomValue = random.randint(0, len(pokeArr) - 1)
                        rarity = 'Epic'
                        newvalues = {
                            "$set": {
                                "platina": platinaCount - 1,
                                "epicpity": 0,
                                "legendpity": numpityl + 1
                            }
                        }
                        mycol.update_one(platFind, newvalues)

                    elif rarityVal == 100:
                        pokeArr = pokeFind["legend"]
                        randomValue = random.randint(0, len(pokeArr) - 1)
                        rarity = 'Legendary'
                        newvalues = {
                            "$set": {
                                "platina": platinaCount - 1,
                                "epicpity": numpitye + 1,
                                "legendpity": 0
                            }
                        }
                        mycol.update_one(platFind, newvalues)

                    result = pokeArr[randomValue]
                    try:
                      response = urllib2.urlopen(
                          f'https://some-random-api.ml/pokemon/pokedex?pokemon={result.lower()}'
                      )
                    except:
                      guild = self.bot.get_guild(GUILDID)
                      channel = guild.get_channel(LOGCH)
                      await channel.send(
                          f"Pokemon error : {result} | index : {randomValue}"
                      )

                    data = json.loads(response.read())
                    resultGif = data["sprites"]["animated"]
                    userFind = mycol.find_one(
                        {"userid": str(interaction.user.id)})
                    pokeInven = userFind["pokeName"]

                    if result in pokeInven:
                        pokeIndex = 0

                        for x in pokeInven:
                            if x == result:
                                break
                            pokeIndex += 1

                        nowLev = userFind["pokeLevel"][pokeIndex] + 1
                        evoPath = data["family"]["evolutionLine"]
                        evoPath = list(dict.fromkeys(evoPath))
                        try:
                            index = evoPath.index(result)
                        except:
                            index = 99

                        if "Eevee" in evoPath and result not in pokeNot:
                            if result != "Eevee":
                                embedVar = discord.Embed(
                                    title=
                                    f"〘 {interaction.user.name}-nyan's PokeCatch Result 〙",
                                    description=
                                    f"*Gotcha!*\n{result} ({rarity})\n ↳ Level Up : **{result} (Lv. {nowLev})**",
                                    color=0xee1515)
                                embedVar.set_image(url=resultGif)
                                await interaction.followup.send(embed=embedVar)

                                stringIndex = "pokeLevel." + str(pokeIndex)
                                if result == userFind["pokemon"]:
                                    newvalues = {
                                        "$set": {
                                            "pokemonlv": nowLev,
                                            stringIndex: nowLev
                                        }
                                    }

                                else:
                                    newvalues = {"$set": {stringIndex: nowLev}}
                                mycol.update_one(userFind, newvalues)

                            else:
                                if nowLev >= 2:
                                    evolved = evoPath[random.randint(
                                        1,
                                        len(evoPath) - 1)]
                                    try:
                                        response2 = urllib2.urlopen(
                                            f'https://some-random-api.ml/pokemon/pokedex?pokemon={evolved.lower()}'
                                        )
                                    except:
                                        guild = self.bot.get_guild(GUILDID)
                                        channel = guild.get_channel(LOGCH)
                                        await channel.send(
                                            f"Pokemon error : {evolved}")
                                    data2 = json.loads(response2.read())
                                    evolvedGif = data2["sprites"]["animated"]

                                    nameIndex = "pokeName." + str(pokeIndex)
                                    levelIndex = "pokeLevel." + str(pokeIndex)

                                    if evolved in pokeInven:
                                        evoIndex = 0

                                        for x in pokeInven:
                                            if x == evolved:
                                                break
                                            evoIndex += 1

                                        evoLev = userFind["pokeLevel"][
                                            evoIndex] + 1
                                        nextPath = data2["family"][
                                            "evolutionLine"]
                                        nextPath = list(
                                            dict.fromkeys(nextPath))
                                        try:
                                            nextIndex = nextPath.index(evolved)
                                        except:
                                            nextIndex = 99

                                        levelEvo = "pokeLevel." + str(evoIndex)

                                        embedVar = discord.Embed(
                                            title=
                                            f"〘 {interaction.user.name}-nyan's PokeCatch Result 〙",
                                            description=
                                            f"*Gotcha!*\n{result} ({rarity})\n ↳ Evolve & Level Up : **{evolved} (Lv. {evoLev})**",
                                            color=0xee1515)
                                        embedVar.set_image(url=evolvedGif)
                                        await interaction.followup.send(
                                            embed=embedVar)

                                        if result == userFind["pokemon"]:
                                            newvalues = {
                                                "$set": {
                                                    "pokemon": '-',
                                                    "pokemonlv": -1,
                                                    nameIndex: "None",
                                                    levelIndex: 0,
                                                    levelEvo: evoLev
                                                }
                                            }

                                        elif evolved == userFind["pokemon"]:
                                            newvalues = {
                                                "$set": {
                                                    "pokemonlv": evoLev,
                                                    nameIndex: "None",
                                                    levelIndex: 0,
                                                    levelEvo: evoLev
                                                }
                                            }

                                        else:
                                            newvalues = {
                                                "$set": {
                                                    nameIndex: "None",
                                                    levelIndex: 0,
                                                    levelEvo: evoLev
                                                }
                                            }

                                        mycol.update_one(userFind, newvalues)

                                    else:
                                        embedVar = discord.Embed(
                                            title=
                                            f"〘 {interaction.user.name}-nyan's PokeCatch Result 〙",
                                            description=
                                            f"*Gotcha!*\n{result} ({rarity})\n ↳ Evolve : **{evolved} (Lv. 1)**",
                                            color=0xee1515)
                                        embedVar.set_image(url=evolvedGif)
                                        await interaction.followup.send(
                                            embed=embedVar)

                                        if result == userFind["pokemon"]:
                                            newvalues = {
                                                "$set": {
                                                    "pokemon": '-',
                                                    "pokemonlv": -1
                                                },
                                                "$push": {
                                                    "pokeName": evolved,
                                                    "pokeLevel": 1
                                                }
                                            }

                                        else:
                                            newvalues = {
                                                "$push": {
                                                    "pokeName": evolved,
                                                    "pokeLevel": 1
                                                }
                                            }

                                        mycol.update_one(userFind, newvalues)
                                        exFind = mycol.find_one({
                                            "userid":
                                            str(interaction.user.id)
                                        })
                                        newvalues = {
                                            "$set": {
                                                nameIndex: "None",
                                                levelIndex: 0
                                            }
                                        }
                                        mycol.update_one(exFind, newvalues)

                        elif nowLev >= 2 and index < len(
                                evoPath
                        ) - 1 and index < 3 and result not in pokeNot:
                            if index >= 2 and len(evoPath) > index + 1:
                                evolved = evoPath[random.randint(
                                    index + 1,
                                    len(evoPath) - 1)]
                            else:
                                evolved = evoPath[index + 1]

                            if evolved not in pokeList:
                                embedVar = discord.Embed(
                                    title=
                                    f"〘 {interaction.user.name}-nyan's PokeCatch Result 〙",
                                    description=
                                    f"*Gotcha!*\n{result} ({rarity})\n ↳ Level Up : **{result} (Lv. {nowLev})**",
                                    color=0xee1515)
                                embedVar.set_image(url=resultGif)
                                await interaction.followup.send(embed=embedVar)

                                stringIndex = "pokeLevel." + str(pokeIndex)
                                if result == userFind["pokemon"]:
                                    newvalues = {
                                        "$set": {
                                            "pokemonlv": nowLev,
                                            stringIndex: nowLev
                                        }
                                    }

                                else:
                                    newvalues = {"$set": {stringIndex: nowLev}}

                                mycol.update_one(userFind, newvalues)

                            try:
                                response2 = urllib2.urlopen(
                                    f'https://some-random-api.ml/pokemon/pokedex?pokemon={evolved.lower()}'
                                )
                            except:
                                guild = self.bot.get_guild(GUILDID)
                                channel = guild.get_channel(LOGCH)
                                await channel.send(f"Pokemon error : {evolved}"
                                                   )
                            data2 = json.loads(response2.read())
                            evolvedGif = data2["sprites"]["animated"]

                            nameIndex = "pokeName." + str(pokeIndex)
                            levelIndex = "pokeLevel." + str(pokeIndex)

                            if evolved in pokeInven:
                                evoIndex = 0

                                for x in pokeInven:
                                    if x == evolved:
                                        break
                                    evoIndex += 1

                                evoLev = userFind["pokeLevel"][evoIndex] + 1
                                nextPath = data2["family"]["evolutionLine"]
                                nextPath = list(dict.fromkeys(nextPath))
                                try:
                                    nextIndex = nextPath.index(evolved)
                                except:
                                    nextIndex = 99

                                nameEvo = "pokeName." + str(evoIndex)
                                levelEvo = "pokeLevel." + str(evoIndex)

                                if "Eevee" in nextPath and evolved != "Eevee":
                                    embedVar = discord.Embed(
                                        title=
                                        f"〘 {interaction.user.name}-nyan's PokeCatch Result 〙",
                                        description=
                                        f"*Gotcha!*\n{result} ({rarity})\n ↳ Evolve & Level Up : **{evolved} (Lv. {evoLev})**",
                                        color=0xee1515)
                                    embedVar.set_image(url=evolvedGif)
                                    await interaction.followup.send(
                                        embed=embedVar)

                                    if result == userFind["pokemon"]:
                                        newvalues = {
                                            "$set": {
                                                "pokemon": '-',
                                                "pokemonlv": -1,
                                                nameIndex: "None",
                                                levelIndex: 0,
                                                levelEvo: evoLev
                                            }
                                        }

                                    elif evolved == userFind["pokemon"]:
                                        newvalues = {
                                            "$set": {
                                                "pokemonlv": evoLev,
                                                nameIndex: "None",
                                                levelIndex: 0,
                                                levelEvo: evoLev
                                            }
                                        }

                                    else:
                                        newvalues = {
                                            "$set": {
                                                nameIndex: "None",
                                                levelIndex: 0,
                                                levelEvo: evoLev
                                            }
                                        }

                                    mycol.update_one(userFind, newvalues)

                                elif evoLev >= 2 and nextIndex < len(
                                        nextPath
                                ) - 1 and nextIndex < 3 and evolved not in pokeNot:
                                    if nextIndex >= 2 and len(
                                            nextPath) > nextIndex + 1:
                                        nexted = nextPath[random.randint(
                                            nextIndex + 1,
                                            len(nextPath) - 1)]
                                    else:
                                        nexted = nextPath[nextIndex + 1]

                                    if nexted not in pokeList:
                                        embedVar = discord.Embed(
                                            title=
                                            f"〘 {interaction.user.name}-nyan's PokeCatch Result 〙",
                                            description=
                                            f"*Gotcha!*\n{result} ({rarity})\n ↳ Evolve & Level Up : **{evolved} (Lv. {evoLev})**",
                                            color=0xee1515)
                                        embedVar.set_image(url=evolvedGif)
                                        await interaction.followup.send(
                                            embed=embedVar)

                                        if result == userFind["pokemon"]:
                                            newvalues = {
                                                "$set": {
                                                    "pokemon": '-',
                                                    "pokemonlv": -1,
                                                    nameIndex: "None",
                                                    levelIndex: 0,
                                                    levelEvo: evoLev
                                                }
                                            }

                                        elif evolved == userFind["pokemon"]:
                                            newvalues = {
                                                "$set": {
                                                    "pokemonlv": evoLev,
                                                    nameIndex: "None",
                                                    levelIndex: 0,
                                                    levelEvo: evoLev
                                                }
                                            }

                                        else:
                                            newvalues = {
                                                "$set": {
                                                    nameIndex: "None",
                                                    levelIndex: 0,
                                                    levelEvo: evoLev
                                                }
                                            }

                                        mycol.update_one(userFind, newvalues)

                                    try:
                                        response3 = urllib2.urlopen(
                                            f'https://some-random-api.ml/pokemon/pokedex?pokemon={nexted.lower()}'
                                        )
                                    except:
                                        guild = self.bot.get_guild(GUILDID)
                                        channel = guild.get_channel(LOGCH)
                                        await channel.send(
                                            f"Pokemon error : {nexted}")
                                    data3 = json.loads(response3.read())
                                    nextedGif = data3["sprites"]["animated"]

                                    if nexted in pokeInven:
                                        nextedIndex = 0

                                        for x in pokeInven:
                                            if x == nexted:
                                                break
                                            nextedIndex += 1

                                        nextedLev = userFind["pokeLevel"][
                                            nextedIndex] + 1
                                        embedVar = discord.Embed(
                                            title=
                                            f"〘 {interaction.user.name}-nyan's PokeCatch Result 〙",
                                            description=
                                            f"*Gotcha!*\n{result} ({rarity})\n ↳ Evolve & Level Up : {evolved} (Lv. 2)\n  ↳ Evolve & Level Up : **{nexted} (Lv. {nextedLev})**",
                                            color=0xee1515)
                                        embedVar.set_image(url=nextedGif)
                                        await interaction.followup.send(
                                            embed=embedVar)

                                        levelNext = "pokeLevel." + str(
                                            nextedIndex)
                                        if result == userFind[
                                                "pokemon"] or evolved == userFind[
                                                    "pokemon"]:
                                            newvalues = {
                                                "$set": {
                                                    "pokemon": '-',
                                                    "pokemonlv": -1,
                                                    nameIndex: "None",
                                                    levelIndex: 0,
                                                    nameEvo: "None",
                                                    levelEvo: 0,
                                                    levelNext: nextedLev
                                                }
                                            }

                                        elif nexted == userFind["pokemon"]:
                                            newvalues = {
                                                "$set": {
                                                    "pokemonlv": nextedLev,
                                                    nameIndex: "None",
                                                    levelIndex: 0,
                                                    nameEvo: "None",
                                                    levelEvo: 0,
                                                    levelNext: nextedLev
                                                }
                                            }

                                        else:
                                            newvalues = {
                                                "$set": {
                                                    nameIndex: "None",
                                                    levelIndex: 0,
                                                    nameEvo: "None",
                                                    levelEvo: 0,
                                                    levelNext: nextedLev
                                                }
                                            }

                                        mycol.update_one(userFind, newvalues)

                                    else:
                                        embedVar = discord.Embed(
                                            title=
                                            f"〘 {interaction.user.name}-nyan's PokeCatch Result 〙",
                                            description=
                                            f"*Gotcha!*\n{result} ({rarity})\n ↳ Evolve & Level Up : {evolved} (Lv. 2)\n  ↳ Evolve : **{nexted} (Lv. 1)**",
                                            color=0xee1515)
                                        embedVar.set_image(url=nextedGif)
                                        await interaction.followup.send(
                                            embed=embedVar)

                                        if result == userFind["pokemon"]:
                                            newvalues = {
                                                "$set": {
                                                    "pokemon": '-',
                                                    "pokemonlv": -1
                                                },
                                                "$push": {
                                                    "pokeName": nexted,
                                                    "pokeLevel": 1
                                                }
                                            }

                                        else:
                                            newvalues = {
                                                "$push": {
                                                    "pokeName": nexted,
                                                    "pokeLevel": 1
                                                }
                                            }

                                        newvalues = {
                                            "$push": {
                                                "pokeName": nexted,
                                                "pokeLevel": 1
                                            }
                                        }
                                        mycol.update_one(userFind, newvalues)
                                        exFind = mycol.find_one({
                                            "userid":
                                            str(interaction.user.id)
                                        })
                                        newvalues = {
                                            "$set": {
                                                nameIndex: "None",
                                                levelIndex: 0,
                                                nameEvo: "None",
                                                levelEvo: 0
                                            }
                                        }
                                        mycol.update_one(exFind, newvalues)

                                else:
                                    embedVar = discord.Embed(
                                        title=
                                        f"〘 {interaction.user.name}-nyan's PokeCatch Result 〙",
                                        description=
                                        f"*Gotcha!*\n{result} ({rarity})\n ↳ Evolve & Level Up : **{evolved} (Lv. {evoLev})**",
                                        color=0xee1515)
                                    embedVar.set_image(url=evolvedGif)
                                    await interaction.followup.send(
                                        embed=embedVar)

                                    if result == userFind["pokemon"]:
                                        newvalues = {
                                            "$set": {
                                                "pokemon": '-',
                                                "pokemonlv": -1,
                                                nameIndex: "None",
                                                levelIndex: 0,
                                                levelEvo: evoLev
                                            }
                                        }

                                    elif evolved == userFind["pokemon"]:
                                        newvalues = {
                                            "$set": {
                                                "pokemonlv": evoLev,
                                                nameIndex: "None",
                                                levelIndex: 0,
                                                levelEvo: evoLev
                                            }
                                        }

                                    else:
                                        newvalues = {
                                            "$set": {
                                                nameIndex: "None",
                                                levelIndex: 0,
                                                levelEvo: evoLev
                                            }
                                        }

                                    mycol.update_one(userFind, newvalues)

                            else:
                                embedVar = discord.Embed(
                                    title=
                                    f"〘 {interaction.user.name}-nyan's PokeCatch Result 〙",
                                    description=
                                    f"*Gotcha!*\n{result} ({rarity})\n ↳ Evolve : **{evolved} (Lv. 1)**",
                                    color=0xee1515)
                                embedVar.set_image(url=evolvedGif)
                                await interaction.followup.send(embed=embedVar)

                                if result == userFind["pokemon"]:
                                    newvalues = {
                                        "$set": {
                                            "pokemon": '-',
                                            "pokemonlv": -1
                                        },
                                        "$push": {
                                            "pokeName": evolved,
                                            "pokeLevel": 1
                                        }
                                    }

                                else:
                                    newvalues = {
                                        "$push": {
                                            "pokeName": evolved,
                                            "pokeLevel": 1
                                        }
                                    }

                                mycol.update_one(userFind, newvalues)
                                exFind = mycol.find_one(
                                    {"userid": str(interaction.user.id)})
                                newvalues = {
                                    "$set": {
                                        nameIndex: "None",
                                        levelIndex: 0
                                    }
                                }
                                mycol.update_one(exFind, newvalues)

                        else:
                            embedVar = discord.Embed(
                                title=
                                f"〘 {interaction.user.name}-nyan's PokeCatch Result 〙",
                                description=
                                f"*Gotcha!*\n{result} ({rarity})\n ↳ Level Up : **{result} (Lv. {nowLev})**",
                                color=0xee1515)
                            embedVar.set_image(url=resultGif)
                            await interaction.followup.send(embed=embedVar)

                            stringIndex = "pokeLevel." + str(pokeIndex)
                            if result == userFind["pokemon"]:
                                newvalues = {
                                    "$set": {
                                        "pokemonlv": nowLev,
                                        stringIndex: nowLev
                                    }
                                }

                            else:
                                newvalues = {"$set": {stringIndex: nowLev}}

                            mycol.update_one(userFind, newvalues)

                    else:
                        embedVar = discord.Embed(
                            title=
                            f"〘 {interaction.user.name}-nyan's PokeCatch Result 〙",
                            description=f"*Gotcha!*\n**{result} ({rarity})**",
                            color=0xee1515)
                        embedVar.set_image(url=resultGif)
                        await interaction.followup.send(embed=embedVar)

                        newvalues = {
                            "$push": {
                                "pokeName": result,
                                "pokeLevel": 1
                            }
                        }
                        mycol.update_one(userFind, newvalues)

        button1.callback = button1_callback
        view = View(timeout=600)
        view.add_item(button1)

        embedVar = discord.Embed(
            title="— PokeCatch! —",
            description=
            "Cost per Catch : 1 Platina\n━━━━━━━━━━━\n**Rate UP : The 3 Legendary Birds (Moltres, Zapdos, Articuno)**\n\nPity System (NEW!!) :\n- In every 30x Catch guaranteed to get at least 1 Epic\n- In every 100x Catch guaranteed to get at least 1 Legendary",
            color=0xee1515)
        embedVar.set_image(
            url="https://mcdn.wallpapersafari.com/medium/61/37/kqVFfY.jpg")
        await ctx.response.send_message(embed=embedVar, view=view)
        checkView = await view.wait()

        if checkView:
            embedEdit = discord.Embed(
                title=f"Thank you for using pokecatch!",
                description="You can type /pokecatch to do more gachas",
                color=0xee1515)
            await ctx.edit_original_response(embed=embedEdit, view=None)

async def setup(bot):
  await bot.add_cog(Pokecatch(bot))