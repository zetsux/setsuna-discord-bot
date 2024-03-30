import discord
import os
import pymongo
import datetime
from discord.ui import Select, Button, Modal, TextInput, View
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

class Blackjack(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    
  @commands.slash_command(name='blackjack', description='Play blackjack against a CPU Dealer')
  async def play_blackjack(self, ctx, number: Option(int, "Number of gold to bet", required=True)):
    if number < 0:
        await ctx.respond(f'Neee anata ngga jelas deh, {ctx.author.name}-nyan',
                          ephemeral=True)
        return

    userFind = mycol.find_one({"userid": str(ctx.author.id)})
    gamer = ctx.author.id
    if userFind == None:
        await ctx.respond(
            f'Neee {ctx.author.name}-nyan, yuk bisa yuk /regist dulu~',
            ephemeral=True)
        return

    goldCount = userFind["gold"]
    if goldCount < number:
        await ctx.respond(
            f'Neee {ctx.author.name}-nyan, gold anata cuma {goldCount}, ngga cukup dong..',
            ephemeral=True)
        return

    cards = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
    cards_values = {
        "A": 11,
        "2": 2,
        "3": 3,
        "4": 4,
        "5": 5,
        "6": 6,
        "7": 7,
        "8": 8,
        "9": 9,
        "10": 10,
        "J": 10,
        "Q": 10,
        "K": 10
    }
    suits = ['♠️', '♥', '♣️', '♦']

    dealerCount = 0
    playerCount = 0
    dealerAs = 0
    playerAs = 0
    arena = []
    tempNum = random.choice(cards)
    tempCard = tempNum + random.choice(suits)

    while tempCard in arena:
        tempNum = random.choice(cards)
        tempCard = tempNum + random.choice(suits)

    dealerCount += cards_values[tempNum]
    arena.append(tempCard)
    if tempNum == 'A':
        dealerAs += 1

    for x in range(2):
        tempNum = random.choice(cards)
        tempCard = tempNum + random.choice(suits)

        while tempCard in arena:
            tempNum = random.choice(cards)
            tempCard = tempNum + random.choice(suits)

        playerCount += cards_values[tempNum]
        arena.append(tempCard)
        if tempNum == 'A':
            playerAs += 1

    dealer = arena[0]
    player = arena[1] + ', ' + arena[2]
    if playerCount == 21:
        playerPure = True
    else:
        playerPure = False
        while playerCount > 21 and playerAs >= 1:
            playerCount -= 10
            playerAs -= 1

    buttonH = Button(label='Hit', style=discord.ButtonStyle.danger, row=0)
    buttonS = Button(label='Stand', style=discord.ButtonStyle.primary, row=0)
    buttonD = Button(label="Double", style=discord.ButtonStyle.green, row=0)

    async def hit_callback(interaction):
        if interaction.user.id != gamer:
            await interaction.response.send_message(
                f"Neee {interaction.user.name}-nyan, mending /blackjack sendiri deh, jangan pake punya orang lain ih",
                ephemeral=True)
            return

        nonlocal playerCount, player, dealerCount, dealer, dealerAs, playerAs
        inNum = random.choice(cards)
        inCard = inNum + random.choice(suits)

        while inCard in arena:
            inNum = random.choice(cards)
            inCard = inNum + random.choice(suits)

        playerCount += cards_values[inNum]
        arena.append(inCard)
        player = player + ', ' + inCard
        if inNum == 'A':
            playerAs += 1

        if playerCount > 21 and playerAs > 0:
            playerCount -= 10
            playerAs -= 1

        if playerCount > 21:
            inNum = random.choice(cards)
            inCard = inNum + random.choice(suits)
            while inCard in arena:
                inNum = random.choice(cards)
                inCard = inNum + random.choice(suits)

            dealerCount += cards_values[inNum]
            arena.append(inCard)
            dealer = dealer + ', ' + inCard

            embedEdit = discord.Embed(
                title=
                f'[ Blackjack | {ctx.author.name} ] - Bet : {number} Gold',
                description="You've lost... (Busted)",
                color=0x8b0000)
            embedEdit.add_field(
                name=f"Dealer's Card(s) | Total : {dealerCount}",
                value='```' + dealer + '```',
                inline=False)
            embedEdit.add_field(
                name=
                f"{ctx.author.name}'s Card(s) | Total : {playerCount} (Bust)",
                value='```' + player + '```',
                inline=False)
            await interaction.response.edit_message(embed=embedEdit, view=None)
            await interaction.followup.send(
                f"Zannen da, {ctx.author.name}-nyan terkena bust karena total scorenya melebihi 21 dan kehilangan senilai {number} Gold"
            )
            newvalues = {"$set": {"gold": goldCount - number}}
            mycol.update_one(userFind, newvalues)
            view.stop()

        else:
            embedEdit = discord.Embed(
                title=
                f'[ Blackjack | {ctx.author.name} ] - Bet : {number} Gold',
                description=
                "Play by pressing the buttons below, find the highest score without getting more than 21",
                color=0x8b0000)
            embedEdit.add_field(
                name=f"Dealer's Card(s) | Total : {dealerCount}",
                value='```' + dealer + ', ???' + '```',
                inline=False)
            embedEdit.add_field(
                name=f"{ctx.author.name}'s Card(s) | Total : {playerCount}",
                value='```' + player + '```',
                inline=False)
            await interaction.response.edit_message(embed=embedEdit)

    async def stand_callback(interaction):
        if interaction.user.id != gamer:
            await interaction.response.send_message(
                f"Neee {interaction.user.name}-nyan, mending /blackjack sendiri deh, jangan pake punya orang lain ih",
                ephemeral=True)
            return

        nonlocal dealerCount, dealer, dealerAs
        inNum = random.choice(cards)
        inCard = inNum + random.choice(suits)

        while inCard in arena:
            inNum = random.choice(cards)
            inCard = inNum + random.choice(suits)

        dealerCount += cards_values[inNum]
        arena.append(inCard)
        dealer = dealer + ', ' + inCard
        if inNum == 'A':
            dealerAs += 1

        if dealerCount == 21:
            dealerPure = True
        else:
            dealerPure = False

        if playerPure and not dealerPure:
            embedEdit = discord.Embed(
                title=
                f'[ Blackjack | {ctx.author.name} ] - Bet : {number} Gold',
                description="You've won! (Pure 21)",
                color=0x8b0000)
            embedEdit.add_field(
                name=f"Dealer's Card(s) | Total : {dealerCount}",
                value='```' + dealer + '```',
                inline=False)
            embedEdit.add_field(
                name=f"{ctx.author.name}'s Card(s) | Total : {playerCount}",
                value='```' + player + '```',
                inline=False)
            await interaction.response.edit_message(embed=embedEdit, view=None)
            await interaction.followup.send(
                f"PURE BLACKJACK!!! {ctx.author.name}-nyan menang dengan skor akhir {playerCount}, mengalahkan dealer dengan skor {dealerCount} dan mendapatkan senilai {number} Gold"
            )
            newvalues = {"$set": {"gold": goldCount + number}}
            mycol.update_one(userFind, newvalues)
            view.stop()
            return

        elif dealerPure and not playerPure:
            embedEdit = discord.Embed(
                title=
                f'[ Blackjack | {ctx.author.name} ] - Bet : {number} Gold',
                description="You've lost... (Dealer has more score)",
                color=0x8b0000)
            embedEdit.add_field(
                name=f"Dealer's Card(s) | Total : {dealerCount}",
                value='```' + dealer + '```',
                inline=False)
            embedEdit.add_field(
                name=f"{ctx.author.name}'s Card(s) | Total : {playerCount}",
                value='```' + player + '```',
                inline=False)
            await interaction.response.edit_message(embed=embedEdit, view=None)
            await interaction.followup.send(
                f"Zannen da, {ctx.author.name}-nyan dengan score {playerCount} masih kalah terhadap dealer dengan pure blackjacknya, lantas kehilangan senilai {number} Gold"
            )
            newvalues = {"$set": {"gold": goldCount - number}}
            mycol.update_one(userFind, newvalues)
            view.stop()
            return

        while dealerCount < playerCount:
            inNum = random.choice(cards)
            inCard = inNum + random.choice(suits)
            while inCard in arena:
                inNum = random.choice(cards)
                inCard = inNum + random.choice(suits)

            dealerCount += cards_values[inNum]
            arena.append(inCard)
            dealer = dealer + ', ' + inCard
            if inNum == 'A':
                dealerAs += 1

            if dealerCount > 21 and dealerAs > 0:
                dealerCount -= 10
                dealerAs -= 1

        if dealerCount > 21:
            embedEdit = discord.Embed(
                title=
                f'[ Blackjack | {ctx.author.name} ] - Bet : {number} Gold',
                description="You've won! (Dealer Busted)",
                color=0x8b0000)
            embedEdit.add_field(
                name=f"Dealer's Card(s) | Total : {dealerCount} (Bust)",
                value='```' + dealer + '```',
                inline=False)
            embedEdit.add_field(
                name=f"{ctx.author.name}'s Card(s) | Total : {playerCount}",
                value='```' + player + '```',
                inline=False)
            await interaction.response.edit_message(embed=embedEdit, view=None)
            await interaction.followup.send(
                f"Omedetou, {ctx.author.name}-nyan menang dengan skor akhir {playerCount} dikarenakan dealer mengalami bust dan endapatkan senilai {number} Gold!"
            )
            newvalues = {"$set": {"gold": goldCount + number}}
            mycol.update_one(userFind, newvalues)
            view.stop()

        elif dealerCount == playerCount:
            embedEdit = discord.Embed(
                title=
                f'[ Blackjack | {ctx.author.name} ] - Bet : {number} Gold',
                description="It's a tie. (Same Score)",
                color=0x8b0000)
            embedEdit.add_field(
                name=f"Dealer's Card(s) | Total : {dealerCount}",
                value='```' + dealer + '```',
                inline=False)
            embedEdit.add_field(
                name=f"{ctx.author.name}'s Card(s) | Total : {playerCount}",
                value='```' + player + '```',
                inline=False)
            await interaction.response.edit_message(embed=embedEdit, view=None)
            await interaction.followup.send(
                f"Nampaknya terjadi seri antara {ctx.author.name}-nyan dengan dealer, skor akhirnya sama-sama {playerCount}"
            )
            view.stop()

        else:
            embedEdit = discord.Embed(
                title=
                f'[ Blackjack | {ctx.author.name} ] - Bet : {number} Gold',
                description="You've lost... (Dealer has more score)",
                color=0x8b0000)
            embedEdit.add_field(
                name=f"Dealer's Card(s) | Total : {dealerCount}",
                value='```' + dealer + '```',
                inline=False)
            embedEdit.add_field(
                name=f"{ctx.author.name}'s Card(s) | Total : {playerCount}",
                value='```' + player + '```',
                inline=False)
            await interaction.response.edit_message(embed=embedEdit, view=None)
            await interaction.followup.send(
                f"Zannen da, {ctx.author.name}-nyan dengan score {playerCount} masih kalah terhadap dealer dengan score {dealerCount}, lantas kehilangan senilai {number} Gold"
            )
            newvalues = {"$set": {"gold": goldCount - number}}
            mycol.update_one(userFind, newvalues)
            view.stop()

    async def double_callback(interaction):
        if interaction.user.id != gamer:
            await interaction.response.send_message(
                f"Neee {interaction.user.name}-nyan, mending /blackjack sendiri deh, jangan pake punya orang lain ih",
                ephemeral=True)
            return

        if goldCount < (number * 2):
            await interaction.response.send_message(
                "Neee, cek dulu gold anata dong, ngga cukup tuh buat double..")
            return

        nonlocal playerCount, player, dealerCount, dealer, dealerAs, playerAs
        inNum = random.choice(cards)
        inCard = inNum + random.choice(suits)

        while inCard in arena:
            inNum = random.choice(cards)
            inCard = inNum + random.choice(suits)

        playerCount += cards_values[inNum]
        arena.append(inCard)
        player = player + ', ' + inCard
        if inNum == 'A':
            playerAs += 1

        if playerCount > 21 and playerAs > 0:
            playerCount -= 10
            playerAs -= 1

        if playerCount > 21:
            inNum = random.choice(cards)
            inCard = inNum + random.choice(suits)
            while inCard in arena:
                inNum = random.choice(cards)
                inCard = inNum + random.choice(suits)

            dealerCount += cards_values[inNum]
            arena.append(inCard)
            dealer = dealer + ', ' + inCard

            embedEdit = discord.Embed(
                title=f'[ Blackjack | {ctx.author} ], Bet : {number*2} Gold',
                description="You've lost... (Busted)",
                color=0x8b0000)
            embedEdit.add_field(
                name=f"Dealer's Card(s) | Total : {dealerCount}",
                value='```' + dealer + '```',
                inline=False)
            embedEdit.add_field(
                name=
                f"{ctx.author.name}'s Card(s) | Total : {playerCount} (Bust)",
                value='```' + player + '```',
                inline=False)
            await interaction.response.edit_message(embed=embedEdit, view=None)
            await interaction.followup.send(
                f"Zannen da, {ctx.author.name}-nyan terkena bust karena total scorenya melebihi 21 dan kehilangan senilai {number*2} Gold"
            )
            newvalues = {"$set": {"gold": goldCount - (number * 2)}}
            mycol.update_one(userFind, newvalues)
            view.stop()

        else:
            inNum = random.choice(cards)
            inCard = inNum + random.choice(suits)

            while inCard in arena:
                inNum = random.choice(cards)
                inCard = inNum + random.choice(suits)

            dealerCount += cards_values[inNum]
            arena.append(inCard)
            dealer = dealer + ', ' + inCard

            if dealerCount == 21:
                dealerPure = True
            else:
                dealerPure = False

            if dealerPure:
                embedEdit = discord.Embed(
                    title=
                    f'[ Blackjack | {ctx.author} ], Bet : {number*2} Gold',
                    description="You've lost... (Dealer has more score)",
                    color=0x8b0000)
                embedEdit.add_field(
                    name=f"Dealer's Card(s) | Total : {dealerCount}",
                    value='```' + dealer + '```',
                    inline=False)
                embedEdit.add_field(
                    name=f"{ctx.author.name}'s Card(s) | Total : {playerCount}",
                    value='```' + player + '```',
                    inline=False)
                await interaction.response.edit_message(embed=embedEdit,
                                                        view=None)
                await interaction.followup.send(
                    f"Zannen da, {ctx.author.name}-nyan dengan score {playerCount} masih kalah terhadap dealer dengan pure blackjacknya, lantas kehilangan senilai {number*2} Gold"
                )
                newvalues = {"$set": {"gold": goldCount - (number * 2)}}
                mycol.update_one(userFind, newvalues)
                view.stop()
                return

            while dealerCount < playerCount:
                inNum = random.choice(cards)
                inCard = inNum + random.choice(suits)
                while inCard in arena:
                    inNum = random.choice(cards)
                    inCard = inNum + random.choice(suits)

                dealerCount += cards_values[inNum]
                arena.append(inCard)
                dealer = dealer + ', ' + inCard
                if inNum == 'A':
                    dealerAs += 1

                if dealerCount > 21 and dealerAs > 0:
                    dealerCount -= 10
                    dealerAs -= 1

            if dealerCount > 21:
                embedEdit = discord.Embed(
                    title=
                    f'[ Blackjack | {ctx.author} ], Bet : {number*2} Gold',
                    description="You've won... (Dealer Busted)",
                    color=0x8b0000)
                embedEdit.add_field(
                    name=f"Dealer's Card(s) | Total : {dealerCount} (Bust)",
                    value='```' + dealer + '```',
                    inline=False)
                embedEdit.add_field(
                    name=f"{ctx.author.name}'s Card(s) | Total : {playerCount}",
                    value='```' + player + '```',
                    inline=False)
                await interaction.response.edit_message(embed=embedEdit,
                                                        view=None)
                await interaction.followup.send(
                    f"Omedetou, {ctx.author.name}-nyan menang dengan skor akhir {playerCount} dikarenakan dealer mengalami bust dan endapatkan senilai {number*2} Gold!"
                )
                newvalues = {"$set": {"gold": goldCount + (number * 2)}}
                mycol.update_one(userFind, newvalues)
                view.stop()

            elif dealerCount == playerCount:
                embedEdit = discord.Embed(
                    title=
                    f'[ Blackjack | {ctx.author} ], Bet : {number*2} Gold',
                    description="It's a tie. (Same Score)",
                    color=0x8b0000)
                embedEdit.add_field(
                    name=f"Dealer's Card(s) | Total : {dealerCount}",
                    value='```' + dealer + '```',
                    inline=False)
                embedEdit.add_field(
                    name=f"{ctx.author.name}'s Card(s) | Total : {playerCount}",
                    value='```' + player + '```',
                    inline=False)
                await interaction.response.edit_message(embed=embedEdit,
                                                        view=None)
                await interaction.followup.send(
                    f"Nampaknya terjadi seri antara {ctx.author.name}-nyan dengan dealer, skor akhirnya sama-sama {playerCount}"
                )
                view.stop()

            else:
                embedEdit = discord.Embed(
                    title=
                    f'[ Blackjack | {ctx.author} ], Bet : {number*2} Gold',
                    description="You've lost... (Dealer has more score)",
                    color=0x8b0000)
                embedEdit.add_field(
                    name=f"Dealer's Card(s) | Total : {dealerCount}",
                    value='```' + dealer + '```',
                    inline=False)
                embedEdit.add_field(
                    name=f"{ctx.author.name}'s Card(s) | Total : {playerCount}",
                    value='```' + player + '```',
                    inline=False)
                await interaction.response.edit_message(embed=embedEdit,
                                                        view=None)
                await interaction.followup.send(
                    f"Zannen da, {ctx.author.name}-nyan dengan score {playerCount} masih kalah terhadap dealer dengan score {dealerCount}, lantas kehilangan senilai {number*2} Gold"
                )
                newvalues = {"$set": {"gold": goldCount - (number * 2)}}
                mycol.update_one(userFind, newvalues)
                view.stop()

    buttonH.callback = hit_callback
    buttonS.callback = stand_callback
    buttonD.callback = double_callback
    view = View(timeout=600)
    view.add_item(buttonH)
    view.add_item(buttonS)
    view.add_item(buttonD)

    embedVar = discord.Embed(
        title=f'[ Blackjack | {ctx.author.name} ] - Bet : {number} Gold',
        description=
        "Play by pressing the buttons below, find the highest score without getting more than 21",
        color=0x8b0000)
    embedVar.add_field(name=f"Dealer's Card(s) | Total : {dealerCount}",
                       value='```' + dealer + ', ???' + '```',
                       inline=False)
    embedVar.add_field(
        name=f"{ctx.author.name}'s Card(s) | Total : {playerCount}",
        value='```' + player + '```',
        inline=False)
    bjMsg = await ctx.respond(embed=embedVar, view=view)
    checkView = await view.wait()

    if checkView:
        embedEdit = discord.Embed(
            title=f'[ Blackjack | {ctx.author.name} ] - Bet : {number} Gold',
            description="You've lost.. (Time limit's up)",
            color=0x8b0000)
        await bjMsg.edit_original_message(embed=embedEdit, view=None)
        await bjMsg.followup.send(
            f"Neee {ctx.author.name}-nyan lama banget sih, udah watashi tungguin dari tadi loh, ngga kabur kan ya? Tapi zannen da, karena waktunya sudah habis jadi anata dianggap kalah dan kehilangan senilai {number} Gold"
        )
        newvalues = {"$set": {"gold": goldCount - number}}
        mycol.update_one(userFind, newvalues)

def setup(bot):
  bot.add_cog(Blackjack(bot))