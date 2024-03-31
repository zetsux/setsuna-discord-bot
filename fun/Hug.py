import discord
import json
import urllib.request as urllib2
from discord.ext import commands
from discord import app_commands
from discord.commands import Option

guilds = [990445490401341511]

class Hug(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @app_commands.command(name='hug', description='Do an anime hug')
  async def hug(self, ctx, member: Option(discord.Member, "The one you will hug", required=False, default=None)):
      response = urllib2.urlopen('https://some-random-api.ml/animu/hug')
      data = json.loads(response.read())
  
      if member == None:
          embed = discord.Embed()
          embed.set_image(url=data['link'])
  
      else:
          mentionUser = '<@' + str(member.id) + '>'
          embed = discord.Embed(description=f"*hugs {mentionUser}*")
          embed.set_image(url=data['link'])
  
      await ctx.response.send_message(embed=embed)

async def setup(bot):
  await bot.add_cog(Hug(bot))