import discord
import os
import wavelink
from wavelink.ext import spotify
from discord.ui import Select, Button, Modal, InputText, View
from discord.ext import commands
from discord.commands import Option
from StaticVars import Songlist
import re
import requests

URL_REGEX = re.compile(r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)+(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))")

guilds = [990445490401341511, 1020927428459241522, 989086863434334279, 494097970208178186, 1028690906901139486]
SPOTIFYSECRET = os.environ['SPOTIFYSECRET']
SPOTIFYID = os.environ['SPOTIFYID']

mgif = 'https://cdn.discordapp.com/attachments/995337235211763722/1033079306143940709/milk-and-mocha-cute.gif'

def getThumbnail(url):
  request = requests.get(url)
  if request.status_code == 200 :
    return url
  else :
    return mgif

class Songinsert(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    
  @commands.slash_command(name='songinsert', description='Insert track/album/playlist from spotify/youtube to the queue')
  async def song_insert(self, ctx, *, search: Option(str, "Link or key to search for", required=True)):
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

    await ctx.defer()
    decoded = spotify.decode_url(search)

    if decoded:
        if decoded['type'] is spotify.SpotifySearchType.track:
            track = await spotify.SpotifyTrack.search(query=search,
                                                      return_first=True)
            if vc.queue.is_empty and not vc.is_playing():
                setattr(vc, "loop", False)
                await vc.play(track)
                embedVar = discord.Embed(
                            title=f'Now Playing :',
                            description=f"{track.title}",
                            color=0xf2bc00)
                embedVar.set_footer(text=f"Requested by : {ctx.author.name}", icon_url=ctx.author.avatar.url)
                embedVar.set_thumbnail(url=getThumbnail(track.thumb))
                await ctx.respond(embed=embedVar)
            else:
                await vc.queue.put_wait(track)
                Songlist.songList.append([track, ctx.author])
                embedVar = discord.Embed(
                    title=f'Queueing :',
                    description=f"{track.title}",
                    color=0xf2bc00)
                embedVar.set_footer(text=f"Requested by : {ctx.author.name}", icon_url=ctx.author.avatar.url)
                embedVar.set_thumbnail(url=getThumbnail(track.thumb))
                await ctx.respond(embed=embedVar)

        elif decoded['type'] is spotify.SpotifySearchType.album:
            embedVar = discord.Embed(
                title=f'Queueing :',
                description=f"[Spotify Album]({str(search)})\n",
                color=0xf2bc00)
            embedVar.set_footer(text=f"Requested by : {ctx.author.name}", icon_url=ctx.author.avatar.url)
            embedVar.set_thumbnail(url=mgif)
            await ctx.respond(embed=embedVar)
            tracks = await spotify.SpotifyTrack.search(query=search)
            if vc.queue.is_empty and not vc.is_playing():
                setattr(vc, "loop", False)
                index = 0
                for track in tracks:
                    index += 1
                    if index == 1:
                        continue
                    await vc.queue.put_wait(track)
                    Songlist.songList.append([track, ctx.author])

                await vc.play(tracks[0])
                embedVar = discord.Embed(
                            title=f'Now Playing :',
                            description=f"{tracks[0].title}",
                            color=0xf2bc00)
                embedVar.set_footer(text=f"Requested by : {ctx.author.name}", icon_url=ctx.author.avatar.url)
                embedVar.set_thumbnail(url=getThumbnail(tracks[0].thumb))
                await ctx.send(embed=embedVar)

            else:
                for track in tracks:
                    await vc.queue.put_wait(track)
                    Songlist.songList.append([track, ctx.author])

        elif decoded['type'] is spotify.SpotifySearchType.playlist:
            embedVar = discord.Embed(
                title=f'Queueing :',
                description=f"[Spotify Playlist]({str(search)})\n",
                color=0xf2bc00)
            embedVar.set_footer(text=f"Requested by : {ctx.author.name}", icon_url=ctx.author.avatar.url)
            embedVar.set_thumbnail(url=mgif)
            await ctx.respond(embed=embedVar)
            if vc.queue.is_empty and not vc.is_playing():
                index = 0
                setattr(vc, "loop", False)
                async for partial in spotify.SpotifyTrack.iterator(
                        query=search, partial_tracks=True):
                    index += 1
                    if index == 1:
                        await vc.play(partial)
                        embedVar = discord.Embed(
                                    title=f'Now Playing :',
                                    description=f"{partial.title}",
                                    color=0xf2bc00)
                        embedVar.set_footer(text=f"Requested by : {ctx.author.name}", icon_url=ctx.author.avatar.url)
                        embedVar.set_thumbnail(url=getThumbnail(partial.thumb))
                        await ctx.send(embed=embedVar)
                    else:
                        await vc.queue.put_wait(partial)
                        Songlist.songList.append([partial, ctx.author])

            else:
                async for partial in spotify.SpotifyTrack.iterator(
                        query=search, partial_tracks=True):
                    await vc.queue.put_wait(partial)
                    Songlist.songList.append([partial, ctx.author])

    else:
        if 'youtube.com/playlist' in search:
          if not URL_REGEX.match(search):
            search = f'ytsearch: {search}'
          
          playlist = await wavelink.NodePool.get_node().get_playlist(wavelink.YouTubePlaylist, search)

          if not playlist : 
            embedVar = discord.Embed(
                        title=f'{search} not found!',
                        color=0xf2bc00)
            await ctx.respond(embed=embedVar)
            return
          
          embedVar = discord.Embed(
              title=f'Queueing :',
              description=f"[{playlist}]({str(search)})\n",
              color=0xf2bc00)
          embedVar.set_footer(text=f"Requested by : {ctx.author.name}", icon_url=ctx.author.avatar.url)
          embedVar.set_thumbnail(url=mgif)
          await ctx.respond(embed=embedVar)
          if vc.queue.is_empty and not vc.is_playing():
            setattr(vc, "loop", False)
            tempIndex = 0
            for track in playlist.tracks:
              tempIndex += 1
              if tempIndex == 1:
                await vc.play(track)
                embedVar = discord.Embed(
                            title=f'Now Playing :',
                            description=f"{track.title}",
                            color=0xf2bc00)
                embedVar.set_footer(text=f"Requested by : {ctx.author.name}", icon_url=ctx.author.avatar.url)
                embedVar.set_thumbnail(url=getThumbnail(track.thumb))
                await ctx.send(embed=embedVar)
              else:
                await vc.queue.put_wait(track)
                Songlist.songList.append([track, ctx.author])

          else:
            for track in playlist.tracks:
              await vc.queue.put_wait(track)
              Songlist.songList.append([track, ctx.author])

        else:
          if not URL_REGEX.match(search):
            search = f'ytsearch: {search}'
          
          tracks = await wavelink.NodePool.get_node().get_tracks(wavelink.YouTubeTrack, search)

          if not tracks : 
            embedVar = discord.Embed(
                        title=f'{search} not found!',
                        color=0xf2bc00)
            await ctx.respond(embed=embedVar)
            return
            
          searchYt = tracks[0]
          
          if vc.queue.is_empty and not vc.is_playing():
            setattr(vc, "loop", False)
            await vc.play(searchYt)
            embedVar = discord.Embed(
                        title=f'Now Playing :',
                        description=f"{searchYt}",
                        color=0xf2bc00)
            embedVar.set_footer(text=f"Requested by : {ctx.author.name}", icon_url=ctx.author.avatar.url)
            embedVar.set_thumbnail(url=getThumbnail(searchYt.thumb))
            await ctx.respond(embed=embedVar)

          else:
            await vc.queue.put_wait(searchYt)
            Songlist.songList.append([searchYt, ctx.author])
            embedVar = discord.Embed(
                title=f'Queueing :',
                description=f"{searchYt}",
                color=0xf2bc00)
            embedVar.set_footer(text=f"Requested by : {ctx.author.name}", icon_url=ctx.author.avatar.url)
            embedVar.set_thumbnail(url=getThumbnail(searchYt.thumb))
            await ctx.respond(embed=embedVar)

    vc.ctx = ctx

def setup(bot):
  bot.add_cog(Songinsert(bot))