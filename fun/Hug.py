import discord
import json
import urllib.request as urllib2
from discord.ext import commands
from discord import app_commands


class Hug(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='hug', description='Do an anime hug')
    @app_commands.describe(member="The member to hug")
    async def hug(self, ctx: discord.Interaction, member: discord.Member = None):
        try:
            response = urllib2.urlopen('https://some-random-api.ml/animu/hug')
            data = json.loads(response.read())

            if member == None:
                embed = discord.Embed(escription=f"*hugs You*")
            else:
                mentionUser = '<@' + str(member.id) + '>'
                embed = discord.Embed(description=f"*hugs {mentionUser}*")
            embed.set_image(url=data['link'])

            await ctx.response.send_message(embed=embed)
        except Exception as error:
            await ctx.response.send_message("Yang bikin gif anime lg turu")
            print(error)


async def setup(bot):
    await bot.add_cog(Hug(bot))
