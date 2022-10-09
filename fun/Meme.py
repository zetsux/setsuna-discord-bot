import discord
import json
import urllib.request as urllib2
from discord.ext import commands

guilds = [990445490401341511]

class Meme(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.slash_command(name='meme', description='Randomly generate a meme', guild_ids=guilds)
  async def meme(self, ctx):
      response = urllib2.urlopen('https://some-random-api.ml/meme')
      data = json.loads(response.read())
      embed = discord.Embed(title="Randomly Generated Meme",
                            description=data['caption'],
                            color=ctx.author.color)
      embed.set_image(url=data['image'])
      await ctx.respond(embed=embed)

def setup(bot):
  bot.add_cog(Meme(bot))