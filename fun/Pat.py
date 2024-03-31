import discord
import json
import urllib.request as urllib2
from discord.ext import commands
from discord import app_commands
from discord.commands import Option

guilds = [990445490401341511]

class Pat(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @app_commands.command(name='pat', description='Do an anime patpat')
  async def pat(self, ctx, member: Option(discord.Member, "The one you will patpat", required=False, default=None)):
      response = urllib2.urlopen('https://some-random-api.ml/animu/pat')
      data = json.loads(response.read())
  
      if member == None:
          embed = discord.Embed()
          embed.set_image(url=data['link'])
  
      else:
          mentionUser = '<@' + str(member.id) + '>'
          embed = discord.Embed(description=f"*patpat {mentionUser}*")
          embed.set_image(url=data['link'])
  
      await ctx.response.send_message(embed=embed)

async def setup(bot):
  await bot.add_cog(Pat(bot))