import discord
import json
import urllib.request as urllib2
from discord.ext import commands
from discord import app_commands


class Meme(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='meme', description='Randomly generate a meme')
    async def meme(self, ctx: discord.Interaction):
        try:
            response = urllib2.urlopen('https://some-random-api.ml/meme')
            data = json.loads(response.read())
            embed = discord.Embed(title="Randomly Generated Meme",
                                  description=data['caption'],
                                  color=ctx.user.color)
            embed.set_image(url=data['image'])
            await ctx.response.send_message(embed=embed)
        except Exception as error:
            await ctx.response.send_message("Yang bikin meme lg turu")
            print(error)


async def setup(bot):
    await bot.add_cog(Meme(bot))
