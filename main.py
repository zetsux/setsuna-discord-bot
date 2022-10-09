from webserver import keep_alive
import os
import random
import discord
from discord.ui import Select, Button, Modal, InputText, View
from discord.ext import commands
from discord.commands import Option
import pymongo
import json
import urllib.request as urllib2
import wavelink
from wavelink.ext import spotify
import datetime
import pytz
import numpy as np
import asyncio
import time

TOKEN = os.environ['TOKEN']
ROLECLAIM = int(os.environ['ROLEMSGID'])
MONGODB = os.environ['MONGODB']
LORENDB = os.environ['LORENDB']
SPOTIFYSECRET = os.environ['SPOTIFYSECRET']
SPOTIFYID = os.environ['SPOTIFYID']
SONGCH = int(os.environ['SONGCHID'])
GUILDID = int(os.environ['GUILDID'])
CSGUILDID = int(os.environ['CSGUILDID'])
CSSONGCH = int(os.environ['SONGCSID'])
LOGCH = int(os.environ['LOGCHID'])

client = pymongo.MongoClient(MONGODB)
mydb = client["familiardb"]
mycol = mydb["user"]

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!$', intents=intents)

row = 10
col = 10


def isPath(arr):
    Dir = [[0, 1], [0, -1], [1, 0], [-1, 0]]
    q = []
    q.append((0, 0))

    while (len(q) > 0):
        p = q[0]
        q.pop(0)
        arr[p[0]][p[1]] = -1
        if (p == (row - 1, col - 1)):
            return True

        for i in range(4):
            a = p[0] + Dir[i][0]
            b = p[1] + Dir[i][1]
            if (a >= 0 and b >= 0 and a < row and b < col and arr[a][b] != -1):
                q.append((a, b))
    return False


@bot.event
async def on_ready():
  print(f'{bot.user.name} has connected to Discord!')
  await bot.change_presence(activity=discord.Activity(
      type=discord.ActivityType.watching, name="u from afar | /help"))
        
  bot.loop.create_task(connect_nodes())
    # change_bot_task.start()


@bot.event
async def on_wavelink_node_ready(node: wavelink.Node):
    print(f'The Node {node.identifier} has also connected to Discord!')


# @tasks.loop(seconds=1800)
# async def change_bot_task():
#   await bot.wait_until_ready()
#   statuses = ["commands | !help", "cues | !help", "orders | !help", "instructions | !help", "directions | !help", "requests | !help", "demands | !help", "mandates | !help", "decrees | !help", "prompts | !help", "signals | !help", "ur bs | !help"]
#   while not bot.is_closed() :
#     status = random.choice(statuses)
#     await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=status))


async def connect_nodes():
    await bot.wait_until_ready()
    await wavelink.NodePool.create_node(bot=bot,
                                        host='lava.islantay.tk',
                                        port=443,
                                        password='AmeliaWatsonisTheBest**!',
                                        https=True,
                                        spotify_client=spotify.SpotifyClient(
                                            client_id=SPOTIFYID,
                                            client_secret=SPOTIFYSECRET))


@bot.event
async def on_wavelink_track_end(player: wavelink.Player, track: wavelink.Track,
                                reason):
    ctx = player.ctx
    vc: player = ctx.voice_client

    if vc.loop:
        await vc.play(track)
        return

    try:
        next_track = vc.queue.get()
        await vc.play(next_track)
        await ctx.channel.send(f'Now Playing : `{next_track.title}`')
    except:
        await vc.stop()


@bot.event
async def on_voice_state_update(member, before, after):
    if member.id == bot.user.id:
        return

    if after.channel is None or before.channel is not None:
        voice = before.channel.guild.voice_client
        if len(before.channel.members) >= 1:
            setexist = False
            for mem in before.channel.members:
                if mem.id == bot.user.id:
                    setexist = True

                if not mem.bot:
                    return

            if not setexist:
                return

            memlen = len(before.channel.members)
            time = 0
            while True:
                await asyncio.sleep(1)
                time = time + 1
                # print(time)
                if voice.is_playing() and not voice.is_paused():
                    if time >= 900:
                        if before.channel.guild.id == CSGUILDID:
                            channel = before.channel.guild.get_channel(
                                CSSONGCH)
                            await channel.send(
                                f"Watashi leave dari {before.channel.name} dulu deh ya, mendokusai ah muter lagu gada yg dengerin, jahat banget ga di-disconnect, nanti /songinsert lagi ajah kalo mau manggil lagi yaa~"
                            )

                        elif before.channel.guild.id == GUILDID:
                            channel = before.channel.guild.get_channel(SONGCH)
                            await channel.send(
                                f"Watashi leave dari {before.channel.name} dulu deh ya, mendokusai ah muter lagu gada yg dengerin, jahat banget ga di-disconnect, nanti /songinsert lagi ajah kalo mau manggil lagi yaa~"
                            )

                        return await voice.disconnect()

                else:
                    if time >= 300:
                        if before.channel.guild.id == CSGUILDID:
                            channel = before.channel.guild.get_channel(
                                CSSONGCH)
                            await channel.send(
                                f"Watashi leave dari {before.channel.name} dulu deh ya, sabishii ah ditinggal sendiri, mana ngga di-disconnect pula, nanti /songinsert lagi ajah kalo mau manggil lagi yaa~"
                            )

                        elif before.channel.guild.id == GUILDID:
                            channel = before.channel.guild.get_channel(SONGCH)
                            await channel.send(
                                f"Watashi leave dari {before.channel.name} dulu deh ya, sabishii ah ditinggal sendiri, mana ngga di-disconnect pula, nanti /songinsert lagi ajah kalo mau manggil lagi yaa~"
                            )

                        return await voice.disconnect()

                if not voice.is_connected():
                    break

                if len(before.channel.members) != memlen:
                    for mem in before.channel.members:
                        if not mem.bot:
                            return

                    memlen = len(before.channel.members)


@bot.slash_command(name='reloadcogs', description='Reload Cogs')
@commands.has_any_role('Encoder Magang', 'Owner')
async def reload(ctx):
  await ctx.defer()
  str = ""
  for folder in os.listdir("./") :
    path = f"./{folder}"
    
    if not os.path.isdir(path) :
      continue
      
    for filename in os.listdir(f"./{folder}") :
      if filename.endswith(".py") :
        try : 
          bot.load_extension(f"{folder}.{filename[:-3]}")
          str += f"{folder}.{filename[:-3]}"
        except Exception as error :
          print(error)

  await ctx.respond(f"{str}")

@bot.slash_command(
    name='songinsert',
    description='Insert track/album/playlist from spotify/youtube to the queue'
)
async def song_insert(ctx, *, search: Option(str,
                                             "Link or key to search for",
                                             required=True)):
    if not ctx.author.voice:
        await ctx.respond('Etlis join vc dlu la dek..', ephemeral=True)
        return
    elif not ctx.voice_client:
        vc: wavelink.Player = await ctx.author.voice.channel.connect(
            cls=wavelink.Player)
    elif ctx.author.voice.channel != ctx.me.voice.channel:
        await ctx.respond(
            f'Hmph {ctx.author.name}-nyan, watashi ngga mau diatur-atur kalo watashitachi ngga satu vc',
            ephemeral=True)
        return
    else:
        vc: wavelink.Player = ctx.voice_client

    decoded = spotify.decode_url(search)

    if decoded:
        if decoded['type'] is spotify.SpotifySearchType.track:
            track = await spotify.SpotifyTrack.search(query=search,
                                                      return_first=True)
            if vc.queue.is_empty and not vc.is_playing():
                setattr(vc, "loop", False)
                await vc.play(track)
                await ctx.respond(
                    f'Now Playing : `{track.title}`, request of {ctx.author.name}-nyan'
                )
            else:
                await vc.queue.put_wait(track)
                await ctx.respond(
                    f'Queueing : `{track.title}`, request of {ctx.author.name}-nyan'
                )

        elif decoded['type'] is spotify.SpotifySearchType.album:
            await ctx.respond(
                f'Queueing : [SpotifyAlbum]({str(search)}), request of {ctx.author.name}-nyan'
            )
            tracks = await spotify.SpotifyTrack.search(query=search)
            if vc.queue.is_empty and not vc.is_playing():
                setattr(vc, "loop", False)
                index = 0
                for track in tracks:
                    index += 1
                    if index == 1:
                        continue
                    await vc.queue.put_wait(track)

                await vc.play(tracks[0])
                await ctx.send(
                    f'Now Playing : `{tracks[0].title}`, request of {ctx.author.name}-nyan'
                )

            else:
                for track in tracks:
                    await vc.queue.put_wait(track)

        elif decoded['type'] is spotify.SpotifySearchType.playlist:
            await ctx.respond(
                f'Queueing : [SpotifyPlaylist]({str(search)}), request of {ctx.author.name}-nyan'
            )
            if vc.queue.is_empty and not vc.is_playing():
                index = 0
                setattr(vc, "loop", False)
                async for partial in spotify.SpotifyTrack.iterator(
                        query=search, partial_tracks=True):
                    index += 1
                    if index == 1:
                        await vc.play(partial)
                        await ctx.send(
                            f'Now Playing : `{partial.title}`, request of {ctx.author.name}-nyan'
                        )
                    else:
                        await vc.queue.put_wait(partial)

            else:
                async for partial in spotify.SpotifyTrack.iterator(
                        query=search, partial_tracks=True):
                    await vc.queue.put_wait(partial)

    else:
        if 'youtube.com/playlist' in search:
            await ctx.respond(
                f'Queueing : [YoutubePlaylist]({str(search)}), request of {ctx.author.name}-nyan'
            )
            search = await wavelink.YouTubePlaylist.search(query=search)
            if vc.queue.is_empty and not vc.is_playing():
                setattr(vc, "loop", False)
                tempIndex = 0
                for track in search.tracks:
                    tempIndex += 1
                    if tempIndex == 1:
                        await vc.play(track)
                        await ctx.send(
                            f'Now Playing : `{track.title}`, request of {ctx.author.name}-nyan'
                        )
                    else:
                        await vc.queue.put_wait(track)

            else:
                for track in search.tracks:
                    await vc.queue.put_wait(track)

        else:
            search = await wavelink.YouTubeTrack.search(query=search,
                                                        return_first=True)
            if vc.queue.is_empty and not vc.is_playing():
                setattr(vc, "loop", False)
                await vc.play(search)
                await ctx.respond(
                    f'Now Playing : `{search.title}`, request of {ctx.author.name}-nyan'
                )

            else:
                await vc.queue.put_wait(search)
                await ctx.respond(
                    f'Queueing : `{search.title}`, request of {ctx.author.name}-nyan'
                )

    vc.ctx = ctx


@bot.slash_command(
    name='songpanel',
    description='Open the song panel to control the song playing')
async def song_panel(ctx):
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
                    color=0xffff00)
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
                    color=0xffff00)
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
                    color=0xffff00)
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
                    color=0x9acd32)
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
                    color=0x9acd32)
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
                            color=0x9acd32)
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
                            color=0x9acd32)
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
                        color=0x9acd32)
                    await interaction.response.send_message(embed=embedVar,
                                                            view=inView,
                                                            ephemeral=True)

                else:
                    embedVar = discord.Embed(
                        title=
                        f"Queue requested by {interaction.user.name}-nyan | {queueIndex} songs waiting to be played",
                        description='```' + queueList[0] + '```',
                        color=0x9acd32)
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
                    color=0x9acd32)
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
                    color=0x9acd32)
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
                    color=0x9acd32)
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
                        color=0x9acd32)
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
                        color=0x9acd32)
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
        view = View(timeout=750)
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
            color=0x9acd32)
        panelMsg = await ctx.respond(embed=embedVar, view=view)
        checkView = await view.wait()

        if checkView:
            embedEdit = discord.Embed(
                title=f"Song Panelnya sudah ditutup karena lama ngga dipakai..",
                description="Tulis /songpanel lagi kalau mau pakai yaa~",
                color=0x9acd32)
            await panelMsg.edit_original_message(embed=embedEdit, view=None)


