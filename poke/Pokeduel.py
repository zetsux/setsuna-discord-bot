import discord
import pymongo
import os
import json
import urllib.request as urllib2
from discord.ext import commands
from discord.commands import Option
import datetime
from discord.ui import Select, Button, Modal, TextInput, View
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

def arrangelb(idUser) :
  inFind = mycol.find_one({'userid' : str(idUser)})

  lbFind = mycol.find_one({'func' : "duellb"})
  newvalues = {'$pull': {'board': str(idUser)}}
  mycol.update_one(lbFind, newvalues)
  
  index = 0
  lbFind = mycol.find_one({'func' : "duellb"})
  lbBoard = lbFind['board']
  dWin = inFind['win']
  dLose = inFind['lose']
  dDraw = inFind['draw']
  
  for i in lbBoard:
      iUser = mycol.find_one({"userid": i})
  
      if dWin > iUser["win"] or (dWin == iUser["win"] and dLose < iUser["lose"]) or (
              dWin == iUser["win"] and dLose == iUser["lose"] and dDraw > iUser["lose"]):
          break
  
      index += 1
  
  lbFind = mycol.find_one({'func' : "duellb"})
  print(index)
  newvalues = {"$push": {'board' : {'$each': [str(idUser)], "$position": index}}}
  mycol.update_one(lbFind, newvalues)

