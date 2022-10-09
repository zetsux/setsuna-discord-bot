import discord
from discord.ext import commands
from discord.commands import Option

guilds = [990445490401341511]

class Pedo(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.slash_command(name='pedo', description='Expose a lolicon')
  async def pedo(self, ctx, member: Option(discord.Member, "The people you want to accuse", required=True)):
      mentionUser = '<@' + str(member.id) + '>'
      embed = discord.Embed()
      embed.set_image(url='https://some-random-api.ml/canvas/lolice?avatar=' +
                      ctx.user.avatar.url)
      await ctx.respond(f"{mentionUser}", embed=embed)

def setup(bot):
  bot.add_cog(Pedo(bot))