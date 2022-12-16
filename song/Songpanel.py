import discord
import os
import wavelink
from wavelink.ext import spotify
from discord.ui import Select, Button, Modal, InputText, View
from discord.ext import commands
from discord.commands import Option
import datetime
import pytz
import numpy as np
import asyncio
import time
import random

guilds = [990445490401341511, 1020927428459241522, 989086863434334279, 494097970208178186, 1028690906901139486]
SPOTIFYSECRET = os.environ['SPOTIFYSECRET']
SPOTIFYID = os.environ['SPOTIFYID']

class Songpanel(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    
  @commands.slash_command(name='songpanel', description='Open the song panel to control the song playing')
  async def song_panel(self, ctx):
    if not ctx.voice_client:
        await ctx.respond(
            f'Watashi aja ngga join vc loh {ctx.author.name}-nyan...',
            ephemeral=True)
        return
    elif not ctx.author.voice:
        await ctx.respond('Etlis join vc dlu la dek..', ephemeral=True)
        return
    elif ctx.author.voice.channel != ctx.me.voice.channel:
        await ctx.respond(
            f'Hmph {ctx.author.name}-nyan, watashi ngga mau diatur-atur kalo watashitachi ngga satu vc',
            ephemeral=True)
        return
    else:
        vc: wavelink.Player = ctx.voice_client
        buttonRP = Button(label='Resume/Pause',
                          emoji='⏯️',
                          style=discord.ButtonStyle.primary,
                          row=0)
        buttonS = Button(label='Skip Song',
                         emoji='⏭',
                         style=discord.ButtonStyle.danger,
                         row=0)
        buttonC = Button(label="What's Playing?",
                         emoji='⏏️',
                         style=discord.ButtonStyle.primary,
                         row=0)
        buttonL = Button(label='Loop On/Off',
                         emoji='🔂',
                         style=discord.ButtonStyle.green,
                         row=1)
        buttonSH = Button(label='Shuffle Queue',
                          emoji='🔀',
                          style=discord.ButtonStyle.primary,
                          row=1)
        buttonQ = Button(label='Open Queue',
                         emoji='🎶',
                         style=discord.ButtonStyle.gray,
                         row=1)
        buttonD = Button(label='Disconnect',
                         emoji='👋',
                         style=discord.ButtonStyle.danger,
                         row=2)

        vcDict = {}
        skipCount = 0

        async def rp_callback(interaction):
            if not ctx.voice_client:
                embedEdit = discord.Embed(
                    title=f"Song Panelnya ditutup karena watashi udah keluar..",
                    description="Tulis /songpanel lagi kalau mau pakai yaa~",
                    color=0x1DB954)
                await interaction.response.edit_message(embed=embedEdit,
                                                        view=None)
                await interaction.followup.send(
                    f"Ahh telat {interaction.user.name}-nyan, watashi udah ngga di dalem vc",
                    ephemeral=True)
            elif not interaction.user.voice:
                await interaction.response.send_message(
                    f"Neee {interaction.user.name}-nyan, join vc dulu laa",
                    ephemeral=True)
            elif interaction.user.voice.channel != ctx.me.voice.channel:
                await interaction.response.send_message(
                    f"Hmph {interaction.user.name}-nyan, watashi ngga mau diatur kalo anata ngga join vc {ctx.me.voice.channel} bareng watashi",
                    ephemeral=True)
            else:
                if not vc.is_playing():
                    await interaction.response.send_message(
                        f'Ih aneh deh {interaction.user.name}-nyan, kan ngga ada yang lagi diputer',
                        ephemeral=True)
                    return

                if vc.is_paused():
                    await interaction.response.send_message(
                        f'`{vc.track.title}` diresume sama {interaction.user}-nyan'
                    )
                    await vc.resume()
                else:
                    await interaction.response.send_message(
                        f'`{vc.track.title}` dipause sama {interaction.user}-nyan'
                    )
                    await vc.pause()

        async def s_callback(interaction):
            if not ctx.voice_client:
                await interaction.response.send_message(
                    f"Ahh telat {interaction.user.name}-nyan, watashi udah ngga di dalem vc",
                    ephemeral=True)
                embedEdit = discord.Embed(
                    title=f"Song Panelnya ditutup karena watashi udah keluar..",
                    description="Tulis /songpanel lagi kalau mau pakai yaa~",
                    color=0x1DB954)
                await interaction.response.edit_message(embed=embedEdit,
                                                        view=None)
            elif not interaction.user.voice:
                await interaction.response.send_message(
                    f"Neee {interaction.user.name}-nyan, join vc dulu laa",
                    ephemeral=True)
            elif interaction.user.voice.channel != ctx.me.voice.channel:
                await interaction.response.send_message(
                    f"Hmph {interaction.user.name}-nyan, watashi ngga mau diatur kalo anata ngga join vc {ctx.me.voice.channel} bareng watashi",
                    ephemeral=True)
            else:
                if not vc.is_playing():
                    await interaction.response.send_message(
                        f'Ih aneh deh {interaction.user.name}-nyan, kan ngga ada yang lagi diputer',
                        ephemeral=True)
                    return

                nonlocal vcDict, skipCount

                memNeed = 0
                for one in vc.channel.members:
                    if not one.bot:
                        memNeed += 1

                memNeed = int(memNeed / 2) + 1

                if str(interaction.user.id) in vcDict:
                    await interaction.response.send_message(
                        f'Anata udah vote buat skip {interaction.user.name}-nyan, sabar yaa, kurang {memNeed - skipCount} orang lagi buat skip lagu yang sedang diputar',
                        ephemeral=True)
                    return

                else:
                    vcDict[str(interaction.user.id)] = True
                    skipCount += 1
                    if skipCount < memNeed:
                        await interaction.response.send_message(
                            f'{interaction.user.name}-nyan berhasil memvote skip terhadap lagu yang sedang diputar [{skipCount} / {memNeed} Vote(s)]'
                        )
                        return

                setattr(vc, "loop", False)
                await interaction.response.send_message(
                    f'`{vc.track.title}` berhasil diskip!')
                skipCount = 0
                vcDict.clear()
                await vc.stop()

        async def l_callback(interaction):
            if not ctx.voice_client:
                await interaction.response.send_message(
                    f"Ahh telat {interaction.user.name}-nyan, watashi udah ngga di dalem vc",
                    ephemeral=True)
                embedEdit = discord.Embed(
                    title=f"Song Panelnya ditutup karena watashi udah keluar..",
                    description="Tulis /songpanel lagi kalau mau pakai yaa~",
                    color=0x1DB954)
                await interaction.response.edit_message(embed=embedEdit,
                                                        view=None)
            elif not interaction.user.voice:
                await interaction.response.send_message(
                    f"Neee {interaction.user.name}-nyan, join vc dulu laa",
                    ephemeral=True)
            elif interaction.user.voice.channel != ctx.me.voice.channel:
                await interaction.response.send_message(
                    f"Hmph {interaction.user.name}-nyan, watashi ngga mau diatur kalo anata ngga join vc {ctx.me.voice.channel} bareng watashi",
                    ephemeral=True)
            else:
                if not vc.is_playing():
                    await interaction.response.send_message(
                        f'Ih aneh deh {interaction.user.name}-nyan, kan ngga ada yang lagi diputer',
                        ephemeral=True)
                    return

                try:
                    vc.loop ^= True
                except Exception:
                    setattr(vc, "loop", False)

                if vc.loop:
                    await interaction.response.send_message(
                        f'Loop buat `{vc.track.title}` dinyalain sama {interaction.user}-nyan'
                    )
                else:
                    await interaction.response.send_message(
                        f'Loop buat `{vc.track.title}` dimatiin sama {interaction.user}-nyan'
                    )

        async def sh_callback(interaction):
            if not ctx.voice_client:
                await interaction.response.send_message(
                    f"Ahh telat {interaction.user.name}-nyan, watashi udah ngga di dalem vc",
                    ephemeral=True)
                embedEdit = discord.Embed(
                    title=f"Song Panelnya ditutup karena watashi udah keluar..",
                    description="Tulis /songpanel lagi kalau mau pakai yaa~",
                    color=0x1DB954)
                await interaction.response.edit_message(embed=embedEdit,
                                                        view=None)
            elif not interaction.user.voice:
                await interaction.response.send_message(
                    f"Neee {interaction.user.name}-nyan, join vc dulu laa",
                    ephemeral=True)
            elif interaction.user.voice.channel != ctx.me.voice.channel:
                await interaction.response.send_message(
                    f"Hmph {interaction.user.name}-nyan, watashi ngga mau diatur kalo anata ngga join vc {ctx.me.voice.channel} bareng watashi",
                    ephemeral=True)
            else:
                if not vc.is_playing():
                    await interaction.response.send_message(
                        f'Ih aneh deh {interaction.user.name}-nyan, kan ngga ada yang lagi diputer',
                        ephemeral=True)
                    return

                if vc.queue.is_empty:
                    await interaction.response.send_message(
                        f'Sekarang queuenya lagi kosong {interaction.user.name}-nyan, silahkan kalau mau diisi yaa~',
                        ephemeral=True)
                    return

                try:
                    arr = []
                    for song in vc.queue:
                        arr.append(song)
                    random.shuffle(arr)
                    vc.queue.clear()
                    vc.queue.extend(arr)
                    await interaction.response.send_message(
                        f"Queue berhasil dishuffle oleh {interaction.user.name}-nyan!"
                    )
                except Exception:
                    await interaction.response.send_message(
                        f"Queue gagal dishuffle oleh {interaction.user.name}-nyan! Coba tanya Zetsu deh.."
                    )

        async def q_callback(interaction):
            if not ctx.voice_client:
                await interaction.response.send_message(
                    f"Ahh anata telat {interaction.user.name}-nyan, watashi udah ngga di dalem vc",
                    ephemeral=True)
                embedEdit = discord.Embed(
                    title=f"Song Panelnya ditutup karena watashi udah keluar..",
                    description="Tulis /songpanel lagi kalau mau pakai yaa~",
                    color=0x1DB954)
                await interaction.response.edit_message(embed=embedEdit,
                                                        view=None)
            elif not interaction.user.voice:
                await interaction.response.send_message(
                    f"Neee {interaction.user.name}-nyan, join vc dulu laa",
                    ephemeral=True)
            elif interaction.user.voice.channel != ctx.me.voice.channel:
                await interaction.response.send_message(
                    f"Hmph {interaction.user.name}-nyan, watashi ngga mau diatur kalo anata ngga join vc {ctx.me.voice.channel} bareng watashi",
                    ephemeral=True)
            else:
                if not vc.is_playing():
                    await interaction.response.send_message(
                        f'Ih aneh deh {interaction.user.name}-nyan, kan ngga ada yang lagi diputer',
                        ephemeral=True)
                    return

                if vc.queue.is_empty:
                    await interaction.response.send_message(
                        f'Sekarang queuenya lagi kosong {interaction.user.name}-nyan, silahkan kalau mau diisi yaa~',
                        ephemeral=True)
                    return

                songQueue = vc.queue.copy()
                queueList = []
                queueIndex = 0

                songCount = len(songQueue)
                num = int(songCount / 40) + 1

                if num == 1:
                    queueIndex = 0
                    queueTemp = []
                    for song in songQueue:
                        queueIndex += 1
                        queueTemp.append(f"{queueIndex}) {song.title}")

                    queueString = '\n'.join(queueTemp)
                    queueList.append(queueString)

                else:
                    queueIndex = 0
                    sub_lists = np.array_split(songQueue, num)
                    for i in sub_lists:
                        queueTemp = []
                        for song in list(i):
                            queueIndex += 1
                            queueTemp.append(f"{queueIndex}) {song.title}")

                        queueString = '\n'.join(queueTemp)
                        queueList.append(queueString)

                if songCount > 50:
                    index = 0
                    buttonPP = Button(label='Previous Page',
                                      emoji='👈',
                                      style=discord.ButtonStyle.gray,
                                      row=0)
                    buttonNP = Button(label='Next Page',
                                      emoji='👉',
                                      style=discord.ButtonStyle.gray,
                                      row=0)

                    async def pp_callback(interaction):
                        nonlocal index
                        if index == 0:
                            await interaction.response.send_message(
                                f"Neee {interaction.user.name}, ini udah page paling awal loh..",
                                ephemeral=True)
                            return

                        index -= 1
                        embedVar = discord.Embed(
                            title=
                            f"Queue requested by {interaction.user.name}-nyan | {queueIndex} songs waiting to be played",
                            description='```' + queueList[index] + '```',
                            color=0x1DB954)
                        await interaction.response.edit_message(embed=embedVar)

                    async def np_callback(interaction):
                        nonlocal index
                        if index == (num - 1):
                            await interaction.response.send_message(
                                f"Neee {interaction.user.name}, ini udah page paling akhir loh..",
                                ephemeral=True)
                            return

                        index += 1
                        embedVar = discord.Embed(
                            title=
                            f"Queue requested by {interaction.user.name}-nyan | {queueIndex} songs waiting to be played",
                            description='```' + queueList[index] + '```',
                            color=0x1DB954)
                        await interaction.response.edit_message(embed=embedVar)

                    buttonPP.callback = pp_callback
                    buttonNP.callback = np_callback
                    inView = View(timeout=None)
                    inView.add_item(buttonPP)
                    inView.add_item(buttonNP)

                    embedVar = discord.Embed(
                        title=
                        f"Queue requested by {interaction.user.name}-nyan | {queueIndex} songs waiting to be played",
                        description='```' + queueList[index] + '```',
                        color=0x1DB954)
                    await interaction.response.send_message(embed=embedVar,
                                                            view=inView,
                                                            ephemeral=True)

                else:
                    embedVar = discord.Embed(
                        title=
                        f"Queue requested by {interaction.user.name}-nyan | {queueIndex} songs waiting to be played",
                        description='```' + queueList[0] + '```',
                        color=0x1DB954)
                    await interaction.response.send_message(embed=embedVar,
                                                            ephemeral=True)

        async def c_callback(interaction):
            if not ctx.voice_client:
                await interaction.response.send_message(
                    f"Ahh telat {interaction.user.name}-nyan, watashi udah ngga di dalem vc",
                    ephemeral=True)
                embedEdit = discord.Embed(
                    title=f"Song Panelnya ditutup karena watashi udah keluar..",
                    description="Tulis /songpanel lagi kalau mau pakai yaa~",
                    color=0x1DB954)
                await interaction.response.edit_message(embed=embedEdit,
                                                        view=None)
            elif not interaction.user.voice:
                await interaction.response.send_message(
                    f"Neee {interaction.user.name}-nyan, join vc dulu laa",
                    ephemeral=True)
            elif interaction.user.voice.channel != ctx.me.voice.channel:
                await interaction.response.send_message(
                    f"Hmph {interaction.user.name}-nyan, watashi ngga mau diatur kalo anata ngga join vc {ctx.me.voice.channel} bareng watashi",
                    ephemeral=True)
            else:
                if not vc.is_playing():
                    await interaction.response.send_message(
                        f'Ih aneh deh {interaction.user.name}-nyan, kan ngga ada yang lagi diputer',
                        ephemeral=True)
                    return

                embedVar = discord.Embed(
                    title=f"Now Playing : {vc.track.title}",
                    description=f"By : {vc.track.author}",
                    color=0x1DB954)
                embedVar.add_field(
                    name="Duration",
                    value=
                    f'`{str(datetime.timedelta(seconds=vc.track.length))}`')
                embedVar.add_field(name="Song URL",
                                   value=f"[Click Me]({str(vc.track.uri)})")
                await interaction.response.send_message(embed=embedVar,
                                                        ephemeral=True)

        async def d_callback(interaction):
            if not ctx.voice_client:
                await interaction.response.send_message(
                    f"Ahh telat {interaction.user.name}-nyan, watashi udah ngga di dalem vc",
                    ephemeral=True)
                embedEdit = discord.Embed(
                    title=f"Song Panelnya ditutup karena watashi udah keluar..",
                    description="Tulis /songpanel lagi kalau mau pakai yaa~",
                    color=0x1DB954)
                await interaction.response.edit_message(embed=embedEdit,
                                                        view=None)
            elif not interaction.user.voice:
                await interaction.response.send_message(
                    f"Neee {interaction.user.name}-nyan, join vc dulu laa",
                    ephemeral=True)
            elif interaction.user.voice.channel != ctx.me.voice.channel:
                await interaction.response.send_message(
                    f"Hmph {interaction.user.name}-nyan, watashi ngga mau diatur kalo anata ngga join vc {ctx.me.voice.channel} bareng watashi",
                    ephemeral=True)
            else:
                if vc.queue.is_empty and not vc.is_playing():
                    embedEdit = discord.Embed(
                        title=
                        f"Song Panelnya ditutup karena watashi udah keluar..",
                        description=
                        "Tulis /songpanel lagi kalau mau pakai yaa~",
                        color=0x1DB954)
                    await interaction.response.edit_message(embed=embedEdit,
                                                            view=None)
                    await interaction.followup.send(
                        f"Watashi disuruh keluar vc sama {ctx.author}-nyan, kalau mau manggil lagi /songinsert aja yaa~"
                    )
                    await vc.disconnect()

                elif len(vc.channel.members) == 2:
                    embedEdit = discord.Embed(
                        title=
                        f"Song Panelnya ditutup karena watashi udah keluar..",
                        description=
                        "Tulis /songpanel lagi kalau mau pakai yaa~",
                        color=0x1DB954)
                    await interaction.response.edit_message(embed=embedEdit,
                                                            view=None)
                    await interaction.followup.send(
                        f"Watashi disuruh keluar vc sama {ctx.author}-nyan, kalau mau manggil lagi /songinsert aja yaa~"
                    )
                    view.stop()
                    await vc.disconnect()

                else:
                    await interaction.response.send_message(
                        f'Watashi masih sibuk ih {interaction.user.name}, nanti aja yah kalau ngga ada lagi yang diputer atau sisa kamu sendiri, baru deh watashi mau leave',
                        ephemeral=True)

        buttonRP.callback = rp_callback
        buttonS.callback = s_callback
        buttonL.callback = l_callback
        buttonSH.callback = sh_callback
        buttonQ.callback = q_callback
        buttonC.callback = c_callback
        buttonD.callback = d_callback
        view = View(timeout=180)
        view.add_item(buttonRP)
        view.add_item(buttonS)
        view.add_item(buttonC)
        view.add_item(buttonL)
        view.add_item(buttonSH)
        view.add_item(buttonQ)
        view.add_item(buttonD)

        embedVar = discord.Embed(
            title=f'[ Song Panel ]',
            description="Control by pressing the buttons below",
            color=0x1DB954)
        panelMsg = await ctx.respond(embed=embedVar, view=view)
        checkView = await view.wait()

        if checkView:
            embedEdit = discord.Embed(
                title=f"Song Panelnya sudah ditutup karena lama ngga dipakai..",
                description="Tulis /songpanel lagi kalau mau pakai yaa~",
                color=0x1DB954)
            await panelMsg.edit_original_message(embed=embedEdit, view=None)

def setup(bot):
  bot.add_cog(Songpanel(bot))