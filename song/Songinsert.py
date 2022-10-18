import discord
import os
import wavelink
from wavelink.ext import spotify
from discord.ui import Select, Button, Modal, InputText, View
from discord.ext import commands
from discord.commands import Option

guilds = [990445490401341511, 1020927428459241522, 989086863434334279, 494097970208178186, 1028690906901139486]
SPOTIFYSECRET = os.environ['SPOTIFYSECRET']
SPOTIFYID = os.environ['SPOTIFYID']

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

def setup(bot):
  bot.add_cog(Songinsert(bot))