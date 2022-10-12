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
          str += f"{folder}.{filename[:-3]}\n"
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


# @bot.slash_command(name='resetcd', description='Reset cooldown of a command for self')
# @commands.has_any_role('Encoder Magang', 'Owner')
# async def reset_cd(ctx, command: Option(str, "Name of command to reset", required=True)):
#   await ctx.defer(ephemeral=True)
#   bot.get_application_command(command).reset_cooldown(ctx)
#   await ctx.respond(f'Cooldown command /{command} pada {ctx.author.name}-nyan berhasil direset!', ephemeral=True)


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