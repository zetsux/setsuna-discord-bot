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
import asyncio
import random

guilds = [990445490401341511, 1020927428459241522, 989086863434334279, 494097970208178186, 1028690906901139486]

MONGODB = os.environ['MONGODB']

client = pymongo.MongoClient(MONGODB)
mydb = client["familiardb"]
mycol = mydb["user"]

class Spygame(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    
  @app_commands.command(name='spygame', description='Play a spyfall game with at least 3 players')
  async def spyfall_game(self, ctx : discord.Interaction):
    playersID = []
    playersName = []
    playerCount = 0
    playerString = ""
    buttonJ = Button(label='Join', style=discord.ButtonStyle.green, row=0)
    buttonS = Button(label='Start', style=discord.ButtonStyle.primary, row=0)

    async def join_callback(interaction):
        nonlocal playerCount, playerString
        if interaction.user.id in playersID:
            await interaction.response.send_message(
                f"Neee anata kan udah kedaftar, {interaction.user.name}-nyan",
                ephemeral=True)
            return

        playersID.append(interaction.user.id)
        playersName.append(interaction.user.name)
        playerCount += 1
        playerString = playerString + f'{playerCount}) {interaction.user.name}\n'
        embedEdit = discord.Embed(
            title=f'[ Game ]',
            description=
            "Press button to join, can start if at least 3 players have joined",
            color=0x330066)
        embedEdit.add_field(name=f"Player List | Count : {playerCount}",
                            value='```' + playerString + '```',
                            inline=False)
        await interaction.response.edit_message(embed=embedEdit)

    async def start_callback(interaction):
        if interaction.user.id not in playersID :
            await interaction.response.send_message(
                f"Minimal join dulu dek {interaction.user.name}-nyan", ephemeral=True)
            return
      
        if playerCount < 3:
            await interaction.response.send_message(
                f"Neee masih kurang {3 - playerCount} player buat distart nih, ajak yang lain dulu gih {interaction.user.name}-nyan",
                ephemeral=True)
            return

        buttonSV = Button(label='Start Voting',
                          style=discord.ButtonStyle.green,
                          row=0)
        buttonCG = Button(label='Check Duration',
                          style=discord.ButtonStyle.gray,
                          row=0)
        flagGame = False
        gameDur = playerCount * 180
        timeGame = 0
        svCount = 0
        svID = []
        svNeed = int(playerCount * 3 / 4)
        spyIndex = random.randint(0, playerCount - 1)
        locationList = [
            'Sekolah',
            'Universitas',
            'Bioskop',
            'Mall',
            'Supermarket',
            'Pasar Tradisional',
            'Restoran',
            'Cafe',
            'Kantor Polisi',
            'Stasiun Kereta Api',
            'Halte Bus',
            'Bandar Udara',
            'Penjara',
            'Rumah Sakit',
            'Hotel',
            'Sawah',
            'Theme Park',
            'Stadion',
            'Apotek',
            'Pantai',
            'Bangunan Kosong',
            'Gedung Pernikahan',
            'Kuburan',
            'Sirkus',
            'Konser',
        ]
        location = random.choice(locationList)
        for player in playersID:
            tempPlayer = await self.bot.fetch_user(int(player))
            await tempPlayer.create_dm()
            if player == playersID[spyIndex]:
                embedMem = discord.Embed(
                    title=f"You are the SPY!",
                    description=
                    f"Misi : Membaurlah dengan yang lain agar tidak ketahuan dan cari tahu lokasi perkumpulan mereka yang sebenarnya",
                    color=0x330066)
            else:
                embedMem = discord.Embed(
                    title=f"You are NOT the spy! The Location is {location}",
                    description=
                    "Misi : Temukan spynya melalui beberapa ronde saling bertanya satu sama lain tanpa membocorkan lokasi pertemuan kalian",
                    color=0x330066)

            await tempPlayer.dm_channel.send(embed=embedMem)

        async def votestart_callback(interaction):
            nonlocal svCount
            if interaction.user.id in svID:
                await interaction.response.send_message(
                    f"Sabar ya {interaction.user.name}-nyan, kurang {svNeed - svCount} orang lagi",
                    ephemeral=True)
                return

            svID.append(interaction.user.id)
            svCount += 1
            if svCount < svNeed:
                await interaction.response.send_message(
                    f"{interaction.user.name}-nyan memvote untuk melakukan voting sekarang juga, watashi perlu {svNeed - svCount} vote lagi untuk langsung menuju ke fase voting.."
                )
                return

            else:
                nonlocal flagGame
                flagGame = True
                votedID = []
                votes = []
                voteCount = []
                flagVote = False
                timeVote = 0
                buttonEV = Button(label='End Vote',
                                  style=discord.ButtonStyle.primary,
                                  row=1)
                select = Select(placeholder="Choose who to vote for")
                for x in range(playerCount):
                    select.add_option(label=playersName[x],
                                      value=str(x),
                                      emoji='👤')
                    voteCount.append(0)

                async def selection_callback(interaction):
                    nonlocal voteCount, votes
                    if interaction.user.id in playersID:
                        votedIndex = int(select.values[0])
                        voteCount[votedIndex] += 1

                        if interaction.user.id in votedID:
                            userIndex = votedID.index(interaction.user.id)
                            beforeIndex = playersName.index(votes[userIndex])
                            voteCount[beforeIndex] -= 1
                            votes[userIndex] = playersName[votedIndex]

                            embedVoteEdit = discord.Embed(
                                title=f"[ SpyGame ]",
                                description=
                                f"< Voting List > | Time Left : {300 - timeVote} seconds",
                                color=0x330066)
                            for i in range(playerCount):
                                embedVoteEdit.add_field(
                                    name=f"{playersName[i]}",
                                    value='```' + 'Vote : ' +
                                    str(voteCount[i]) + '```',
                                    inline=False)
                            await interaction.response.edit_message(
                                embed=embedVoteEdit)
                            await interaction.followup.send(
                                f"Anata berhasil mengubah vote ke {playersName[votedIndex]}-nyan...",
                                ephemeral=True)

                        else:
                            votedID.append(interaction.user.id)
                            votes.append(playersName[votedIndex])
                            embedVoteEdit = discord.Embed(
                                title=f"[ SpyGame ]",
                                description=
                                f"< Voting List > | Time Left : {300 - timeVote} seconds",
                                color=0x330066)
                            for i in range(playerCount):
                                embedVoteEdit.add_field(
                                    name=f"{playersName[i]}",
                                    value='```' + 'Vote : ' +
                                    str(voteCount[i]) + '```',
                                    inline=False)
                            await interaction.response.edit_message(
                                embed=embedVoteEdit)
                            await interaction.followup.send(
                                f"Anata berhasil melakukan vote terhadap {playersName[votedIndex]}-nyan...",
                                ephemeral=True)

                    else:
                        await interaction.response.send_message(
                            f"Anata kan ngga join gamenya, {interaction.user.name}-nyan...",
                            ephemeral=True)

                async def endvote_callback(interaction):
                    if interaction.user.id not in playersID:
                        await interaction.response.send_message(
                            f"Anata kan ngga join gamenya, {interaction.user.name}-nyan...",
                            ephemeral=True)
                        return

                    if len(votes) < int(playerCount * 3 / 4):
                        await interaction.response.send_message(
                            f"Masih kurang {int(playerCount*3/4) - len(votes)} orang nih yang voting baru bisa lanjut, yuk yuk diajak vote dulu temennya yang belum vote baru disubmit",
                            ephemeral=True)
                        return

                    elif len(votes) >= int(playerCount * 3 / 4):
                        chosen = max(votes, key=votes.count)
                        numChosen = votes.count(chosen)
                        flag = 0
                        checked = []
                        sameNum = []

                        for x in votes:
                            if x in checked:
                                continue

                            checked.append(x)
                            if votes.count(x) == numChosen:
                                flag += 1
                                sameNum.append(x)

                        if flag > 1:
                            tieString = ', '.join(sameNum)
                            await interaction.response.send_message(
                                f"Votenya masih seri nih antara {tieString}. Yuk ganti vote yuk.."
                            )
                            return

                        else:
                            if playersName.index(chosen) == spyIndex:
                                spyGet = True
                            else:
                                spyGet = False

                            spySelect = Select(
                                placeholder="Guess the location!")
                            for x in locationList:
                                spySelect.add_option(label=x)

                            async def spy_callback(interaction):
                                if interaction.user.id != playersID[spyIndex]:
                                    await interaction.response.send_message(
                                        f"Neee anata bukan spy ih {interaction.user.name}-nyan, tunggu spynya jawab yaa..",
                                        ephemeral=True)
                                    return

                                if spySelect.values[0] == location:
                                    locGet = True

                                else:
                                    locGet = False

                                embedSpyDone = discord.Embed(
                                    title=f"[ SpyGame ]",
                                    description=
                                    f"Spy sudah selesai menebak, silahkan scroll ke bawah untuk melihat hasilnya",
                                    color=0x330066)
                                await interaction.response.edit_message(
                                    embed=embedSpyDone, view=None)
                                spyView.stop()
                                if locGet and spyGet:
                                    embedRes = discord.Embed(
                                        title=f"[ SpyGame ]",
                                        description=
                                        f"{interaction.user}-nyan berhasil ditebak sebagai spy dan lokasi {location} juga berhasil ditebak oleh sang spy. It's a tie game!",
                                        color=0x330066)
                                    embedRes.set_image(
                                        url=
                                        'https://c.tenor.com/wyfhYqF1tJIAAAAM/mark-wahlberg-wahlberg.gif'
                                    )

                                elif locGet:
                                    embedRes = discord.Embed(
                                        title=f"[ SpyGame ]",
                                        description=
                                        f"{interaction.user}-nyan gagal ditebak sebagai spy karena kesalahan menebak terhadap {chosen}. Sementara lokasi {location} berhasil ditebak oleh sang spy. Spy Wins!",
                                        color=0x330066)
                                    embedRes.set_image(
                                        url=
                                        'https://some-random-api.ml/canvas/passed?avatar='
                                        + interaction.user.avatar.url)

                                elif spyGet:
                                    embedRes = discord.Embed(
                                        title=f"[ SpyGame ]",
                                        description=
                                        f"{interaction.user}-nyan berhasil ditebak sebagai spy, tetapi lokasi {location} gagal ditebak oleh sang spy karena menebak {spySelect.values[0]}. Spy Loses!",
                                        color=0x330066)
                                    embedRes.set_image(
                                        url=
                                        'https://some-random-api.ml/canvas/jail?avatar='
                                        + interaction.user.avatar.url)

                                else:
                                    embedRes = discord.Embed(
                                        title=f"[ SpyGame ]",
                                        description=
                                        f"{interaction.user}-nyan gagal ditebak sebagai spy karena kesalahan menebak terhadap {chosen}. Tetapi lokasi {location} juga gagal ditebak oleh sang spy karena menebak {spySelect.values[0]}. It's a tie game!",
                                        color=0x330066)
                                    embedRes.set_image(
                                        url=
                                        'https://c.tenor.com/wyfhYqF1tJIAAAAM/mark-wahlberg-wahlberg.gif'
                                    )

                                await interaction.followup.send(embed=embedRes)

                            embedVoteDone = discord.Embed(
                                title=f"[ SpyGame ]",
                                description=
                                f"Voting sudah selesai, kini giliran spy menebak lokasi",
                                color=0x330066)
                            await interaction.response.edit_message(
                                embed=embedVoteDone, view=None)
                            nonlocal flagVote
                            flagVote = True
                            spySelect.callback = spy_callback
                            spyView = View(timeout=300)
                            spyView.add_item(spySelect)
                            embedSpy = discord.Embed(
                                title=f"[ SpyGame ]",
                                description=
                                f"Untuk spy, silahkan menebak lokasi para pemain lain!",
                                color=0x330066)
                            spyMsg = await voteMsg.channel.send(embed=embedSpy,
                                                                view=spyView)
                            checkSpyView = await spyView.wait()

                            if checkSpyView:
                                embedSpyNot = discord.Embed(
                                    title=f"[ SpyGame ]",
                                    description=
                                    f"Spy tidak menebak dalam kurun waktu yang telah ditentukan, silahkan scroll ke bawah untuk melihat hasilnya",
                                    color=0x330066)
                                await spyMsg.edit(embed=embedSpyNot, view=None)

                                if spyGet:
                                    embedRes = discord.Embed(
                                        title=f"[ SpyGame ]",
                                        description=
                                        f"{interaction.user}-nyan berhasil ditebak sebagai spy, tetapi lokasi {location} gagal ditebak oleh sang spy karena kehabisan waktu. Spy Loses!",
                                        color=0x330066)
                                    embedRes.set_image(
                                        url=
                                        'https://some-random-api.ml/canvas/jail?avatar='
                                        + interaction.user.avatar.url)

                                else:
                                    embedRes = discord.Embed(
                                        title=f"[ SpyGame ]",
                                        description=
                                        f"{interaction.user}-nyan gagal ditebak sebagai spy karena kesalahan menebak terhadap {chosen}. Tetapi lokasi {location} juga gagal ditebak oleh sang spy karena kehabisan waktu. It's a tie game!",
                                        color=0x330066)
                                    embedRes.set_image(
                                        url=
                                        'https://c.tenor.com/wyfhYqF1tJIAAAAM/mark-wahlberg-wahlberg.gif'
                                    )

                                await spyMsg.channel.send(embed=embedRes,
                                                          view=None)

                select.callback = selection_callback
                buttonEV.callback = endvote_callback
                voteView = View(timeout=None)
                voteView.add_item(select)
                voteView.add_item(buttonEV)

                embedGame = discord.Embed(
                    title=f"[ SpyGame ]",
                    description=
                    f"Game kini memasuki fase voting, silahkan scroll ke bawah untuk melanjutkan",
                    color=0x330066)
                await interaction.response.edit_message(embed=embedGame,
                                                        view=None)
                embedEdit = discord.Embed(
                    title=f"[ SpyGame ]",
                    description=
                    f"< Voting List > | Time Left : {300 - timeVote} seconds",
                    color=0x330066)
                for i in range(playerCount):
                    embedEdit.add_field(name=f"{playersName[i]}",
                                        value='```' + 'Vote : ' +
                                        str(voteCount[i]) + '```',
                                        inline=False)
                voteMsg = await gameMsg.channel.send(embed=embedEdit,
                                                     view=voteView)
                flagVoteTime = False
                while True:
                    await asyncio.sleep(1)
                    timeVote += 1
                    # print(timeVote)
                    if timeVote == 300:
                        flagVoteTime = True
                        break
                    if flagVote:
                        break

                if flagVoteTime:
                    if len(votes) >= 1:
                        chosen = max(votes, key=votes.count)

                        numChosen = votes.count(chosen)
                        flag = 0
                        checked = []
                        sameNum = []

                        for x in votes:
                            if x in checked:
                                continue

                            checked.append(x)
                            if votes.count(x) == numChosen:
                                flag += 1
                                sameNum.append(x)

                        if flag > 1:
                            spyGet = False
                            chosen = "nihil (ngga bisa ditentukan karena seri)"

                        else:
                            if playersName.index(chosen) == spyIndex:
                                spyGet = True
                            else:
                                spyGet = False

                    else:
                        spyGet = False
                        chosen = "nihil (ngga ada yang vote)"

                    spySelect = Select(placeholder="Guess the location!")
                    for x in locationList:
                        spySelect.add_option(label=x)

                    async def spy_callback(interaction):
                        if interaction.user.id != playersID[spyIndex]:
                            await interaction.response.send_message(
                                f"Neee anata bukan spy ih {interaction.user.name}-nyan, tunggu spynya jawab yaa..",
                                ephemeral=True)
                            return

                        if spySelect.values[0] == location:
                            locGet = True

                        else:
                            locGet = False

                        embedSpyDoneLoc = discord.Embed(
                            title=f"[ SpyGame ]",
                            description=
                            f"Spy telah selesai memilih lokasi, silahkan scroll ke bawah untuk melanjutkan",
                            color=0x330066)
                        await interaction.response.edit_message(
                            embed=embedSpyDoneLoc, view=None)
                        spyView.stop()
                        if locGet and spyGet:
                            embedRes = discord.Embed(
                                title=f"[ SpyGame ]",
                                description=
                                f"{interaction.user}-nyan berhasil ditebak sebagai spy dan lokasi {location} juga berhasil ditebak oleh sang spy. It's a tie game!",
                                color=0x330066)
                            embedRes.set_image(
                                url=
                                'https://c.tenor.com/wyfhYqF1tJIAAAAM/mark-wahlberg-wahlberg.gif'
                            )

                        elif locGet:
                            embedRes = discord.Embed(
                                title=f"[ SpyGame ]",
                                description=
                                f"{interaction.user}-nyan gagal ditebak sebagai spy karena kesalahan menebak terhadap {chosen}. Sementara lokasi {location} berhasil ditebak oleh sang spy. Spy Wins!",
                                color=0x330066)
                            embedRes.set_image(
                                url=
                                'https://some-random-api.ml/canvas/passed?avatar='
                                + interaction.user.avatar.url)

                        elif spyGet:
                            embedRes = discord.Embed(
                                title=f"[ SpyGame ]",
                                description=
                                f"{interaction.user}-nyan berhasil ditebak sebagai spy, tetapi lokasi {location} gagal ditebak oleh sang spy karena menebak {spySelect.values[0]}. Spy Loses!",
                                color=0x330066)
                            embedRes.set_image(
                                url=
                                'https://some-random-api.ml/canvas/jail?avatar='
                                + interaction.user.avatar.url)

                        else:
                            embedRes = discord.Embed(
                                title=f"[ SpyGame ]",
                                description=
                                f"{interaction.user}-nyan gagal ditebak sebagai spy karena kesalahan menebak terhadap {chosen}. Tetapi lokasi {location} juga gagal ditebak oleh sang spy karena menebak {spySelect.values[0]}. It's a tie game!",
                                color=0x330066)
                            embedRes.set_image(
                                url=
                                'https://c.tenor.com/wyfhYqF1tJIAAAAM/mark-wahlberg-wahlberg.gif'
                            )

                        await interaction.followup.send(embed=embedRes)

                    spySelect.callback = spy_callback
                    spyView = View(timeout=300)
                    spyView.add_item(spySelect)
                    embedVoteDoneHhe = discord.Embed(
                        title=f"[ SpyGame ]",
                        description=
                        f"Voting telah selesai, sekarang saatnya spy menebak lokasi, silahkan scroll ke bawah untuk melanjutkan",
                        color=0x330066)
                    await voteMsg.edit(embed=embedVoteDoneHhe, view=None)
                    embedSpy = discord.Embed(
                        title=f"[ SpyGame ]",
                        description=
                        f"Untuk spy, silahkan menebak lokasi para pemain lain!",
                        color=0x330066)
                    spyMsg = await voteMsg.channel.send(embed=embedSpy,
                                                        view=spyView)
                    checkSpyView = await spyView.wait()

                    if checkSpyView:
                        embedSpyDoneNow = discord.Embed(
                            title=f"[ SpyGame ]",
                            description=
                            f"Spy sudah menentukan lokasi, silahkan scroll ke bawah untuk melanjutkan",
                            color=0x330066)
                        await spyMsg.edit(embed=embedSpyDoneNow, view=None)

                        if spyGet:
                            embedRes = discord.Embed(
                                title=f"[ SpyGame ]",
                                description=
                                f"{interaction.user}-nyan berhasil ditebak sebagai spy, tetapi lokasi {location} gagal ditebak oleh sang spy karena kehabisan waktu. Spy Loses!",
                                color=0x330066)
                            embedRes.set_image(
                                url=
                                'https://some-random-api.ml/canvas/jail?avatar='
                                + interaction.user.avatar.url)

                        else:
                            embedRes = discord.Embed(
                                title=f"[ SpyGame ]",
                                description=
                                f"{interaction.user}-nyan gagal ditebak sebagai spy karena kesalahan menebak terhadap {chosen}. Tetapi lokasi {location} juga gagal ditebak oleh sang spy karena kehabisan waktu. It's a tie game!",
                                color=0x330066)
                            embedRes.set_image(
                                url=
                                'https://c.tenor.com/wyfhYqF1tJIAAAAM/mark-wahlberg-wahlberg.gif'
                            )

                        await spyMsg.channel.send(embed=embedRes, view=None)

        async def checkgame_callback(interaction):
            await interaction.response.send_message(
                f"Waktu permainan tersisa {gameDur - timeGame} detik lagi, {interaction.user.name}-nyan",
                ephemeral=True)

        buttonSV.callback = votestart_callback
        buttonCG.callback = checkgame_callback
        inView = View(timeout=None)
        inView.add_item(buttonSV)
        inView.add_item(buttonCG)

        playerString = ""
        tempNames = playersName
        random.shuffle(tempNames)
        tmpIdx = 1
        for i in tempNames :
          playerString += f"{tmpIdx}) {i}\n"
          tmpIdx += 1

        embedEdit = discord.Embed(
            title=f"[ SpyGame ]",
            description=
            f"Game telah dimulai! Silahkan saling menanyakan pertanyaan bergantian sesuai dengan urutan member yang telah disediakan. Waktu sebelum babak voting : {playerCount*3} Menit, bisa juga memulai lebih cepat dengan menekan tombol di bawah",
            color=0x330066)
        embedEdit.add_field(name=f"Player Order | Count : {playerCount}",
                            value='```' + playerString + '```',
                            inline=False)
        embedDel = discord.Embed(
            title=f"[ SpyGame ]",
            description=f"Game sudah dimulai, silahkan scroll ke bawah",
            color=0x330066)
        view.stop()
        await interaction.response.edit_message(embed=embedDel, view=None)
        gameMsg = await panelMsg.channel.send(embed=embedEdit, view=inView)

        flagGameTime = False
        while True:
            await asyncio.sleep(1)
            timeGame += 1
            # print(timeGame)
            if timeGame == gameDur:
                flagGameTime = True
                break
            if flagGame:
                break

        if flagGameTime:
            votedID = []
            votes = []
            voteCount = []
            timeVote = 0
            flagVote = False
            buttonEV = Button(label='End Vote',
                              style=discord.ButtonStyle.primary,
                              row=1)
            select = Select(placeholder="Choose who to vote for")
            for x in range(playerCount):
                select.add_option(label=playersName[x],
                                  value=str(x),
                                  emoji='👤')
                voteCount.append(0)

            async def selection_callback(interaction):
                nonlocal voteCount, votes
                if interaction.user.id in playersID:
                    votedIndex = int(select.values[0])
                    voteCount[votedIndex] += 1

                    if interaction.user.id in votedID:
                        userIndex = votedID.index(interaction.user.id)
                        beforeIndex = playersName.index(votes[userIndex])
                        voteCount[beforeIndex] -= 1
                        votes[userIndex] = playersName[votedIndex]

                        embedVoteEdit = discord.Embed(
                            title=f"[ SpyGame ]",
                            description=
                            f"< Voting List > | Time Left : {300 - timeVote} seconds",
                            color=0x330066)
                        for i in range(playerCount):
                            embedVoteEdit.add_field(name=f"{playersName[i]}",
                                                    value='```' + 'Vote : ' +
                                                    str(voteCount[i]) + '```',
                                                    inline=False)
                        await interaction.response.edit_message(
                            embed=embedVoteEdit)
                        await interaction.followup.send(
                            f"Anata berhasil mengubah vote ke {playersName[votedIndex]}-nyan...",
                            ephemeral=True)

                    else:
                        votedID.append(interaction.user.id)
                        votes.append(playersName[votedIndex])
                        embedVoteEdit = discord.Embed(
                            title=f"[ SpyGame ]",
                            description=
                            f"< Voting List > | Time Left : {300 - timeVote} seconds",
                            color=0x330066)
                        for i in range(playerCount):
                            embedVoteEdit.add_field(name=f"{playersName[i]}",
                                                    value='```' + 'Vote : ' +
                                                    str(voteCount[i]) + '```',
                                                    inline=False)
                        await interaction.response.edit_message(
                            embed=embedVoteEdit)
                        await interaction.followup.send(
                            f"Anata berhasil melakukan vote terhadap {playersName[votedIndex]}-nyan...",
                            ephemeral=True)

                else:
                    await interaction.response.send_message(
                        f"Anata kan ngga join gamenya, {interaction.user.name}-nyan...",
                        ephemeral=True)

            async def endvote_callback(interaction):
                if interaction.user.id not in playersID:
                    await interaction.response.send_message(
                        f"Anata kan ngga join gamenya, {interaction.user.name}-nyan...",
                        ephemeral=True)
                    return

                if len(votes) < playerCount:
                    await interaction.response.send_message(
                        f"Masih blom voting semua nih, yuk yuk diajak vote dulu temennya yang belum vote baru disubmit",
                        ephemeral=True)
                    return

                elif len(votes) == playerCount:
                    chosen = max(votes, key=votes.count)
                    numChosen = votes.count(chosen)
                    flag = 0
                    checked = []
                    sameNum = []

                    for x in votes:
                        if x in checked:
                            continue

                        checked.append(x)
                        if votes.count(x) == numChosen:
                            flag += 1
                            sameNum.append(x)

                    if flag > 1:
                        tieString = ', '.join(sameNum)
                        await interaction.response.send_message(
                            f"Votenya masih seri nih antara {tieString}. Yuk ganti vote yuk.."
                        )
                        return

                    else:
                        if playersName.index(chosen) == spyIndex:
                            spyGet = True
                        else:
                            spyGet = False

                        spySelect = Select(placeholder="Guess the location!")
                        for x in locationList:
                            spySelect.add_option(label=x)

                        async def spy_callback(interaction):
                            if interaction.user.id != playersID[spyIndex]:
                                await interaction.response.send_message(
                                    f"Neee anata bukan spy ih {interaction.user.name}-nyan, tunggu spynya jawab yaa..",
                                    ephemeral=True)
                                return

                            if spySelect.values[0] == location:
                                locGet = True

                            else:
                                locGet = False

                            embedSpyDone = discord.Embed(
                                title=f"[ SpyGame ]",
                                description=
                                f"Spy sudah selesai menebak, silahkan scroll ke bawah untuk melihat hasilnya",
                                color=0x330066)
                            await interaction.response.edit_message(
                                embed=embedSpyDone, view=None)
                            spyView.stop()
                            if locGet and spyGet:
                                embedRes = discord.Embed(
                                    title=f"[ SpyGame ]",
                                    description=
                                    f"{interaction.user}-nyan berhasil ditebak sebagai spy dan lokasi {location} juga berhasil ditebak oleh sang spy. It's a tie game!",
                                    color=0x330066)
                                embedRes.set_image(
                                    url=
                                    'https://c.tenor.com/wyfhYqF1tJIAAAAM/mark-wahlberg-wahlberg.gif'
                                )

                            elif locGet:
                                embedRes = discord.Embed(
                                    title=f"[ SpyGame ]",
                                    description=
                                    f"{interaction.user}-nyan gagal ditebak sebagai spy karena kesalahan menebak terhadap {chosen}. Sementara lokasi {location} berhasil ditebak oleh sang spy. Spy Wins!",
                                    color=0x330066)
                                embedRes.set_image(
                                    url=
                                    'https://some-random-api.ml/canvas/passed?avatar='
                                    + interaction.user.avatar.url)

                            elif spyGet:
                                embedRes = discord.Embed(
                                    title=f"[ SpyGame ]",
                                    description=
                                    f"{interaction.user}-nyan berhasil ditebak sebagai spy, tetapi lokasi {location} gagal ditebak oleh sang spy karena menebak {spySelect.values[0]}. Spy Loses!",
                                    color=0x330066)
                                embedRes.set_image(
                                    url=
                                    'https://some-random-api.ml/canvas/jail?avatar='
                                    + interaction.user.avatar.url)

                            else:
                                embedRes = discord.Embed(
                                    title=f"[ SpyGame ]",
                                    description=
                                    f"{interaction.user}-nyan gagal ditebak sebagai spy karena kesalahan menebak terhadap {chosen}. Tetapi lokasi {location} juga gagal ditebak oleh sang spy karena menebak {spySelect.values[0]}. It's a tie game!",
                                    color=0x330066)
                                embedRes.set_image(
                                    url=
                                    'https://c.tenor.com/wyfhYqF1tJIAAAAM/mark-wahlberg-wahlberg.gif'
                                )

                            await interaction.followup.send(embed=embedRes)

                        embedVoteDone = discord.Embed(
                            title=f"[ SpyGame ]",
                            description=
                            f"Voting sudah selesai, kini giliran spy menebak lokasi",
                            color=0x330066)
                        await interaction.response.edit_message(
                            embed=embedVoteDone, view=None)
                        nonlocal flagVote
                        flagVote = True
                        spySelect.callback = spy_callback
                        spyView = View(timeout=300)
                        spyView.add_item(spySelect)
                        embedSpy = discord.Embed(
                            title=f"[ SpyGame ]",
                            description=
                            f"Untuk spy, silahkan menebak lokasi para pemain lain!",
                            color=0x330066)
                        spyMsg = await voteMsg.channel.send(embed=embedSpy,
                                                            view=spyView)
                        checkSpyView = await spyView.wait()

                        if checkSpyView:
                            embedSpyNot = discord.Embed(
                                title=f"[ SpyGame ]",
                                description=
                                f"Spy tidak menebak dalam kurun waktu yang telah ditentukan, silahkan scroll ke bawah untuk melihat hasilnya",
                                color=0x330066)
                            await spyMsg.edit(embed=embedSpyNot, view=None)

                            if spyGet:
                                embedRes = discord.Embed(
                                    title=f"[ SpyGame ]",
                                    description=
                                    f"{interaction.user}-nyan berhasil ditebak sebagai spy, tetapi lokasi {location} gagal ditebak oleh sang spy karena kehabisan waktu. Spy Loses!",
                                    color=0x330066)
                                embedRes.set_image(
                                    url=
                                    'https://some-random-api.ml/canvas/jail?avatar='
                                    + interaction.user.avatar.url)

                            else:
                                embedRes = discord.Embed(
                                    title=f"[ SpyGame ]",
                                    description=
                                    f"{interaction.user}-nyan gagal ditebak sebagai spy karena kesalahan menebak terhadap {chosen}. Tetapi lokasi {location} juga gagal ditebak oleh sang spy karena kehabisan waktu. It's a tie game!",
                                    color=0x330066)
                                embedRes.set_image(
                                    url=
                                    'https://c.tenor.com/wyfhYqF1tJIAAAAM/mark-wahlberg-wahlberg.gif'
                                )

                            await spyMsg.channel.send(embed=embedRes,
                                                      view=None)

            select.callback = selection_callback
            buttonEV.callback = endvote_callback
            voteView = View(timeout=None)
            voteView.add_item(select)
            voteView.add_item(buttonEV)

            embedGame = discord.Embed(
                title=f"[ SpyGame ]",
                description=
                f"Waktu Game telah habis dan game telah memasuki fase voting, silahkan scroll ke bawah untuk melanjutkan",
                color=0x330066)
            await gameMsg.edit(embed=embedGame, view=None)
            embedEdit = discord.Embed(
                title=f"[ SpyGame ]",
                description=
                f"< Voting List > | Time Left : {300 - timeVote} seconds",
                color=0x330066)
            for i in range(playerCount):
                embedEdit.add_field(name=f"{playersName[i]}",
                                    value='```' + 'Vote : ' +
                                    str(voteCount[i]) + '```',
                                    inline=False)
            voteMsg = await gameMsg.channel.send(embed=embedEdit,
                                                 view=voteView)
            flagVoteTime = False
            while True:
                await asyncio.sleep(1)
                timeVote += 1
                # print(timeVote)
                if timeVote == 300:
                    flagVoteTime = True
                    break
                if flagVote:
                    break

            if flagVoteTime:
                chosen = max(votes, key=votes.count)

                if playersName.index(chosen) == spyIndex:
                    spyGet = True
                else:
                    spyGet = False

                spySelect = Select(placeholder="Guess the location!")
                for x in locationList:
                    spySelect.add_option(label=x)

                async def spy_callback(interaction):
                    if interaction.user.id != playersID[spyIndex]:
                        await interaction.response.send_message(
                            f"Neee anata bukan spy ih {interaction.user.name}-nyan, tunggu spynya jawab yaa..",
                            ephemeral=True)
                        return

                    if spySelect.values[0] == location:
                        locGet = True

                    else:
                        locGet = False

                    embedSpyDoneLoc = discord.Embed(
                        title=f"[ SpyGame ]",
                        description=
                        f"Spy telah selesai memilih lokasi, silahkan scroll ke bawah untuk melanjutkan",
                        color=0x330066)
                    await interaction.response.edit_message(
                        embed=embedSpyDoneLoc, view=None)
                    spyView.stop()
                    if locGet and spyGet:
                        embedRes = discord.Embed(
                            title=f"[ SpyGame ]",
                            description=
                            f"{interaction.user}-nyan berhasil ditebak sebagai spy dan lokasi {location} juga berhasil ditebak oleh sang spy. It's a tie game!",
                            color=0x330066)
                        embedRes.set_image(
                            url=
                            'https://c.tenor.com/wyfhYqF1tJIAAAAM/mark-wahlberg-wahlberg.gif'
                        )

                    elif locGet:
                        embedRes = discord.Embed(
                            title=f"[ SpyGame ]",
                            description=
                            f"{interaction.user}-nyan gagal ditebak sebagai spy karena kesalahan menebak terhadap {chosen}. Sementara lokasi {location} berhasil ditebak oleh sang spy. Spy Wins!",
                            color=0x330066)
                        embedRes.set_image(
                            url=
                            'https://some-random-api.ml/canvas/passed?avatar='
                            + interaction.user.avatar.url)

                    elif spyGet:
                        embedRes = discord.Embed(
                            title=f"[ SpyGame ]",
                            description=
                            f"{interaction.user}-nyan berhasil ditebak sebagai spy, tetapi lokasi {location} gagal ditebak oleh sang spy karena menebak {spySelect.values[0]}. Spy Loses!",
                            color=0x330066)
                        embedRes.set_image(
                            url='https://some-random-api.ml/canvas/jail?avatar='
                            + interaction.user.avatar.url)

                    else:
                        embedRes = discord.Embed(
                            title=f"[ SpyGame ]",
                            description=
                            f"{interaction.user}-nyan gagal ditebak sebagai spy karena kesalahan menebak terhadap {chosen}. Tetapi lokasi {location} juga gagal ditebak oleh sang spy karena menebak {spySelect.values[0]}. It's a tie game!",
                            color=0x330066)
                        embedRes.set_image(
                            url=
                            'https://c.tenor.com/wyfhYqF1tJIAAAAM/mark-wahlberg-wahlberg.gif'
                        )

                    await interaction.followup.send(embed=embedRes)

                spySelect.callback = spy_callback
                spyView = View(timeout=300)
                spyView.add_item(spySelect)
                embedVoteSpyNow = discord.Embed(
                    title=f"[ SpyGame ]",
                    description=
                    f"Waktu Voting telah habis, kini giliran spy menebak lokasi, silahkan scroll ke bawah untuk melanjutkan",
                    color=0x330066)
                await voteMsg.edit(embed=embedVoteSpyNow, view=None)
                embedSpy = discord.Embed(
                    title=f"[ SpyGame ]",
                    description=
                    f"Untuk spy, silahkan menebak lokasi para pemain lain!",
                    color=0x330066)
                spyMsg = await voteMsg.channel.send(embed=embedSpy,
                                                    view=spyView)
                checkSpyView = await spyView.wait()

                if checkSpyView:
                    embedSpyDoneNow = discord.Embed(
                        title=f"[ SpyGame ]",
                        description=
                        f"Spy sudah menentukan lokasi, silahkan scroll ke bawah untuk melanjutkan",
                        color=0x330066)
                    await spyMsg.edit(embed=embedSpyDoneNow, view=None)

                    if spyGet:
                        embedRes = discord.Embed(
                            title=f"[ SpyGame ]",
                            description=
                            f"{interaction.user}-nyan berhasil ditebak sebagai spy, tetapi lokasi {location} gagal ditebak oleh sang spy karena kehabisan waktu. Spy Loses!",
                            color=0x330066)
                        embedRes.set_image(
                            url='https://some-random-api.ml/canvas/jail?avatar='
                            + interaction.user.avatar.url)

                    else:
                        embedRes = discord.Embed(
                            title=f"[ SpyGame ]",
                            description=
                            f"{interaction.user}-nyan gagal ditebak sebagai spy karena kesalahan menebak terhadap {chosen}. Tetapi lokasi {location} juga gagal ditebak oleh sang spy karena kehabisan waktu. It's a tie game!",
                            color=0x330066)
                        embedRes.set_image(
                            url=
                            'https://c.tenor.com/wyfhYqF1tJIAAAAM/mark-wahlberg-wahlberg.gif'
                        )

                    await spyMsg.channel.send(embed=embedRes, view=None)

    buttonJ.callback = join_callback
    buttonS.callback = start_callback
    view = View(timeout=600)
    view.add_item(buttonJ)
    view.add_item(buttonS)

    embedVar = discord.Embed(
        title=f'[ SpyGame ]',
        description=
        "Press button to join, can start after at least 3 players have joined",
        color=0x330066)
    panelMsg = await ctx.response.send_message(embed=embedVar, view=view)
    checkView = await view.wait()

    if checkView:
        embedEdit = discord.Embed(
            title=f"Game telah ditutup karena tak kunjung distart",
            description="Watashi udah nunggu lama tapi belum distart juga..",
            color=0x330066)
        await panelMsg.edit_original_response(embed=embedEdit, view=None)

async def setup(bot):
  await bot.add_cog(Spygame(bot))