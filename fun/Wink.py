import discord
import json
import urllib.request as urllib2
from discord.ext import commands
from discord.commands import Option

guilds = [990445490401341511]

class Wink(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.slash_command(name='wink', description='Do an anime wink')
  async def wink(self, ctx, member: Option(discord.Member, "The one you will wink to", required=False, default=None)):
      response = urllib2.urlopen('https://some-random-api.ml/animu/wink')
      data = json.loads(response.read())
  
      if member == None:
          embed = discord.Embed()
          embed.set_image(url=data['link'])
  
      else:
          mentionUser = '<@' + str(member.id) + '>'
          embed = discord.Embed(description=f"*winks to {mentionUser}*")
          embed.set_image(url=data['link'])
  
      await ctx.respond(embed=embed)

def setup(bot):
  bot.add_cog(Wink(bot))