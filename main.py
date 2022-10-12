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
