import discord
import os
import wavelink
from wavelink.ext import spotify
from discord.ui import Select, Button, Modal, TextInput, View
from discord.ext import commands
from discord.commands import Option
import re
import requests
from StaticVars import Songlist

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

class Songinsertto(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    
  @commands.slash_command(name='songinsertto', description='Insert track/album/playlist from spotify/youtube to the inserted position of the queue')
  @commands.has_any_role('Encoder Magang', 'Owner')
  async def song_to(self, ctx, *, search: Option(str, "Link or key to search for", required=True), position: Option(int, "The position to insert song in queue", required=True)):
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
    elif position <= 0 :
      await ctx.respond(
            f'Hmph {ctx.author.name}-nyan, gajelas ah masa positionnya gitu, mulai dari 1 dong..',
            ephemeral=True)
      return
    
    else:
        vc: wavelink.Player = ctx.voice_client

    position -= 1

    if position > len(Songlist.songList) :
      position = len(Songlist.songList)

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
                vc.queue.put_at_index(position, track)
                Songlist.songList.insert(position, [track, ctx.author])
                embedVar = discord.Embed(
                    title=f'Queueing to position {position + 1} :',
                    description=f"{track.title}",
                    color=0xf2bc00)
                embedVar.set_footer(text=f"Requested by : {ctx.author.name}", icon_url=ctx.author.avatar.url)
                embedVar.set_thumbnail(url=getThumbnail(track.thumb))
                await ctx.respond(embed=embedVar)

        elif decoded['type'] is spotify.SpotifySearchType.album:
            embedVar = discord.Embed(
                title=f'Queueing to position {position + 1} :',
                description=f"[Spotify Album]({str(search)})\n",
                color=0xf2bc00)
            embedVar.set_footer(text=f"Requested by : {ctx.author.name}", icon_url=ctx.author.avatar.url)
            embedVar.set_thumbnail(url=mgif)
            await ctx.respond(embed=embedVar)
            tracks = await spotify.SpotifyTrack.search(query=search)
            if vc.queue.is_empty and not vc.is_playing():
                setattr(vc, "loop", False)
                index = position
                for track in tracks:
                    if index == position:
                        await vc.play(tracks[0])
                        embedVar = discord.Embed(
                                    title=f'Now Playing :',
                                    description=f"{tracks[0].title}",
                                    color=0xf2bc00)
                        embedVar.set_footer(text=f"Requested by : {ctx.author.name}", icon_url=ctx.author.avatar.url)
                        embedVar.set_thumbnail(url=getThumbnail(tracks[0].thumb))
                        await ctx.send(embed=embedVar)

                    else :
                      vc.queue.put_at_index(index - 1, track)
                      Songlist.songList.insert(index - 1, [track, ctx.author])

                    index += 1

            else:
                index = position
                for track in tracks:
                  vc.queue.put_at_index(index, track)
                  Songlist.songList.insert(index, [track, ctx.author])
                  index += 1

        elif decoded['type'] is spotify.SpotifySearchType.playlist:
            embedVar = discord.Embed(
                title=f'Queueing to position {position + 1} :',
                description=f"[Spotify Playlist]({str(search)})\n",
                color=0xf2bc00)
            embedVar.set_footer(text=f"Requested by : {ctx.author.name}", icon_url=ctx.author.avatar.url)
            embedVar.set_thumbnail(url=mgif)
            await ctx.respond(embed=embedVar)
            if vc.queue.is_empty and not vc.is_playing():
                index = position
                setattr(vc, "loop", False)
                async for partial in spotify.SpotifyTrack.iterator(
                        query=search, partial_tracks=True):
                    if index == position:
                        await vc.play(partial)
                        embedVar = discord.Embed(
                                    title=f'Now Playing :',
                                    description=f"{partial.title}",
                                    color=0xf2bc00)
                        embedVar.set_footer(text=f"Requested by : {ctx.author.name}", icon_url=ctx.author.avatar.url)
                        embedVar.set_thumbnail(url=getThumbnail(partial.thumb))
                        await ctx.send(embed=embedVar)
                    else:
                        vc.queue.put_at_index(index - 1, partial)
                        Songlist.songList.insert(index - 1, [partial, ctx.author])

                    index += 1

            else:
              index = position
              async for partial in spotify.SpotifyTrack.iterator(
                      query=search, partial_tracks=True):
                  vc.queue.put_at_index(index, partial)
                  Songlist.songList.insert(index, [partial, ctx.author])
                  index += 1

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
                title=f'Queueing to position {position + 1} :',
                description=f"[{playlist}]({str(search)})\n",
                color=0xf2bc00)
            embedVar.set_footer(text=f"Requested by : {ctx.author.name}", icon_url=ctx.author.avatar.url)
            embedVar.set_thumbnail(url=mgif)
            await ctx.respond(embed=embedVar)
            if vc.queue.is_empty and not vc.is_playing():
                setattr(vc, "loop", False)
                tempIndex = position
                for track in playlist.tracks:
                    if tempIndex == position:
                        await vc.play(track)
                        embedVar = discord.Embed(
                                    title=f'Now Playing :',
                                    description=f"{track.title}",
                                    color=0xf2bc00)
                        embedVar.set_footer(text=f"Requested by : {ctx.author.name}", icon_url=ctx.author.avatar.url)
                        embedVar.set_thumbnail(url=getThumbnail(track.thumb))
                        await ctx.send(embed=embedVar)
                    else:
                        vc.queue.put_at_index(tempIndex - 1, track)
                        Songlist.songList.insert(tempIndex - 1, [track, ctx.author])
                    
                    tempIndex += 1

            else:
              index = position
              for track in playlist.tracks:
                vc.queue.put_at_index(index, track)
                Songlist.songList.insert(index, [track, ctx.author])
                index += 1

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
                vc.queue.put_at_index(position, searchYt)
                Songlist.songList.insert(position, [searchYt, ctx.author])
                embedVar = discord.Embed(
                    title=f'Queueing to position {position + 1} :',
                    description=f"{searchYt.title}",
                    color=0xf2bc00)
                embedVar.set_footer(text=f"Requested by : {ctx.author.name}", icon_url=ctx.author.avatar.url)
                embedVar.set_thumbnail(url=getThumbnail(searchYt.thumb))
                await ctx.respond(embed=embedVar)

    vc.ctx = ctx

def setup(bot):
  bot.add_cog(Songinsertto(bot))