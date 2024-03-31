import discord
from discord.ext import commands
from discord import app_commands
from discord.commands import Option

guilds = [990445490401341511]

class Pedo(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @app_commands.command(name='pedo', description='Expose a lolicon')
  async def pedo(self, ctx : discord.Interaction, member: Option(discord.Member, "The people you want to accuse", required=True)):
      mentionUser = '<@' + str(member.id) + '>'
      embed = discord.Embed()
      embed.set_image(url='https://some-random-api.ml/canvas/lolice?avatar=' +
                      ctx.user.avatar.url)
      await ctx.response.send_message(f"{mentionUser}", embed=embed)

async def setup(bot):
  await bot.add_cog(Pedo(bot))