import discord
import os
import wavelink
from wavelink.ext import spotify
from discord.ui import Select, Button, Modal, InputText, View
from discord.ext import commands
from discord.commands import Option
import datetime

guilds = [990445490401341511, 1020927428459241522, 989086863434334279, 494097970208178186, 1028690906901139486]
SPOTIFYSECRET = os.environ['SPOTIFYSECRET']
SPOTIFYID = os.environ['SPOTIFYID']

mgif = 'https://cdn.discordapp.com/attachments/995337235211763722/1033079306143940709/milk-and-mocha-cute.gif'

class Songtopinsert(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    
  @commands.slash_command(name='songinserttop', description='Insert track/album/playlist from spotify/youtube to the top of the queue')
  @commands.has_any_role('Encoder Magang', 'Owner')
  async def song_top(self, ctx, *, search: Option(str, "Link or key to search for", required=True)):
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
                            color=0x1DB954)
                embedVar.set_footer(text=f"Requested by : {ctx.author.name}", icon_url=ctx.author.avatar.url)
                embedVar.set_thumbnail(url=mgif)
                await ctx.respond(embed=embedVar)
            else:
                vc.queue.put_at_front(track)
                embedVar = discord.Embed(
                    title=f'Top Queueing :',
                    description=f"{track.title}",
                    color=0x1DB954)
                embedVar.set_footer(text=f"Requested by : {ctx.author.name}", icon_url=ctx.author.avatar.url)
                embedVar.set_thumbnail(url=mgif)
                await ctx.respond(embed=embedVar)

        elif decoded['type'] is spotify.SpotifySearchType.album:
            embedVar = discord.Embed(
                title=f'Top Queueing :',
                description=f"[Spotify Album]({str(search)})\n",
                color=0x1DB954)
            embedVar.set_footer(text=f"Requested by : {ctx.author.name}", icon_url=ctx.author.avatar.url)
            embedVar.set_thumbnail(url=mgif)
            await ctx.respond(embed=embedVar)
            tracks = await spotify.SpotifyTrack.search(query=search)
            if vc.queue.is_empty and not vc.is_playing():
                setattr(vc, "loop", False)
                index = 0
                for track in tracks:
                    if index == 0:
                        continue
                    vc.queue.put_at_index(index, track)
                    index += 1

                await vc.play(tracks[0])
                embedVar = discord.Embed(
                            title=f'Now Playing :',
                            description=f"{tracks[0].title}",
                            color=0x1DB954)
                embedVar.set_footer(text=f"Requested by : {ctx.author.name}", icon_url=ctx.author.avatar.url)
                embedVar.set_thumbnail(url=mgif)
                await ctx.send(embed=embedVar)

            else:
                for track in tracks:
                    vc.queue.put_at_front(track)

        elif decoded['type'] is spotify.SpotifySearchType.playlist:
            embedVar = discord.Embed(
                title=f'Top Queueing :',
                description=f"[Spotify Playlist]({str(search)})\n",
                color=0x1DB954)
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
                                    color=0x1DB954)
                        embedVar.set_footer(text=f"Requested by : {ctx.author.name}", icon_url=ctx.author.avatar.url)
                        embedVar.set_thumbnail(url=mgif)
                        await ctx.send(embed=embedVar)
                    else:
                        vc.queue.put_at_front(partial)

            else:
                async for partial in spotify.SpotifyTrack.iterator(
                        query=search, partial_tracks=True):
                    vc.queue.put_at_front(partial)

    else:
        if 'youtube.com/playlist' in search:
            embedVar = discord.Embed(
                title=f'Top Queueing :',
                description=f"[Youtube Playlist]({str(search)})\n",
                color=0x1DB954)
            embedVar.set_footer(text=f"Requested by : {ctx.author.name}", icon_url=ctx.author.avatar.url)
            embedVar.set_thumbnail(url=mgif)
            await ctx.respond(embed=embedVar)
            search = await wavelink.YouTubePlaylist.search(query=search)
            if vc.queue.is_empty and not vc.is_playing():
                setattr(vc, "loop", False)
                tempIndex = 0
                for track in search.tracks:
                    if tempIndex == 0:
                        await vc.play(track)
                        embedVar = discord.Embed(
                                    title=f'Now Playing :',
                                    description=f"{track.title}",
                                    color=0x1DB954)
                        embedVar.set_footer(text=f"Requested by : {ctx.author.name}", icon_url=ctx.author.avatar.url)
                        embedVar.set_thumbnail(url=mgif)
                        await ctx.send(embed=embedVar)
                    else:
                        vc.queue.put_at_index(tempIndex, track)

                    tempIndex += 1

            else:
              index = 0
              for track in search.tracks:
                vc.queue.put_at_index(index, track)
                index += 1

        else:
            search = await wavelink.YouTubeTrack.search(query=search,
                                                        return_first=True)
            if vc.queue.is_empty and not vc.is_playing():
                setattr(vc, "loop", False)
                await vc.play(search)
                embedVar = discord.Embed(
                            title=f'Now Playing :',
                            description=f"{search.title}",
                            color=0x1DB954)
                embedVar.set_footer(text=f"Requested by : {ctx.author.name}", icon_url=ctx.author.avatar.url)
                embedVar.set_thumbnail(url=mgif)
                await ctx.respond(embed=embedVar)

            else:
                vc.queue.put_at_front(search)
                embedVar = discord.Embed(
                    title=f'Top Queueing :',
                    description=f"{search.title}",
                    color=0x1DB954)
                embedVar.set_footer(text=f"Requested by : {ctx.author.name}", icon_url=ctx.author.avatar.url)
                embedVar.set_thumbnail(url=mgif)
                await ctx.respond(embed=embedVar)

    vc.ctx = ctx

def setup(bot):
  bot.add_cog(Songtopinsert(bot))