class Pokeduel(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.slash_command(name='pokeduel', description='Find a challenger to battle each other in a Pokemon Duel')
  async def pokemon_duel(self, ctx):
    userFind = mycol.find_one({"userid": str(ctx.author.id)})
    if userFind == None:
        await ctx.respond(
            f'Neee {ctx.author.name}-nyan, yuk /regist dulu yuk baru liat pokemon..',
            ephemeral=True)
        return

    userInven = userFind["pokeName"]
    if userFind["pokemon"] not in userInven:
        await ctx.respond(
            f"Neee {ctx.author.name}-nyan, /pokepartner dulu yuk buat set pokemon yang mau dipake",
            ephemeral=True)
        return

    typeEff = {
        "Normal": "222221201222222222",
        "Fighting": "421124104222214241",
        "Flying": "242221421224122222",
        "Poison": "222111210224222224",
        "Ground": "220424124421422222",
        "Rock": "214212421422224222",
        "Bug": "211122211124242241",
        "Ghost": "022222242222242212",
        "Steel": "222224221112124224",
        "Fire": "222221424114224122",
        "Water": "222244222411222122",
        "Grass": "221144121141222122",
        "Electric": "224202222241122122",
        "Psychic": "242422221222212202",
        "Ice": "224242221114221422",
        "Dragon": "222222221222222420",
        "Dark": "212222242222242211",
        "Fairy": "242122221122222442"
    }

    indexEff = {
        "Normal": 0,
        "Fighting": 1,
        "Flying": 2,
        "Poison": 3,
        "Ground": 4,
        "Rock": 5,
        "Bug": 6,
        "Ghost": 7,
        "Steel": 8,
        "Fire": 9,
        "Water": 10,
        "Grass": 11,
        "Electric": 12,
        "Psychic": 13,
        "Ice": 14,
        "Dragon": 15,
        "Dark": 16,
        "Fairy": 17
    }

    buttonB = Button(label='Battle!',
                     style=discord.ButtonStyle.green,
                     row=0,
                     emoji='👍')
    buttonC = Button(label='Cancel Challenge',
                     style=discord.ButtonStyle.danger,
                     row=0,
                     emoji='👎')
    player = []
    playerName = []
    player.append(ctx.author.id)
    playerName.append(ctx.author.name)

    async def cancel_callback(interaction):
        if interaction.user.id != ctx.author.id:
            await interaction.response.send_message(
                f"Neee {interaction.user.name}-nyan, itu challenge orang ih, jangan dimainin..",
                ephemeral=True)
            return

        embedEdit = discord.Embed(
            title=f"[ PokeDuel Challenge Cancelled... ]",
            description=
            f"Cause : Cancelled manually by {interaction.user.name}-nyan",
            color=0xee1515)
        await interaction.response.edit_message(embed=embedEdit, view=None)
        view.stop()

    async def battle_callback(interaction):
        if interaction.user.id == ctx.author.id:
            await interaction.response.send_message(
                f"Neee {interaction.user.name}-nyan, masa mau duel sama diri sendiri sih..",
                ephemeral=True)
            return

        tapFind = mycol.find_one({"userid": str(interaction.user.id)})
        if tapFind == None:
            await interaction.response.send_message(
                f'Neee {ctx.author.name}-nyan, yuk /regist dulu yuk baru battle..',
                ephemeral=True)
            return

        tapInven = tapFind["pokeName"]
        if tapFind["pokemon"] not in tapInven:
            await interaction.response.send_message(
                f"Neee {interaction.user.name}-nyan, /pokepartner dulu yuk buat set pokemon yang mau dipake",
                ephemeral=True)
            return

        embedDel = discord.Embed(title=f'[ PokeDuel Challenge is underway! ]',
                                 description=f"Scroll down below...",
                                 color=0xee1515)
        await interaction.response.edit_message(embed=embedDel, view=None)
        view.stop()

        buttonA = Button(label='Attack',
                         style=discord.ButtonStyle.danger,
                         row=0,
                         emoji='⚔️')
        buttonSA = Button(label='Special',
                          style=discord.ButtonStyle.danger,
                          row=0,
                          emoji='💥')
        buttonAA = Button(label='Alt. Attack',
                          style=discord.ButtonStyle.green,
                          row=1,
                          emoji='🗡️')
        buttonSAA = Button(label='Alt. Special',
                           style=discord.ButtonStyle.green,
                           row=1,
                           emoji='🧨')
        buttonBA = Button(label='Boost Atk',
                          style=discord.ButtonStyle.primary,
                          row=2,
                          emoji='🚀')
        buttonBS = Button(label='Boost Sp. Atk',
                          style=discord.ButtonStyle.primary,
                          row=2,
                          emoji='📈')
        buttonF = Button(label='Forfeit',
                         style=discord.ButtonStyle.gray,
                         row=3,
                         emoji='🙏')
        buttonD = Button(label='Vote to Draw',
                         style=discord.ButtonStyle.gray,
                         row=3,
                         emoji='🤝')

        nonlocal player, playerName
        player.append(interaction.user.id)
        playerName.append(interaction.user.name)
        draw = [False, False]
        player0 = mycol.find_one({"userid": str(player[0])})
        player1 = mycol.find_one({"userid": str(player[1])})
        poke0 = player0["pokemon"]
        poke1 = player1["pokemon"]
        partLevel0 = player0["pokemonlv"]
        partLevel1 = player1["pokemonlv"]
        response0 = urllib2.urlopen(
            f'https://some-random-api.ml/pokemon/pokedex?pokemon={poke0.lower()}')
        data0 = json.loads(response0.read())
        response1 = urllib2.urlopen(
            f'https://some-random-api.ml/pokemon/pokedex?pokemon={poke1.lower()}')
        data1 = json.loads(response1.read())
        hp = [
            int(
                int(data0["stats"]["hp"]) *
                ((((partLevel0 * 2) - 1) + 19) / 20)),
            int(
                int(data1["stats"]["hp"]) *
                ((((partLevel1 * 2) - 1) + 19) / 20))
        ]
        atk = [
            int(
                int(data0["stats"]["attack"]) *
                ((((partLevel0 * 2) - 1) + 19) / 20)),
            int(
                int(data1["stats"]["attack"]) *
                ((((partLevel1 * 2) - 1) + 19) / 20))
        ]
        spatk = [
            int(
                int(data0["stats"]["sp_atk"]) *
                ((((partLevel0 * 2) - 1) + 19) / 20)),
            int(
                int(data1["stats"]["sp_atk"]) *
                ((((partLevel1 * 2) - 1) + 19) / 20))
        ]
        defense = [
            int(
                int(data0["stats"]["defense"]) *
                ((((partLevel0 * 2) - 1) + 19) / 20)),
            int(
                int(data1["stats"]["defense"]) *
                ((((partLevel1 * 2) - 1) + 19) / 20))
        ]
        spdef = [
            int(
                int(data0["stats"]["sp_def"]) *
                ((((partLevel0 * 2) - 1) + 19) / 20)),
            int(
                int(data1["stats"]["sp_def"]) *
                ((((partLevel1 * 2) - 1) + 19) / 20))
        ]
        speed = [
            int(
                int(data0["stats"]["speed"]) *
                ((((partLevel0 * 2) - 1) + 19) / 20)),
            int(
                int(data1["stats"]["speed"]) *
                ((((partLevel1 * 2) - 1) + 19) / 20))
        ]
        element = [data0["type"], data1["type"]]
        eleString = [', '.join(data0["type"]), ', '.join(data1["type"])]

        boosta = [2, 2]
        boosts = [2, 2]

        if speed[0] > speed[1]:
            turn = player[0]

        elif speed[1] > speed[0]:
            turn = player[1]

        else:
            turn = player[random.randint(0, 1)]

        async def atk_callback(dinteraction):
            if dinteraction.user.id != player[
                    0] and dinteraction.user.id != player[1]:
                await dinteraction.response.send_message(
                    f'Neee {dinteraction.user.name}-nyan, kamu kan ngga ikut battlenya sih.. /pokeduel sendiri deh',
                    ephemeral=True)
                return

            nonlocal turn
            if dinteraction.user.id == turn:
                if turn == player[0]:
                    atkerIndex = 0
                    dmgdIndex = 1
                    turn = player[1]

                elif turn == player[1]:
                    atkerIndex = 1
                    dmgdIndex = 0
                    turn = player[0]

                if len(element[dmgdIndex]) == 1:
                    if len(element[atkerIndex]) == 1:
                        dmgMul = int(typeEff[element[atkerIndex][0]][indexEff[
                            element[dmgdIndex][0]]]) / 2
                        atkElement = element[atkerIndex][0]

                    elif len(element[atkerIndex]) == 2:
                        mul1 = int(typeEff[element[atkerIndex][0]][indexEff[
                            element[dmgdIndex][0]]]) / 2
                        mul2 = int(typeEff[element[atkerIndex][1]][indexEff[
                            element[dmgdIndex][0]]]) / 2

                        if mul1 >= mul2:
                            dmgMul = mul1
                            atkElement = element[atkerIndex][0]

                        else:
                            dmgMul = mul2
                            atkElement = element[atkerIndex][1]

                elif len(element[dmgdIndex]) == 2:
                    if len(element[atkerIndex]) == 1:
                        dmgMul = (int(typeEff[element[atkerIndex][0]][indexEff[
                            element[dmgdIndex][0]]]) /
                                  2) * (int(typeEff[element[atkerIndex][0]][
                                      indexEff[element[dmgdIndex][1]]]) / 2)
                        atkElement = element[atkerIndex][0]

                    elif len(element[atkerIndex]) == 2:
                        mul1 = (int(typeEff[element[atkerIndex][0]][indexEff[
                            element[dmgdIndex][0]]]) /
                                2) * (int(typeEff[element[atkerIndex][0]][
                                    indexEff[element[dmgdIndex][1]]]) / 2)
                        mul2 = (int(typeEff[element[atkerIndex][1]][indexEff[
                            element[dmgdIndex][0]]]) /
                                2) * (int(typeEff[element[atkerIndex][1]][
                                    indexEff[element[dmgdIndex][1]]]) / 2)

                        if mul1 >= mul2:
                            dmgMul = mul1
                            atkElement = element[atkerIndex][0]

                        else:
                            dmgMul = mul2
                            atkElement = element[atkerIndex][1]

                damageDealt = int(
                    ((70 *
                      (atk[atkerIndex] *
                       (boosta[atkerIndex] / 2)) / defense[dmgdIndex]) / 7.5) *
                    ((10 + int(partLevel1)) / 10) * 1.5 * dmgMul)

                if damageDealt < 0:
                    damageDealt = 0
                hp[dmgdIndex] -= damageDealt

                if dinteraction.user.id == player[1]:
                    logPlay = playerName[1]
                    logPoke = poke1

                elif dinteraction.user.id == player[0]:
                    logPlay = playerName[0]
                    logPoke = poke0

                if hp[dmgdIndex] <= 0:
                    if dinteraction.user.id == player[1]:
                        loseFind = mycol.find_one({"userid": str(player[0])})
                        newvalues = {
                            "$set": {
                                "lose": (loseFind["lose"] + 1),
                                "latest":
                                f"Lost to {poke1} (Lv. {partLevel1}) using {poke0} (Lv. {partLevel0})"
                            }
                        }
                        mycol.update_one(loseFind, newvalues)

                        winFind = mycol.find_one({"userid": str(player[1])})
                        newvalues = {
                            "$set": {
                                "win": (winFind["win"] + 1),
                                "latest":
                                f"Win against {poke0} (Lv. {partLevel0}) using {poke1} (Lv. {partLevel1})"
                            }
                        }
                        mycol.update_one(winFind, newvalues)

                        embedRes = discord.Embed(
                            title=f"[ PokeDuel Challenge Ended... ]",
                            description=
                            f"Result : <@{str(player[1])}> wins by KOing enemy's pokemon!",
                            color=0xee1515)
                        await dinteraction.response.edit_message(
                            embed=embedRes, view=None)
                        if dmgMul < 1:
                            await dinteraction.followup.send(
                                f"Duel telah berakhir karena {logPoke} milik {logPlay}-nyan berhasil mengalahkan lawannya dengan {damageDealt} damage menggunakan {atkElement}-type Attack yang kurang efektif."
                            )
                        elif dmgMul == 1:
                            await dinteraction.followup.send(
                                f"Duel telah berakhir karena {logPoke} milik {logPlay}-nyan berhasil mengalahkan lawannya dengan {damageDealt} damage menggunakan {atkElement}-type Attack."
                            )
                        elif dmgMul > 1:
                            await dinteraction.followup.send(
                                f"Duel telah berakhir karena {logPoke} milik {logPlay}-nyan berhasil mengalahkan lawannya dengan {damageDealt} damage menggunakan {atkElement}-type Attack yang super efektif."
                            )

                        viewGame.stop()

                        arrangelb(str(player[0]))
                        arrangelb(str(player[1]))

                    elif dinteraction.user.id == player[0]:
                        loseFind = mycol.find_one({"userid": str(player[1])})
                        newvalues = {
                            "$set": {
                                "lose": (loseFind["lose"] + 1),
                                "latest":
                                f"Lost to {poke0} (Lv. {partLevel0}) using {poke1} (Lv. {partLevel1})"
                            }
                        }
                        mycol.update_one(loseFind, newvalues)

                        winFind = mycol.find_one({"userid": str(player[0])})
                        newvalues = {
                            "$set": {
                                "win": (winFind["win"] + 1),
                                "latest":
                                f"Win against {poke1} (Lv. {partLevel1}) using {poke0} (Lv. {partLevel0})"
                            }
                        }
                        mycol.update_one(winFind, newvalues)

                        embedRes = discord.Embed(
                            title=f"[ PokeDuel Challenge Ended... ]",
                            description=
                            f"Result : <@{str(player[0])}> wins by KOing enemy's pokemon!",
                            color=0xee1515)
                        await dinteraction.response.edit_message(
                            embed=embedRes, view=None)
                        if dmgMul < 1:
                            await dinteraction.followup.send(
                                f"Duel telah berakhir karena {logPoke} milik {logPlay}-nyan berhasil mengalahkan lawannya dengan {damageDealt} damage menggunakan {atkElement}-type Attack yang kurang efektif."
                            )
                        elif dmgMul == 1:
                            await dinteraction.followup.send(
                                f"Duel telah berakhir karena {logPoke} milik {logPlay}-nyan berhasil mengalahkan lawannya dengan {damageDealt} damage menggunakan {atkElement}-type Attack."
                            )
                        elif dmgMul > 1:
                            await dinteraction.followup.send(
                                f"Duel telah berakhir karena {logPoke} milik {logPlay}-nyan berhasil mengalahkan lawannya dengan {damageDealt} damage menggunakan {atkElement}-type Attack yang super efektif."
                            )
                        viewGame.stop()

                        arrangelb(str(player[0]))
                        arrangelb(str(player[1]))

                else:
                    embedChange = discord.Embed(
                        title=f'[ PokeDuel ]',
                        description=f"<@{str(turn)}>'s Turn",
                        color=0xee1515)
                    embedChange.add_field(
                        name=f"| {playerName[0]}'s {poke0} |",
                        value='```' + f'Type     : {str(eleString[0])}\n' +
                        f'Level    : {str(partLevel0)}\n' +
                        f'HP       : {str(hp[0])}\n' +
                        f'Atk      : {str(int(atk[0]*(boosta[0]/2)))}\n' +
                        f'Sp. Atk  : {str(int(spatk[0]*(boosts[0]/2)))}\n' +
                        f'Def      : {str(defense[0])}\n' +
                        f'Sp. Def  : {str(spdef[0])}\n' +
                        f'Speed    : {str(speed[0])}\n' + '```',
                        inline=True)
                    embedChange.add_field(
                        name=f"—————————",
                        value=
                        ' \u200b \u200b \u200b \u200b \u200b \u200b \u200b \u200b \u200b \u200b \u200b \u200b \u200b \u200b \u200b \u200b\u200b\u200b`VS`',
                        inline=True)
                    embedChange.add_field(
                        name=f"| {playerName[1]}'s {poke1} |",
                        value='```' + f'Type     : {str(eleString[1])}\n' +
                        f'Level    : {str(partLevel1)}\n' +
                        f'HP       : {str(hp[1])}\n' +
                        f'Atk      : {str(int(atk[1]*(boosta[1]/2)))}\n' +
                        f'Sp. Atk  : {str(int(spatk[1]*(boosts[1]/2)))}\n' +
                        f'Def      : {str(defense[1])}\n' +
                        f'Sp. Def  : {str(spdef[1])}\n' +
                        f'Speed    : {str(speed[1])}\n' + '```',
                        inline=True)

                    if dmgMul == 0:
                        embedChange.add_field(
                            name="— Duel Log —",
                            value='```' +
                            f"{logPlay}'s {logPoke} uses it's {atkElement}-type Attack but it doesn't affect the opposing pokemon"
                            + '```',
                            inline=False)
                    elif dmgMul < 1:
                        embedChange.add_field(
                            name="— Duel Log —",
                            value='```' +
                            f"{logPlay}'s {logPoke} deals {damageDealt} damage(s) to the opposing pokemon using it's {atkElement}-type Attack. It's not very effective!"
                            + '```',
                            inline=False)
                    elif dmgMul == 1:
                        embedChange.add_field(
                            name="— Duel Log —",
                            value='```' +
                            f"{logPlay}'s {logPoke} deals {damageDealt} damage(s) to the opposing pokemon using it's {atkElement}-type Attack"
                            + '```',
                            inline=False)
                    elif dmgMul > 1:
                        embedChange.add_field(
                            name="— Duel Log —",
                            value='```' +
                            f"{logPlay}'s {logPoke} deals {damageDealt} damage(s) to the opposing pokemon using it's {atkElement}-type Attack. It's super effective!"
                            + '```',
                            inline=False)
                    await dinteraction.response.edit_message(embed=embedChange)
                    await turnMsg.edit(
                        f"<@{str(turn)}>-nyan, giliran anata nih!")

            else:
                await dinteraction.response.send_message(
                    f'Neee {dinteraction.user.name}-nyan, belum turn anata ini. Sabar yah...',
                    ephemeral=True)
                # print(turn)

        async def spatk_callback(dinteraction):
            if dinteraction.user.id != player[
                    0] and dinteraction.user.id != player[1]:
                await dinteraction.response.send_message(
                    f'Neee {dinteraction.user.name}-nyan, kamu kan ngga ikut battlenya sih.. /pokeduel sendiri deh',
                    ephemeral=True)
                return

            nonlocal turn
            if dinteraction.user.id == turn:
                if turn == player[0]:
                    atkerIndex = 0
                    dmgdIndex = 1
                    turn = player[1]

                elif turn == player[1]:
                    atkerIndex = 1
                    dmgdIndex = 0
                    turn = player[0]

                if len(element[dmgdIndex]) == 1:
                    if len(element[atkerIndex]) == 1:
                        dmgMul = int(typeEff[element[atkerIndex][0]][indexEff[
                            element[dmgdIndex][0]]]) / 2
                        atkElement = element[atkerIndex][0]

                    elif len(element[atkerIndex]) == 2:
                        mul1 = int(typeEff[element[atkerIndex][0]][indexEff[
                            element[dmgdIndex][0]]]) / 2
                        mul2 = int(typeEff[element[atkerIndex][1]][indexEff[
                            element[dmgdIndex][0]]]) / 2

                        if mul1 >= mul2:
                            dmgMul = mul1
                            atkElement = element[atkerIndex][0]

                        else:
                            dmgMul = mul2
                            atkElement = element[atkerIndex][1]

                elif len(element[dmgdIndex]) == 2:
                    if len(element[atkerIndex]) == 1:
                        dmgMul = (int(typeEff[element[atkerIndex][0]][indexEff[
                            element[dmgdIndex][0]]]) /
                                  2) * (int(typeEff[element[atkerIndex][0]][
                                      indexEff[element[dmgdIndex][1]]]) / 2)
                        atkElement = element[atkerIndex][0]

                    elif len(element[atkerIndex]) == 2:
                        mul1 = (int(typeEff[element[atkerIndex][0]][indexEff[
                            element[dmgdIndex][0]]]) /
                                2) * (int(typeEff[element[atkerIndex][0]][
                                    indexEff[element[dmgdIndex][1]]]) / 2)
                        mul2 = (int(typeEff[element[atkerIndex][1]][indexEff[
                            element[dmgdIndex][0]]]) /
                                2) * (int(typeEff[element[atkerIndex][1]][
                                    indexEff[element[dmgdIndex][1]]]) / 2)

                        if mul1 >= mul2:
                            dmgMul = mul1
                            atkElement = element[atkerIndex][0]

                        else:
                            dmgMul = mul2
                            atkElement = element[atkerIndex][1]

                damageDealt = int(
                    ((70 *
                      (spatk[atkerIndex] *
                       (boosts[atkerIndex] / 2)) / spdef[dmgdIndex]) / 7.5) *
                    ((10 + int(partLevel1)) / 10) * 1.5 * dmgMul)

                if damageDealt < 0:
                    damageDealt = 0
                hp[dmgdIndex] -= damageDealt

                if dinteraction.user.id == player[1]:
                    logPlay = playerName[1]
                    logPoke = poke1

                elif dinteraction.user.id == player[0]:
                    logPlay = playerName[0]
                    logPoke = poke0

                if hp[dmgdIndex] <= 0:
                    if dinteraction.user.id == player[1]:
                        loseFind = mycol.find_one({"userid": str(player[0])})
                        newvalues = {
                            "$set": {
                                "lose": (loseFind["lose"] + 1),
                                "latest":
                                f"Lost to {poke1} (Lv. {partLevel1}) using {poke0} (Lv. {partLevel0})"
                            }
                        }
                        mycol.update_one(loseFind, newvalues)

                        winFind = mycol.find_one({"userid": str(player[1])})
                        newvalues = {
                            "$set": {
                                "win": (winFind["win"] + 1),
                                "latest":
                                f"Win against {poke0} (Lv. {partLevel0}) using {poke1} (Lv. {partLevel1})"
                            }
                        }
                        mycol.update_one(winFind, newvalues)

                        embedRes = discord.Embed(
                            title=f"[ PokeDuel Challenge Ended... ]",
                            description=
                            f"Result : <@{str(player[1])}> wins by KOing enemy's pokemon!",
                            color=0xee1515)
                        await dinteraction.response.edit_message(
                            embed=embedRes, view=None)
                        if dmgMul < 1:
                            await dinteraction.followup.send(
                                f"Duel telah berakhir karena {logPoke} milik {logPlay}-nyan berhasil mengalahkan lawannya dengan {damageDealt} damage menggunakan {atkElement}-type Special yang kurang efektif."
                            )
                        elif dmgMul == 1:
                            await dinteraction.followup.send(
                                f"Duel telah berakhir karena {logPoke} milik {logPlay}-nyan berhasil mengalahkan lawannya dengan {damageDealt} damage menggunakan {atkElement}-type Special."
                            )
                        elif dmgMul > 1:
                            await dinteraction.followup.send(
                                f"Duel telah berakhir karena {logPoke} milik {logPlay}-nyan berhasil mengalahkan lawannya dengan {damageDealt} damage menggunakan {atkElement}-type Special yang super efektif."
                            )

                        viewGame.stop()
                      
                        arrangelb(str(player[0]))
                        arrangelb(str(player[1]))

                    elif dinteraction.user.id == player[0]:
                        loseFind = mycol.find_one({"userid": str(player[1])})
                        newvalues = {
                            "$set": {
                                "lose": (loseFind["lose"] + 1),
                                "latest":
                                f"Lost to {poke0} (Lv. {partLevel0}) using {poke1} (Lv. {partLevel1})"
                            }
                        }
                        mycol.update_one(loseFind, newvalues)

                        winFind = mycol.find_one({"userid": str(player[0])})
                        newvalues = {
                            "$set": {
                                "win": (winFind["win"] + 1),
                                "latest":
                                f"Win against {poke1} (Lv. {partLevel1}) using {poke0} (Lv. {partLevel0})"
                            }
                        }
                        mycol.update_one(winFind, newvalues)

                        embedRes = discord.Embed(
                            title=f"[ PokeDuel Challenge Ended... ]",
                            description=
                            f"Result : <@{str(player[0])}> wins by KOing enemy's pokemon!",
                            color=0xee1515)
                        await dinteraction.response.edit_message(
                            embed=embedRes, view=None)
                        if dmgMul < 1:
                            await dinteraction.followup.send(
                                f"Duel telah berakhir karena {logPoke} milik {logPlay}-nyan berhasil mengalahkan lawannya dengan {damageDealt} damage menggunakan {atkElement}-type Special yang kurang efektif."
                            )
                        elif dmgMul == 1:
                            await dinteraction.followup.send(
                                f"Duel telah berakhir karena {logPoke} milik {logPlay}-nyan berhasil mengalahkan lawannya dengan {damageDealt} damage menggunakan {atkElement}-type Special."
                            )
                        elif dmgMul > 1:
                            await dinteraction.followup.send(
                                f"Duel telah berakhir karena {logPoke} milik {logPlay}-nyan berhasil mengalahkan lawannya dengan {damageDealt} damage menggunakan {atkElement}-type Special yang super efektif."
                            )

                        viewGame.stop()
                      
                        arrangelb(str(player[0]))
                        arrangelb(str(player[1]))

                else:
                    embedChange = discord.Embed(
                        title=f'[ PokeDuel ]',
                        description=f"<@{str(turn)}>'s Turn",
                        color=0xee1515)
                    embedChange.add_field(
                        name=f"| {playerName[0]}'s {poke0} |",
                        value='```' + f'Type     : {str(eleString[0])}\n' +
                        f'Level    : {str(partLevel0)}\n' +
                        f'HP       : {str(hp[0])}\n' +
                        f'Atk      : {str(int(atk[0]*(boosta[0]/2)))}\n' +
                        f'Sp. Atk  : {str(int(spatk[0]*(boosts[0]/2)))}\n' +
                        f'Def      : {str(defense[0])}\n' +
                        f'Sp. Def  : {str(spdef[0])}\n' +
                        f'Speed    : {str(speed[0])}\n' + '```',
                        inline=True)
                    embedChange.add_field(
                        name=f"—————————",
                        value=
                        ' \u200b \u200b \u200b \u200b \u200b \u200b \u200b \u200b \u200b \u200b \u200b \u200b \u200b \u200b \u200b \u200b\u200b\u200b`VS`',
                        inline=True)
                    embedChange.add_field(
                        name=f"| {playerName[1]}'s {poke1} |",
                        value='```' + f'Type     : {str(eleString[1])}\n' +
                        f'Level    : {str(partLevel1)}\n' +
                        f'HP       : {str(hp[1])}\n' +
                        f'Atk      : {str(int(atk[1]*(boosta[1]/2)))}\n' +
                        f'Sp. Atk  : {str(int(spatk[1]*(boosts[1]/2)))}\n' +
                        f'Def      : {str(defense[1])}\n' +
                        f'Sp. Def  : {str(spdef[1])}\n' +
                        f'Speed    : {str(speed[1])}\n' + '```',
                        inline=True)

                    if dmgMul == 0:
                        embedChange.add_field(
                            name="— Duel Log —",
                            value='```' +
                            f"{logPlay}'s {logPoke} uses it's {atkElement}-type Special but it doesn't affect the opposing pokemon"
                            + '```',
                            inline=False)
                    elif dmgMul < 1:
                        embedChange.add_field(
                            name="— Duel Log —",
                            value='```' +
                            f"{logPlay}'s {logPoke} deals {damageDealt} damage(s) to the opposing pokemon using it's {atkElement}-type Special. It's not very effective!"
                            + '```',
                            inline=False)
                    elif dmgMul == 1:
                        embedChange.add_field(
                            name="— Duel Log —",
                            value='```' +
                            f"{logPlay}'s {logPoke} deals {damageDealt} damage(s) to the opposing pokemon using it's {atkElement}-type Special"
                            + '```',
                            inline=False)
                    elif dmgMul > 1:
                        embedChange.add_field(
                            name="— Duel Log —",
                            value='```' +
                            f"{logPlay}'s {logPoke} deals {damageDealt} damage(s) to the opposing pokemon using it's {atkElement}-type Special. It's super effective!"
                            + '```',
                            inline=False)
                    await dinteraction.response.edit_message(embed=embedChange)
                    await turnMsg.edit(
                        f"<@{str(turn)}>-nyan, giliran anata nih!")

            else:
                await dinteraction.response.send_message(
                    f'Neee {dinteraction.user.name}-nyan, belum turn anata ini. Sabar yah...',
                    ephemeral=True)
                # print(turn)

        async def altatk_callback(dinteraction):
            if dinteraction.user.id != player[
                    0] and dinteraction.user.id != player[1]:
                await dinteraction.response.send_message(
                    f'Neee {dinteraction.user.name}-nyan, kamu kan ngga ikut battlenya sih.. /pokeduel sendiri deh',
                    ephemeral=True)
                return

            nonlocal turn
            if dinteraction.user.id == turn:
                if turn == player[0]:
                    atkerIndex = 0
                    dmgdIndex = 1
                    turn = player[1]

                elif turn == player[1]:
                    atkerIndex = 1
                    dmgdIndex = 0
                    turn = player[0]

                damageDealt = int(
                    ((70 *
                      (atk[atkerIndex] *
                       (boosta[atkerIndex] / 2)) / defense[dmgdIndex]) / 7.5) *
                    ((10 + int(partLevel1)) / 10))
                if damageDealt < 0:
                    damageDealt = 0
                hp[dmgdIndex] -= damageDealt

                if hp[dmgdIndex] <= 0:
                    if dinteraction.user.id == player[1]:
                        loseFind = mycol.find_one({"userid": str(player[0])})
                        newvalues = {
                            "$set": {
                                "lose": (loseFind["lose"] + 1),
                                "latest":
                                f"Lost to {poke1} (Lv. {partLevel1}) using {poke0} (Lv. {partLevel0})"
                            }
                        }
                        mycol.update_one(loseFind, newvalues)

                        winFind = mycol.find_one({"userid": str(player[1])})
                        newvalues = {
                            "$set": {
                                "win": (winFind["win"] + 1),
                                "latest":
                                f"Win against {poke0} (Lv. {partLevel0}) using {poke1} (Lv. {partLevel1})"
                            }
                        }
                        mycol.update_one(winFind, newvalues)

                        embedRes = discord.Embed(
                            title=f"[ PokeDuel Challenge Ended... ]",
                            description=
                            f"Result : <@{str(player[1])}> wins by KOing enemy's pokemon!",
                            color=0xee1515)
                        await dinteraction.response.edit_message(
                            embed=embedRes, view=None)
                        await dinteraction.followup.send(
                            f"Duel telah berakhir karena pokemon {dinteraction.user.name}-nyan berhasil mengalahkan lawannya dengan {damageDealt} menggunakan Alt. Attack!"
                        )
                        viewGame.stop()
                        arrangelb(str(player[0]))
                        arrangelb(str(player[1]))

                    elif dinteraction.user.id == player[0]:
                        loseFind = mycol.find_one({"userid": str(player[1])})
                        newvalues = {
                            "$set": {
                                "lose": (loseFind["lose"] + 1),
                                "latest":
                                f"Lost to {poke0} (Lv. {partLevel0}) using {poke1} (Lv. {partLevel1})"
                            }
                        }
                        mycol.update_one(loseFind, newvalues)

                        winFind = mycol.find_one({"userid": str(player[0])})
                        newvalues = {
                            "$set": {
                                "win": (winFind["win"] + 1),
                                "latest":
                                f"Win against {poke1} (Lv. {partLevel1}) using {poke0} (Lv. {partLevel0})"
                            }
                        }
                        mycol.update_one(winFind, newvalues)

                        embedRes = discord.Embed(
                            title=f"[ PokeDuel Challenge Ended... ]",
                            description=
                            f"Result : <@{str(player[0])}> wins by KOing enemy's pokemon!",
                            color=0xee1515)
                        await dinteraction.response.edit_message(
                            embed=embedRes, view=None)
                        await dinteraction.followup.send(
                            f"Duel telah berakhir karena pokemon {dinteraction.user.name}-nyan berhasil mengalahkan lawannya dengan {damageDealt} menggunakan Alt. Attack!"
                        )
                        viewGame.stop()
                        arrangelb(str(player[0]))
                        arrangelb(str(player[1]))

                else:
                    embedChange = discord.Embed(
                        title=f'[ PokeDuel ]',
                        description=f"<@{str(turn)}>'s Turn",
                        color=0xee1515)
                    embedChange.add_field(
                        name=f"| {playerName[0]}'s {poke0} |",
                        value='```' + f'Type     : {str(eleString[0])}\n' +
                        f'Level    : {str(partLevel0)}\n' +
                        f'HP       : {str(hp[0])}\n' +
                        f'Atk      : {str(int(atk[0]*(boosta[0]/2)))}\n' +
                        f'Sp. Atk  : {str(int(spatk[0]*(boosts[0]/2)))}\n' +
                        f'Def      : {str(defense[0])}\n' +
                        f'Sp. Def  : {str(spdef[0])}\n' +
                        f'Speed    : {str(speed[0])}\n' + '```',
                        inline=True)
                    embedChange.add_field(
                        name=f"—————————",
                        value=
                        ' \u200b \u200b \u200b \u200b \u200b \u200b \u200b \u200b \u200b \u200b \u200b \u200b \u200b \u200b \u200b \u200b\u200b\u200b`VS`',
                        inline=True)
                    embedChange.add_field(
                        name=f"| {playerName[1]}'s {poke1} |",
                        value='```' + f'Type     : {str(eleString[1])}\n' +
                        f'Level    : {str(partLevel1)}\n' +
                        f'HP       : {str(hp[1])}\n' +
                        f'Atk      : {str(int(atk[1]*(boosta[1]/2)))}\n' +
                        f'Sp. Atk  : {str(int(spatk[1]*(boosts[1]/2)))}\n' +
                        f'Def      : {str(defense[1])}\n' +
                        f'Sp. Def  : {str(spdef[1])}\n' +
                        f'Speed    : {str(speed[1])}\n' + '```',
                        inline=True)

                    if atkerIndex == 0:
                        embedChange.add_field(
                            name="— Duel Log —",
                            value='```' +
                            f"{playerName[0]}'s {poke0} deals {damageDealt} damage(s) to the opposing pokemon using Alt. Attack"
                            + '```',
                            inline=False)

                    elif atkerIndex == 1:
                        embedChange.add_field(
                            name="— Duel Log —",
                            value='```' +
                            f"{playerName[1]}'s {poke1} deals {damageDealt} damage(s) to the opposing pokemon using Alt. Attack"
                            + '```',
                            inline=False)
                    await dinteraction.response.edit_message(embed=embedChange)
                    await turnMsg.edit(
                        f"<@{str(turn)}>-nyan, giliran anata nih!")

            else:
                await dinteraction.response.send_message(
                    f'Neee {dinteraction.user.name}-nyan, belum turn anata ini. Sabar yah...',
                    ephemeral=True)

        async def altspatk_callback(dinteraction):
            if dinteraction.user.id != player[
                    0] and dinteraction.user.id != player[1]:
                await dinteraction.response.send_message(
                    f'Neee {dinteraction.user.name}-nyan, kamu kan ngga ikut battlenya sih.. /pokeduel sendiri deh',
                    ephemeral=True)
                return

            nonlocal turn
            if dinteraction.user.id == turn:
                if turn == player[0]:
                    atkerIndex = 0
                    dmgdIndex = 1
                    turn = player[1]

                elif turn == player[1]:
                    atkerIndex = 1
                    dmgdIndex = 0
                    turn = player[0]

                damageDealt = int(
                    ((70 *
                      (spatk[atkerIndex] *
                       (boosts[atkerIndex] / 2)) / spdef[dmgdIndex]) / 7.5) *
                    ((10 + int(partLevel1)) / 10))
                if damageDealt < 0:
                    damageDealt = 0
                hp[dmgdIndex] -= damageDealt

                if hp[dmgdIndex] <= 0:
                    if dinteraction.user.id == player[1]:
                        loseFind = mycol.find_one({"userid": str(player[0])})
                        newvalues = {
                            "$set": {
                                "lose": (loseFind["lose"] + 1),
                                "latest":
                                f"Lost to {poke1} (Lv. {partLevel1}) using {poke0} (Lv. {partLevel0})"
                            }
                        }
                        mycol.update_one(loseFind, newvalues)

                        winFind = mycol.find_one({"userid": str(player[1])})
                        newvalues = {
                            "$set": {
                                "win": (winFind["win"] + 1),
                                "latest":
                                f"Win against {poke0} (Lv. {partLevel0}) using {poke1} (Lv. {partLevel1})"
                            }
                        }
                        mycol.update_one(winFind, newvalues)

                        embedRes = discord.Embed(
                            title=f"[ PokeDuel Challenge Ended... ]",
                            description=
                            f"Result : <@{str(player[1])}> wins by KOing enemy's pokemon!",
                            color=0xee1515)
                        await dinteraction.response.edit_message(
                            embed=embedRes, view=None)
                        await dinteraction.followup.send(
                            f"Duel telah berakhir karena pokemon {dinteraction.user.name}-nyan berhasil mengalahkan lawannya dengan {damageDealt} menggunakan Alt. Special!"
                        )
                        viewGame.stop()
                        arrangelb(str(player[0]))
                        arrangelb(str(player[1]))

                    elif dinteraction.user.id == player[0]:
                        loseFind = mycol.find_one({"userid": str(player[1])})
                        newvalues = {
                            "$set": {
                                "lose": (loseFind["lose"] + 1),
                                "latest":
                                f"Lost to {poke0} (Lv. {partLevel0}) using {poke1} (Lv. {partLevel1})"
                            }
                        }
                        mycol.update_one(loseFind, newvalues)

                        winFind = mycol.find_one({"userid": str(player[0])})
                        newvalues = {
                            "$set": {
                                "win": (winFind["win"] + 1),
                                "latest":
                                f"Win against {poke1} (Lv. {partLevel1}) using {poke0} (Lv. {partLevel0})"
                            }
                        }
                        mycol.update_one(winFind, newvalues)

                        embedRes = discord.Embed(
                            title=f"[ PokeDuel Challenge Ended... ]",
                            description=
                            f"Result : <@{str(player[0])}> wins by KOing enemy's pokemon!",
                            color=0xee1515)
                        await dinteraction.response.edit_message(
                            embed=embedRes, view=None)
                        await dinteraction.followup.send(
                            f"Duel telah berakhir karena pokemon {dinteraction.user.name}-nyan berhasil mengalahkan lawannya dengan {damageDealt} menggunakan Alt. Special!"
                        )
                        viewGame.stop()
                        arrangelb(str(player[0]))
                        arrangelb(str(player[1]))

                else:
                    embedChange = discord.Embed(
                        title=f'[ PokeDuel ]',
                        description=f"<@{str(turn)}>'s Turn",
                        color=0xee1515)
                    embedChange.add_field(
                        name=f"| {playerName[0]}'s {poke0} |",
                        value='```' + f'Type     : {str(eleString[0])}\n' +
                        f'Level    : {str(partLevel0)}\n' +
                        f'HP       : {str(hp[0])}\n' +
                        f'Atk      : {str(int(atk[0]*(boosta[0]/2)))}\n' +
                        f'Sp. Atk  : {str(int(spatk[0]*(boosts[0]/2)))}\n' +
                        f'Def      : {str(defense[0])}\n' +
                        f'Sp. Def  : {str(spdef[0])}\n' +
                        f'Speed    : {str(speed[0])}\n' + '```',
                        inline=True)
                    embedChange.add_field(
                        name=f"—————————",
                        value=
                        ' \u200b \u200b \u200b \u200b \u200b \u200b \u200b \u200b \u200b \u200b \u200b \u200b \u200b \u200b \u200b \u200b\u200b\u200b`VS`',
                        inline=True)
                    embedChange.add_field(
                        name=f"| {playerName[1]}'s {poke1} |",
                        value='```' + f'Type     : {str(eleString[1])}\n' +
                        f'Level    : {str(partLevel1)}\n' +
                        f'HP       : {str(hp[1])}\n' +
                        f'Atk      : {str(int(atk[1]*(boosta[1]/2)))}\n' +
                        f'Sp. Atk  : {str(int(spatk[1]*(boosts[1]/2)))}\n' +
                        f'Def      : {str(defense[1])}\n' +
                        f'Sp. Def  : {str(spdef[1])}\n' +
                        f'Speed    : {str(speed[1])}\n' + '```',
                        inline=True)

                    if atkerIndex == 0:
                        embedChange.add_field(
                            name="— Duel Log —",
                            value='```' +
                            f"{playerName[0]}'s {poke0} deals {damageDealt} damage(s) to the opposing pokemon using Alt. Special"
                            + '```',
                            inline=False)

                    elif atkerIndex == 1:
                        embedChange.add_field(
                            name="— Duel Log —",
                            value='```' +
                            f"{playerName[1]}'s {poke1} deals {damageDealt} damage(s) to the opposing pokemon using Alt. Special"
                            + '```',
                            inline=False)
                    await dinteraction.response.edit_message(embed=embedChange)
                    await turnMsg.edit(
                        f"<@{str(turn)}>-nyan, giliran anata nih!")

            else:
                await dinteraction.response.send_message(
                    f'Neee {dinteraction.user.name}-nyan, belum turn anata ini. Sabar yah...',
                    ephemeral=True)

        async def boostatk_callback(dinteraction):
            if dinteraction.user.id != player[
                    0] and dinteraction.user.id != player[1]:
                await dinteraction.response.send_message(
                    f'Neee {dinteraction.user.name}-nyan, kamu kan ngga ikut battlenya sih.. /pokeduel sendiri deh',
                    ephemeral=True)
                return

            nonlocal turn
            if dinteraction.user.id == turn:
                if turn == player[0]:
                    tempIndex = 0
                    turn = player[1]

                elif turn == player[1]:
                    tempIndex = 1
                    turn = player[0]

                boosta[tempIndex] += 1

                embedChange = discord.Embed(
                    title=f'[ PokeDuel ]',
                    description=f"<@{str(turn)}>'s Turn",
                    color=0xee1515)
                embedChange.add_field(
                    name=f"| {playerName[0]}'s {poke0} |",
                    value='```' + f'Type     : {str(eleString[0])}\n' +
                    f'Level    : {str(partLevel0)}\n' +
                    f'HP       : {str(hp[0])}\n' +
                    f'Atk      : {str(int(atk[0]*(boosta[0]/2)))}\n' +
                    f'Sp. Atk  : {str(int(spatk[0]*(boosts[0]/2)))}\n' +
                    f'Def      : {str(defense[0])}\n' +
                    f'Sp. Def  : {str(spdef[0])}\n' +
                    f'Speed    : {str(speed[0])}\n' + '```',
                    inline=True)
                embedChange.add_field(
                    name=f"—————————",
                    value=
                    ' \u200b \u200b \u200b \u200b \u200b \u200b \u200b \u200b \u200b \u200b \u200b \u200b \u200b \u200b \u200b \u200b\u200b\u200b`VS`',
                    inline=True)
                embedChange.add_field(
                    name=f"| {playerName[1]}'s {poke1} |",
                    value='```' + f'Type     : {str(eleString[1])}\n' +
                    f'Level    : {str(partLevel1)}\n' +
                    f'HP       : {str(hp[1])}\n' +
                    f'Atk      : {str(int(atk[1]*(boosta[1]/2)))}\n' +
                    f'Sp. Atk  : {str(int(spatk[1]*(boosts[1]/2)))}\n' +
                    f'Def      : {str(defense[1])}\n' +
                    f'Sp. Def  : {str(spdef[1])}\n' +
                    f'Speed    : {str(speed[1])}\n' + '```',
                    inline=True)

                if tempIndex == 0:
                    embedChange.add_field(
                        name="— Duel Log —",
                        value='```' +
                        f"{playerName[0]}'s {poke0} boosts it's Attack to {int(atk[0]*(boosta[0]/2))}"
                        + '```',
                        inline=False)

                elif tempIndex == 1:
                    embedChange.add_field(
                        name="— Duel Log —",
                        value='```' +
                        f"{playerName[1]}'s {poke1} boosts it's Attack to {int(atk[1]*(boosta[1]/2))}"
                        + '```',
                        inline=False)
                await dinteraction.response.edit_message(embed=embedChange)
                await turnMsg.edit(f"<@{str(turn)}>-nyan, giliran anata nih!")

            else:
                await dinteraction.response.send_message(
                    f'Neee {dinteraction.user.name}-nyan, belum turn anata ini. Sabar yah...',
                    ephemeral=True)

        async def boostspatk_callback(dinteraction):
            if dinteraction.user.id != player[
                    0] and dinteraction.user.id != player[1]:
                await dinteraction.response.send_message(
                    f'Neee {dinteraction.user.name}-nyan, kamu kan ngga ikut battlenya sih.. /pokeduel sendiri deh',
                    ephemeral=True)
                return

            nonlocal turn
            if dinteraction.user.id == turn:
                if turn == player[0]:
                    tempIndex = 0
                    turn = player[1]

                elif turn == player[1]:
                    tempIndex = 1
                    turn = player[0]

                boosts[tempIndex] += 1

                embedChange = discord.Embed(
                    title=f'[ PokeDuel ]',
                    description=f"<@{str(turn)}>'s Turn",
                    color=0xee1515)
                embedChange.add_field(
                    name=f"| {playerName[0]}'s {poke0} |",
                    value='```' + f'Type     : {str(eleString[0])}\n' +
                    f'Level    : {str(partLevel0)}\n' +
                    f'HP       : {str(hp[0])}\n' +
                    f'Atk      : {str(int(atk[0]*(boosta[0]/2)))}\n' +
                    f'Sp. Atk  : {str(int(spatk[0]*(boosts[0]/2)))}\n' +
                    f'Def      : {str(defense[0])}\n' +
                    f'Sp. Def  : {str(spdef[0])}\n' +
                    f'Speed    : {str(speed[0])}\n' + '```',
                    inline=True)
                embedChange.add_field(
                    name=f"—————————",
                    value=
                    ' \u200b \u200b \u200b \u200b \u200b \u200b \u200b \u200b \u200b \u200b \u200b \u200b \u200b \u200b \u200b \u200b\u200b\u200b`VS`',
                    inline=True)
                embedChange.add_field(
                    name=f"| {playerName[1]}'s {poke1} |",
                    value='```' + f'Type     : {str(eleString[1])}\n' +
                    f'Level    : {str(partLevel1)}\n' +
                    f'HP       : {str(hp[1])}\n' +
                    f'Atk      : {str(int(atk[1]*(boosta[1]/2)))}\n' +
                    f'Sp. Atk  : {str(int(spatk[1]*(boosts[1]/2)))}\n' +
                    f'Def      : {str(defense[1])}\n' +
                    f'Sp. Def  : {str(spdef[1])}\n' +
                    f'Speed    : {str(speed[1])}\n' + '```',
                    inline=True)

                if tempIndex == 0:
                    embedChange.add_field(
                        name="— Duel Log —",
                        value='```' +
                        f"{playerName[0]}'s {poke0} boosts it's Sp. Atk to {int(spatk[0]*(boosts[0]/2))}"
                        + '```',
                        inline=False)

                elif tempIndex == 1:
                    embedChange.add_field(
                        name="— Duel Log —",
                        value='```' +
                        f"{playerName[1]}'s {poke1} boosts it's Sp. Atk to {int(spatk[1]*(boosts[1]/2))}"
                        + '```',
                        inline=False)
                await dinteraction.response.edit_message(embed=embedChange)
                await turnMsg.edit(f"<@{str(turn)}>-nyan, giliran anata nih!")

            else:
                await dinteraction.response.send_message(
                    f'Neee {dinteraction.user.name}-nyan, belum turn anata ini. Sabar yah...',
                    ephemeral=True)

        async def forfeit_callback(dinteraction):
            if dinteraction.user.id != player[
                    0] and dinteraction.user.id != player[1]:
                await dinteraction.response.send_message(
                    f'Neee {dinteraction.user.name}-nyan, kamu kan ngga ikut battlenya sih.. /pokeduel sendiri deh',
                    ephemeral=True)
                return

            if dinteraction.user.id == player[0]:
                loseFind = mycol.find_one({"userid": str(player[0])})
                newvalues = {
                    "$set": {
                        "lose": (loseFind["lose"] + 1),
                        "latest":
                        f"Lost to {poke1} (Lv. {partLevel1}) using {poke0} (Lv. {partLevel0})"
                    }
                }
                mycol.update_one(loseFind, newvalues)

                winFind = mycol.find_one({"userid": str(player[1])})
                newvalues = {
                    "$set": {
                        "win": (winFind["win"] + 1),
                        "latest":
                        f"Win against {poke0} (Lv. {partLevel0}) using {poke1} (Lv. {partLevel1})"
                    }
                }
                mycol.update_one(winFind, newvalues)

                embedRes = discord.Embed(
                    title=f"[ PokeDuel Challenge Ended... ]",
                    description=
                    f"Result : <@{str(player[1])}> wins cause of forfeit!",
                    color=0xee1515)
                await dinteraction.response.edit_message(embed=embedRes,
                                                         view=None)
                await dinteraction.followup.send(
                    f"Duel telah berakhir karena {dinteraction.user.name}-nyan menyerah!"
                )
                viewGame.stop()
                arrangelb(str(player[0]))
                arrangelb(str(player[1]))

            elif dinteraction.user.id == player[1]:
                loseFind = mycol.find_one({"userid": str(player[1])})
                newvalues = {
                    "$set": {
                        "lose": (loseFind["lose"] + 1),
                        "latest":
                        f"Lost to {poke0} (Lv. {partLevel0}) using {poke1} (Lv. {partLevel1})"
                    }
                }
                mycol.update_one(loseFind, newvalues)

                winFind = mycol.find_one({"userid": str(player[0])})
                newvalues = {
                    "$set": {
                        "win": (winFind["win"] + 1),
                        "latest":
                        f"Win against {poke1} (Lv. {partLevel1}) using {poke0} (Lv. {partLevel0})"
                    }
                }
                mycol.update_one(winFind, newvalues)

                embedRes = discord.Embed(
                    title=f"[ PokeDuel Challenge Ended... ]",
                    description=
                    f"Result : <@{str(player[0])}> wins cause of forfeit!",
                    color=0xee1515)
                await dinteraction.response.edit_message(embed=embedRes,
                                                         view=None)
                await dinteraction.followup.send(
                    f"Duel telah berakhir karena {dinteraction.user.name}-nyan menyerah!"
                )
                viewGame.stop()
                arrangelb(str(player[0]))
                arrangelb(str(player[1]))

        async def draw_callback(dinteraction):
            if dinteraction.user.id != player[
                    0] and dinteraction.user.id != player[1]:
                await dinteraction.response.send_message(
                    f'Neee {dinteraction.user.name}-nyan, kamu kan ngga ikut battlenya sih.. /pokeduel sendiri deh',
                    ephemeral=True)
                return

            if (dinteraction.user.id == player[0]
                    and draw[0]) or (dinteraction.user.id == player[1]
                                     and draw[1]):
                await dinteraction.response.send_message(
                    f'Sabar yah {dinteraction.user.name}-nyan, lawan anata kayanya belum mau draw deh. Coba tanyain lagi aja...',
                    ephemeral=True)
                return

            if dinteraction.user.id == player[0]:
                draw[0] = True

            elif dinteraction.user.id == player[1]:
                draw[1] = True

            if draw[0] and draw[1]:
                embedDraw = discord.Embed(
                    title=f"[ PokeDuel Challenge Ended... ]",
                    description=
                    f"Result : Both Parties agreed to end the match in a draw",
                    color=0xee1515)
                await dinteraction.response.edit_message(embed=embedDraw,
                                                         view=None)
                await dinteraction.followup.send(
                    "Duel telah diakhiri dengan draw hasil keputusan kedua pihak!"
                )
                firstFind = mycol.find_one({"userid": str(player[1])})
                newvalues = {
                    "$set": {
                        "draw": (firstFind["draw"] + 1),
                        "latest":
                        f"Draw against {poke0} (Lv. {partLevel0}) using {poke1} (Lv. {partLevel1})"
                    }
                }
                mycol.update_one(firstFind, newvalues)

                secondFind = mycol.find_one({"userid": str(player[0])})
                newvalues = {
                    "$set": {
                        "draw": (secondFind["draw"] + 1),
                        "latest":
                        f"Draw against {poke1} (Lv. {partLevel1}) using {poke0} (Lv. {partLevel0})"
                    }
                }
                mycol.update_one(secondFind, newvalues)
                viewGame.stop()
                arrangelb(str(player[0]))
                arrangelb(str(player[1]))

            elif draw[0]:
                await dinteraction.response.send_message(
                    f"<@{str(player[1])}>, lawan anata telah mengajukan draw, silahkan tekan tombol 'Vote to Draw' untuk menerima"
                )

            elif draw[1]:
                await dinteraction.response.send_message(
                    f"<@{str(player[0])}>, lawan anata telah mengajukan draw, silahkan tekan tombol 'Vote to Draw' untuk menerima"
                )

        buttonA.callback = atk_callback
        buttonSA.callback = spatk_callback
        buttonAA.callback = altatk_callback
        buttonSAA.callback = altspatk_callback
        buttonBA.callback = boostatk_callback
        buttonBS.callback = boostspatk_callback
        buttonF.callback = forfeit_callback
        buttonD.callback = draw_callback
        viewGame = View(timeout=750)
        viewGame.add_item(buttonA)
        viewGame.add_item(buttonSA)
        viewGame.add_item(buttonAA)
        viewGame.add_item(buttonSAA)
        viewGame.add_item(buttonBA)
        viewGame.add_item(buttonBS)
        viewGame.add_item(buttonF)
        viewGame.add_item(buttonD)

        embedGame = discord.Embed(title=f'[ PokeDuel ]',
                                  description=f"<@{str(turn)}>'s Turn",
                                  color=0xee1515)
        embedGame.add_field(
            name=f"| {playerName[0]}'s {poke0} |",
            value='```' + f'Type     : {str(eleString[0])}\n' +
            f'Level    : {str(partLevel0)}\n' + f'HP       : {str(hp[0])}\n' +
            f'Atk      : {str(int(atk[0]*(boosta[0]/2)))}\n' +
            f'Sp. Atk  : {str(int(spatk[0]*(boosts[0]/2)))}\n' +
            f'Def      : {str(defense[0])}\n' +
            f'Sp. Def  : {str(spdef[0])}\n' + f'Speed    : {str(speed[0])}\n' +
            '```',
            inline=True)
        embedGame.add_field(
            name=f"—————————",
            value=
            ' \u200b \u200b \u200b \u200b \u200b \u200b \u200b \u200b \u200b \u200b \u200b \u200b \u200b \u200b \u200b \u200b\u200b\u200b`VS`',
            inline=True)
        embedGame.add_field(
            name=f"| {playerName[1]}'s {poke1} |",
            value='```' + f'Type     : {str(eleString[1])}\n' +
            f'Level    : {str(partLevel1)}\n' + f'HP       : {str(hp[1])}\n' +
            f'Atk      : {str(int(atk[1]*(boosts[1]/2)))}\n' +
            f'Sp. Atk  : {str(int(spatk[1]*(boosts[1]/2)))}\n' +
            f'Def      : {str(defense[1])}\n' +
            f'Sp. Def  : {str(spdef[1])}\n' + f'Speed    : {str(speed[1])}\n' +
            '```',
            inline=True)
        embedGame.add_field(name="— Duel Log —",
                            value='```' + f"Duel Starts!" + '```',
                            inline=False)
        gameMsg = await panelMsg.channel.send(embed=embedGame, view=viewGame)
        turnMsg = await gameMsg.channel.send(
            f"<@{str(turn)}>-nyan, giliran anata nih!")
        checkGame = await viewGame.wait()

        if checkGame:
            if turn == player[1]:
                loseFind = mycol.find_one({"userid": str(player[1])})
                newvalues = {
                    "$set": {
                        "lose": (loseFind["lose"] + 1),
                        "latest":
                        f"Lost to {poke0} (Lv. {partLevel0}) using {poke1} (Lv. {partLevel1})"
                    }
                }
                mycol.update_one(loseFind, newvalues)

                winFind = mycol.find_one({"userid": str(player[0])})
                newvalues = {
                    "$set": {
                        "win": (winFind["win"] + 1),
                        "latest":
                        f"Win against {poke1} (Lv. {partLevel1}) using {poke0} (Lv. {partLevel0})"
                    }
                }
                mycol.update_one(winFind, newvalues)

                embedRes = discord.Embed(
                    title=f"[ PokeDuel Challenge Ended... ]",
                    description=
                    f"Result : <@{str(player[0])}> wins due to enemy not playing for too long!",
                    color=0xee1515)
                await gameMsg.edit_original_message(embed=embedRes, view=None)
                await gameMsg.channel.send(f"Duel telah berakhir karena <@{str(player[1])}> kehabisan waktu!")
                arrangelb(str(player[0]))
                arrangelb(str(player[1]))

            else:
                loseFind = mycol.find_one({"userid": str(player[0])})
                newvalues = {
                    "$set": {
                        "lose": (loseFind["lose"] + 1),
                        "latest":
                        f"Lost to {poke1} (Lv. {partLevel1}) using {poke0} (Lv. {partLevel0})"
                    }
                }
                mycol.update_one(loseFind, newvalues)

                winFind = mycol.find_one({"userid": str(player[1])})
                newvalues = {
                    "$set": {
                        "win": (winFind["win"] + 1),
                        "latest":
                        f"Win against {poke0} (Lv. {partLevel0}) using {poke1} (Lv. {partLevel1})"
                    }
                }
                mycol.update_one(winFind, newvalues)

                embedRes = discord.Embed(
                    title=f"[ PokeDuel Challenge Ended... ]",
                    description=
                    f"Result : <@{str(player[1])}> wins due to enemy not playing for too long!",
                    color=0xee1515)
                await gameMsg.edit_original_message(embed=embedRes, view=None)
                await gameMsg.channel.send(f"Duel telah berakhir karena <@{str(player[0])}> kehabisan waktu!")

                arrangelb(str(player[0]))
                arrangelb(str(player[1]))

    buttonB.callback = battle_callback
    buttonC.callback = cancel_callback
    view = View(timeout=750)
    view.add_item(buttonB)
    view.add_item(buttonC)

    embedVar = discord.Embed(
        title=f'[ PokeDuel Challenge by {ctx.author.name}-nyan ]',
        description=f"Click the 'Battle!' button to accept",
        color=0xee1515)
    panelMsg = await ctx.respond(embed=embedVar, view=view)
    checkView = await view.wait()

    if checkView:
        embedEdit = discord.Embed(
            title=f"[ PokeDuel Challenge Cancelled... ]",
            description=
            f"Cause : Timed out, no one accepted the duel for too long",
            color=0xee1515)
        await panelMsg.edit_original_message(embed=embedEdit, view=None)

def setup(bot):
  bot.add_cog(Pokeduel(bot))