@bot.slash_command(description='Disconnect the bot from the voice channel')
@commands.has_any_role('Encoder Magang', 'Owner')
async def songbye(ctx):
    if not ctx.voice_client:
        await ctx.respond(
            f'Ihh aneh deh {ctx.author.name}-nyan, watashi aja ngga di vc',
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

    await vc.disconnect()
    await ctx.respond(
        f'Hmph, watashi dipaksa keluar sama {ctx.author.name}-nyan, yauda deh sayonara'
    )


@bot.slash_command(description='Force skip the current song playing')
@commands.has_any_role('Encoder Magang', 'Owner')
async def songskip(ctx):
    if not ctx.voice_client:
        await ctx.respond(
            f'Ihh aneh deh {ctx.author.name}-nyan, watashi aja ngga di vc',
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

    setattr(vc, "loop", False)
    await ctx.respond(
        f'`{vc.track.title}` berhasil diskip paksa oleh {ctx.author.name}-nyan'
    )
    await vc.stop()


@bot.event
async def on_member_join(member):
    if member.bot:
        return

    await member.create_dm()
    await member.dm_channel.send(
        f'Halo {member.name}-nyan, watashi Setsuna yang akan mengurus anata di server baru, yoroshiku~'
    )


# @bot.event
# async def on_message(message):
#     if message.author == bot.user:
#       return

#     if "ajg" in message.content.lower() or "bgst" in message.content.lower():
#       await message.add_reaction('\U0001F974')
#       await message.channel.send(f'Kasar yaa, {message.author.name}-nyan')

#     await bot.process_commands(message)

# @bot.event
# async def on_message_edit(before, after):
#     if before.author == bot.user:
#         return

#     await before.add_reaction('\U0001F9D0')
#     await before.channel.send(
#         f'{before.author} abis edit msg nich di {before.channel.name}!\n\n'
#         f'Jadi awalnya gini :\n[ {before.content} ]\n\n'
#         f'Eh trus jadi gini :\n[ {after.content} ]'
#     )


@bot.event
async def on_raw_reaction_add(payload):
    if payload.member == bot.user:
        return

    guild = bot.get_guild(payload.guild_id)
    channel = guild.get_channel(payload.channel_id)
    if payload.message_id == ROLECLAIM:
        if payload.emoji.name == '🗿':
            role = discord.utils.get(guild.roles, name='Player')
            await payload.member.add_roles(role)
        elif payload.emoji.name == '💀':
            role = discord.utils.get(guild.roles, name='Hunter')
            await payload.member.add_roles(role)
        elif payload.emoji.name == '🤑':
            role = discord.utils.get(guild.roles, name='Shopkeeper')
            await payload.member.add_roles(role)
        elif payload.emoji.name == '🧑‍🌾':
            role = discord.utils.get(guild.roles, name='Villager')
            await payload.member.add_roles(role)
        elif payload.emoji.name == '👨‍🍳':
            role = discord.utils.get(guild.roles, name='Cook')
            await payload.member.add_roles(role)


@bot.event
async def on_raw_reaction_remove(payload):
    if payload.message_id != ROLECLAIM:
        return

    guild = bot.get_guild(payload.guild_id)
    member = guild.get_member(payload.user_id)

    if payload.emoji.name == '🗿':
        role = discord.utils.get(guild.roles, name='Player')
        await member.remove_roles(role)
    elif payload.emoji.name == '💀':
        role = discord.utils.get(guild.roles, name='Hunter')
        await member.remove_roles(role)
    elif payload.emoji.name == '🤑':
        role = discord.utils.get(guild.roles, name='Shopkeeper')
        await member.remove_roles(role)
    elif payload.emoji.name == '🧑‍🌾':
        role = discord.utils.get(guild.roles, name='Villager')
        await member.remove_roles(role)
    elif payload.emoji.name == '👨‍🍳':
        role = discord.utils.get(guild.roles, name='Cook')
        await member.remove_roles(role)


@bot.event
async def on_command_error(ctx, error):
    userFind = mycol.find_one({"userid": str(ctx.author.id)})
    if userFind == None:
        await ctx.channel.send(
            f'Neee {ctx.author.name}-nyan, yuk bisa yuk /regist dulu~')
        return

    if isinstance(error, commands.errors.CheckFailure):
        await ctx.channel.send(
            f'Gomenasai {ctx.message.author}-nyan, anata ngga punya hak buat nyuruh watashi pakai command itu...'
        )

    elif isinstance(error, commands.CommandOnCooldown):
        if error.retry_after > 3600:
            hourLeft = error.retry_after / 3600
            minLeft = (error.retry_after % 3600) / 60
            secLeft = (error.retry_after % 3600) % 60
            await ctx.channel.send(
                f'Command !{ctx.invoked_with} is still on cooldown...\nDuration Left : {int(hourLeft)} hour(s), {int(minLeft)} minute(s), and {int(secLeft)} second(s)'
            )

        elif error.retry_after > 60:
            minLeft = error.retry_after / 60
            secLeft = error.retry_after % 60
            await ctx.channel.send(
                f'Command !{ctx.invoked_with} is still on cooldown...\nDuration Left : {int(minLeft)} minute(s) and {int(secLeft)} second(s)'
            )

        else:
            await ctx.channel.send(
                f'Command !{ctx.invoked_with} is still on cooldown...\nDuration Left : {int(error.retry_after)} second(s)'
            )

    else:
        print(error)
        guild = bot.get_guild(GUILDID)
        channel = guild.get_channel(LOGCH)
        try:
            await channel.send(error)
        except:
            await channel.send('Error tapi kepanjangan bro...')


@bot.event
async def on_application_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.respond(
            f'Gomenasai {ctx.author.name}-nyan, anata ngga punya hak buat nyuruh watashi pakai command itu...'
        )
        return

    userFind = mycol.find_one({"userid": str(ctx.author.id)})
    if userFind == None:
        await ctx.respond(
            f'Neee {ctx.author.name}-nyan, yuk bisa yuk /regist dulu~',
            ephemeral=True)
        return

    elif isinstance(error, commands.CommandOnCooldown):
        if error.retry_after > 3600:
            hourLeft = error.retry_after / 3600
            minLeft = (error.retry_after % 3600) / 60
            secLeft = (error.retry_after % 3600) % 60
            await ctx.respond(
                f'Command is still on cooldown...\nDuration Left : {int(hourLeft)} hour(s), {int(minLeft)} minute(s), and {int(secLeft)} second(s)',
                ephemeral=True)

        elif error.retry_after > 60:
            minLeft = error.retry_after / 60
            secLeft = error.retry_after % 60
            await ctx.respond(
                f'Command is still on cooldown...\nDuration Left : {int(minLeft)} minute(s) and {int(secLeft)} second(s)',
                ephemeral=True)

        else:
            await ctx.respond(
                f'Command is still on cooldown...\nDuration Left : {int(error.retry_after)} second(s)',
                ephemeral=True)

    else:
        print(error)
        guild = bot.get_guild(GUILDID)
        channel = guild.get_channel(LOGCH)
        try:
            await channel.send(error)
        except:
            await channel.send('Error tapi kepanjangan bro...')


@bot.slash_command(
    name='gamblegold',
    description=
    'Gamble your gold with approximately 50/50 odds of getting double or losing all'
)
async def gold_gamble(ctx, number: Option(int, "Number to add",
                                          required=True)):
    if number <= 0:
        await ctx.respond(f'Neee anata ngga jelas deh, {ctx.author.name}-nyan',
                          ephemeral=True)
        return

    userFind = mycol.find_one({"userid": str(ctx.author.id)})
    if userFind == None:
        await ctx.respond(
            f'Neee {ctx.author.name}-nyan, yuk bisa yuk /regist dulu~',
            ephemeral=True)

    else:
        goldCount = userFind["gold"]
        if number > goldCount:
            await ctx.respond(
                f'Gold anata ngga cukup, {ctx.author.name}-nyan...',
                ephemeral=True)

        else:
            randValue = random.randint(0, 100)
            if randValue % 2 == 1:
                goldCount += number
                newvalues = {"$set": {"gold": goldCount}}
                mycol.update_one(userFind, newvalues)
                await ctx.respond(
                    f'Omedetou! Gold {ctx.author.name}-nyan menjadi {goldCount}',
                    ephemeral=True)

            else:
                goldCount -= number
                newvalues = {"$set": {"gold": goldCount}}
                mycol.update_one(userFind, newvalues)
                await ctx.respond(
                    f'Yahh kalah, gold {ctx.author.name}-nyan menjadi {goldCount}',
                    ephemeral=True)


@bot.slash_command(
    name='gambleplat',
    description=
    'Gamble your platina with approximately 50/50 odds of getting double or losing all'
)
async def platina_gamble(ctx, number: Option(int,
                                             "Number to gamble",
                                             required=True)):
    if number <= 0:
        await ctx.respond(f'Neee anata ngga jelas deh, {ctx.author.name}-nyan',
                          ephemeral=True)
        return

    userFind = mycol.find_one({"userid": str(ctx.author.id)})
    if userFind == None:
        await ctx.respond(
            f'Neee {ctx.author.name}-nyan, yuk bisa yuk /regist dulu~',
            ephemeral=True)

    else:
        platinaCount = userFind["platina"]
        if number > platinaCount:
            await ctx.respond(
                f'Platina anata ngga cukup, {ctx.author.name}-nyan...',
                ephemeral=True)

        else:
            randValue = random.randint(0, 100)
            if randValue % 2 == 1:
                platinaCount += number
                newvalues = {"$set": {"platina": platinaCount}}
                mycol.update_one(userFind, newvalues)
                await ctx.respond(
                    f'Omedetou! platina {ctx.author.name}-nyan menjadi {platinaCount}',
                    ephemeral=True)

            else:
                platinaCount -= number
                newvalues = {"$set": {"platina": platinaCount}}
                mycol.update_one(userFind, newvalues)
                await ctx.respond(
                    f'Yahh kalah, platina {ctx.author.name}-nyan menjadi {platinaCount}',
                    ephemeral=True)


# @bot.slash_command(name='resetcd', description='Reset cooldown of a command for self')
# @commands.has_any_role('Encoder Magang', 'Owner')
# async def reset_cd(ctx, command: Option(str, "Name of command to reset", required=True)):
#   await ctx.defer(ephemeral=True)
#   bot.get_application_command(command).reset_cooldown(ctx)
#   await ctx.respond(f'Cooldown command /{command} pada {ctx.author.name}-nyan berhasil direset!', ephemeral=True)


@bot.slash_command(
    name='resethunt',
    description=
    'Reset cooldown of /hunt command for chosen user or self (if not choose)')
@commands.has_any_role('Encoder Magang', 'Owner')
async def reset_hunt(ctx, member: Option(discord.Member,
                                         "The profile you want to check of",
                                         required=False,
                                         default=None)):
    await ctx.defer()
    if not member:
        member = ctx.author

    userFind = mycol.find_one({"userid": str(member.id)})
    if userFind == None:
        await ctx.respond(
            f'{member.name}-nyan belum terdaftar, watashi tidak bisa membuka profilenya',
            ephemeral=True)

    else:
        await ctx.respond(
            f"Cooldown command /hunt punya {member.name}-nyan berhasil direset!"
        )
        newvalues = {
            "$set": {
                "hunt": datetime.datetime(2021, 10, 24, 10, 0, 38, 917000)
            }
        }
        mycol.update_one(userFind, newvalues)


@bot.slash_command(
    name='resetdaily',
    description=
    'Reset cooldown of /dailymaze command for chosen user or self (if not choose)'
)
@commands.has_any_role('Encoder Magang', 'Owner')
async def reset_maze(ctx, member: Option(discord.Member,
                                         "The profile you want to check of",
                                         required=False,
                                         default=None)):
    await ctx.defer()
    if not member:
        member = ctx.author

    userFind = mycol.find_one({"userid": str(member.id)})
    if userFind == None:
        await ctx.respond(
            f'{member.name}-nyan belum terdaftar, watashi tidak bisa membuka profilenya',
            ephemeral=True)

    else:
        await ctx.respond(
            f"Cooldown command /dailymaze punya {member.name}-nyan berhasil direset!"
        )
        newvalues = {"$set": {"daily": "15/9/2022"}}
        mycol.update_one(userFind, newvalues)


@bot.slash_command(
    name='dailymaze',
    description='Play in daily minigame from level 1-7 with different prizes')
async def daily_dungeon(ctx, level: Option(int,
                                           "Level of difficulty (1-7)",
                                           required=True)):
    if level <= 0:
        await ctx.respond(f'Sumpa gajelas lu {ctx.author.name}-nyan',
                          ephemeral=True)
        return

    elif level > 7:
        await ctx.respond(
            f'Kegedean bro {ctx.author.name}-nyan, levelnya cuma 1-7',
            ephemeral=True)
        return

    userFind = mycol.find_one({"userid": str(ctx.author.id)})
    indoTz = pytz.timezone("Asia/Jakarta")
    nowDay = datetime.datetime.now(indoTz)
    # print(str(nowDay.hour) + '/' + str(nowDay.minute) + '/' + str(nowDay.second))
    currentDay = str(nowDay.day) + '/' + str(nowDay.month) + '/' + str(
        nowDay.year)

    if userFind == None:
        await ctx.respond(
            f'Neee {ctx.author.name}-nyan, yuk bisa yuk /regist dulu~',
            ephemeral=True)
        return

    if currentDay == userFind['daily']:
        await ctx.respond(
            f'Neee {ctx.author.name}-nyan, hari ini kan anata udah pake /dailymaze, besok lagi yaa~',
            ephemeral=True)
        return

    await ctx.defer()
    global row, col
    row = level * 2
    col = level * 2
    button1 = Button(label=' ',
                     style=discord.ButtonStyle.gray,
                     disabled=True,
                     row=0)
    buttonU = Button(emoji='⬆', style=discord.ButtonStyle.primary, row=0)
    button3 = Button(label=' ',
                     style=discord.ButtonStyle.gray,
                     disabled=True,
                     row=0)
    buttonL = Button(emoji='⬅️', style=discord.ButtonStyle.primary, row=1)
    button5 = Button(emoji='🕹️',
                     style=discord.ButtonStyle.green,
                     disabled=True,
                     row=1)
    buttonR = Button(emoji='➡️', style=discord.ButtonStyle.primary, row=1)
    button7 = Button(label=' ',
                     style=discord.ButtonStyle.gray,
                     disabled=True,
                     row=2)
    buttonD = Button(emoji="⬇️", style=discord.ButtonStyle.primary, row=2)
    button9 = Button(label=' ',
                     style=discord.ButtonStyle.gray,
                     disabled=True,
                     row=2)

    dgMap = [[0 for x in range(row)] for y in range(col)]
    arr = [[0 for x in range(row)] for y in range(col)]

    for x in range(row):
        for y in range(col):
            num = random.randint(-1, 0)
            dgMap[x][y] = num
            arr[x][y] = num

    dgMap[0][0] = 0
    dgMap[row - 1][col - 1] = 0
    arr[0][0] = 0
    arr[row - 1][col - 1] = 0

    while isPath(arr) is not True:
        for x in range(row):
            for y in range(col):
                num = random.randint(-1, 0)
                dgMap[x][y] = num
                arr[x][y] = num

        dgMap[0][0] = 0
        dgMap[row - 1][col - 1] = 0
        arr[0][0] = 0
        arr[row - 1][col - 1] = 0

    dungeonArea = [[0 for x in range(row)] for y in range(col)]

    for x in range(row):
        for y in range(col):
            if dgMap[x][y] == 0:
                dungeonArea[x][y] = '◻️'
            elif dgMap[x][y] == -1:
                dungeonArea[x][y] = '🔥'

    dungeonArea[0][0] = '😨'
    dungeonArea[row - 1][col - 1] = '🎁'
    xPos = 0
    yPos = 0

    # for x in range(row):
    #   print(dungeonArea[x])
    async def left_callback(interaction):
        if interaction.user.id != ctx.author.id:
            await interaction.response.send_message(
                f"Neeee, itu maze punya {ctx.author.name}-nyan, kalau mau main /dailymaze sendiri deh ya {interaction.user.name}-nyan~",
                ephemeral=True)
        else:
            nonlocal yPos, xPos
            if yPos - 1 == row - 1 and xPos == col - 1:
                dungeonArea[xPos][yPos] = '◻️'
                dungeonArea[row - 1][col - 1] = '😊'

                rtMap = ""
                for x in range(row):
                    if x > 0:
                        rtMap = rtMap + '\n'
                    for y in range(col):
                        rtMap = rtMap + dungeonArea[x][y]

                embedEdit = discord.Embed(
                    title=f"— Daily Maze —",
                    description="You've reached the prize!",
                    color=ctx.author.color)
                embedEdit.add_field(name="[ Map ]", value=rtMap, inline=False)
                embedEdit.set_footer(text="Resets daily at 00:00 WIB (GMT+7)")
                embedEdit.set_author(name=interaction.user.name,
                                     icon_url=interaction.user.avatar.url)
                await interaction.response.edit_message(
                    content=
                    f"Omedetou! {ctx.author.name}-nyan berhasil memenangkan {level*50} Gold dan mendapat {level*3} EXP dari Dungeon",
                    embed=embedEdit,
                    view=None)
                goldCount = userFind["gold"] + (level * 50)
                number = level * 3
                xpCount = userFind["exp"]
                levelCount = userFind["level"]
                if number < ((levelCount * 2) - xpCount):
                    xpCount += number
                    newvalues = {
                        "$set": {
                            "exp": xpCount,
                            "gold": goldCount,
                            "daily": currentDay
                        }
                    }

                else:
                    number -= ((levelCount * 2) - xpCount)
                    levelCount += 1

                    while number >= (levelCount * 2):
                        number -= (levelCount * 2)
                        levelCount += 1

                    xpCount = number
                    newvalues = {
                        "$set": {
                            "level": levelCount,
                            "exp": xpCount,
                            "gold": goldCount,
                            "daily": currentDay
                        }
                    }

                mycol.update_one(userFind, newvalues)
                view.stop()

            elif yPos > 0 and dungeonArea[xPos][yPos - 1] == '🔥':
                dungeonArea[xPos][yPos] = '💀'
                rtMap = ""
                for x in range(row):
                    if x > 0:
                        rtMap = rtMap + '\n'
                    for y in range(col):
                        rtMap = rtMap + dungeonArea[x][y]

                embedEdit = discord.Embed(
                    title=f"— Daily Maze —",
                    description="You've died... ( Cause : Running into fire )",
                    color=ctx.author.color)
                embedEdit.add_field(name="[ Map ]", value=rtMap, inline=False)
                embedEdit.set_footer(text="Resets daily at 00:00 WIB (GMT+7)")
                embedEdit.set_author(name=interaction.user.name,
                                     icon_url=interaction.user.avatar.url)
                await interaction.response.edit_message(
                    content=
                    f"Aduhh {ctx.author.name}-nyan, bisa-bisanya masuk ke api..",
                    embed=embedEdit,
                    view=None)
                newvalues = {"$set": {"daily": currentDay}}
                mycol.update_one(userFind, newvalues)
                view.stop()

            elif yPos > 0 and dungeonArea[xPos][yPos - 1] == '◻️':
                dungeonArea[xPos][yPos] = '◻️'
                yPos -= 1
                dungeonArea[xPos][yPos] = '😨'

                rtMap = ""
                for x in range(row):
                    if x > 0:
                        rtMap = rtMap + '\n'
                    for y in range(col):
                        rtMap = rtMap + dungeonArea[x][y]

                embedEdit = discord.Embed(
                    title=f"— Daily Maze —",
                    description=
                    "Travel to the prize using buttons rapidly without going into the fire",
                    color=ctx.author.color)
                embedEdit.add_field(name="[ Map ]", value=rtMap, inline=False)
                embedEdit.set_author(name=interaction.user.name,
                                     icon_url=interaction.user.avatar.url)
                await interaction.response.edit_message(embed=embedEdit)

            else:
                await interaction.response.defer()

    async def up_callback(interaction):
        if interaction.user.id != ctx.author.id:
            await interaction.response.send_message(
                f"Neeee, itu maze punya {ctx.author.name}-nyan, kalau mau main /dailymaze sendiri deh ya {interaction.user.name}-nyan~",
                ephemeral=True)
        else:
            nonlocal yPos, xPos
            if xPos - 1 == row - 1 and yPos == col - 1:
                dungeonArea[xPos][yPos] = '◻️'
                dungeonArea[row - 1][col - 1] = '😊'

                rtMap = ""
                for x in range(row):
                    if x > 0:
                        rtMap = rtMap + '\n'
                    for y in range(col):
                        rtMap = rtMap + dungeonArea[x][y]

                embedEdit = discord.Embed(
                    title=f"— Daily Maze —",
                    description="You've reached the prize!",
                    color=ctx.author.color)
                embedEdit.add_field(name="[ Map ]", value=rtMap, inline=False)
                embedEdit.set_footer(text="Resets daily at 00:00 WIB (GMT+7)")
                embedEdit.set_author(name=interaction.user.name,
                                     icon_url=interaction.user.avatar.url)
                await interaction.response.edit_message(
                    content=
                    f"Omedetou! {ctx.author.name}-nyan berhasil memenangkan {level*50} Gold dan mendapat {level*3} EXP dari Dungeon",
                    embed=embedEdit,
                    view=None)
                goldCount = userFind["gold"] + (level * 50)
                number = level * 3
                xpCount = userFind["exp"]
                levelCount = userFind["level"]
                if number < ((levelCount * 2) - xpCount):
                    xpCount += number
                    newvalues = {
                        "$set": {
                            "exp": xpCount,
                            "gold": goldCount,
                            "daily": currentDay
                        }
                    }

                else:
                    number -= ((levelCount * 2) - xpCount)
                    levelCount += 1

                    while number >= (levelCount * 2):
                        number -= (levelCount * 2)
                        levelCount += 1

                    xpCount = number
                    newvalues = {
                        "$set": {
                            "level": levelCount,
                            "exp": xpCount,
                            "gold": goldCount,
                            "daily": currentDay
                        }
                    }

                mycol.update_one(userFind, newvalues)
                view.stop()

            elif xPos > 0 and dungeonArea[xPos - 1][yPos] == '🔥':
                dungeonArea[xPos][yPos] = '💀'
                rtMap = ""
                for x in range(row):
                    if x > 0:
                        rtMap = rtMap + '\n'
                    for y in range(col):
                        rtMap = rtMap + dungeonArea[x][y]

                embedEdit = discord.Embed(
                    title=f"— Daily Maze —",
                    description="You've died... ( Cause : Running into fire )",
                    color=ctx.author.color)
                embedEdit.add_field(name="[ Map ]", value=rtMap, inline=False)
                embedEdit.set_footer(text="Resets daily at 00:00 WIB (GMT+7)")
                embedEdit.set_author(name=interaction.user.name,
                                     icon_url=interaction.user.avatar.url)
                await interaction.response.edit_message(
                    content=
                    f"Aduhh {ctx.author.name}-nyan, bisa-bisanya masuk ke api..",
                    embed=embedEdit,
                    view=None)
                newvalues = {"$set": {"daily": currentDay}}
                mycol.update_one(userFind, newvalues)
                view.stop()

            elif xPos > 0 and dungeonArea[xPos - 1][yPos] == '◻️':
                dungeonArea[xPos][yPos] = '◻️'
                xPos -= 1
                dungeonArea[xPos][yPos] = '😨'

                rtMap = ""
                for x in range(row):
                    if x > 0:
                        rtMap = rtMap + '\n'
                    for y in range(col):
                        rtMap = rtMap + dungeonArea[x][y]

                embedEdit = discord.Embed(
                    title=f"— Daily Maze —",
                    description=
                    "Travel to the prize using buttons rapidly without going into the fire",
                    color=ctx.author.color)
                embedEdit.add_field(name="[ Map ]", value=rtMap, inline=False)
                embedEdit.set_author(name=interaction.user.name,
                                     icon_url=interaction.user.avatar.url)
                await interaction.response.edit_message(embed=embedEdit)

            else:
                await interaction.response.defer()

    async def down_callback(interaction):
        if interaction.user.id != ctx.author.id:
            await interaction.response.send_message(
                f"Neeee, itu maze punya {ctx.author.name}-nyan, kalau mau main /dailymaze sendiri deh ya {interaction.user.name}-nyan~",
                ephemeral=True)
        else:
            nonlocal yPos, xPos
            if xPos + 1 == row - 1 and yPos == col - 1:
                dungeonArea[xPos][yPos] = '◻️'
                dungeonArea[row - 1][col - 1] = '😊'

                rtMap = ""
                for x in range(row):
                    if x > 0:
                        rtMap = rtMap + '\n'
                    for y in range(col):
                        rtMap = rtMap + dungeonArea[x][y]

                embedEdit = discord.Embed(
                    title=f"— Daily Maze —",
                    description="You've reached the prize!",
                    color=ctx.author.color)
                embedEdit.add_field(name="[ Map ]", value=rtMap, inline=False)
                embedEdit.set_footer(text="Resets daily at 00:00 WIB (GMT+7)")
                embedEdit.set_author(name=interaction.user.name,
                                     icon_url=interaction.user.avatar.url)
                await interaction.response.edit_message(
                    content=
                    f"Omedetou! {ctx.author.name}-nyan berhasil memenangkan {level*50} Gold dan mendapat {level*3} EXP dari Dungeon",
                    embed=embedEdit,
                    view=None)
                goldCount = userFind["gold"] + (level * 50)
                number = level * 3
                xpCount = userFind["exp"]
                levelCount = userFind["level"]
                if number < ((levelCount * 2) - xpCount):
                    xpCount += number
                    newvalues = {
                        "$set": {
                            "exp": xpCount,
                            "gold": goldCount,
                            "daily": currentDay
                        }
                    }

                else:
                    number -= ((levelCount * 2) - xpCount)
                    levelCount += 1

                    while number >= (levelCount * 2):
                        number -= (levelCount * 2)
                        levelCount += 1

                    xpCount = number
                    newvalues = {
                        "$set": {
                            "level": levelCount,
                            "exp": xpCount,
                            "gold": goldCount,
                            "daily": currentDay
                        }
                    }

                mycol.update_one(userFind, newvalues)
                view.stop()

            elif xPos < row - 1 and dungeonArea[xPos + 1][yPos] == '🔥':
                dungeonArea[xPos][yPos] = '💀'
                rtMap = ""
                for x in range(row):
                    if x > 0:
                        rtMap = rtMap + '\n'
                    for y in range(col):
                        rtMap = rtMap + dungeonArea[x][y]

                embedEdit = discord.Embed(
                    title=f"— Daily Maze —",
                    description="You've died... ( Cause : Running into fire )",
                    color=ctx.author.color)
                embedEdit.add_field(name="[ Map ]", value=rtMap, inline=False)
                embedEdit.set_footer(text="Resets daily at 00:00 WIB (GMT+7)")
                embedEdit.set_author(name=interaction.user.name,
                                     icon_url=interaction.user.avatar.url)
                await interaction.response.edit_message(
                    content=
                    f"Aduhh {ctx.author.name}-nyan, bisa-bisanya masuk ke api..",
                    embed=embedEdit,
                    view=None)
                newvalues = {"$set": {"daily": currentDay}}
                mycol.update_one(userFind, newvalues)
                view.stop()

            elif xPos < row - 1 and dungeonArea[xPos + 1][yPos] == '◻️':
                dungeonArea[xPos][yPos] = '◻️'
                xPos += 1
                dungeonArea[xPos][yPos] = '😨'

                rtMap = ""
                for x in range(row):
                    if x > 0:
                        rtMap = rtMap + '\n'
                    for y in range(col):
                        rtMap = rtMap + dungeonArea[x][y]

                embedEdit = discord.Embed(
                    title=f"— Daily Maze —",
                    description=
                    "Travel to the prize using buttons rapidly without going into the fire",
                    color=ctx.author.color)
                embedEdit.add_field(name="[ Map ]", value=rtMap, inline=False)
                embedEdit.set_author(name=interaction.user.name,
                                     icon_url=interaction.user.avatar.url)
                await interaction.response.edit_message(embed=embedEdit)

            else:
                await interaction.response.defer()

    async def right_callback(interaction):
        if interaction.user.id != ctx.author.id:
            await interaction.response.send_message(
                f"Neeee, itu maze punya {ctx.author.name}-nyan, kalau mau main /dailymaze sendiri deh ya {interaction.user.name}-nyan~",
                ephemeral=True)
        else:
            nonlocal yPos, xPos
            if yPos + 1 == row - 1 and xPos == col - 1:
                dungeonArea[xPos][yPos] = '◻️'
                dungeonArea[row - 1][col - 1] = '😊'

                rtMap = ""
                for x in range(row):
                    if x > 0:
                        rtMap = rtMap + '\n'
                    for y in range(col):
                        rtMap = rtMap + dungeonArea[x][y]

                embedEdit = discord.Embed(
                    title=f"— Daily Maze —",
                    description="You've reached the prize!",
                    color=ctx.author.color)
                embedEdit.add_field(name="[ Map ]", value=rtMap, inline=False)
                embedEdit.set_footer(text="Resets daily at 00:00 WIB (GMT+7)")
                embedEdit.set_author(name=interaction.user.name,
                                     icon_url=interaction.user.avatar.url)
                await interaction.response.edit_message(
                    content=
                    f"Omedetou! {ctx.author.name}-nyan berhasil memenangkan {level*50} Gold dan mendapat {level*3} EXP dari Dungeon",
                    embed=embedEdit,
                    view=None)
                goldCount = userFind["gold"] + (level * 50)
                number = level * 3
                xpCount = userFind["exp"]
                levelCount = userFind["level"]
                if number < ((levelCount * 2) - xpCount):
                    xpCount += number
                    newvalues = {
                        "$set": {
                            "exp": xpCount,
                            "gold": goldCount,
                            "daily": currentDay
                        }
                    }

                else:
                    number -= ((levelCount * 2) - xpCount)
                    levelCount += 1

                    while number >= (levelCount * 2):
                        number -= (levelCount * 2)
                        levelCount += 1

                    xpCount = number
                    newvalues = {
                        "$set": {
                            "level": levelCount,
                            "exp": xpCount,
                            "gold": goldCount,
                            "daily": currentDay
                        }
                    }

                mycol.update_one(userFind, newvalues)
                view.stop()

            elif yPos < row - 1 and dungeonArea[xPos][yPos + 1] == '🔥':
                dungeonArea[xPos][yPos] = '💀'
                rtMap = ""
                for x in range(row):
                    if x > 0:
                        rtMap = rtMap + '\n'
                    for y in range(col):
                        rtMap = rtMap + dungeonArea[x][y]

                embedEdit = discord.Embed(
                    title=f"— Daily Maze —",
                    description="You've died... ( Cause : Running into fire )",
                    color=ctx.author.color)
                embedEdit.add_field(name="[ Map ]", value=rtMap, inline=False)
                embedEdit.set_footer(text="Resets daily at 00:00 WIB (GMT+7)")
                embedEdit.set_author(name=interaction.user.name,
                                     icon_url=interaction.user.avatar.url)
                await interaction.response.edit_message(
                    content=
                    f"Aduhh {ctx.author.name}-nyan, bisa-bisanya masuk ke api..",
                    embed=embedEdit,
                    view=None)
                newvalues = {"$set": {"daily": currentDay}}
                mycol.update_one(userFind, newvalues)
                view.stop()

            elif yPos < row - 1 and dungeonArea[xPos][yPos + 1] == '◻️':
                dungeonArea[xPos][yPos] = '◻️'
                yPos += 1
                dungeonArea[xPos][yPos] = '😨'

                rtMap = ""
                for x in range(row):
                    if x > 0:
                        rtMap = rtMap + '\n'
                    for y in range(col):
                        rtMap = rtMap + dungeonArea[x][y]

                embedEdit = discord.Embed(
                    title=f"— Daily Maze —",
                    description=
                    "Travel to the prize using buttons rapidly without going into the fire",
                    color=ctx.author.color)
                embedEdit.add_field(name="[ Map ]", value=rtMap, inline=False)
                embedEdit.set_author(name=interaction.user.name,
                                     icon_url=interaction.user.avatar.url)
                await interaction.response.edit_message(embed=embedEdit)

            else:
                await interaction.response.defer()

    buttonU.callback = up_callback
    buttonL.callback = left_callback
    buttonR.callback = right_callback
    buttonD.callback = down_callback
    view = View(timeout=7)
    view.add_item(button1)
    view.add_item(buttonU)
    view.add_item(button3)
    view.add_item(buttonL)
    view.add_item(button5)
    view.add_item(buttonR)
    view.add_item(button7)
    view.add_item(buttonD)
    view.add_item(button9)

    firstMap = ""
    for x in range(row):
        if x > 0:
            firstMap = firstMap + '\n'
        for y in range(col):
            firstMap = firstMap + dungeonArea[x][y]

    embedVar = discord.Embed(
        title=f'— Daily Maze —',
        description=
        "Travel to the prize by using buttons rapidly without going into the fire",
        color=ctx.author.color)
    embedVar.add_field(name="[ Map ]", value=firstMap, inline=False)
    embedVar.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)
    dgMessage = await ctx.respond(embed=embedVar, view=view)
    checkView = await view.wait()

    if checkView:
        dungeonArea[xPos][yPos] = '💀'
        rtMap = ""
        for x in range(row):
            if x > 0:
                rtMap = rtMap + '\n'
            for y in range(col):
                rtMap = rtMap + dungeonArea[x][y]

        embedEdit = discord.Embed(
            title=f"— Daily Maze —",
            description=
            "You've died... ( Cause : Standing still for too long )",
            color=ctx.author.color)
        embedEdit.add_field(name="[ Map ]", value=rtMap, inline=False)
        embedEdit.set_footer(text="Resets daily at 00:00 WIB (GMT+7)")
        embedEdit.set_author(name=ctx.author.name,
                             icon_url=ctx.author.avatar.url)
        await dgMessage.edit(
            content=
            f"Yah {ctx.author.name}-nyan mati, kelamaan ga gerak sih anata..",
            embed=embedEdit,
            view=None)
        newvalues = {"$set": {"daily": currentDay}}
        mycol.update_one(userFind, newvalues)


@bot.slash_command(name='hunt',
                   description='Hunt for loots once per 10 minutes')
async def hunting(ctx):
    userFind = mycol.find_one({"userid": str(ctx.author.id)})

    if userFind == None:
        await ctx.respond(
            f'Neee {ctx.author.name}-nyan, yuk bisa yuk /regist dulu~',
            ephemeral=True)
        return

    now = datetime.datetime.now()
    then = userFind["hunt"]
    duration = now - then
    duration = int(duration.total_seconds())

    if duration < 600:
        duration = 600 - duration
        if duration > 60:
            minLeft = duration / 60
            secLeft = duration % 60
            embedVar = discord.Embed(
                title=
                f"Hunt Command for {ctx.author.name}-nyan is still on cooldown...",
                description=
                f'Duration Left : {int(minLeft)} minute(s) and {int(secLeft)} second(s)',
                color=0x808080)

        else:
            embedVar = discord.Embed(
                title=
                f"Hunt Command for {ctx.author.name}-nyan is still on cooldown...",
                description=f'Duration Left : {int(duration)} second(s)',
                color=0x808080)

        await ctx.respond(embed=embedVar, ephemeral=True)
        return

    await ctx.defer()
    randValue = random.randint(0, 100)
    d = datetime.datetime.strptime(str(datetime.datetime.now().isoformat()),
                                   "%Y-%m-%dT%H:%M:%S.%f")
    if randValue <= 10:
        embedVar = discord.Embed(
            title="Hunt Result by " + ctx.author.name,
            description=
            f'Waduh, {ctx.author.name}-nyan menemukan seorang loli yang tengah menari-nari dan malah menghabiskan waktunya memandanginya..',
            color=0x808080)
        loliGifs = [
            'https://cdn.discordapp.com/attachments/995337235211763722/1014927108633542656/loli30.gif',
            'https://cdn.discordapp.com/attachments/995337235211763722/1014933310612443246/loli29n.gif',
            'https://cdn.discordapp.com/attachments/995337235211763722/1014927109258498078/loli28.gif',
            'https://cdn.discordapp.com/attachments/995337235211763722/1014927109594038312/loli27.gif',
            'https://cdn.discordapp.com/attachments/995337235211763722/1014927109904404621/loli26.gif',
            'https://cdn.discordapp.com/attachments/995337235211763722/1014927110244139018/loli25.gif',
            'https://cdn.discordapp.com/attachments/995337235211763722/1014927110730694656/loli24.gif',
            'https://cdn.discordapp.com/attachments/995337235211763722/1014927111041069167/loli23.gif',
            'https://cdn.discordapp.com/attachments/995337235211763722/1014927111368212490/loli22.gif',
            'https://cdn.discordapp.com/attachments/995337235211763722/1014927111938646138/loli21.gif',
            'https://cdn.discordapp.com/attachments/995337235211763722/1014928168659988580/loli20.gif',
            'https://cdn.discordapp.com/attachments/995337235211763722/1014928169071026226/loli19.gif',
            'https://cdn.discordapp.com/attachments/995337235211763722/1014928169553375282/loli18.gif',
            'https://cdn.discordapp.com/attachments/995337235211763722/1014928169884717096/loli17.gif',
            'https://cdn.discordapp.com/attachments/995337235211763722/1014928170190897233/loli16.gif',
            'https://cdn.discordapp.com/attachments/995337235211763722/1014928170509668404/loli15.gif',
            'https://cdn.discordapp.com/attachments/995337235211763722/1014928170941698098/loli14.gif',
            'https://cdn.discordapp.com/attachments/995337235211763722/1014928171252072498/loli13.gif',
            'https://cdn.discordapp.com/attachments/995337235211763722/1014928171570831481/loli12.gif',
            'https://cdn.discordapp.com/attachments/995337235211763722/1014928171897978962/loli11.gif',
            'https://cdn.discordapp.com/attachments/995337235211763722/1014928666100240504/loli10.gif',
            'https://cdn.discordapp.com/attachments/995337235211763722/1014928666582597632/loli9.gif',
            'https://cdn.discordapp.com/attachments/995337235211763722/1014928666964275230/loli8.gif',
            'https://cdn.discordapp.com/attachments/995337235211763722/1014928667450810388/loli7.gif',
            'https://cdn.discordapp.com/attachments/995337235211763722/1014928667853467688/loli6.gif',
            'https://cdn.discordapp.com/attachments/995337235211763722/1014928668226768916/loli5.gif',
            'https://cdn.discordapp.com/attachments/995337235211763722/1014928668730073118/loli4.gif',
            'https://cdn.discordapp.com/attachments/995337235211763722/1014928669489254511/loli3.gif',
            'https://cdn.discordapp.com/attachments/995337235211763722/1014928670114193409/loli2.gif',
            'https://cdn.discordapp.com/attachments/995337235211763722/1014928669027860601/loli1.gif'
        ]

        gifLink = random.choice(loliGifs)
        embedVar.set_thumbnail(url=gifLink)
        newvalues = {"$set": {"hunt": d}}

    elif randValue <= 50:
        goldCount = userFind["gold"] + 20
        number = 2
        xpCount = userFind["exp"]
        levelCount = userFind["level"]
        if number < ((levelCount * 2) - xpCount):
            xpCount += number
            newvalues = {
                "$set": {
                    "exp": xpCount,
                    "gold": goldCount,
                    "hunt": d
                }
            }

        else:
            number -= ((levelCount * 2) - xpCount)
            levelCount += 1

            while number >= (levelCount * 2):
                number -= (levelCount * 2)
                levelCount += 1

            xpCount = number
            newvalues = {
                "$set": {
                    "level": levelCount,
                    "exp": xpCount,
                    "gold": goldCount,
                    "hunt": d
                }
            }

        embedVar = discord.Embed(
            title="Hunt Result by " + ctx.author.name,
            description=
            f'Agak miris, {ctx.author.name}-nyan hanya berhasil membunuh satu slime dan mendapat 20 Gold dan 2 EXP',
            color=0x32cd32)
        embedVar.set_thumbnail(
            url=
            "https://cdn.discordapp.com/attachments/995337235211763722/1014523086890078278/slimy.gif"
        )

    elif randValue <= 75:
        goldCount = userFind["gold"] + 40
        number = 4
        xpCount = userFind["exp"]
        levelCount = userFind["level"]
        if number < ((levelCount * 2) - xpCount):
            xpCount += number
            newvalues = {
                "$set": {
                    "exp": xpCount,
                    "gold": goldCount,
                    "hunt": d
                }
            }

        else:
            number -= ((levelCount * 2) - xpCount)
            levelCount += 1

            while number >= (levelCount * 2):
                number -= (levelCount * 2)
                levelCount += 1

            xpCount = number
            newvalues = {
                "$set": {
                    "level": levelCount,
                    "exp": xpCount,
                    "gold": goldCount,
                    "hunt": d
                }
            }

        embedVar = discord.Embed(
            title="Hunt Result by " + ctx.author.name,
            description=
            f'Walau tak seberapa, {ctx.author.name}-nyan setidaknya berhasil membunuh satu goblin dan mendapat 40 Gold dan 4 EXP',
            color=0x877a23)
        embedVar.set_thumbnail(
            url=
            "https://cdn.discordapp.com/attachments/995337235211763722/1014500269360414731/goblin.gif"
        )

    elif randValue <= 90:
        goldCount = userFind["gold"] + 70
        number = 6
        xpCount = userFind["exp"]
        levelCount = userFind["level"]
        if number < ((levelCount * 2) - xpCount):
            xpCount += number
            newvalues = {
                "$set": {
                    "exp": xpCount,
                    "gold": goldCount,
                    "hunt": d
                }
            }

        else:
            number -= ((levelCount * 2) - xpCount)
            levelCount += 1

            while number >= (levelCount * 2):
                number -= (levelCount * 2)
                levelCount += 1

            xpCount = number
            newvalues = {
                "$set": {
                    "level": levelCount,
                    "exp": xpCount,
                    "gold": goldCount,
                    "hunt": d
                }
            }

        embedVar = discord.Embed(
            title="Hunt Result by " + ctx.author.name,
            description=
            f'Sedikit beruntung, {ctx.author.name}-nyan berhasil membunuh satu skeleton dan mendapat 70 Gold dan 6 EXP',
            color=0x6699cc)
        embedVar.set_thumbnail(
            url=
            "https://cdn.discordapp.com/attachments/995337235211763722/1014513523910512720/skeleviolin.gif"
        )

    elif randValue <= 96:
        goldCount = userFind["gold"] + 100
        number = 10
        xpCount = userFind["exp"]
        levelCount = userFind["level"]
        if number < ((levelCount * 2) - xpCount):
            xpCount += number
            newvalues = {
                "$set": {
                    "exp": xpCount,
                    "gold": goldCount,
                    "hunt": d
                }
            }

        else:
            number -= ((levelCount * 2) - xpCount)
            levelCount += 1

            while number >= (levelCount * 2):
                number -= (levelCount * 2)
                levelCount += 1

            xpCount = number
            newvalues = {
                "$set": {
                    "level": levelCount,
                    "exp": xpCount,
                    "gold": goldCount,
                    "hunt": d
                }
            }

        embedVar = discord.Embed(
            title="Hunt Result by " + ctx.author.name,
            description=
            f'Berusaha lumayan keras, {ctx.author.name}-nyan akhirnya berhasil membunuh satu ogre dan mendapat 100 Gold dan 10 EXP',
            color=0xbdb369)
        embedVar.set_thumbnail(
            url=
            "https://cdn.discordapp.com/attachments/995337235211763722/1014922579745722408/shrekik.gif"
        )

    elif randValue <= 99:
        goldCount = userFind["gold"] + 200
        number = 14
        xpCount = userFind["exp"]
        levelCount = userFind["level"]
        if number < ((levelCount * 2) - xpCount):
            xpCount += number
            newvalues = {
                "$set": {
                    "exp": xpCount,
                    "gold": goldCount,
                    "hunt": d
                }
            }

        else:
            number -= ((levelCount * 2) - xpCount)
            levelCount += 1

            while number >= (levelCount * 2):
                number -= (levelCount * 2)
                levelCount += 1

            xpCount = number
            newvalues = {
                "$set": {
                    "level": levelCount,
                    "exp": xpCount,
                    "gold": goldCount,
                    "hunt": d
                }
            }

        embedVar = discord.Embed(
            title="Hunt Result by " + ctx.author.name,
            description=
            f'Wah ngeri, {ctx.author.name}-nyan dengan kerennya berhasil membunuh satu golem dan mendapat 200 Gold dan 14 EXP',
            color=0x9d00ff)
        embedVar.set_thumbnail(
            url=
            "https://cdn.discordapp.com/attachments/995337235211763722/1014523953764647014/golemm.gif"
        )

    elif randValue <= 100:
        goldCount = userFind["gold"] + 600
        number = 20
        xpCount = userFind["exp"]
        levelCount = userFind["level"]
        if number < ((levelCount * 2) - xpCount):
            xpCount += number
            newvalues = {
                "$set": {
                    "exp": xpCount,
                    "gold": goldCount,
                    "hunt": d
                }
            }

        else:
            number -= ((levelCount * 2) - xpCount)
            levelCount += 1

            while number >= (levelCount * 2):
                number -= (levelCount * 2)
                levelCount += 1

            xpCount = number
            newvalues = {
                "$set": {
                    "level": levelCount,
                    "exp": xpCount,
                    "gold": goldCount,
                    "hunt": d
                }
            }

        embedVar = discord.Embed(
            title="Hunt Result by " + ctx.author.name,
            description=
            f"JACKPOT!! {ctx.author.name}-nyan berhasil mengalahkan seekor naga api dan menjual kepalanya seharga 600 Gold dan 20 EXP",
            color=0xf73718)
        embedVar.set_thumbnail(
            url=
            "https://cdn.discordapp.com/attachments/995337235211763722/1014922986442211338/drago.gif"
        )

    embedVar.set_footer(text="Cooldown : 10 Minutes",
                        icon_url=ctx.author.avatar.url)
    await ctx.respond(embed=embedVar)
    mycol.update_one(userFind, newvalues)


@bot.slash_command(name='transfergold',
                   description='Transfer the entered number of gold to a user')
async def gold_transfer(ctx, number: Option(int,
                                            "Number of gold to transfer",
                                            required=True),
                        member: Option(discord.Member,
                                       "Who to transfer gold to",
                                       required=True)):
    await ctx.defer()
    if number <= 0:
        await ctx.respond(f'Neee anata ngga jelas deh, {ctx.author.name}-nyan',
                          ephemeral=True)
        return

    userFind = mycol.find_one({"userid": str(ctx.author.id)})
    if userFind == None:
        await ctx.respond(
            f'Neee {ctx.author.name}-nyan, yuk bisa yuk /regist dulu~',
            ephemeral=True)

    targetFind = mycol.find_one({"userid": str(member.id)})
    if targetFind == None:
        await ctx.respond(
            f'Neee {ctx.author.name}-nyan, {member.name}-nyan tuh blom regist, bisa yuk disuruh /regist dulu~',
            ephemeral=True)

    if ctx.user.id == member.id:
        await ctx.respond(
            f'Neee {ctx.author.name}-nyan, masa transfer ke diri sendiri sih {member.name}-nyan...',
            ephemeral=True)

    else:
        goldCount = userFind["gold"]
        if number > goldCount:
            await ctx.respond(
                f'Gold anata ngga cukup, {ctx.author.name}-nyan...',
                ephemeral=True)

        else:
            goldCount = userFind["gold"] - number
            newvalues = {"$set": {"gold": goldCount}}
            mycol.update_one(userFind, newvalues)
            goldCount = targetFind["gold"] + number
            newvalues = {"$set": {"gold": goldCount}}
            mycol.update_one(targetFind, newvalues)
            await ctx.respond(
                f'{ctx.author.name}-nyan berhasil memberikan {number} gold kepada {member.name}-nyan!'
            )


@bot.slash_command(name='transferplat',
                   description='Transfer the entered number of plat to a user')
async def plat_transfer(ctx, number: Option(int,
                                            "Number of gold to transfer",
                                            required=True),
                        member: Option(discord.Member,
                                       "Who to transfer gold to",
                                       required=True)):
    await ctx.defer()
    if number <= 0:
        await ctx.respond(f'Neee anata ngga jelas deh, {ctx.author.name}-nyan',
                          ephemeral=True)
        return

    userFind = mycol.find_one({"userid": str(ctx.author.id)})
    if userFind == None:
        await ctx.respond(
            f'Neee {ctx.author.name}-nyan, yuk bisa yuk /regist dulu~',
            ephemeral=True)

    targetFind = mycol.find_one({"userid": str(member.id)})
    if targetFind == None:
        await ctx.respond(
            f'Neee {ctx.author.name}-nyan, {member.name}-nyan tuh blom regist, bisa yuk disuruh /regist dulu~',
            ephemeral=True)

    if ctx.user.id == member.id:
        await ctx.respond(
            f'Neee {ctx.author.name}-nyan, masa transfer ke diri sendiri sih {member.name}-nyan...',
            ephemeral=True)

    else:
        platinaCount = userFind["platina"]
        if number > platinaCount:
            await ctx.respond(
                f'Platina anata ngga cukup, {ctx.author.name}-nyan...',
                ephemeral=True)

        else:
            platinaCount = userFind["platina"] - number
            newvalues = {"$set": {"platina": platinaCount}}
            mycol.update_one(userFind, newvalues)
            platinaCount = targetFind["platina"] + number
            newvalues = {"$set": {"platina": platinaCount}}
            mycol.update_one(targetFind, newvalues)
            await ctx.respond(
                f'{ctx.author.name}-nyan berhasil memberikan {number} platina kepada {member.name}-nyan!'
            )


@bot.slash_command(
    name='giveawaygold',
    description='Giveaway the entered number of gold to the fastest claimer')
async def gold_giveaway(ctx, number: Option(int,
                                            "Number to giveaway",
                                            required=True)):
    await ctx.defer()
    if number <= 0:
        await ctx.respond(f'Neee anata ngga jelas deh, {ctx.author.name}-nyan',
                          ephemeral=True)
        bot.get_application_command('giveawaygold').reset_cooldown(ctx)
        return

    userFind = mycol.find_one({"userid": str(ctx.author.id)})
    if userFind == None:
        await ctx.respond(
            f'Neee {ctx.author.name}-nyan, yuk bisa yuk /regist dulu~',
            ephemeral=True)
        bot.get_application_command('giveawaygold').reset_cooldown(ctx)

    else:
        goldCount = userFind["gold"]
        if number > goldCount:
            await ctx.respond(
                f'Gold anata ngga cukup, {ctx.author.name}-nyan...',
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
                        ctx.author.name + "-nyan",
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
                title=str(number) + " Gold Giveaway by " + ctx.author.name +
                "-nyan",
                description="Penekan tombol tercepat akan mendapatkannya!",
                color=0xffd700)
            embedVar.set_thumbnail(
                url=
                "https://i.ibb.co/BZPbJ6W/pngfind-com-gold-coins-png-37408.png"
            )
            await ctx.respond(embed=embedVar, view=view)


@bot.slash_command(
    name='giveawayplat',
    description='Giveaway the entered number of platina to the fastest claimer'
)
async def platina_giveaway(ctx, number: Option(int,
                                               "Number to giveaway",
                                               required=True)):
    await ctx.defer()
    if number <= 0:
        await ctx.respond(f'Neee anata ngga jelas deh, {ctx.author.name}-nyan',
                          ephemeral=True)
        bot.get_application_command('giveawaygold').reset_cooldown(ctx)
        return

    userFind = mycol.find_one({"userid": str(ctx.author.id)})
    if userFind == None:
        await ctx.respond(
            f'Neee {ctx.author.name}-nyan, yuk bisa yuk /regist dulu~',
            ephemeral=True)
        bot.get_application_command('giveawaygold').reset_cooldown(ctx)

    else:
        platinaCount = userFind["platina"]
        if number > platinaCount:
            await ctx.respond(
                f'Platina anata ngga cukup, {ctx.author.name}-nyan...',
                ephemeral=True)
            bot.get_application_command('giveawaygold').reset_cooldown(ctx)

        else:
            flag = True
            platinaCount = userFind["platina"] - number
            newvalues = {"$set": {"platina": platinaCount}}
            mycol.update_one(userFind, newvalues)
            buttons = Button(label="Claim Platina",
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
                        title=str(number) + " Platina Giveaway by " +
                        ctx.author.name + "-nyan",
                        description=
                        f">> Claimed by {interaction.user.name}-nyan",
                        color=0xffd700)
                    await interaction.response.edit_message(embed=embedEdit,
                                                            view=None)

                    nonlocal flag
                    if flag:
                        flag = False
                        platinaCount = userFind["platina"] + number
                        newvalues = {"$set": {"platina": platinaCount}}
                        mycol.update_one(userFind, newvalues)

            buttons.callback = button_callback
            view = View()
            view.add_item(buttons)

            embedVar = discord.Embed(
                title=str(number) + " Platina Giveaway by " + ctx.author.name +
                "-nyan",
                description="Penekan tombol tercepat akan mendapatkannya!",
                color=0xe5e4e2)
            embedVar.set_thumbnail(
                url=
                "https://i.ibb.co/F3rgw7r/kisspng-junk-silver-silver-coin-coin-collecting-5b2ecbbdd0c336-2118554315297934698551.png"
            )
            await ctx.respond(embed=embedVar, view=view)


@bot.slash_command(
    name='addgold',
    description='Add gold for the mentioned user (or to self if without mention)'
)
@commands.has_any_role('Encoder Magang', 'Owner')
async def gold_add(ctx, number: Option(int, "Number to add", required=True),
                   member: Option(discord.Member,
                                  "Who to add gold or self if empty",
                                  required=False,
                                  default=None)):
    await ctx.defer()
    if number <= 0:
        await ctx.respond(f'Neee anata ngga jelas deh, {ctx.author.name}-nyan',
                          ephemeral=True)
        return

    if not member:
        userID = ctx.author.id
    else:
        userID = member.id

    userFind = mycol.find_one({"userid": str(userID)})
    mentionUser = '<@' + str(userID) + '>'
    if userFind == None:
        await ctx.respond(
            f'{mentionUser}-nyan, /regist dulu yuk biar bisa ditambah goldnya')

    else:
        goldCount = userFind["gold"] + number
        newvalues = {"$set": {"gold": goldCount}}
        mycol.update_one(userFind, newvalues)
        await ctx.respond(
            f'Goldnya {mentionUser}-nyan berhasil ditambah menjadi {goldCount}'
        )


@bot.slash_command(
    name='reducegold',
    description=
    'Reduce gold for the mentioned user (or to self if without mention)')
@commands.has_any_role('Encoder Magang', 'Owner')
async def gold_reduce(ctx, number: Option(int,
                                          "Number to reduce",
                                          required=True),
                      member: Option(discord.Member,
                                     "Who to reduce gold or self if empty",
                                     required=False,
                                     default=None)):
    await ctx.defer()
    if number <= 0:
        await ctx.respond(f'Neee anata ngga jelas deh, {ctx.author.name}-nyan',
                          ephemeral=True)
        return

    if not member:
        userID = ctx.author.id
    else:
        userID = member.id

    userFind = mycol.find_one({"userid": str(userID)})
    mentionUser = '<@' + str(userID) + '>'
    if userFind == None:
        await ctx.respond(
            f'{mentionUser}-nyan belum terdaftar nih, /regist dulu yuk')

    else:
        goldCount = userFind["gold"]
        if goldCount == 0:
            await ctx.respond(
                f'Goldnya {mentionUser}-nyan sudah habis nih, apalagi yang mau dikurangi'
            )
        else:
            goldCount -= number
            if goldCount < 0:
                goldCount = 0
            newvalues = {"$set": {"gold": goldCount}}
            mycol.update_one(userFind, newvalues)
            await ctx.respond(
                f'Goldnya {mentionUser}-nyan berhasil dikurangi menjadi {goldCount}'
            )


@bot.slash_command(
    name='addplat',
    description=
    'Add platina for the mentioned user (or to self if without mention)')
@commands.has_any_role('Encoder Magang', 'Owner')
async def platina_add(ctx, number: Option(int, "Number to add", required=True),
                      member: Option(discord.Member,
                                     "Who to add platina or self if empty",
                                     required=False,
                                     default=None)):
    await ctx.defer()
    if number <= 0:
        await ctx.respond(f'Neee anata ngga jelas deh, {ctx.author.name}-nyan',
                          ephemeral=True)
        return

    if not member:
        userID = ctx.author.id
    else:
        userID = member.id

    userFind = mycol.find_one({"userid": str(userID)})
    mentionUser = '<@' + str(userID) + '>'
    if userFind == None:
        await ctx.respond(
            f'{mentionUser}-nyan belum terdaftar nih, /regist dulu yuk')

    else:
        platCount = userFind["platina"] + number
        newvalues = {"$set": {"platina": platCount}}
        mycol.update_one(userFind, newvalues)
        await ctx.respond(
            f'Platinanya {mentionUser}-nyan berhasil ditambah menjadi {platCount}'
        )


@bot.slash_command(
    name='reduceplat',
    description=
    'Reduce platina for the mentioned user (or to self if without mention)')
@commands.has_any_role('Encoder Magang', 'Owner')
async def platina_reduce(ctx, number: Option(int,
                                             "Number to reduce",
                                             required=True),
                         member: Option(
                             discord.Member,
                             "Who to reduce platina or self if empty",
                             required=False,
                             default=None)):
    await ctx.defer()
    if number <= 0:
        await ctx.respond(f'Neee anata ngga jelas deh, {ctx.author.name}-nyan',
                          ephemeral=True)
        return

    if not member:
        userID = ctx.author.id
    else:
        userID = member.id

    userFind = mycol.find_one({"userid": str(userID)})
    mentionUser = '<@' + str(userID) + '>'
    if userFind == None:
        await ctx.respond(
            f'{mentionUser}-nyan belum terdaftar nih, /regist dulu yuk')

    else:
        platCount = userFind["platina"]
        if platCount == 0:
            await ctx.respond(
                f'Platinanya {mentionUser}-nyan sudah habis nih, apalagi yang mau dikurangi'
            )
        else:
            platCount -= number
            if platCount < 0:
                platCount = 0
            newvalues = {"$set": {"platina": platCount}}
            mycol.update_one(userFind, newvalues)
            await ctx.respond(
                f'Platinanya {mentionUser}-nyan berhasil dikurangi menjadi {platCount}'
            )


@bot.slash_command(
    name='converttoplat',
    description='Convert gold to platina with the entered number ( 100 : 1 )')
async def convert_to_plat(ctx, number: Option(int,
                                              "Number of platina to get",
                                              required=True)):
    await ctx.defer(ephemeral=True)
    if number <= 0:
        await ctx.respond(f'Neee anata ngga jelas deh, {ctx.author.name}-nyan',
                          ephemeral=True)
        return

    userFind = mycol.find_one({"userid": str(ctx.author.id)})
    if userFind == None:
        await ctx.respond(
            f'{ctx.author.name}-nyan belum terdaftar nih, /regist dulu yuk',
            ephemeral=True)

    else:
        goldCount = userFind["gold"]
        platCount = userFind["platina"]
        if goldCount < (number * 100):
            await ctx.respond(
                f'Gold {ctx.author.name}-nyan tidak cukup buat dijadikan {number} Platina',
                ephemeral=True)
        else:
            goldCount -= (number * 100)
            platCount += number
            newvalues = {"$set": {"platina": platCount, "gold": goldCount}}
            mycol.update_one(userFind, newvalues)
            await ctx.respond(
                f'Convert berhasil, Platina {ctx.author.name}-nyan menjadi {platCount} dan goldnya menjadi {goldCount}',
                ephemeral=True)


@bot.slash_command(
    name='convertcstoplat',
    description=
    'Convert gold in Loraine to platina with the entered number ( 2000 : 1 )')
async def csconvert_to_plat(ctx, number: Option(int,
                                                "Number of platina to get",
                                                required=True)):
    await ctx.defer(ephemeral=True)
    if number <= 0:
        await ctx.respond(f'Neee anata ngga jelas deh, {ctx.author.name}-nyan',
                          ephemeral=True)
        return

    lclient = pymongo.MongoClient(LORENDB)
    lmydb = lclient["LoraineDB"]
    lmycol = lmydb["profilemodels"]
    luserFind = lmycol.find_one({"userID": str(ctx.author.id)})
    userFind = mycol.find_one({"userid": str(ctx.author.id)})
    if userFind == None:
        await ctx.respond(
            f'{ctx.author.name}-nyan belum terdaftar nih, /regist dulu yuk',
            ephemeral=True)

    elif luserFind == None:
        await ctx.respond(
            f'{ctx.author.name}-nyan belum terdaftar di loren nih, /register dulu atau minta role dulu deh..',
            ephemeral=True)

    else:
        goldCount = luserFind["userGold"]
        platCount = userFind["platina"]
        if goldCount < (number * 2000):
            await ctx.respond(
                f'Gold CS {ctx.author.name}-nyan cuma {goldCount}, mana cukup sih buat dijadikan {number} Platina',
                ephemeral=True)
        else:
            goldCount -= (number * 2000)
            platCount += number
            newvalues = {"$set": {"platina": platCount}}
            mycol.update_one(userFind, newvalues)
            newvalues = {"$set": {"userGold": goldCount}}
            lmycol.update_one(luserFind, newvalues)
            await ctx.respond(
                f'Convert berhasil, Platina {ctx.author.name}-nyan menjadi {platCount} dan gold CSnya menjadi {goldCount}',
                ephemeral=True)


@bot.slash_command(
    name='converttogold',
    description='Convert platina to gold with the entered number ( 1 : 100 )')
async def convert_to_gold(ctx, number: Option(int,
                                              "Number of platina to convert",
                                              required=True)):
    await ctx.defer(ephemeral=True)
    if number <= 0:
        await ctx.respond(f'Neee anata ngga jelas deh, {ctx.author.name}-nyan',
                          ephemeral=True)
        return

    userFind = mycol.find_one({"userid": str(ctx.author.id)})
    if userFind == None:
        await ctx.respond(
            f'{ctx.author.name}-nyan belum terdaftar nih, /regist dulu yuk',
            ephemeral=True)

    else:
        goldCount = userFind["gold"]
        platCount = userFind["platina"]
        if platCount < number:
            await ctx.respond(
                f'Platina {ctx.author.name}-nyan tidak cukup buat dijadikan {number*100} Gold',
                ephemeral=True)
        else:
            goldCount += (number * 100)
            platCount -= number
            newvalues = {"$set": {"platina": platCount, "gold": goldCount}}
            mycol.update_one(userFind, newvalues)
            await ctx.respond(
                f'Convert berhasil, Platina {ctx.author.name}-nyan menjadi {platCount} dan goldnya menjadi {goldCount}',
                ephemeral=True)


@bot.slash_command(
    name='addxp',
    description='Add exp for the mentioned user (or to self if without mention)'
)
@commands.has_any_role('Encoder Magang', 'Owner')
async def exp_add(ctx, number: Option(int, "Number to add", required=True),
                  member: Option(discord.Member,
                                 "Who to give xp or self if empty",
                                 required=False,
                                 default=None)):
    await ctx.defer()
    if number <= 0:
        await ctx.respond(f'Neee {ctx.author.name}-nyan, ngga jelas deh ih',
                          ephemeral=True)
        return

    if not member:
        userID = ctx.author.id
    else:
        userID = member.id

    userFind = mycol.find_one({"userid": str(userID)})
    mentionUser = '<@' + str(userID) + '>'
    if userFind == None:
        await ctx.respond(
            f'{mentionUser}-nyan belum terdaftar nih, /regist dulu yuk')

    else:
        xpCount = userFind["exp"]
        levelCount = userFind["level"]
        if number < ((levelCount * 2) - xpCount):
            xpCount += number
            newvalues = {"$set": {"exp": xpCount}}
            mycol.update_one(userFind, newvalues)
            await ctx.respond(
                f'Level {mentionUser}-nyan berhasil ditambah menjadi {levelCount} dengan EXP {xpCount}/{levelCount*2}'
            )

        else:
            number -= ((levelCount * 2) - xpCount)
            levelCount += 1

            while number >= (levelCount * 2):
                number -= (levelCount * 2)
                levelCount += 1

            xpCount = number
            newvalues = {"$set": {"level": levelCount, "exp": xpCount}}
            mycol.update_one(userFind, newvalues)
            await ctx.respond(
                f'Level {mentionUser}-nyan berhasil ditambah menjadi {levelCount} dengan EXP {xpCount}/{levelCount*2}'
            )


@bot.slash_command(
    name='rng',
    description='Generates a random number from 1 to the entered number')
async def random_number_generate(ctx, max: Option(int,
                                                  "Max range of rng",
                                                  required=True),
                                 count: Option(int,
                                               "Number of rolls wanted",
                                               required=False,
                                               default=1)):
    await ctx.defer()
    if max > 1 and count >= 1:
        rngStr = ""

        for n in range(count):
            randValue = random.randint(1, max)
            if n % 2 == 0:
                rngStr = rngStr + f"➳ {n+1}) [{randValue}]\n"

            else:
                rngStr = rngStr + f"➸ {n+1}) [{randValue}]\n"

        embedVar = discord.Embed(
            title=f"[ RNG Result ( 1 - {max} | {count}x ) ]",
            description=f"```{rngStr}```",
            color=ctx.user.color)
        embedVar.set_author(name=ctx.author.name,
                            icon_url=ctx.author.avatar.url)
        await ctx.respond(embed=embedVar)

    elif max <= 1:
        await ctx.respond(
            f'Neee {ctx.author.name}-nyan, yang bener dong masukkin angka maxnya. Masa maxnya {max} sih..',
            ephemeral=True)

    elif count < 1:
        await ctx.respond(
            f'Neee {ctx.author.name}-nyan, yang bener dong masukkin countnya. Masa countnya {count} sih..',
            ephemeral=True)


@bot.slash_command(name='help', description='Shows the guide to use Setsuna')
async def show_helpp(ctx):
    await ctx.defer(ephemeral=True)
    embedVar = discord.Embed(
        title=f"Yoroshiku {ctx.user.name}-nyan, watashi wa Setsuna desu!",
        description=
        "Buat pakai watashi tinggal ketik '/' di chat discord, lalu tekan tab yang ada gambar pfp watashinya, nanti keluar deh command-command yang bisa anata pakai!",
        color=ctx.user.color)
    embedVar.add_field(
        name=f"[ Additional Helps List ]",
        value='```' +
        '/songhelp\n↪ All about song commands and how to utilize it!\n' +
        '/anihelp\n↪ All about anime commands and collecting waifu/husbando!\n'
        + "/pokehelp\n↪ All about pokemon commands and catchin'em all!\n" +
        '/spyhelp\n↪ All about spygame and how to play it with nakama-tachi!\n'
        + '```',
        inline=False)
    await ctx.respond(embed=embedVar, ephemeral=True)


@bot.slash_command(name='songhelp',
                   description='Explains how to use song commands')
async def song_helpp(ctx):
    await ctx.defer(ephemeral=True)
    embedVar = discord.Embed(
        title=f"[ Setsuna's Song Commands Help ]",
        description=
        'Seluruh song commands yang terdapat pada watashi diawali dengan kata "song" dan dapat digunakan untuk mendengarkan lagu melalui discord voice channel maupun voice stage!\n',
        color=0x9acd32)
    embedVar.add_field(
        name=f"[ Song Commands List ]",
        value='```' +
        '/songinsert\n  ↪ Digunakan untuk memutar lagu atau menambahkan lagu ke dalam antrian. Masukkan dapat berupa link spotify album, spotify playlist, spotify song, youtube playlist, maupun youtube video. Bila bukan berupa link, maka Setsuna akan mengambil video pertama dari Youtube Search menggunakan keyword masukkan (Setsuna akan masuk ke voice channel pengguna command secara otomatis bila tidak sedang berada di vc)!\n'
        +
        '/songpanel\n  ↪ Berisi berbagai tombol yang dapat digunakan untuk membantu dalam mendengarkan lagu, yakni Resume, Pause, Skip, Loop, Shuffle, dan Disconnect (hanya bila ada satu orang saja di dalam VC atau Setsuna tidak sedang melakukan apa-apa). Selain itu, juga bisa digunakan untuk mengecek lagu yang sedang diputar serta antrian yang menunggu!\n'
        + '```',
        inline=False)
    await ctx.respond(embed=embedVar, ephemeral=True)


@bot.slash_command(name='anihelp',
                   description='Explains how to use anicommands')
async def ani_helpp(ctx):
    await ctx.defer(ephemeral=True)
    embedVar = discord.Embed(
        title=f"[ Setsuna's AniCommands Help ]",
        description=
        'AniCommands pada Setsuna digunakan untuk anata-tachi para manusia yang ingin mengoleksi karakter anime 2D!\n',
        color=0xff69b4)
    embedVar.add_field(
        name=f"[ AniCommands List ]",
        value='```' +
        '/anigacha\n  ↪ Dimana semuanya bermula, tempat anata mendapatkan waifu/husbando dengan mengorbankan 1 Platina saja. Terdiri dari pilihan Male dan Female, dengan hanya satu sentuhan pada tombol, anata akan mendapatkannya!\n'
        +
        '/anifav\n  ↪ Memasangkan karakter anime yang dimiliki pada kolom "Favorite Anime Character" untuk membanggakannya!\n'
        +
        '/anidel\n  ↪ Menghapus sejumlah karakter anime yang dimiliki dari inventory jika diinginkan.\n'
        +
        '/anigive\n  ↪ Memberikan sejumlah karakter anime yang dimiliki dari inventory kepada orang yang dimention secara cuma-cuma.\n'
        +
        '/anitrade\n  ↪ Membuka trading board dengan orang yang dimention untuk saling bertukar koleksi anime.\n'
        + '```',
        inline=False)
    await ctx.respond(embed=embedVar, ephemeral=True)


@bot.slash_command(name='pokehelp',
                   description='Explains how to use pokecommands')
async def poke_helpp(ctx):
    await ctx.defer(ephemeral=True)
    embedVar = discord.Embed(
        title=f"[ Setsuna's PokeCommands Help ]",
        description=
        'PokeCommands hadir di Setsuna bagi anata-tachi para penggemar pokemon yang ingin menangkap, mengoleksi, mempelajari, melatih, dan juga berduel dengan pokemon kalian\n',
        color=0xee1515)
    embedVar.add_field(
        name=f"[ PokeCommands List ]",
        value='```' +
        '/pokecatch\n  ↪ Awal dari perjalanan pokemon anata, tempat anata menangkap pokemon dengan bermodalkan 1 platina. Terdiri dari Rarity Basic dengan chance 67%, Advanced dengan chance 25%, Epic dengan chance 7%, dan Legendary dengan chance 1% (Gen 1 - 5)\n'
        +
        '/pokeinfo\n  ↪ Digunakan untuk mengecek atau mempelajari tentang suatu pokemon yang sudah tersedia di /pokecatch!\n'
        +
        '/pokepartner\n  ↪ Digunakan untuk mengecek atau mengganti partner pokemon battle anata secara diam-diam.\n'
        +
        '/pokeduel\n  ↪ Melakukan matchmaking dan mencari lawan untuk berduel menggunakan pokemon satu sama lain. Pokemon Duel pada bot Setsuna agak berbeda dimana terdapat 6 tipe Move yang dapat dilakukan dalam setiap turn player\n'
        + '```',
        inline=False)
    embedVar.add_field(
        name=f"[ PokeDuel Move List ]",
        value='```' +
        '➤ Attack : Menyerang pokemon lawan dengan 100% status Atk dan dikurangi oleh status Def lawan ( Terpengaruh oleh Type Effectivity )\n'
        +
        '➤ Special : Menyerang pokemon lawan dengan 100% status Sp. Atk dan dikurangi oleh status Sp. Def lawan ( Terpengaruh oleh Type Effectivity )\n'
        +
        '➤ Alt. Attack : Menyerang pokemon lawan dengan 65% status Atk dan dikurangi oleh status Def lawan ( Tidak terpengaruh oleh Type Effectivity )\n'
        +
        '➤ Alt. Special : Menyerang pokemon lawan dengan 65% status Sp. Atk dan dikurangi oleh status Sp. Def lawan ( Tidak terpengaruh oleh Type Effectivity )\n'
        + '➤ Boost Atk : Meningkatkan status Atk pokemon sebanyak 1 stage\n'
        '➤ Boost Atk : Meningkatkan status Sp. Atk pokemon sebanyak 1 stage\n'
        + '```',
        inline=False)
    await ctx.respond(embed=embedVar, ephemeral=True)


@bot.slash_command(name='spyhelp', description='Explains how to play SpyGame')
async def spy_helpp(ctx):
    await ctx.defer(ephemeral=True)
    embedVar = discord.Embed(
        title=f"[ Setsuna's SpyGame Help ]",
        description=
        'SpyGame merupakan adaptasi dari SpyFall yang di bawa ke Setsuna untuk dimainkan oleh minimal 3 orang! Dapat dimainkan dengan menggunakan command /spygame\n',
        color=0x330066)
    embedVar.add_field(
        name=f"[ How To Play ]",
        value='```' +
        '1) Setelah permainan dimulai, para pemain akan mendapatkan rolenya masing-masing secara random. 1 Pemain akan menjadi Spy dan sisanya menjadi Citizen\n2) Akan diberikan durasi waktu tergantung dari jumlah pemain dan para pemain dapat saling bertanya jawab sesuai dengan giliran yang diberikan. Pemain akan bergantian sesuai giliran menunjuk satu orang lain dan memberikannya satu pertanyaan yang berhubungan dengan lokasi. Ini akan dilakukan hingga waktu habis atau voting dimulai secara paksa\n3) Tombol "Start Vote" dapat ditekan apabila sudah merasa yakin dan apabila kuota tercukupi maka permainan akan langsung memasuki babak Voting\n4) Pada babak voting, setiap pemain diberi kesempatan untuk memasang satu vote terhadap satu orang pilihannya secara anonymous dan menebak siapa spynya berdasarkan tanya jawab\n5) Kemudian Spy akan diberi kesempatan untuk memilih lokasi dari pilihan yang ada dan barulah diumumkan hasil permainannya.'
        + '```',
        inline=False)
    embedVar.add_field(
        name=f"[ Roles ]",
        value='```' +
        '➤ Citizen : Seluruh citizen dalam satu game akan mendapatkan lokasi pertemuan yang sama dan harus melindunginya dari Spy. Tugas dari Citizen adalah mencari tahu siapa Spynya tanpa membongkar lokasi pertemuan mereka melalui serangkaian tanya jawab dengan hati-hati.\n'
        +
        '➤ Spy : Hanya ada 1 Spy dalam suatu game yang tidak mendapatkan lokasi. Tugasnya adalah mencari tahu lokasi pertemuan para Citizen melalui serangkaian tanya jawab sambil membaur dengan mereka tanpa membongkar kedoknya sendiri\n'
        + '```',
        inline=True)
    embedVar.add_field(
        name=f"[ Outcomes ]",
        value='```' +
        '➤ Citizens Win\n  ↪ Spy tertangkap dan lokasi gagal ditebak oleh Spy\n'
        +
        '➤ Spy Win\n  ↪ Lokasi berhasil ditebak oleh spy dan spy tidak tertangkap\n'
        +
        '➤ Draw\n  ↪ Lokasi berhasil ditebak oleh spy namun spy tertangkap / Lokasi gagal ditebak oleh spy dan spy tidak tertangkap\n'
        + '```',
        inline=True)
    await ctx.respond(embed=embedVar, ephemeral=True)


@bot.slash_command(name='diss', description='Disses a target')
@commands.has_any_role('Encoder Magang', 'Owner')
async def diss_target(ctx, member: Option(discord.Member,
                                          "Member to diss",
                                          required=True)):
    dissLines = [
        'Cupu bgt si', 'Diem ya lemah', 'Sini gelud penakut',
        'Gausah sok jago', 'Janji ga nangis dek?', 'Belajar dulu sana'
    ]

    dissString = random.choice(dissLines)
    await ctx.respond(f'Oi {member.name}, {dissString}')


@bot.slash_command(name='rps', description='Battle RPS against a target')
async def rps_battle(ctx, member: Option(discord.Member,
                                         "Member to diss",
                                         required=True)):
    if member.bot:
        await ctx.respond(
            f'Masa nantang bewan sama bot sih {ctx.author.name}-nyan, aneh banget deh',
            ephemeral=True)
        return

    if member.id == ctx.author.id:
        await ctx.respond(
            f'Masa battle sama diri sendiri sih {ctx.author.name}-nyan, aneh banget deh',
            ephemeral=True)
        return

    player1 = "kosong"
    player2 = "kosong"
    select = Select(placeholder="Choose your hand!!",
                    options=[
                        discord.SelectOption(
                            label="The Resilient Rock",
                            emoji="🪨",
                            value="r",
                            description="Rock blunts Scissors"),
                        discord.SelectOption(label="The Purposeful Paper",
                                             emoji="📄",
                                             value="p",
                                             description="Paper wraps Rock"),
                        discord.SelectOption(label="The Sharp Scissors",
                                             emoji="✂️",
                                             value="s",
                                             description="Scissors cut Paper")
                    ])

    async def rps_callback(interaction):
        nonlocal player1, player2
        if interaction.user.id == member.id:
            if select.values[0] == "r":
                player2 = '🪨'
                await interaction.response.send_message(
                    f"{interaction.user.name}-nyan, anata telah memutuskan untuk memilih 🪨",
                    ephemeral=True)

            elif select.values[0] == "p":
                player2 = '📄'
                await interaction.response.send_message(
                    f"{interaction.user.name}-nyan, anata telah memutuskan untuk memilih 📄",
                    ephemeral=True)

            elif select.values[0] == "s":
                player2 = '✂️'
                await interaction.response.send_message(
                    f"{interaction.user.name}-nyan, anata telah memutuskan untuk memilih ✂️",
                    ephemeral=True)

            if player1 == "kosong":
                mentionUser = '<@' + str(ctx.author.id) + '>'
                await interaction.followup.send(
                    f"{interaction.user.name}-nyan telah menentukan pilihannya, yuk dipilih yuk cepat {mentionUser}-nyan"
                )

            else:
                await interaction.followup.send(
                    f"{interaction.user.name}-nyan telah menentukan pilihannya!"
                )

        elif interaction.user.id == ctx.author.id:
            if select.values[0] == "r":
                player1 = '🪨'
                await interaction.response.send_message(
                    f"{interaction.user.name}-nyan, anata telah memutuskan untuk memilih 🪨",
                    ephemeral=True)

            elif select.values[0] == "p":
                player1 = '📄'
                await interaction.response.send_message(
                    f"{interaction.user.name}-nyan, anata telah memutuskan untuk memilih 📄",
                    ephemeral=True)

            elif select.values[0] == "s":
                player1 = '✂️'
                await interaction.response.send_message(
                    f"{interaction.user.name}-nyan, anata telah memutuskan untuk memilih ✂️",
                    ephemeral=True)

            if player2 == "kosong":
                mentionUser = '<@' + str(member.id) + '>'
                await interaction.followup.send(
                    f"{interaction.user.name}-nyan telah menentukan pilihannya, yuk dipilih yuk cepat {mentionUser}-nyan"
                )

            else:
                await interaction.followup.send(
                    f"{interaction.user.name}-nyan telah menentukan pilihannya!"
                )

        else:
            await interaction.response.send_message(
                f"Kamu kan ngga ikut gamenya {interaction.user.name}-nyan, bikin game sendiri aja kalau mau main yaa",
                ephemeral=True)
            return

        if player1 != "kosong" and player2 != "kosong":
            if player1 == player2:
                embedEdit = discord.Embed(
                    title=
                    f"{ctx.author.name} ({player1}) VS {member.name} ({player2})",
                    description=f"It's a tie!",
                    color=0xadd8e6)
                embedEdit.set_image(
                    url=
                    'https://c.tenor.com/wyfhYqF1tJIAAAAM/mark-wahlberg-wahlberg.gif'
                )
                await rpsMessage.edit_original_message(embed=embedEdit,
                                                       view=None)
                await rpsMessage.followup.send(
                    f"Nampaknya terjadi tie game minna-san!")
                view.stop()
                return

            else:
                if player1 == '🪨':
                    if player2 == '📄':
                        winner = member
                    elif player2 == '✂️':
                        winner = ctx.author

                elif player1 == '📄':
                    if player2 == '🪨':
                        winner = ctx.author
                    elif player2 == '✂️':
                        winner = member

                if player1 == '✂️':
                    if player2 == '📄':
                        winner = ctx.author
                    elif player2 == '🪨':
                        winner = member

                embedEdit = discord.Embed(
                    title=
                    f"{ctx.author.name} ({player1}) VS {member.name} ({player2})",
                    description=f"{winner.name} wins!",
                    color=0xf73718)
                embedEdit.set_image(url=winner.avatar.url)
                await rpsMessage.edit_original_message(embed=embedEdit,
                                                       view=None)
                await rpsMessage.followup.send(
                    f"Omedetou, {winner.name}-nyan berhasil menjadi pemenang!")
                view.stop()

    select.callback = rps_callback
    view = View(timeout=600)
    view.add_item(select)

    embedVar = discord.Embed(title="Rock, Paper, Scissors Battle",
                             description=f"{ctx.author.name} VS {member.name}",
                             color=0xf73718)
    embedVar.set_image(
        url=
        'https://cdn.pixabay.com/photo/2013/07/12/15/02/fingers-149296__340.png'
    )
    rpsMessage = await ctx.respond(embed=embedVar, view=view)
    checkView = await view.wait()

    if checkView:
        embedEdit = discord.Embed(
            title=f"Rock, Paper, Scissors Battle ended",
            description=
            "Kelamaan ihh, masa dah 5 menit ada yang blom milih juga",
            color=0x808080)
        await rpsMessage.edit_original_message(embed=embedEdit, view=None)
        if player1 == "kosong" and player2 == "kosong":
            await rpsMessage.followup.send(
                f"Hmph, battlenya watashi tutup deh, {ctx.author.name}-nyan sama {member.name}-nyan pada belum milih sih, lama banget..",
                ephemeral=True)
        elif player1 == "kosong":
            await rpsMessage.followup.send(
                f"Hmph, battlenya watashi tutup deh, {ctx.author.name}-nyan belum milih sih, lama banget. Kasian tuh {member.name} udah nungguin..",
                ephemeral=True)
        elif player2 == "kosong":
            await rpsMessage.followup.send(
                f"Hmph, battlenya watashi tutup deh, {member.name}-nyan belum milih sih, lama banget. Kasian tuh {ctx.author.name} udah nungguin..",
                ephemeral=True)


@bot.slash_command(name='blackjack',
                   description='Play blackjack against a CPU Dealer')
async def play_blackjack(ctx, number: Option(int,
                                             "Number of gold to bet",
                                             required=True)):
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


@bot.slash_command(name='spygame',
                   description='Play a spyfall game with at least 3 players')
async def spyfall_game(ctx):
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
            tempPlayer = await bot.fetch_user(int(player))
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

        embedEdit = discord.Embed(
            title=f"[ SpyGame ]",
            description=
            f"Game telah dimulai! Silahkan saling menanyakan pertanyaan bergantian sesuai dengan urutan member yang telah disediakan. Waktu sebelum babak voting : {playerCount*3} Menit, bisa juga memulai lebih cepat dengan menekan tombol di bawah",
            color=0x330066)
        embedEdit.add_field(name=f"Player List | Count : {playerCount}",
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
    panelMsg = await ctx.respond(embed=embedVar, view=view)
    checkView = await view.wait()

    if checkView:
        embedEdit = discord.Embed(
            title=f"Game telah ditutup karena tak kunjung distart",
            description="Watashi udah nunggu lama tapi belum distart juga..",
            color=0x330066)
        await panelMsg.edit_original_message(embed=embedEdit, view=None)


@bot.slash_command(
    name='timer',
    description='Create a button that auto end after a set period of time')
async def timer_test(ctx, timer: Option(int, "Seconds to wait",
                                        required=True)):
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
        time = time + 1
        # print(time)
        if time == timer:
            embedEnd = discord.Embed(title=f"Timer ditutup karena waktu habis",
                                     description="Sudah abis kak",
                                     color=0xffff00)
            await timerMsg.edit_original_message(embed=embedEnd, view=None)
            break
        if flag:
            break


@bot.slash_command(name='pokeinfo',
                   description='Check the information of a specific pokemon')
async def pokemon_info(ctx,
                       poke: Option(str,
                                    "The name of the pokemon to check for",
                                    required=True)):
    pokeFind = mycol.find_one({"func": "pokedb"})
    pokeBasic = pokeFind["basic"]
    pokeElite = pokeFind["elite"]
    pokeEpic = pokeFind["epic"]
    pokeLegend = pokeFind["legend"]
    poke = poke[0].upper() + poke[1:].lower()

    if poke.lower() == 'porygon-z':
        poke = 'Porygon-Z'

    if poke in pokeBasic or poke in pokeElite or poke in pokeEpic or poke in pokeLegend:
        response = urllib2.urlopen(
            f'https://some-random-api.ml/pokedex?pokemon={poke.lower()}')
        data = json.loads(response.read())
        embedVar = discord.Embed(
            title=f"PokeInfo!",
            description=f'{poke} | ID : {str(data["id"])}',
            color=0xee1515)
        eleString = ', '.join(data["type"])
        evoString = ', '.join(data["family"]["evolutionLine"])
        if len(evoString) == 0:
            evoString = poke

        if poke in pokeBasic:
            rarityChk = 'Basic'

        elif poke in pokeElite:
            rarityChk = 'Advanced'

        elif poke in pokeEpic:
            rarityChk = 'Epic'

        elif poke in pokeLegend:
            rarityChk = 'Legendary'

        embedVar.add_field(name=f"[ General ]",
                           value='```' + f'Type     : {eleString}\n' +
                           f'Rarity   : {rarityChk}\n' +
                           f'Gen      : {data["generation"]}\n' +
                           f'Species  : {data["species"][0]}\n' +
                           f'Height   : {data["height"]}\n' +
                           f'Weight   : {data["weight"]}\n' + '```',
                           inline=True)

        embedVar.add_field(
            name=f"[ Stats (Lv. 1) ]",
            value='```' + f'HP       : {str(data["stats"]["hp"])}\n'
            f'Atk      : {str(data["stats"]["attack"])}\n' +
            f'Sp. Atk  : {str(data["stats"]["sp_atk"])}\n' +
            f'Def      : {str(data["stats"]["defense"])}\n' +
            f'Sp. Def  : {str(data["stats"]["sp_def"])}\n' +
            f'Speed    : {str(data["stats"]["speed"])}\n' + '```',
            inline=True)

        embedVar.add_field(name=f"[ Evolutionary ]",
                           value='```' +
                           f'Stage    : {data["family"]["evolutionStage"]}\n' +
                           f'EvoPath  : {evoString}\n' + '```',
                           inline=False)
        embedVar.set_thumbnail(url=data['sprites']['animated'])
        embedVar.set_footer(text=data["description"],
                            icon_url=data["sprites"]["normal"])
        await ctx.respond(embed=embedVar)

    else:
        await ctx.respond(
            "Pokemon yang anata cari tidak / belum terdaftar, coba dicek lagi yah..",
            ephemeral=True)


@bot.slash_command(name='poketype',
                   description='Open a chart to see pokemon typing')
async def pokemochart(ctx):
    embedVar = discord.Embed(title=f"[ PokeType Chart ]",
                             description=f' ▼ ▼ ▼ ▼ ▼ ▼ ▼ ▼ ▼ ▼ ▼ ▼ ▼ ▼ ▼ ▼ ▼',
                             color=0xee1515)
    embedVar.set_image(
        url=
        'https://cdn.discordapp.com/attachments/995337235211763722/1019540327507435560/pokechart.png'
    )
    await ctx.respond(embed=embedVar)


@bot.slash_command(
    name='pokecatch',
    description='Catch a random pokemon from the wild for 1 Platina')
async def poke_gacha(ctx):
    firstFind = mycol.find_one({"userid": str(ctx.author.id)})
    if firstFind == None:
        await ctx.respond(
            f'Neee {ctx.author.name}-nyan, yuk bisa yuk /regist dulu~',
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
                            f'https://some-random-api.ml/pokedex?pokemon={result.lower()}'
                        )
                    except:
                        guild = bot.get_guild(GUILDID)
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
                                            f'https://some-random-api.ml/pokedex?pokemon={evolved.lower()}'
                                        )
                                    except:
                                        guild = bot.get_guild(GUILDID)
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
                                    f'https://some-random-api.ml/pokedex?pokemon={evolved.lower()}'
                                )
                            except:
                                guild = bot.get_guild(GUILDID)
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
                                            f'https://some-random-api.ml/pokedex?pokemon={nexted.lower()}'
                                        )
                                    except:
                                        guild = bot.get_guild(GUILDID)
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
        gachaMsg = await ctx.respond(embed=embedVar, view=view)
        checkView = await view.wait()

        if checkView:
            embedEdit = discord.Embed(
                title=f"Thank you for using pokecatch!",
                description="You can type /pokecatch to do more gachas",
                color=0xee1515)
            await gachaMsg.edit_original_message(embed=embedEdit, view=None)


