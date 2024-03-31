import discord
import json
import urllib.request as urllib2
from discord.ext import commands
from discord import app_commands


class Lyrics(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name='lyrics',
        description='Generate the lyrics of the song title requested')
    @app_commands.describe(songtitle='The title of the song')
    async def lyrics(self, ctx: discord.Interaction, songtitle: str):
        songsearch = ''.join(e for e in songtitle if e.isalnum() or e == ' ')
        try:
            response = urllib2.urlopen(
                'https://some-random-api.ml/lyrics?title=' +
                songsearch.replace(' ', '-'))
            data = json.loads(response.read())

        except:
            geniusLink = 'https://genius.com/search?q=' + songsearch.replace(
                ' ', '-')
            embed = discord.Embed(
                title=
                f"Gomenasai, watashi kurang canggih sepertinya jadi tidak bisa menemukan lagu '{songtitle}' pencarian anata. Ini watashi cariin di web lain deh ya, silahkan dibuka~",
                description=f"Lyrics : <{geniusLink}>",
                color=ctx.user.color)
            await ctx.response.send_message(embed=embed)
            return

        if len(data['lyrics']) > 4096:
            embed = discord.Embed(
                title=
                f"Gomenasai, lirik lagu '{songtitle}' yang watashi temuin agak kepanjangan, jadi watashi kasih linknya aja yaa~",
                description=f"Lyrics : <{data['links']['genius']}>",
                color=ctx.user.color)
            await ctx.response.send_message(embed=embed)
            return

        embed = discord.Embed(
            title=
            f"Lyrics for '{data['title']}' | Requested by {ctx.user.name}",
            description=data['lyrics'],
            color=ctx.user.color)
        embed.set_thumbnail(url=data['thumbnail']['genius'])
        embed.set_author(name=data['author'])
        await ctx.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Lyrics(bot))