@bot.slash_command(
    name='pokepity',
    description='Check how many catches left for you to get pity at /pokecatch'
)
async def pokemon_pity(ctx):
    userFind = mycol.find_one({"userid": str(ctx.author.id)})
    if userFind == None:
        await ctx.respond(
            f'Neee {ctx.author.name}-nyan, yuk /regist dulu yuk baru liat pokemon..',
            ephemeral=True)
        return

    epicPity = userFind["epicpity"]
    if epicPity > 30:
        epicPity = 30

    legendPity = userFind["legendpity"]
    if legendPity > 100:
        legendPity = 100

    embedVar = discord.Embed(
        title=f"〘 {ctx.user.name}-nyan's PokeCatch Pity 〙",
        description=
        f"- Epic : {30 - epicPity} catch(es) left!\n- Legendary : {100 - legendPity} catch(es) left!",
        color=0xee1515)
    embedVar.set_footer(text="— May good luck bless you in /pokecatch!",
                        icon_url=ctx.author.avatar.url)
    await ctx.respond(embed=embedVar)


@bot.slash_command(
    name='pokepartner',
    description=
    'Check your current pokemon partner to battle and change it if you want')
async def pokemon_partner(ctx):
    userFind = mycol.find_one({"userid": str(ctx.author.id)})
    if userFind == None:
        await ctx.respond(
            f'Neee {ctx.author.name}-nyan, yuk /regist dulu yuk baru liat pokemon..',
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
            InputText(label='Pokemon Name',
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
                    f'https://some-random-api.ml/pokedex?pokemon={name.lower()}'
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

        tempFind = mycol.find_one({"userid": str(ctx.author.id)})
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
            f'https://some-random-api.ml/pokedex?pokemon={partName.lower()}')
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

    panelMsg = await ctx.respond(embed=embedVar, view=view, ephemeral=True)
    checkView = await view.wait()

    if checkView:
        tempFind = mycol.find_one({"userid": str(ctx.author.id)})
        embedEdit = discord.Embed(
            title=f"Poke Partner Timed Out...",
            description=f"Partner : {tempFind['pokemon']}",
            color=0xffff00)
        await panelMsg.edit_original_message(embed=embedEdit, view=None)


@bot.slash_command(
    name='pokeduel',
    description='Find a challenger to battle each other in a Pokemon Duel')
async def pokemon_duel(ctx):
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
            f'https://some-random-api.ml/pokedex?pokemon={poke0.lower()}')
        data0 = json.loads(response0.read())
        response1 = urllib2.urlopen(
            f'https://some-random-api.ml/pokedex?pokemon={poke1.lower()}')
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
                await gameMsg.channel.send(
                    f"Duel telah berakhir karena <@{str(player[1])}> kehabisan waktu!"
                )

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
                await gameMsg.channel.send(
                    f"Duel telah berakhir karena <@{str(player[0])}> kehabisan waktu!"
                )

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


for folder in os.listdir("./") :
  path = f"./{folder}"
  
  if not os.path.isdir(path) :
    continue
    
  for filename in os.listdir(f"./{folder}") :
    if filename.endswith(".py") :
      try : 
        print(f"{folder}.{filename[:-3]}")
        bot.load_extension(f"{folder}.{filename[:-3]}")
      except Exception as error :
        print(error)

keep_alive()
try:
    bot.run(TOKEN)
except:
    os.system("kill 1")
